"""Diagnostics support for SpacePC."""

from __future__ import annotations

from typing import Any

from homeassistant.core import HomeAssistant

from . import SpacePCConfigEntry


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant,
    entry: SpacePCConfigEntry,
) -> dict[str, Any]:
    """Return diagnostics without credentials or network identifiers."""
    del hass
    info = entry.runtime_data.device_info
    coordinator = entry.runtime_data.coordinator
    return {
        "api_version": info.api_version,
        "project_id": info.project_id,
        "manufacturer": info.manufacturer,
        "model": info.model,
        "firmware": {
            "version": info.firmware.version,
            "build_date": info.firmware.build_date,
            "source_commit": info.firmware.source_commit,
        },
        "entity_count": len(info.entities),
        "diagnostics": coordinator.data.diagnostics,
    }
