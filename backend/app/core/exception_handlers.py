"""Global exception handlers for the FastAPI application.

Wired into ``create_app()`` via ``register_exception_handlers(app)``.

Two handlers cover the unhandled-exception surface:
  - ``OperationalError``  → 503  (database-connectivity failure, §22.1)
  - ``Exception``         → 500  (any other unexpected error, generic message)

Both return the same envelope: ``{"error": "<message>", "request_id": "<uuid>"}``.

A lightweight middleware assigns ``request.state.request_id`` once per request so
both handlers can echo it back, letting operators correlate a client-visible error
with the matching ``logger.error()`` line in stderr.

NON-GOALS (explicitly deferred to Phase 19 per the spec):
  - Structured-log ``extra`` fields on the JSONFormatter
  - Coordinate redaction in the app log
  - Rate limiting

NOTE: this module intentionally does NOT touch any of the codebase's existing,
deliberate HTTPException raises (coordinate-validation 422, facility-not-found 404,
health-endpoint 503, etc.).  FastAPI resolves its own ``HTTPException`` handler
before reaching the ``Exception`` catch-all here.
"""

import logging
import uuid

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import OperationalError

logger = logging.getLogger(__name__)


async def _assign_request_id(request: Request, call_next):
    """Middleware: stamp every request with a fresh UUID before any handler runs."""
    request.state.request_id = str(uuid.uuid4())
    return await call_next(request)


async def _operational_error_handler(request: Request, exc: OperationalError) -> JSONResponse:
    """Map database-connectivity failures to 503.

    §22.1: "The service is temporarily unavailable."
    The real exception detail (including the connection string fragment SQLAlchemy
    may include in the message) is kept server-side in the structured log only —
    never forwarded to the client.
    """
    request_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    logger.error(f"Database operational error [request_id={request_id}]", exc_info=True)
    return JSONResponse(
        status_code=503,
        content={
            "error": "The service is temporarily unavailable.",
            "request_id": request_id,
        },
    )


async def _unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Catch-all for any exception not handled by a more specific handler.

    Returns 500 with a deliberately generic message — no exception detail, type
    name, or traceback is forwarded to the client.  The full detail (including
    ``exc_info``) goes to the existing stderr JSON logger only.
    """
    request_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    logger.error(f"Unhandled exception [request_id={request_id}]", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "An unexpected error occurred.",
            "request_id": request_id,
        },
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Wire middleware and exception handlers into a FastAPI application.

    Call once from ``create_app()``, alongside CORS middleware registration.
    Order matters: the middleware is registered first (so ``request_id`` is
    always set before any handler reads it), then the two exception handlers.
    FastAPI dispatches to the most-specific registered handler for a given
    exception's MRO, so ``OperationalError`` (a subclass of ``Exception``)
    correctly reaches the 503 handler, not the generic 500 one.
    """
    app.middleware("http")(_assign_request_id)
    app.add_exception_handler(OperationalError, _operational_error_handler)
    app.add_exception_handler(Exception, _unhandled_exception_handler)
