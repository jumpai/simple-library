"""Application configuration helpers."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class AppConfig:
    """Configuration for the library application."""

    data_file: Path
    autosave: bool = True

    @staticmethod
    def default() -> "AppConfig":
        """Return a configuration pointing to the default data file."""
        home = Path(os.environ.get("HOME", "."))
        return AppConfig(data_file=home / ".simple_library.json")


def load_config() -> AppConfig:
    """Load configuration from environment variables."""
    path = os.environ.get("LIBAPP_DATA_FILE")
    autosave_flag = os.environ.get("LIBAPP_AUTOSAVE")

    if path:
        data_file = Path(path).expanduser()
    else:
        data_file = AppConfig.default().data_file

    if autosave_flag is None:
        autosave = True
    else:
        autosave = autosave_flag.lower() in {"1", "true", "yes", "on"}

    return AppConfig(data_file=data_file, autosave=autosave)
