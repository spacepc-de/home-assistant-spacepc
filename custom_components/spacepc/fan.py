"""Fan platform for SpacePC."""

from __future__ import annotations

from typing import Any

from homeassistant.components.fan import FanEntity, FanEntityFeature
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
    """Set up SpacePC fans."""
    del hass
    async_add_entities(entities_for_platform(entry.runtime_data.coordinator, "fan", SpacePCFan))


class SpacePCFan(SpacePCEntity, FanEntity):
    """A variable-speed fan exposed by a SpacePC device."""

    _attr_supported_features = FanEntityFeature.SET_SPEED
    _attr_speed_count = 100

    @property
    def is_on(self) -> bool | None:
        """Return whether the fan is on."""
        state = self.state_data
        return bool(state.attributes.get("on")) if state else None

    @property
    def percentage(self) -> int | None:
        """Return the current fan percentage."""
        state = self.state_data
        value = state.attributes.get("percentage") if state else None
        return value if isinstance(value, int) else None

    async def async_turn_on(
        self,
        percentage: int | None = None,
        preset_mode: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Turn on the fan."""
        del preset_mode, kwargs
        command: dict[str, Any] = {"on": True}
        if percentage is not None:
            command["percentage"] = percentage
        await self.coordinator.client.async_set_entity(self.definition.entity_id, command)
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off the fan."""
        await self.coordinator.client.async_set_entity(self.definition.entity_id, {"on": False})
        await self.coordinator.async_request_refresh()

    async def async_set_percentage(self, percentage: int) -> None:
        """Set fan speed."""
        await self.coordinator.client.async_set_entity(
            self.definition.entity_id,
            {"on": percentage > 0, "percentage": percentage},
        )
        await self.coordinator.async_request_refresh()
