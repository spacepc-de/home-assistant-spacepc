"""Tests for SpacePC API data models."""

import pytest

from custom_components.spacepc.models import (
    SpacePCDataError,
    parse_device_info,
    parse_device_state,
)


def test_parse_device_info() -> None:
    """A valid information payload is parsed."""
    info = parse_device_info(
        {
            "api_version": 1,
            "device_id": "device-1",
            "name": "Room sensor",
            "manufacturer": "SpacePC",
            "model": "ESP32 DevKit",
            "project_id": "room-sensor",
            "firmware": {"version": "0.1.0"},
            "auth_required": False,
            "entities": [
                {
                    "id": "temperature",
                    "name": "Temperature",
                    "platform": "sensor",
                    "unit": "°C",
                }
            ],
        }
    )

    assert info.device_id == "device-1"
    assert info.entities[0].unit == "°C"


def test_parse_device_info_rejects_missing_identifier() -> None:
    """Device identity is required."""
    with pytest.raises(SpacePCDataError, match="device_id"):
        parse_device_info(
            {
                "api_version": 1,
                "name": "Room sensor",
                "manufacturer": "SpacePC",
                "model": "ESP32 DevKit",
                "project_id": "room-sensor",
                "firmware": {"version": "0.1.0"},
                "entities": [],
            }
        )


def test_parse_device_state_separates_attributes() -> None:
    """Platform attributes are separated from the primary value."""
    state = parse_device_state(
        {
            "entities": {
                "fan": {
                    "value": None,
                    "available": True,
                    "on": True,
                    "percentage": 60,
                }
            },
            "diagnostics": {"wifi_rssi_dbm": -61},
        }
    )

    assert state.entities["fan"].attributes == {"on": True, "percentage": 60}
    assert state.diagnostics["wifi_rssi_dbm"] == -61
