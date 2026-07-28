"""SpacePC integration."""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import SpacePCClient
from .const import CONF_API_TOKEN, DEFAULT_PORT, PLATFORMS
from .const import DOMAIN as DOMAIN
from .coordinator import SpacePCDataUpdateCoordinator
from .models import DeviceInfo


@dataclass(slots=True)
class SpacePCRuntimeData:
    """Runtime data stored on a SpacePC config entry."""

    coordinator: SpacePCDataUpdateCoordinator
    device_info: DeviceInfo


type SpacePCConfigEntry = ConfigEntry[SpacePCRuntimeData]


async def async_setup_entry(hass: HomeAssistant, entry: SpacePCConfigEntry) -> bool:
    """Set up SpacePC from a config entry."""
    client = SpacePCClient(
        async_get_clientsession(hass),
        entry.data[CONF_HOST],
        entry.data.get(CONF_PORT, DEFAULT_PORT),
        entry.data.get(CONF_API_TOKEN),
    )
    device_info = await client.async_get_info()
    coordinator = SpacePCDataUpdateCoordinator(hass, client, device_info)
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = SpacePCRuntimeData(coordinator, device_info)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: SpacePCConfigEntry) -> bool:
    """Unload a SpacePC config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
