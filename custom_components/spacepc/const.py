"""Constants for the SpacePC integration."""

from typing import Final

from homeassistant.const import Platform

DOMAIN: Final = "spacepc"
DEFAULT_PORT: Final = 80
DEFAULT_SCAN_INTERVAL_SECONDS: Final = 30
SUPPORTED_API_VERSION: Final = 1

CONF_API_TOKEN: Final = "api_token"
CONF_IP_ADDRESS: Final = "ip_address"
CONF_DISPLAY_INTERVAL: Final = "display_interval"
CONF_DISPLAY_TITLE: Final = "display_title"
CONF_DISPLAY_WIDGETS: Final = "display_widgets"
DEFAULT_DISPLAY_INTERVAL_SECONDS: Final = 600

PLATFORMS: Final = (
    Platform.SENSOR,
    Platform.BINARY_SENSOR,
    Platform.SWITCH,
    Platform.LIGHT,
    Platform.FAN,
    Platform.UPDATE,
)
