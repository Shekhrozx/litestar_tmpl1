from __future__ import annotations

from pathlib import Path
from typing import Final

from litestar.utils.module_loader import module_to_os_path

DEFAULT_MODULE_NAME = "app"
"""The default module name for the application."""

BASE_DIR: Final[Path] = module_to_os_path(DEFAULT_MODULE_NAME)
"""The base directory of the application module."""

DEFAULT_ACCESS_ROLE = "User"
"""The name of the default access role."""

SUPERUSER_ACCESS_ROLE = "Superuser"
"""The name of the superuser access role."""

DEFAULT_PAGINATION_SIZE = 20
"""The default pagination size for paginated responses."""