"""SpacePC integration."""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import SpacePCClient, SpacePCConnectionError
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


def _create_client(hass: HomeAssistant, entry: SpacePCConfigEntry) -> SpacePCClient:
    """Create a client from the current config entry connection data."""
    return SpacePCClient(
        async_get_clientsession(hass),
        entry.data[CONF_HOST],
        entry.data.get(CONF_PORT, DEFAULT_PORT),
        entry.data.get(CONF_API_TOKEN),
    )


async def async_setup_entry(hass: HomeAssistant, entry: SpacePCConfigEntry) -> bool:
    """Set up SpacePC from a config entry."""
    client = _create_client(hass, entry)
    try:
        device_info = await client.async_get_info()
    except SpacePCConnectionError as err:
        raise ConfigEntryNotReady from err
    coordinator = SpacePCDataUpdateCoordinator(hass, client, device_info)
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = SpacePCRuntimeData(coordinator, device_info)
    entry.async_on_unload(entry.add_update_listener(_async_update_listener))
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def _async_update_listener(
    hass: HomeAssistant,
    entry: SpacePCConfigEntry,
) -> None:
    """Reload connection data and device capabilities after an entry update."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: SpacePCConfigEntry) -> bool:
    """Unload a SpacePC config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
