import os
from pathlib import Path
from typing import Iterator

import pytest
from fastapi.testclient import TestClient

from app.config import AppConfig
from app.web.app import create_app


@pytest.fixture()
def tmp_catalog_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Iterator[Path]:
    path = tmp_path / "catalog.json"
    monkeypatch.setenv("LIBAPP_DATA_FILE", str(path))
    yield path
    if "LIBAPP_DATA_FILE" in os.environ:
        monkeypatch.delenv("LIBAPP_DATA_FILE", raising=False)


@pytest.fixture()
def api_client(tmp_path: Path) -> Iterator[TestClient]:
    config = AppConfig(data_file=tmp_path / "api_catalog.json", autosave=False)
    app = create_app(config=config)
    with TestClient(app) as client:
        yield client
