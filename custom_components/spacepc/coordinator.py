"""Data coordinator for SpacePC devices."""

from __future__ import annotations

from datetime import timedelta

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import SpacePCClient, SpacePCError
from .const import DEFAULT_SCAN_INTERVAL_SECONDS, DOMAIN
from .models import DeviceInfo, DeviceState


class SpacePCDataUpdateCoordinator(DataUpdateCoordinator[DeviceState]):
    """Coordinate polling and commands for one device."""

    def __init__(
        self,
        hass: HomeAssistant,
        client: SpacePCClient,
        device_info: DeviceInfo,
        *,
        ip_address: str | None,
        configuration_url: str,
    ) -> None:
        super().__init__(
            hass,
            logger=__import__("logging").getLogger(__name__),
            name=f"{DOMAIN}-{device_info.device_id}",
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL_SECONDS),
        )
        self.client = client
        self.device_info = device_info
        self.ip_address = ip_address
        self.configuration_url = configuration_url

    async def _async_update_data(self) -> DeviceState:
        try:
            return await self.client.async_get_state()
        except SpacePCError as err:
            raise UpdateFailed(f"Unable to update SpacePC device: {err}") from err
