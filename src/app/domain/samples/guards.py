"""Sample domain guards."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from litestar.exceptions import PermissionDeniedException

if TYPE_CHECKING:
    from litestar.connection import ASGIConnection
    from litestar.handlers.base import BaseRouteHandler


def requires_sample_access(connection: ASGIConnection[Any, Any, Any, Any], _: BaseRouteHandler) -> None:
    """Allow only active users to access sample routes.

    Raises:
        PermissionDeniedException: Not authorized
    """
    user = connection.user
    if user is not None and getattr(user, "is_active", False):
        return
    raise PermissionDeniedException(detail="Insufficient privileges")
