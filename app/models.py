"""Domain models for the library application."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Book:
    """Represents a book entry in the catalog."""

    isbn: str
    title: str
    author: str
    added_at: datetime = field(default_factory=datetime.utcnow)
    borrower: Optional[str] = None
    borrowed_at: Optional[datetime] = None

    def checkout(self, borrower: str) -> None:
        """Mark the book as borrowed by the given user."""
        self.borrower = borrower
        self.borrowed_at = datetime.utcnow()

    def checkin(self) -> None:
        """Return the book to the catalog."""
        self.borrower = None
        self.borrowed_at = None

    @property
    def is_available(self) -> bool:
        """A book is available when it has no borrower."""
        return self.borrower is None
