"""Tests for SpacePC entity state mapping."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

from homeassistant.components.sensor import SensorDeviceClass, SensorStateClass

from custom_components.spacepc.helpers import entities_for_platform
from custom_components.spacepc.models import DeviceInfo, DeviceState
from custom_components.spacepc.sensor import (
    IP_ADDRESS_DEFINITION,
    SpacePCIPAddressSensor,
    SpacePCSensor,
)


def test_sensor_maps_value_and_metadata(
    device_info: DeviceInfo,
    device_state: DeviceState,
) -> None:
    """Sensor entities expose API value, availability and metadata."""
    coordinator = MagicMock()
    coordinator.device_info = device_info
    coordinator.data = device_state
    coordinator.last_update_success = True
    coordinator.ip_address = "192.168.2.28"
    coordinator.configuration_url = "http://192.168.2.28"
    coordinator.async_add_listener.return_value = MagicMock()
    coordinator.async_request_refresh = AsyncMock()

    entity = SpacePCSensor(coordinator, device_info.entities[0])

    assert entity.unique_id == "spacepc-aabbcc_temperature"
    assert entity.native_value == 23.5
    assert entity.native_unit_of_measurement == "°C"
    assert entity.device_class is SensorDeviceClass.TEMPERATURE
    assert entity.state_class is SensorStateClass.MEASUREMENT
    assert entity.available
    assert str(entity.device_info["configuration_url"]) == "http://192.168.2.28"


def test_entity_is_unavailable_when_device_or_sensor_is_offline(
    device_info: DeviceInfo,
    device_state: DeviceState,
) -> None:
    """Coordinator and per-entity availability both affect the entity."""
    coordinator = MagicMock()
    coordinator.device_info = device_info
    coordinator.data = device_state
    coordinator.last_update_success = False
    coordinator.ip_address = "192.168.2.28"
    coordinator.configuration_url = "http://192.168.2.28"
    coordinator.async_add_listener.return_value = MagicMock()

    entity = SpacePCSensor(coordinator, device_info.entities[0])
    assert not entity.available


def test_multiple_named_sensors_are_created_independently(
    device_info: DeviceInfo,
    device_state: DeviceState,
) -> None:
    """Every sensor definition becomes its own Home Assistant entity."""
    coordinator = MagicMock()
    coordinator.device_info = device_info
    coordinator.data = device_state
    coordinator.last_update_success = True
    coordinator.ip_address = "192.168.2.28"
    coordinator.configuration_url = "http://192.168.2.28"
    coordinator.async_add_listener.return_value = MagicMock()

    entities = entities_for_platform(coordinator, "sensor", SpacePCSensor)

    assert [entity.name for entity in entities] == [
        "Room temperature",
        "Outside temperature",
    ]
    assert entities[0].available
    assert not entities[1].available


def test_ip_address_diagnostic_sensor(
    device_info: DeviceInfo,
    device_state: DeviceState,
) -> None:
    """The device IP is visible and shares the clickable device URL."""
    coordinator = MagicMock()
    coordinator.device_info = device_info
    coordinator.data = device_state
    coordinator.last_update_success = True
    coordinator.ip_address = "192.168.2.28"
    coordinator.configuration_url = "http://192.168.2.28"
    coordinator.async_add_listener.return_value = MagicMock()

    entity = SpacePCIPAddressSensor(coordinator, IP_ADDRESS_DEFINITION)

    assert entity.native_value == "192.168.2.28"
    assert entity.available
    assert str(entity.device_info["configuration_url"]) == "http://192.168.2.28"
