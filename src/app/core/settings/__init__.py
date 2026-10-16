"""All configuration via environment.

Take note of the environment variable prefixes required for each
settings class, except `AppSettings`.
"""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import TYPE_CHECKING

import structlog
from dotenv import load_dotenv
from litestar.cli._utils import console

from app.core.settings.app import AppSettings
from app.core.settings.db import DatabaseSettings
from app.core.settings.log import LogSettings
from app.core.settings.server import ServerSettings


@dataclass
class Settings:
    app: AppSettings = field(default_factory=AppSettings)
    db: DatabaseSettings = field(default_factory=DatabaseSettings)
    server: ServerSettings = field(default_factory=ServerSettings)
    log: LogSettings = field(default_factory=LogSettings)

    @classmethod
    @lru_cache(maxsize=1, typed=True)
    def from_env(cls, dotenv_filename: str = ".env") -> Settings:
        logger = structlog.get_logger()
        _secret_id = os.environ.get("ENV_SECRETS", None)  # use this to load secrets in a container
        env_file = Path(f"{os.curdir}/{dotenv_filename}")
        env_file_exists = env_file.is_file()
        if env_file_exists:
            console.print(f"[yellow]Loading environment configuration from {dotenv_filename}[/]")
            load_dotenv(env_file, override=False)  # Env vars take precedence over .env file
        try:
            db: DatabaseSettings = DatabaseSettings()
            server: ServerSettings = ServerSettings()
            app: AppSettings = AppSettings()
            log: LogSettings = LogSettings()
        except Exception as e:  # noqa: BLE001
            logger.fatal("Could not load settings. %s", e)
            sys.exit(1)
        return Settings(app=app, db=db, server=server, log=log)


def get_settings(dotenv_filename: str = ".env") -> Settings:
    return Settings.from_env(dotenv_filename)


def provide_app_settings() -> AppSettings:
    """Return application settings for dependency injection.

    Returns:
        The application settings instance.
    """
    return get_settings().app