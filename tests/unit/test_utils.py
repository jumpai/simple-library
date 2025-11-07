import pytest

from app.utils import chunked, normalize_isbn, tabulate


def test_normalize_isbn_removes_separators():
    assert normalize_isbn("978-0-14-312854-0") == "9780143128540"


def test_normalize_isbn_upper_cases():
    assert normalize_isbn("abc123x") == "ABC123X"


def test_chunked_splits_sequence():
    assert chunked([1, 2, 3, 4, 5], 2) == [[1, 2], [3, 4], [5]]


def test_chunked_invalid_size():
    with pytest.raises(ValueError):
        chunked([1, 2, 3], 0)


def test_tabulate_formats_table():
    output = tabulate([(1, "Book")], headers=("ID", "Title"))
    assert "ID" in output
    assert "Book" in output
