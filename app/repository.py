"""Repository abstraction for managing books."""

from __future__ import annotations

from typing import Dict, Iterable, List, Optional

from .exceptions import BookAlreadyExistsError, BookNotFoundError
from .models import Book
from .storage import LibraryStorage
from .utils import normalize_isbn


class LibraryRepository:
    """In-memory repository backed by ``LibraryStorage``."""

    def __init__(self, storage: LibraryStorage) -> None:
        self.storage = storage
        self._books: Dict[str, Book] = {}
        self._load()

    def _load(self) -> None:
        for book in self.storage.load_books():
            self._books[book.isbn] = book

    def _persist(self) -> None:
        self.storage.save_books(self._books.values())

    def list_books(self) -> List[Book]:
        return sorted(self._books.values(), key=lambda book: book.added_at)

    def get(self, isbn: str) -> Book:
        key = normalize_isbn(isbn)
        if key not in self._books:
            raise BookNotFoundError(f"Book with ISBN {isbn} not found")
        return self._books[key]

    def add(self, book: Book, autosave: bool = True) -> None:
        key = normalize_isbn(book.isbn)
        if key in self._books:
            raise BookAlreadyExistsError(f"Book with ISBN {book.isbn} already exists")
        book.isbn = key
        self._books[key] = book
        if autosave:
            self._persist()

    def remove(self, isbn: str, autosave: bool = True) -> None:
        key = normalize_isbn(isbn)
        if key not in self._books:
            raise BookNotFoundError(f"Book with ISBN {isbn} not found")
        del self._books[key]
        if autosave:
            self._persist()

    def find_by_author(self, author: str) -> List[Book]:
        author_lower = author.lower()
        return [book for book in self._books.values() if author_lower in book.author.lower()]

    def find_available(self) -> List[Book]:
        return [book for book in self._books.values() if book.is_available]

    def snapshot(self) -> List[Book]:
        return list(self._books.values())

    def update(self, book: Book, autosave: bool = True) -> None:
        key = normalize_isbn(book.isbn)
        if key not in self._books:
            raise BookNotFoundError(f"Book with ISBN {book.isbn} not found")
        book.isbn = key
        self._books[key] = book
        if autosave:
            self._persist()

    def save_all(self, books: Iterable[Book]) -> None:
        self._books = {normalize_isbn(book.isbn): book for book in books}
        self._persist()
