"""Static data used across the application."""

from __future__ import annotations

from typing import Sequence


def default_catalog() -> Sequence[dict[str, str]]:
    """Return the default catalog seeded on first run."""
    return [
        {"isbn": "9780143127741", "title": "The Alchemist", "author": "Paulo Coelho"},
        {"isbn": "9780679783268", "title": "Pride and Prejudice", "author": "Jane Austen"},
        {"isbn": "9780307474278", "title": "The Girl with the Dragon Tattoo", "author": "Stieg Larsson"},
        {"isbn": "9780747532743", "title": "Harry Potter and the Philosopher's Stone", "author": "J.K. Rowling"},
        {"isbn": "9780061120084", "title": "To Kill a Mockingbird", "author": "Harper Lee"},
    ]
