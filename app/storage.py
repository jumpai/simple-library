"""Persistence layer for the library application."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable, List

from .models import Book


class LibraryStorage:
    """Handles reading and writing book data to disk."""

    def __init__(self, path: Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._ensure_file()

    def _ensure_file(self) -> None:
        if not self.path.exists():
            self.path.write_text("[]", encoding="utf-8")

    def load_books(self) -> List[Book]:
        data = self.path.read_text(encoding="utf-8").strip()
        if not data:
            return []
        payload = json.loads(data)
        return [self._from_dict(item) for item in payload]

    def save_books(self, books: Iterable[Book]) -> None:
        payload = [self._to_dict(book) for book in books]
        self.path.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")

    @staticmethod
    def _to_dict(book: Book) -> Dict:
        return {
            "isbn": book.isbn,
            "title": book.title,
            "author": book.author,
            "added_at": book.added_at.isoformat(),
            "borrower": book.borrower,
            "borrowed_at": book.borrowed_at.isoformat() if book.borrowed_at else None,
        }

    @staticmethod
    def _from_dict(data: Dict) -> Book:
        added_at = datetime.fromisoformat(data["added_at"])
        borrowed_at = datetime.fromisoformat(data["borrowed_at"]) if data.get("borrowed_at") else None
        return Book(
            isbn=data["isbn"],
            title=data["title"],
            author=data["author"],
            added_at=added_at,
            borrower=data.get("borrower"),
            borrowed_at=borrowed_at,
        )
