"""Helpers shared by SpacePC entity platforms."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from ipaddress import ip_address
from typing import Any

from .coordinator import SpacePCDataUpdateCoordinator
from .models import EntityDefinition


def entities_for_platform[EntityT](
    coordinator: SpacePCDataUpdateCoordinator,
    platform: str,
    factory: Callable[[SpacePCDataUpdateCoordinator, EntityDefinition], EntityT],
) -> list[EntityT]:
    """Create all device entities for a Home Assistant platform."""
    return [
        factory(coordinator, definition)
        for definition in coordinator.device_info.entities
        if definition.platform == platform
    ]


def device_configuration_url(data: Mapping[str, Any]) -> str:
    """Build the local setup URL, preferring the latest discovered IP."""
    from homeassistant.const import CONF_HOST, CONF_PORT

    from .const import CONF_IP_ADDRESS, DEFAULT_PORT

    host = str(data.get(CONF_IP_ADDRESS) or data[CONF_HOST]).rstrip(".")
    try:
        parsed_ip = ip_address(host)
    except ValueError:
        url_host = host
    else:
        url_host = f"[{host}]" if parsed_ip.version == 6 else host

    port = int(data.get(CONF_PORT, DEFAULT_PORT))
    port_suffix = "" if port == 80 else f":{port}"
    return f"http://{url_host}{port_suffix}"
