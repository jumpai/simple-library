"""Service layer containing application business logic."""

from __future__ import annotations

from collections import Counter
from dataclasses import asdict
from typing import Dict, Iterable, List, Optional

from .config import AppConfig
from .data import default_catalog
from .exceptions import BookNotFoundError, BookUnavailableError
from .models import Book
from .repository import LibraryRepository
from .storage import LibraryStorage
from .utils import normalize_isbn, tabulate


class LibraryService:
    """Provides operations for managing the library catalog."""

    def __init__(self, config: Optional[AppConfig] = None, repository: Optional[LibraryRepository] = None) -> None:
        self.config = config or AppConfig.default()
        self.repository = repository or LibraryRepository(LibraryStorage(self.config.data_file))
        self._initialize_defaults()

    # Catalog management -------------------------------------------------

    def register_book(self, isbn: str, title: str, author: str) -> Book:
        """Register a new book in the catalog."""
        normalized = normalize_isbn(isbn)
        book = Book(isbn=normalized, title=title.strip(), author=author.strip())
        self.repository.add(book, autosave=self.config.autosave)
        return book

    def remove_book(self, isbn: str) -> None:
        """Remove a book entirely from the catalog."""
        self.repository.remove(isbn, autosave=self.config.autosave)

    def list_books(self, available_only: bool = False) -> List[Book]:
        """List all books, optionally filtering to those currently available."""
        if available_only:
            return self.repository.find_available()
        return self.repository.list_books()

    # Circulation --------------------------------------------------------

    def borrow_book(self, isbn: str, borrower: str) -> Book:
        """Borrow a book for the specified borrower."""
        book = self.repository.get(isbn)
        if not book.is_available:
            raise BookUnavailableError(f"Book '{book.title}' is already borrowed by {book.borrower}.")
        book.checkout(borrower)
        self.repository.update(book, autosave=self.config.autosave)
        return book

    def return_book(self, isbn: str) -> Book:
        """Return a previously borrowed book to the catalog."""
        book = self.repository.get(isbn)
        if book.is_available:
            raise BookUnavailableError(f"Book '{book.title}' is not currently borrowed.")
        book.checkin()
        self.repository.update(book, autosave=self.config.autosave)
        return book

    # Discovery ----------------------------------------------------------

    def search_by_author(self, author: str) -> List[Book]:
        """Return all books where the author string matches."""
        return self.repository.find_by_author(author)

    def search_by_title(self, fragment: str) -> List[Book]:
        """Return all books whose title contains the fragment."""
        fragment_lower = fragment.lower()
        return [book for book in self.repository.snapshot() if fragment_lower in book.title.lower()]

    def get_book(self, isbn: str) -> Book:
        """Fetch a single book by ISBN."""
        return self.repository.get(isbn)

    # Reporting ----------------------------------------------------------

    def catalog_snapshot(self) -> List[Dict]:
        """Return a serializable snapshot of the catalog."""
        return [self._book_to_dict(book) for book in self.repository.snapshot()]

    def usage_summary(self) -> Dict[str, int]:
        """Return a summary of usage statistics grouped by author."""
        authors = [book.author for book in self.repository.snapshot()]
        return dict(Counter(authors))

    def render_catalog_table(self, books: Optional[Iterable[Book]] = None, available_only: bool = False) -> str:
        """Return a human-readable table of the catalog."""
        if books is None:
            books = self.list_books(available_only=available_only)
        else:
            books = list(books)
        rows = [
            (
                book.isbn,
                book.title,
                book.author,
                "yes" if book.is_available else f"no ({book.borrower})",
            )
            for book in books
        ]
        headers = ("ISBN", "Title", "Author", "Available")
        return tabulate(rows, headers=headers)

    # Utilities ----------------------------------------------------------

    def import_catalog(self, books: Iterable[Dict[str, str]]) -> List[Book]:
        """Bulk import books, replacing existing catalog."""
        imported = []
        for entry in books:
            book = Book(
                isbn=normalize_isbn(entry["isbn"]),
                title=entry["title"].strip(),
                author=entry["author"].strip(),
            )
            imported.append(book)
        self.repository.save_all(imported)
        return imported

    def reset_catalog(self) -> None:
        """Clear the catalog entirely."""
        self.repository.save_all([])

    @staticmethod
    def _book_to_dict(book: Book) -> Dict:
        data = asdict(book)
        data["added_at"] = book.added_at.isoformat()
        data["borrowed_at"] = book.borrowed_at.isoformat() if book.borrowed_at else None
        return data

    def _initialize_defaults(self) -> None:
        """Seed the catalog with default books when empty."""
        existing_isbns = {book.isbn for book in self.repository.snapshot()}
        missing_entries = [
            entry for entry in default_catalog() if normalize_isbn(entry["isbn"]) not in existing_isbns
        ]
        if not missing_entries:
            return
        for entry in missing_entries:
            book = Book(
                isbn=normalize_isbn(entry["isbn"]),
                title=entry["title"],
                author=entry["author"],
            )
            self.repository.add(book, autosave=self.config.autosave)
