"""Custom exceptions used across the library application."""


class LibraryError(Exception):
    """Base exception for library related errors."""


class BookNotFoundError(LibraryError):
    """Raised when a book cannot be located."""


class BookAlreadyExistsError(LibraryError):
    """Raised when an attempt is made to add a duplicate book."""


class BookUnavailableError(LibraryError):
    """Raised when a book is not available for the requested action."""
