"""Tests for setup and offline recovery."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.spacepc import async_setup_entry
from custom_components.spacepc.api import SpacePCConnectionError
from custom_components.spacepc.const import DOMAIN


async def test_offline_device_retries_setup(hass: HomeAssistant) -> None:
    """An offline device remains retryable instead of failing permanently."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        unique_id="spacepc-aabbcc",
        data={CONF_HOST: "spacepc-aabbcc.local", CONF_PORT: 80},
    )
    entry.add_to_hass(hass)
    client = AsyncMock()
    client.async_get_info.side_effect = SpacePCConnectionError("offline")

    with (
        patch("custom_components.spacepc._create_client", return_value=client),
        pytest.raises(ConfigEntryNotReady),
    ):
        await async_setup_entry(hass, entry)
