# Simple Library Application

A deceptively simple looking application for managing a personal library catalog. The code base is intentionally structured into several layers (configuration, persistence, repository, services, CLI, web API) to showcase a medium-sized Python project while keeping the surface level workflow easy to follow.

## Features

- Launch with a seeded catalog of five classics so the UI never looks empty.
- Register, list, borrow, and return books through a REST API or CLI.
- Search by title fragments or author names.
- Import/export friendly catalog snapshot.
- JSON-backed storage with configurable location.

## Usage

### Web API

```bash
uvicorn "app.web.app:create_app" --factory --reload
```

The API will automatically seed the catalog with:

- *The Alchemist* — Paulo Coelho
- *Pride and Prejudice* — Jane Austen
- *The Girl with the Dragon Tattoo* — Stieg Larsson
- *Harry Potter and the Philosopher's Stone* — J.K. Rowling
- *To Kill a Mockingbird* — Harper Lee

In a separate terminal, start the React frontend (Node.js ≥ 18):

```bash
cd frontend
npm install   # or npm ci
npm run dev
```

The development server proxies API calls to `http://localhost:8000`, so you can visit the UI at the port printed by Vite (default `http://localhost:5173`). Build for production with `npm run build`, which outputs static assets under `frontend/dist/`.

When `frontend/dist/` exists, the FastAPI app will serve the static bundle directly at `/`, so deploying the backend after a `npm run build` gives you the full UI + API from a single process.

Example API requests:

```bash
curl -X POST http://localhost:8000/books \
  -H "Content-Type: application/json" \
  -d '{"isbn":"9780143128540","title":"Sapiens","author":"Yuval Noah Harari"}'

curl http://localhost:8000/books?available_only=true
curl -X POST http://localhost:8000/books/9780143128540/borrow -d '{"borrower":"Alice"}'
curl http://localhost:8000/summary
```

### CLI

```bash
python -m app.cli add 9780143128540 "Sapiens" "Yuval Noah Harari"
python -m app.cli list --available
python -m app.cli borrow 9780143128540 "Alice"
python -m app.cli summary
```

Set `LIBAPP_DATA_FILE=/path/to/catalog.json` to customize the storage location used by both the CLI and web server.

## Tests

```bash
pytest
```

## Continuous Integration

A simple CI harness is provided at `scripts/ci.sh` to exercise both the backend tests and the frontend build. Make it executable (`chmod +x scripts/ci.sh`) and run it from the project root:

```bash
./scripts/ci.sh
```

## Docker Deployment

Build and run the entire stack (backend + prebuilt React frontend) with Docker:

```bash
docker build -t simple-library-app .
docker run -p 8000:8000 --env PORT=8000 simple-library-app
```

The container entrypoint launches `uvicorn` with the bundled static assets served at `/`. Visit `http://localhost:8000/` after the container starts to interact with the UI.
