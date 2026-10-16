"""Domain auto-discovery for Litestar."""

from app.core.utils.domain._config import DomainPluginConfig
from app.core.utils.domain._discovery import (
    discover_domain_controllers,
    find_controllers_in_module,
)
from app.core.utils.domain._plugin import DomainPlugin
from app.core.utils.domain._state import cache

__all__ = [
    "DomainPlugin",
    "DomainPluginConfig",
    "clear_discovery_cache",
    "discover_domain_controllers",
    "find_controllers_in_module",
]


def clear_discovery_cache() -> None:
    """Clear the controller discovery cache and reset logging flags."""
    from app.core.utils.domain._state import DiscoveryState

    cache.clear()
    DiscoveryState.reset()