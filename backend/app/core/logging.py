"""Structured (JSON) logging configuration.

Sets up Python's standard logging module with a JSON formatter so that
log output is machine-parseable from day one.  The default level is INFO;
override via the LOG_LEVEL environment variable if needed.

NOTE: Raw coordinates and stack traces must NEVER appear in client-facing
responses.  That rule is enforced starting Phase 19 — this comment exists
so it isn't forgotten during implementation.
"""

import json
import logging
import sys
from datetime import UTC, datetime


class JSONFormatter(logging.Formatter):
    """Emit each log record as a single JSON object."""

    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": datetime.now(tz=UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info and record.exc_info[1] is not None:
            log_entry["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_entry)


def setup_logging(level: str = "INFO") -> None:
    """Configure the root logger with JSON output to stderr."""
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(JSONFormatter())

    root = logging.getLogger()
    root.setLevel(getattr(logging, level.upper(), logging.INFO))
    root.handlers.clear()
    root.addHandler(handler)
