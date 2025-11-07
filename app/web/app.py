"""Factory for the FastAPI application."""

from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Depends, FastAPI, HTTPException, Response, status
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.config import AppConfig
from app.exceptions import BookAlreadyExistsError, BookNotFoundError, BookUnavailableError
from app.services import LibraryService

from .schemas import BookCreate, BookResponse, BorrowRequest, CatalogImport, SummaryResponse, serialize_books


def create_app(config: AppConfig | None = None, service: LibraryService | None = None) -> FastAPI:
    """Create and configure the FastAPI app."""
    app = FastAPI(title="Simple Library API", version="0.1.0")
    app.state.service = service or LibraryService(config=config)

    def get_service() -> LibraryService:
        return app.state.service

    router = APIRouter()

    project_root = Path(__file__).resolve().parents[2]
    dist_dir = project_root / "frontend" / "dist"
    index_file = dist_dir / "index.html"

    assets_dir = dist_dir / "assets"
    if dist_dir.exists() and index_file.exists():
        if assets_dir.exists():
            app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

        @router.get("/", include_in_schema=False)
        def serve_index() -> FileResponse:
            return FileResponse(index_file)
    else:
        @router.get("/", tags=["meta"])
        def root() -> dict[str, str]:
            return {"message": "Simple Library API"}

    @router.get("/health", tags=["meta"])
    def health_check() -> dict[str, str]:
        return {"status": "ok"}

    @router.get("/books", response_model=list[BookResponse], tags=["books"])
    def list_books(
        available_only: bool = False,
        svc: LibraryService = Depends(get_service),
    ) -> list[BookResponse]:
        books = svc.list_books(available_only=available_only)
        return serialize_books(books)

    @router.post("/books", response_model=BookResponse, status_code=status.HTTP_201_CREATED, tags=["books"])
    def create_book(payload: BookCreate, svc: LibraryService = Depends(get_service)) -> BookResponse:
        try:
            book = svc.register_book(payload.isbn, payload.title, payload.author)
        except BookAlreadyExistsError as exc:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
        return BookResponse.from_book(book)

    @router.get("/books/{isbn}", response_model=BookResponse, tags=["books"])
    def get_book(isbn: str, svc: LibraryService = Depends(get_service)) -> BookResponse:
        try:
            book = svc.get_book(isbn)
        except BookNotFoundError as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
        return BookResponse.from_book(book)

    @router.delete(
        "/books/{isbn}",
        status_code=status.HTTP_204_NO_CONTENT,
        response_class=Response,
        tags=["books"],
    )
    def delete_book(isbn: str, svc: LibraryService = Depends(get_service)) -> Response:
        try:
            svc.remove_book(isbn)
        except BookNotFoundError as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    @router.post(
        "/books/{isbn}/borrow",
        response_model=BookResponse,
        tags=["circulation"],
    )
    def borrow_book(isbn: str, payload: BorrowRequest, svc: LibraryService = Depends(get_service)) -> BookResponse:
        try:
            book = svc.borrow_book(isbn, payload.borrower)
        except BookUnavailableError as exc:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
        except BookNotFoundError as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
        return BookResponse.from_book(book)

    @router.post(
        "/books/{isbn}/return",
        response_model=BookResponse,
        tags=["circulation"],
    )
    def return_book(isbn: str, svc: LibraryService = Depends(get_service)) -> BookResponse:
        try:
            book = svc.return_book(isbn)
        except BookUnavailableError as exc:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
        except BookNotFoundError as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
        return BookResponse.from_book(book)

    @router.get("/books/search", response_model=list[BookResponse], tags=["books"])
    def search_books(
        title: str | None = None,
        author: str | None = None,
        svc: LibraryService = Depends(get_service),
    ) -> list[BookResponse]:
        if title:
            books = svc.search_by_title(title)
        elif author:
            books = svc.search_by_author(author)
        else:
            books = svc.list_books()
        return serialize_books(books)

    @router.get("/summary", response_model=SummaryResponse, tags=["reports"])
    def summary(svc: LibraryService = Depends(get_service)) -> SummaryResponse:
        usage = svc.usage_summary()
        return SummaryResponse.from_usage(usage)

    @router.post("/import", response_model=list[BookResponse], tags=["books"])
    def import_catalog(payload: CatalogImport, svc: LibraryService = Depends(get_service)) -> list[BookResponse]:
        books = svc.import_catalog([book.model_dump() for book in payload.books])
        return serialize_books(books)

    @router.delete(
        "/catalog",
        status_code=status.HTTP_204_NO_CONTENT,
        response_class=Response,
        tags=["books"],
    )
    def reset_catalog(svc: LibraryService = Depends(get_service)) -> Response:
        svc.reset_catalog()
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    app.include_router(router)

    if dist_dir.exists() and index_file.exists():

        @app.get("/{path:path}", include_in_schema=False)
        def serve_spa_fallback(path: str) -> FileResponse:
            static_prefixes = {"books", "summary", "import", "catalog", "health"}
            first_segment = path.split("/", 1)[0]
            if first_segment in static_prefixes or first_segment == "":
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")
            return FileResponse(index_file)

    return app
