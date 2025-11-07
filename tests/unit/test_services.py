import pytest

from app.config import AppConfig
from app.exceptions import BookUnavailableError
from app.services import LibraryService


@pytest.fixture()
def service(tmp_path):
    config = AppConfig(data_file=tmp_path / "catalog.json", autosave=True)
    svc = LibraryService(config=config)
    svc.reset_catalog()
    return svc


def test_register_and_list(service):
    service.register_book("123", "Test Book", "Author")
    books = service.list_books()
    assert len(books) == 1
    assert books[0].title == "Test Book"


def test_borrow_and_return_flow(service):
    service.register_book("123", "Test Book", "Author")
    borrowed = service.borrow_book("123", "Alice")
    assert borrowed.borrower == "Alice"
    returned = service.return_book("123")
    assert returned.is_available


def test_borrowing_unavailable_book_fails(service):
    service.register_book("123", "Test Book", "Author")
    service.borrow_book("123", "Alice")
    with pytest.raises(BookUnavailableError):
        service.borrow_book("123", "Bob")


def test_search_by_title(service):
    service.import_catalog(
        [
            {"isbn": "1", "title": "The First Book", "author": "Author A"},
            {"isbn": "2", "title": "Another Tale", "author": "Author B"},
        ]
    )
    matches = service.search_by_title("first")
    assert len(matches) == 1
    assert matches[0].title == "The First Book"


def test_usage_summary(service):
    service.import_catalog(
        [
            {"isbn": "1", "title": "One", "author": "Author"},
            {"isbn": "2", "title": "Two", "author": "Author"},
            {"isbn": "3", "title": "Three", "author": "Someone Else"},
        ]
    )
    summary = service.usage_summary()
    assert summary["Author"] == 2


def test_default_catalog_seeded(tmp_path):
    config = AppConfig(data_file=tmp_path / "seeded.json", autosave=True)
    seeded_service = LibraryService(config=config)
    defaults = seeded_service.list_books()
    assert len(defaults) >= 5


def test_default_catalog_top_up(tmp_path):
    config = AppConfig(data_file=tmp_path / "topup.json", autosave=True)
    initial_service = LibraryService(config=config)
    initial_service.reset_catalog()
    initial_service.register_book("111", "Custom Title", "Custom Author")

    refreshed_service = LibraryService(config=config)
    titles = {book.title for book in refreshed_service.list_books()}
    assert "Custom Title" in titles
    expected_titles = {
        "The Alchemist",
        "Pride and Prejudice",
        "The Girl with the Dragon Tattoo",
        "Harry Potter and the Philosopher's Stone",
        "To Kill a Mockingbird",
    }
    assert expected_titles.issubset(titles)
