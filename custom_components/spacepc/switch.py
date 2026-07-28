"""Switch platform for SpacePC."""

from __future__ import annotations

from homeassistant.components.switch import SwitchEntity
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
    """Set up SpacePC switches."""
    del hass
    async_add_entities(
        entities_for_platform(entry.runtime_data.coordinator, "switch", SpacePCSwitch)
    )


class SpacePCSwitch(SpacePCEntity, SwitchEntity):
    """A switch exposed by a SpacePC device."""

    @property
    def is_on(self) -> bool | None:
        """Return whether the switch is on."""
        state = self.state_data
        if state is None:
            return None
        return bool(state.attributes.get("on", state.value))

    async def async_turn_on(self, **kwargs: object) -> None:
        """Turn on the switch."""
        await self.coordinator.client.async_set_entity(self.definition.entity_id, {"on": True})
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: object) -> None:
        """Turn off the switch."""
        await self.coordinator.client.async_set_entity(self.definition.entity_id, {"on": False})
        await self.coordinator.async_request_refresh()
