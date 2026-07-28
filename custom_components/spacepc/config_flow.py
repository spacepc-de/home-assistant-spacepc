"""Config flow for SpacePC devices."""

from __future__ import annotations

from ipaddress import ip_address
from typing import Any

import voluptuous as vol
from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.service_info.zeroconf import ZeroconfServiceInfo

from .api import (
    SpacePCAuthenticationError,
    SpacePCClient,
    SpacePCConnectionError,
    SpacePCUnsupportedApiError,
)
from .const import CONF_API_TOKEN, CONF_IP_ADDRESS, DEFAULT_PORT, DOMAIN
from .models import DeviceInfo, SpacePCDataError


class SpacePCConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for SpacePC."""

    VERSION = 1

    def __init__(self) -> None:
        self._discovered_host: str | None = None
        self._discovered_ip: str | None = None
        self._discovered_port = DEFAULT_PORT
        self._info: DeviceInfo | None = None

    async def async_step_zeroconf(
        self,
        discovery_info: ZeroconfServiceInfo,
    ) -> ConfigFlowResult:
        """Handle a discovered SpacePC device."""
        properties = discovery_info.properties
        if properties.get("api") != "1":
            return self.async_abort(reason="unsupported_api")

        device_id = properties.get("id")
        if not device_id:
            return self.async_abort(reason="invalid_discovery")

        discovered_host = _discovery_host(discovery_info)
        discovered_ip = str(discovery_info.ip_address)
        discovered_port = discovery_info.port or DEFAULT_PORT
        await self.async_set_unique_id(device_id)
        existing_entry = next(
            (
                entry
                for entry in self._async_current_entries()
                if entry.unique_id == device_id
            ),
            None,
        )
        if existing_entry is not None:
            updated_data = {
                **existing_entry.data,
                CONF_HOST: discovered_host,
                CONF_IP_ADDRESS: discovered_ip,
                CONF_PORT: discovered_port,
            }
            if updated_data != existing_entry.data:
                self.hass.config_entries.async_update_entry(
                    existing_entry,
                    data=updated_data,
                )
            else:
                self.hass.async_create_task(
                    self.hass.config_entries.async_reload(existing_entry.entry_id),
                )
            return self.async_abort(reason="already_configured")
        self._abort_if_unique_id_configured(
            updates={CONF_HOST: discovered_host, CONF_PORT: discovered_port}
        )

        self._discovered_host = discovered_host
        self._discovered_ip = discovered_ip
        self._discovered_port = discovered_port
        errors: dict[str, str] = {}
        try:
            self._info = await self._async_probe(
                self._discovered_host,
                self._discovered_port,
                None,
            )
        except (SpacePCConnectionError, SpacePCDataError):
            errors["base"] = "cannot_connect"
        except SpacePCUnsupportedApiError:
            errors["base"] = "unsupported_api"

        if errors:
            return self.async_abort(reason=errors["base"])
        if self._info is None:
            return self.async_abort(reason="cannot_connect")

        self.context["title_placeholders"] = {"name": self._info.name}
        return await self.async_step_confirm()

    async def async_step_confirm(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> ConfigFlowResult:
        """Confirm a discovered device."""
        if self._info is None or self._discovered_host is None:
            return self.async_abort(reason="invalid_discovery")

        errors: dict[str, str] = {}
        if user_input is not None:
            token = user_input.get(CONF_API_TOKEN) or None
            try:
                self._info = await self._async_probe(
                    self._discovered_host,
                    self._discovered_port,
                    token,
                    include_state=True,
                )
            except SpacePCAuthenticationError:
                errors["base"] = "invalid_auth"
            except (SpacePCConnectionError, SpacePCDataError):
                errors["base"] = "cannot_connect"
            except SpacePCUnsupportedApiError:
                errors["base"] = "unsupported_api"
            else:
                return self._async_create_device_entry(
                    self._discovered_host,
                    self._discovered_port,
                    token,
                    discovered_ip=self._discovered_ip,
                )

        schema: dict[vol.Marker, type[str]] = {}
        if self._info.auth_required:
            schema[vol.Required(CONF_API_TOKEN)] = str
        return self.async_show_form(
            step_id="confirm",
            data_schema=vol.Schema(schema),
            errors=errors,
            description_placeholders={"name": self._info.name},
        )

    async def async_step_user(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> ConfigFlowResult:
        """Handle manual setup."""
        errors: dict[str, str] = {}
        if user_input is not None:
            host = user_input[CONF_HOST].strip()
            port = user_input[CONF_PORT]
            token = user_input.get(CONF_API_TOKEN) or None
            try:
                info = await self._async_probe(host, port, token, include_state=True)
            except SpacePCAuthenticationError:
                errors["base"] = "invalid_auth"
            except (SpacePCConnectionError, SpacePCDataError):
                errors["base"] = "cannot_connect"
            except SpacePCUnsupportedApiError:
                errors["base"] = "unsupported_api"
            else:
                await self.async_set_unique_id(info.device_id)
                self._abort_if_unique_id_configured(updates={CONF_HOST: host, CONF_PORT: port})
                self._info = info
                return self._async_create_device_entry(
                    host,
                    port,
                    token,
                    discovered_ip=_literal_ip(host),
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_HOST): str,
                    vol.Required(CONF_PORT, default=DEFAULT_PORT): vol.All(
                        vol.Coerce(int),
                        vol.Range(min=1, max=65535),
                    ),
                    vol.Optional(CONF_API_TOKEN): str,
                }
            ),
            errors=errors,
        )

    async def _async_probe(
        self,
        host: str,
        port: int,
        token: str | None,
        *,
        include_state: bool = False,
    ) -> DeviceInfo:
        client = SpacePCClient(async_get_clientsession(self.hass), host, port, token)
        info = await client.async_get_info()
        if include_state:
            await client.async_get_state()
        return info

    def _async_create_device_entry(
        self,
        host: str,
        port: int,
        token: str | None,
        *,
        discovered_ip: str | None = None,
    ) -> ConfigFlowResult:
        if self._info is None:
            return self.async_abort(reason="cannot_connect")
        data: dict[str, Any] = {CONF_HOST: host, CONF_PORT: port}
        if discovered_ip:
            data[CONF_IP_ADDRESS] = discovered_ip
        if token:
            data[CONF_API_TOKEN] = token
        return self.async_create_entry(title=self._info.name, data=data)


def _discovery_host(discovery_info: ZeroconfServiceInfo) -> str:
    """Prefer the stable mDNS hostname over a DHCP address."""
    hostname = discovery_info.hostname.rstrip(".")
    return hostname or discovery_info.host


def _literal_ip(host: str) -> str | None:
    """Return a normalized IP when manual setup used a literal address."""
    try:
        return str(ip_address(host))
    except ValueError:
        return None
