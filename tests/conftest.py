"""Shared fixtures for SpacePC integration tests."""

from __future__ import annotations

from collections.abc import Generator
from unittest.mock import AsyncMock, patch

import pytest

from custom_components.spacepc.models import (
    DeviceInfo,
    DeviceState,
    EntityDefinition,
    EntityState,
    FirmwareInfo,
)


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(
    enable_custom_integrations: None,
) -> Generator[None]:
    """Allow Home Assistant to load the integration from custom_components."""
    yield


@pytest.fixture
def device_info() -> DeviceInfo:
    """Return representative device metadata."""
    return DeviceInfo(
        api_version=1,
        device_id="spacepc-aabbcc",
        name="Workshop sensor",
        manufacturer="SpacePC",
        model="DS18B20 Temperature Sensor",
        project_id="ds18b20-mqtt-sensor",
        firmware=FirmwareInfo(version="0.1.0", build_date="2026-07-28"),
        auth_required=False,
        entities=(
            EntityDefinition(
                entity_id="temperature",
                name="Temperature",
                platform="sensor",
                device_class="temperature",
                state_class="measurement",
                unit="°C",
            ),
            EntityDefinition(
                entity_id="connected",
                name="Sensor connected",
                platform="binary_sensor",
                device_class="connectivity",
            ),
        ),
    )


@pytest.fixture
def device_state() -> DeviceState:
    """Return representative live device state."""
    return DeviceState(
        entities={
            "temperature": EntityState(value=23.5),
            "connected": EntityState(value=True),
        },
        diagnostics={"wifi_rssi": -54},
    )


@pytest.fixture
def mock_spacepc_client(
    device_info: DeviceInfo,
    device_state: DeviceState,
) -> Generator[AsyncMock]:
    """Mock all device I/O while preserving real integration behaviour."""
    with patch(
        "custom_components.spacepc.config_flow.SpacePCClient",
        autospec=True,
    ) as flow_client_class:
        flow_client = flow_client_class.return_value
        flow_client.async_get_info = AsyncMock(return_value=device_info)
        flow_client.async_get_state = AsyncMock(return_value=device_state)
        yield flow_client
