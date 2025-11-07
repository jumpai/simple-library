"""Command line interface for the library application."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Iterable

from .config import load_config
from .exceptions import BookAlreadyExistsError, BookNotFoundError, BookUnavailableError
from .services import LibraryService


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Simple Library Manager")
    parser.add_argument(
        "--config",
        dest="config_file",
        help="Optional configuration file with overrides (JSON format).",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    add_parser = subparsers.add_parser("add", help="Register a new book.")
    add_parser.add_argument("isbn")
    add_parser.add_argument("title")
    add_parser.add_argument("author")

    list_parser = subparsers.add_parser("list", help="List books in the catalog.")
    list_parser.add_argument("--available", action="store_true", help="Only show available books.")

    borrow_parser = subparsers.add_parser("borrow", help="Borrow a book.")
    borrow_parser.add_argument("isbn")
    borrow_parser.add_argument("borrower")

    return_parser = subparsers.add_parser("return", help="Return a borrowed book.")
    return_parser.add_argument("isbn")

    search_parser = subparsers.add_parser("search", help="Search for books by title.")
    search_parser.add_argument("fragment")

    author_parser = subparsers.add_parser("author", help="Find books by author.")
    author_parser.add_argument("author")

    subparsers.add_parser("summary", help="Show summary statistics.")

    import_parser = subparsers.add_parser("import", help="Import a catalog from a JSON file.")
    import_parser.add_argument("file")

    subparsers.add_parser("reset", help="Clear the catalog.")

    return parser


def load_overrides(config_file: str | None) -> dict:
    if not config_file:
        return {}
    path = Path(config_file)
    if not path.exists():
        raise FileNotFoundError(f"Configuration file {config_file} does not exist.")
    return json.loads(path.read_text(encoding="utf-8"))


def create_service(args: argparse.Namespace) -> LibraryService:
    base_config = load_config()
    overrides = load_overrides(args.config_file)
    if "data_file" in overrides:
        from dataclasses import replace

        base_config = replace(base_config, data_file=Path(overrides["data_file"]))
    if "autosave" in overrides:
        from dataclasses import replace

        autosave_value = overrides["autosave"]
        if isinstance(autosave_value, str):
            autosave = autosave_value.lower() in {"1", "true", "yes", "on"}
        else:
            autosave = bool(autosave_value)
        base_config = replace(base_config, autosave=autosave)
    return LibraryService(config=base_config)


def main(argv: Iterable[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    service = create_service(args)

    try:
        if args.command == "add":
            book = service.register_book(args.isbn, args.title, args.author)
            print(f"Added {book.title} ({book.isbn}) by {book.author}")
        elif args.command == "list":
            print(service.render_catalog_table(available_only=args.available))
        elif args.command == "borrow":
            book = service.borrow_book(args.isbn, args.borrower)
            print(f"{book.title} borrowed by {book.borrower}")
        elif args.command == "return":
            book = service.return_book(args.isbn)
            print(f"{book.title} returned")
        elif args.command == "search":
            books = service.search_by_title(args.fragment)
            if books:
                print(service.render_catalog_table(books=books))
            else:
                print("No matches found.")
        elif args.command == "author":
            books = service.search_by_author(args.author)
            if books:
                print(service.render_catalog_table(books=books))
            else:
                print("No matches found.")
        elif args.command == "summary":
            summary = service.usage_summary()
            for author, count in summary.items():
                print(f"{author}: {count} book(s)")
        elif args.command == "import":
            payload = json.loads(Path(args.file).read_text(encoding="utf-8"))
            service.import_catalog(payload)
            print(f"Imported {len(payload)} books.")
        elif args.command == "reset":
            service.reset_catalog()
            print("Catalog cleared.")
        else:
            parser.print_help()
            return 1
    except FileNotFoundError as exc:
        parser.error(str(exc))
    except BookAlreadyExistsError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    except BookUnavailableError as exc:
        print(str(exc), file=sys.stderr)
        return 3
    except BookNotFoundError as exc:
        print(str(exc), file=sys.stderr)
        return 4

    return 0


if __name__ == "__main__":
    sys.exit(main())
