"""Sensor platform for SpacePC."""

from __future__ import annotations

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorStateClass
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import SpacePCConfigEntry
from .entity import SpacePCEntity
from .helpers import entities_for_platform
from .models import EntityDefinition

IP_ADDRESS_DEFINITION = EntityDefinition(
    entity_id="ip_address",
    name="IP address",
    platform="sensor",
    icon="mdi:ip-network",
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: SpacePCConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up SpacePC sensors."""
    del hass
    coordinator = entry.runtime_data.coordinator
    entities: list[SpacePCSensor | SpacePCIPAddressSensor] = [
        *entities_for_platform(coordinator, "sensor", SpacePCSensor),
        SpacePCIPAddressSensor(coordinator, IP_ADDRESS_DEFINITION),
    ]
    async_add_entities(entities)


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
    def device_class(self) -> SensorDeviceClass | None:
        """Return the device class reported by the device."""
        if self.definition.device_class is None:
            return None
        try:
            return SensorDeviceClass(self.definition.device_class)
        except ValueError:
            return None

    @property
    def state_class(self) -> SensorStateClass | None:
        """Return the state class reported by the device."""
        if self.definition.state_class is None:
            return None
        try:
            return SensorStateClass(self.definition.state_class)
        except ValueError:
            return None


class SpacePCIPAddressSensor(SpacePCEntity, SensorEntity):
    """Diagnostic sensor showing the latest discovered device address."""

    _attr_entity_category = EntityCategory.DIAGNOSTIC

    @property
    def native_value(self) -> str | None:
        """Return the latest IP address announced over mDNS."""
        return self.coordinator.ip_address

    @property
    def available(self) -> bool:
        """Return whether an address is known and the device is reachable."""
        return self.coordinator.last_update_success and bool(self.coordinator.ip_address)
