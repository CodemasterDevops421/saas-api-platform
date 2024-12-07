from typing import TypeVar, Generic, Sequence
from fastapi import Query
from pydantic import BaseModel

T = TypeVar('T')

class PageParams:
    def __init__(
        self,
        page: int = Query(1, ge=1),
        size: int = Query(50, ge=1, le=100)
    ):
        self.page = page
        self.size = size
        self.offset = (page - 1) * size

class Page(BaseModel, Generic[T]):
    items: Sequence[T]
    total: int
    page: int
    size: int
    pages: int