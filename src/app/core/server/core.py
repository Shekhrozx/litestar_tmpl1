# pylint: disable=[invalid-name,import-outside-toplevel]
from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, TypeVar
from uuid import UUID

from advanced_alchemy.exceptions import DuplicateKeyError, RepositoryError
from httpx_oauth.oauth2 import OAuth2Token
from litestar.di import Provide
from litestar.enums import RequestEncodingType
from litestar.openapi.config import OpenAPIConfig
from litestar.openapi.plugins import ScalarRenderPlugin
from litestar.params import Body
from litestar.plugins import CLIPluginProtocol, InitPluginProtocol
from litestar.security.jwt import OAuth2Login, Token

from app.__metadata__ import __version__
from app.core.server import plugins
from app.core.settings import AppSettings, config, get_settings, provide_app_settings
from app.core.utils.exceptions import (
    ApplicationClientError,
    ApplicationError,
    exception_to_http_response,
)
from app.db import models as m
from app.domain.accounts.guards import auth, provide_user

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator

    from click import Group
    from litestar.config.app import AppConfig
    from litestar.datastructures import State


T = TypeVar("T")


class ApplicationCore(InitPluginProtocol, CLIPluginProtocol):
    """Application core configuration plugin.

    This class is responsible for configuring the main Litestar application with our routes, guards, and various plugins

    """

    __slots__ = ("app_slug",)
    app_slug: str

    def on_cli_init(self, cli: Group) -> None:
        # from app.cli.commands import user_management_group

        settings = get_settings()
        self.app_slug = settings.app.slug
        # cli.add_command(user_management_group)

    def on_app_init(self, app_config: AppConfig) -> AppConfig:
        """Configure application for use with SQLAlchemy.

        Args:
            app_config: The :class:`AppConfig <litestar.config.app.AppConfig>` instance.

        Returns:
            The configured app config.
        """
        settings = get_settings()
        self.app_slug = settings.app.slug
        app_config.debug = settings.app.DEBUG
        app_config.path = "/api/v1/"

        app_config.openapi_config = OpenAPIConfig(
            title=settings.app.NAME,
            version=__version__,
            components=[auth.openapi_components],
            security=[auth.security_requirement],
            render_plugins=[ScalarRenderPlugin(version="latest")],
        )
        app_config = auth.on_app_init(app_config)
        app_config.cors_config = config.cors

        app_config.plugins.extend(
            [
                # plugins.structlog,
                # plugins.granian,
                plugins.alchemy,
                # plugins.problem_details,
                plugins.oauth2_provider,
                plugins.domain,
            ],
        )

        app_config.signature_namespace.update(
            {
                "Token": Token,
                "OAuth2Login": OAuth2Login,
                "RequestEncodingType": RequestEncodingType,
                "Body": Body,
                "m": m,
                "UUID": UUID,
                "datetime": datetime,
                "OAuth2Token": OAuth2Token,
                "AppSettings": AppSettings,
                "User": m.User,
            },
        )
        app_config.exception_handlers = {
            ApplicationError: exception_to_http_response,
            ApplicationClientError: exception_to_http_response,
            RepositoryError: exception_to_http_response,
            DuplicateKeyError: exception_to_http_response,
        }

        app_config.dependencies.update(
            {
                "current_user": Provide(provide_user, sync_to_thread=False),
                "settings": Provide(provide_app_settings, sync_to_thread=False),
            }
        )

        return app_config


