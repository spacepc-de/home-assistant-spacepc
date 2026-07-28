"""Tests for the SpacePC config flow and discovery."""

from __future__ import annotations

from ipaddress import IPv4Address
from unittest.mock import patch

from homeassistant.config_entries import SOURCE_USER, SOURCE_ZEROCONF
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from homeassistant.helpers.service_info.zeroconf import ZeroconfServiceInfo
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.spacepc.const import DOMAIN


async def test_manual_config_flow(
    hass: HomeAssistant,
    mock_spacepc_client: object,
) -> None:
    """A reachable device can be added manually."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": SOURCE_USER},
    )
    assert result["type"] is FlowResultType.FORM

    with patch(
        "custom_components.spacepc.async_setup_entry",
        return_value=True,
    ):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {CONF_HOST: "spacepc-aabbcc.local", CONF_PORT: 80},
        )

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["title"] == "Workshop sensor"
    assert result["data"] == {
        CONF_HOST: "spacepc-aabbcc.local",
        CONF_PORT: 80,
    }


async def test_zeroconf_discovery_uses_stable_hostname(
    hass: HomeAssistant,
    mock_spacepc_client: object,
) -> None:
    """Discovery stores the mDNS hostname instead of a temporary IP."""
    discovery = ZeroconfServiceInfo(
        ip_address=IPv4Address("192.168.2.28"),
        ip_addresses=[IPv4Address("192.168.2.28")],
        hostname="spacepc-aabbcc.local.",
        name="Workshop sensor._spacepc._tcp.local.",
        port=80,
        properties={"api": "1", "id": "spacepc-aabbcc"},
        type="_spacepc._tcp.local.",
    )
    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": SOURCE_ZEROCONF},
        data=discovery,
    )
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "confirm"

    with patch(
        "custom_components.spacepc.async_setup_entry",
        return_value=True,
    ):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {},
        )

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["data"][CONF_HOST] == "spacepc-aabbcc.local"


async def test_rediscovery_updates_connection_data(
    hass: HomeAssistant,
    mock_spacepc_client: object,
) -> None:
    """Rediscovery updates an existing entry after DHCP or port changes."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        unique_id="spacepc-aabbcc",
        data={CONF_HOST: "192.168.2.10", CONF_PORT: 80},
    )
    entry.add_to_hass(hass)
    discovery = ZeroconfServiceInfo(
        ip_address=IPv4Address("192.168.2.28"),
        ip_addresses=[IPv4Address("192.168.2.28")],
        hostname="spacepc-aabbcc.local.",
        name="Workshop sensor._spacepc._tcp.local.",
        port=8080,
        properties={"api": "1", "id": "spacepc-aabbcc"},
        type="_spacepc._tcp.local.",
    )

    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": SOURCE_ZEROCONF},
        data=discovery,
    )

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "already_configured"
    assert entry.data[CONF_HOST] == "spacepc-aabbcc.local"
    assert entry.data[CONF_PORT] == 8080
