"""Binary sensor platform for SpacePC."""

from __future__ import annotations

from homeassistant.components.binary_sensor import BinarySensorEntity
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
    """Set up SpacePC binary sensors."""
    del hass
    async_add_entities(
        entities_for_platform(
            entry.runtime_data.coordinator,
            "binary_sensor",
            SpacePCBinarySensor,
        )
    )


class SpacePCBinarySensor(SpacePCEntity, BinarySensorEntity):
    """A binary sensor exposed by a SpacePC device."""

    @property
    def is_on(self) -> bool | None:
        """Return the binary state."""
        state = self.state_data
        return bool(state.value) if state and state.value is not None else None

    @property
    def device_class(self) -> str | None:
        """Return the device class reported by the device."""
        return self.definition.device_class
