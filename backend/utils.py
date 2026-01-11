from typing import TypeVar, Generic, List, Optional
from pydantic import BaseModel, Field
from sqlalchemy.orm import Query

T = TypeVar("T")

class Page(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    size: int
    pages: int

def paginate(query: Query, page: int = 1, size: int = 20) -> Page:
    if page < 1:
        page = 1
    if size < 1:
        size = 20
    
    total = query.count()
    pages = (total + size - 1) // size
    
    items = query.offset((page - 1) * size).limit(size).all()
    
    return Page(
        items=items,
        total=total,
        page=page,
        size=size,
        pages=pages
    )
