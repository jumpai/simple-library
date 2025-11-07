# syntax=docker/dockerfile:1.7

FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json ./ 
RUN npm ci
COPY frontend/ ./
RUN npm run build

FROM python:3.13-slim AS backend-base
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends build-essential && rm -rf /var/lib/apt/lists/*
COPY requirements.txt pyproject.toml README.md ./ 
RUN pip install --no-cache-dir -r requirements.txt && pip install --no-cache-dir .

FROM backend-base AS runtime
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist
COPY app ./app
COPY scripts ./scripts
COPY tests ./tests
ENV PORT=8000
EXPOSE 8000
CMD ["uvicorn", "app.web.app:create_app", "--factory", "--host", "0.0.0.0", "--port", "8000"]
