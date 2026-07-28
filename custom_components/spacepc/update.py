"""Firmware update platform for SpacePC."""

from __future__ import annotations

from typing import Any

from homeassistant.components.update import UpdateEntity, UpdateEntityFeature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import SpacePCConfigEntry
from .entity import SpacePCEntity
from .helpers import entities_for_platform


async def async_setup_entry(
    hass: HomeAssistant,
    entry: SpacePCConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up SpacePC firmware updates."""
    del hass
    async_add_entities(
        entities_for_platform(entry.runtime_data.coordinator, "update", SpacePCUpdate)
    )


class SpacePCUpdate(SpacePCEntity, UpdateEntity):
    """A firmware update exposed by a SpacePC device."""

    _attr_supported_features = UpdateEntityFeature.INSTALL

    @property
    def installed_version(self) -> str | None:
        """Return the installed firmware version."""
        state = self.state_data
        value = state.attributes.get("installed_version") if state else None
        return value if isinstance(value, str) else None

    @property
    def latest_version(self) -> str | None:
        """Return the latest compatible firmware version."""
        state = self.state_data
        value = state.attributes.get("latest_version") if state else None
        return value if isinstance(value, str) else None

    @property
    def release_url(self) -> str | None:
        """Return the firmware release URL."""
        state = self.state_data
        value = state.attributes.get("release_url") if state else None
        return value if isinstance(value, str) else None

    @property
    def release_summary(self) -> str | None:
        """Return release notes."""
        state = self.state_data
        value = state.attributes.get("release_summary") if state else None
        return value if isinstance(value, str) else None

    async def async_install(
        self,
        version: str | None,
        backup: bool,
        **kwargs: Any,
    ) -> None:
        """Install the advertised update."""
        del version, backup, kwargs
        await self.coordinator.client.async_install_update(self.definition.entity_id)
        await self.coordinator.async_request_refresh()
