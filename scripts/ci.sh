#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "Running Python tests..."
cd "$ROOT_DIR"
python3 -m pytest

echo "Building frontend..."
cd "$ROOT_DIR/frontend"
npm ci
npm run build

echo "Building Docker image..."
cd "$ROOT_DIR"
docker build -t simple-library-app-ci .
