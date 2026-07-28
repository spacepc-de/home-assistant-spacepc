"""Sensor platform for SpacePC."""

from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
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
    """Set up SpacePC sensors."""
    del hass
    async_add_entities(
        entities_for_platform(entry.runtime_data.coordinator, "sensor", SpacePCSensor)
    )


class SpacePCSensor(SpacePCEntity, SensorEntity):
    """A sensor exposed by a SpacePC device."""

    @property
    def native_value(self) -> str | int | float | None:
        """Return the sensor value."""
        state = self.state_data
        value = state.value if state else None
        return value if isinstance(value, str | int | float) else None

    @property
    def native_unit_of_measurement(self) -> str | None:
        """Return the native unit."""
        return self.definition.unit

    @property
    def device_class(self) -> str | None:
        """Return the device class reported by the device."""
        return self.definition.device_class

    @property
    def state_class(self) -> str | None:
        """Return the state class reported by the device."""
        return self.definition.state_class
