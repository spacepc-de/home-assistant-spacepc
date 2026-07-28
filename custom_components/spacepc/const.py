"""Constants for the SpacePC integration."""

from typing import Final

from homeassistant.const import Platform

DOMAIN: Final = "spacepc"
DEFAULT_PORT: Final = 80
DEFAULT_SCAN_INTERVAL_SECONDS: Final = 30
SUPPORTED_API_VERSION: Final = 1

CONF_API_TOKEN: Final = "api_token"

PLATFORMS: Final = (
    Platform.SENSOR,
    Platform.BINARY_SENSOR,
    Platform.SWITCH,
    Platform.LIGHT,
    Platform.FAN,
    Platform.UPDATE,
)
