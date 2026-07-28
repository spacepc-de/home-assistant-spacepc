"""Light platform for SpacePC."""

from __future__ import annotations

from typing import Any

from homeassistant.components.light import ATTR_BRIGHTNESS, LightEntity
from homeassistant.components.light.const import ColorMode
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
    """Set up SpacePC lights."""
    del hass
    async_add_entities(entities_for_platform(entry.runtime_data.coordinator, "light", SpacePCLight))


class SpacePCLight(SpacePCEntity, LightEntity):
    """A dimmable light exposed by a SpacePC device."""

    _attr_color_mode = ColorMode.BRIGHTNESS
    _attr_supported_color_modes = {ColorMode.BRIGHTNESS}

    @property
    def is_on(self) -> bool | None:
        """Return whether the light is on."""
        state = self.state_data
        return bool(state.attributes.get("on")) if state else None

    @property
    def brightness(self) -> int | None:
        """Return brightness from 0 to 255."""
        state = self.state_data
        value = state.attributes.get("brightness") if state else None
        return value if isinstance(value, int) else None

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on the light."""
        command: dict[str, Any] = {"on": True}
        if ATTR_BRIGHTNESS in kwargs:
            command["brightness"] = kwargs[ATTR_BRIGHTNESS]
        await self.coordinator.client.async_set_entity(self.definition.entity_id, command)
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off the light."""
        await self.coordinator.client.async_set_entity(self.definition.entity_id, {"on": False})
        await self.coordinator.async_request_refresh()
