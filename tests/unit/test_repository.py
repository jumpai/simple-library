import pytest

from app.exceptions import BookAlreadyExistsError, BookNotFoundError
from app.models import Book
from app.repository import LibraryRepository
from app.storage import LibraryStorage


@pytest.fixture()
def repository(tmp_path):
    storage = LibraryStorage(tmp_path / "library.json")
    return LibraryRepository(storage)


def test_add_and_get_book(repository):
    book = Book(isbn="123", title="Test Book", author="Author")
    repository.add(book)
    fetched = repository.get("123")
    assert fetched.title == "Test Book"


def test_add_duplicate_book_raises(repository):
    book = Book(isbn="123", title="A", author="B")
    repository.add(book)
    with pytest.raises(BookAlreadyExistsError):
        repository.add(Book(isbn="123", title="Another", author="B"))


def test_remove_book(repository):
    book = Book(isbn="123", title="A", author="B")
    repository.add(book)
    repository.remove("123")
    with pytest.raises(BookNotFoundError):
        repository.get("123")


def test_find_by_author(repository):
    repository.add(Book(isbn="1", title="A", author="Jane Doe"))
    repository.add(Book(isbn="2", title="B", author="John Roe"))
    matches = repository.find_by_author("jane")
    assert len(matches) == 1
    assert matches[0].title == "A"


def test_find_available(repository):
    available = Book(isbn="1", title="A", author="A")
    borrowed = Book(isbn="2", title="B", author="B")
    borrowed.checkout("Alice")
    repository.add(available)
    repository.add(borrowed)
    result = repository.find_available()
    assert [book.isbn for book in result] == ["1"]
