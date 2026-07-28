"""Tests for shared SpacePC helpers."""

from homeassistant.const import CONF_HOST, CONF_PORT

from custom_components.spacepc.const import CONF_IP_ADDRESS
from custom_components.spacepc.helpers import device_configuration_url


def test_configuration_url_prefers_discovered_ip() -> None:
    """The GUI link uses the current IP while communication keeps mDNS."""
    assert (
        device_configuration_url(
            {
                CONF_HOST: "spacepc-aabbcc.local",
                CONF_IP_ADDRESS: "192.168.2.28",
                CONF_PORT: 80,
            }
        )
        == "http://192.168.2.28"
    )


def test_configuration_url_formats_ipv6_and_non_default_port() -> None:
    """IPv6 addresses are bracketed in URLs."""
    assert (
        device_configuration_url(
            {
                CONF_HOST: "spacepc-aabbcc.local",
                CONF_IP_ADDRESS: "fe80::1234",
                CONF_PORT: 8080,
            }
        )
        == "http://[fe80::1234]:8080"
    )
