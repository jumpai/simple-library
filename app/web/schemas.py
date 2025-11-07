"""Pydantic schemas for the web API layer."""

from __future__ import annotations

from datetime import datetime
from typing import Iterable, List

from pydantic import BaseModel, Field, field_validator

from app.models import Book
from app.utils import normalize_isbn


class BookCreate(BaseModel):
    isbn: str = Field(..., description="Book ISBN identifier.")
    title: str = Field(..., min_length=1, description="Title of the book.")
    author: str = Field(..., min_length=1, description="Author of the book.")

    @field_validator("isbn")
    def _normalize_isbn(cls, value: str) -> str:
        return normalize_isbn(value)


class BookResponse(BaseModel):
    isbn: str
    title: str
    author: str
    added_at: datetime
    available: bool
    borrower: str | None = None
    borrowed_at: datetime | None = None

    @classmethod
    def from_book(cls, book: Book) -> "BookResponse":
        return cls(
            isbn=book.isbn,
            title=book.title,
            author=book.author,
            added_at=book.added_at,
            available=book.is_available,
            borrower=book.borrower,
            borrowed_at=book.borrowed_at,
        )


class CatalogImport(BaseModel):
    books: List[BookCreate]


class BorrowRequest(BaseModel):
    borrower: str = Field(..., min_length=1, description="Name of the borrower.")


class SummaryItem(BaseModel):
    author: str
    count: int


class SummaryResponse(BaseModel):
    items: List[SummaryItem]

    @classmethod
    def from_usage(cls, usage: dict[str, int]) -> "SummaryResponse":
        items = [SummaryItem(author=author, count=count) for author, count in usage.items()]
        return cls(items=items)


def serialize_books(books: Iterable[Book]) -> List[BookResponse]:
    """Convert iterable of ``Book`` instances into serialized responses."""
    return [BookResponse.from_book(book) for book in books]
