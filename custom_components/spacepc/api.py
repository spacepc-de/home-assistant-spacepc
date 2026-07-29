"""Async client for the SpacePC local API."""

from __future__ import annotations

from http import HTTPStatus
from typing import Any
from urllib.parse import quote

from aiohttp import ClientError, ClientSession, ClientTimeout

from .const import SUPPORTED_API_VERSION
from .models import DeviceInfo, DeviceState, parse_device_info, parse_device_state

REQUEST_TIMEOUT = ClientTimeout(total=10)


class SpacePCError(Exception):
    """Base exception for SpacePC API errors."""


class SpacePCConnectionError(SpacePCError):
    """Raised when a device cannot be reached."""


class SpacePCAuthenticationError(SpacePCError):
    """Raised when a device rejects the API token."""


class SpacePCUnsupportedApiError(SpacePCError):
    """Raised when a device uses an unsupported API version."""


class SpacePCClient:
    """Client for one SpacePC device."""

    def __init__(
        self,
        session: ClientSession,
        host: str,
        port: int,
        api_token: str | None = None,
    ) -> None:
        self._session = session
        self._base_url = f"http://{host.rstrip('.')}:{port}/api/v1"
        self._api_token = api_token

    async def async_get_info(self) -> DeviceInfo:
        """Return static device and capability information."""
        payload = await self._async_request("GET", "/info", authenticated=False)
        info = parse_device_info(payload)
        if info.api_version != SUPPORTED_API_VERSION:
            raise SpacePCUnsupportedApiError(
                f"Device uses API v{info.api_version}; v{SUPPORTED_API_VERSION} is supported"
            )
        return info

    async def async_get_state(self) -> DeviceState:
        """Return current entity states and diagnostics."""
        return parse_device_state(await self._async_request("GET", "/state"))

    async def async_set_entity(self, entity_id: str, command: dict[str, Any]) -> None:
        """Send a state command to a writable entity."""
        await self._async_request(
            "POST",
            f"/entities/{quote(entity_id, safe='')}",
            json=command,
            expect_json=False,
        )

    async def async_install_update(self, entity_id: str) -> None:
        """Ask the device to install its advertised firmware update."""
        await self._async_request(
            "POST",
            "/update/install",
            json={"entity_id": entity_id},
            expect_json=False,
        )

    async def async_update_display(self, payload: dict[str, Any]) -> None:
        """Send a Home Assistant widget layout to a display device."""
        await self._async_request(
            "PUT",
            "/display",
            json=payload,
            expect_json=False,
        )

    async def _async_request(
        self,
        method: str,
        path: str,
        *,
        authenticated: bool = True,
        json: dict[str, Any] | None = None,
        expect_json: bool = True,
    ) -> object:
        headers = {}
        if authenticated and self._api_token:
            headers["Authorization"] = f"Bearer {self._api_token}"

        try:
            async with self._session.request(
                method,
                f"{self._base_url}{path}",
                headers=headers,
                json=json,
                timeout=REQUEST_TIMEOUT,
            ) as response:
                if response.status == HTTPStatus.UNAUTHORIZED:
                    raise SpacePCAuthenticationError
                response.raise_for_status()
                return await response.json() if expect_json else None
        except SpacePCAuthenticationError:
            raise
        except (ClientError, TimeoutError) as err:
            raise SpacePCConnectionError from err
