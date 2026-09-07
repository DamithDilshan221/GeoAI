from pydantic import BaseModel


class CategoryRead(BaseModel):
    id: int
    code: str
    label: str
