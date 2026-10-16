from __future__ import annotations

import binascii
import json
import os
from dataclasses import dataclass, field
from typing import cast

from advanced_alchemy.utils.text import slugify
from litestar.config.compression import CompressionConfig
from litestar.config.cors import CORSConfig
from litestar.plugins.problem_details import ProblemDetailsConfig

from app.__metadata__ import __version__ as current_version
from app.core.utils.env import get_env


@dataclass
class AppSettings:
    """Application configuration"""

    NAME: str = field(default_factory=lambda: "Litestar Fullstack Template")
    """Application name."""
    VERSION: str = field(default=f"v{current_version}")
    """Current application"""
    CONTACT_NAME: str = field(default="Admin")
    """Application contact name"""
    CONTACT_EMAIL: str = field(default="admin@localhost")
    """Application contact email"""
    URL: str = field(default_factory=get_env("APP_URL", "http://localhost:8000"))
    """The frontend base URL"""
    DEBUG: bool = field(default_factory=get_env("LITESTAR_DEBUG", True))
    """Run `Litestar` with `debug=True`."""
    SECRET_KEY: str = field(
        default_factory=get_env("SECRET_KEY", binascii.hexlify(os.urandom(32)).decode(encoding="utf-8")),
    )
    """Application secret key."""
    JWT_ENCRYPTION_ALGORITHM: str = "HS256"
    """JWT Algorithm to use"""
    ALLOWED_CORS_ORIGINS: list[str] | str = field(default_factory=get_env("ALLOWED_CORS_ORIGINS", ["*"], list[str]))
    """Allowed CORS Origins"""
    COOKIE_SECURE: bool = field(default_factory=get_env("COOKIE_SECURE", False))
    """Use secure cookies (set to True in production with HTTPS)"""
    # STATIC_DIR: Path = field(default_factory=get_env("STATIC_DIR", STATIC_DIR))
    """Default URL where static assets are located."""
    STATIC_URL: str = field(default_factory=get_env("STATIC_URL", "/static/web/"))
    """URL Location for Static assets."""
    BASE_URL: str | None = None
    """Fully qualified path to optional use for URL generation."""
    DEV_MODE: bool = field(default_factory=get_env("VITE_DEV_MODE", False))
    """Toggle dev mode flag.  This can be used enable extra processes during development."""
    ENABLE_INSTRUMENTATION: bool = False
    """Enable OpenTelemetry instrumentation"""
    GOOGLE_OAUTH2_CLIENT_ID: str = field(default_factory=get_env("GOOGLE_OAUTH2_CLIENT_ID", ""))
    """Google Client ID"""
    GOOGLE_OAUTH2_CLIENT_SECRET: str = field(default_factory=get_env("GOOGLE_OAUTH2_CLIENT_SECRET", ""))
    """Google Client Secret"""
    GITHUB_OAUTH2_CLIENT_ID: str = field(default_factory=get_env("GITHUB_OAUTH2_CLIENT_ID", ""))
    """GitHub Client ID"""
    GITHUB_OAUTH2_CLIENT_SECRET: str = field(default_factory=get_env("GITHUB_OAUTH2_CLIENT_SECRET", ""))
    """GitHub Client Secret"""
    ENV_SECRETS: str = field(default_factory=get_env("ENV_SECRETS", "runtime-secrets"))
    """Path to environment secrets."""

    @property
    def google_oauth_enabled(self) -> bool:
        """Check if Google OAuth is configured.

        Returns:
            True if Google OAuth credentials are set.
        """
        return bool(self.GOOGLE_OAUTH2_CLIENT_ID and self.GOOGLE_OAUTH2_CLIENT_SECRET)

    @property
    def github_oauth_enabled(self) -> bool:
        """Check if GitHub OAuth is configured.

        Returns:
            True if GitHub OAuth credentials are set.
        """
        return bool(self.GITHUB_OAUTH2_CLIENT_ID and self.GITHUB_OAUTH2_CLIENT_SECRET)

    @property
    def slug(self) -> str:
        """Return a slugified name.

        Returns:
            `self.NAME`, all lowercase and hyphens instead of spaces.
        """
        return slugify(self.NAME)

    def get_compression_config(self) -> CompressionConfig:
        return CompressionConfig(backend="gzip")

    def get_cors_config(self) -> CORSConfig:
        return CORSConfig(allow_origins=cast("list[str]", self.ALLOWED_CORS_ORIGINS))

    def get_problem_details_config(self) -> ProblemDetailsConfig:
        return ProblemDetailsConfig(enable_for_all_http_exceptions=True)

    def __post_init__(self) -> None:
        # Check if the ALLOWED_CORS_ORIGINS is a string.
        if isinstance(self.ALLOWED_CORS_ORIGINS, str):
            # Check if the string starts with "[" and ends with "]", indicating a list.
            if self.ALLOWED_CORS_ORIGINS.startswith("[") and self.ALLOWED_CORS_ORIGINS.endswith("]"):
                try:
                    # Safely evaluate the string as a Python list.
                    self.ALLOWED_CORS_ORIGINS = json.loads(self.ALLOWED_CORS_ORIGINS)  # pyright: ignore[reportConstantRedefinition]
                except (SyntaxError, ValueError):
                    # Handle potential errors if the string is not a valid Python literal.
                    msg = "ALLOWED_CORS_ORIGINS is not a valid list representation."
                    raise ValueError(msg) from None
            else:
                # Split the string by commas into a list if it is not meant to be a list representation.
                self.ALLOWED_CORS_ORIGINS = [host.strip() for host in self.ALLOWED_CORS_ORIGINS.split(",")]  # pyright: ignore[reportConstantRedefinition]

