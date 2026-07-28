<p align="center">
  <a href="https://spacepc.dev">
    <img src="assets/spacepc-logo.png" alt="SpacePC.dev" width="520">
  </a>
</p>

<h1 align="center">SpacePC for Home Assistant</h1>

Local-first Home Assistant integration for SpacePC devices.

SpacePC devices are discovered over mDNS and communicate with Home Assistant
through the versioned local SpacePC HTTP API. MQTT remains available as an
optional interface for users and systems outside Home Assistant, but it is not
required by this integration.

## Status

This repository is an initial development release. The integration and the
device API contract are not yet stable. Do not treat it as production-ready.

## Features

- automatic discovery via `_spacepc._tcp.local.`
- automatic recovery after Wi-Fi reconnects or DHCP address changes
- manual setup by hostname or IP address
- sensors and binary sensors
- switches, lights and fans
- device and connection diagnostics
- firmware update entities
- optional bearer-token authentication
- English and German setup text

The entities exposed for a device come from its API capabilities. A temperature
sensor firmware therefore uses the same integration as a fan or e-paper
project, without project-specific Home Assistant code.

Discovered devices are stored by their stable mDNS hostname instead of their
current DHCP address. If discovery updates connection data, the integration
rebuilds its API client and requests fresh state without restarting Home
Assistant.

## Installation for development

Copy `custom_components/spacepc` to the `custom_components` directory in your
Home Assistant configuration and restart Home Assistant. Then open
**Settings → Devices & services → Add integration → SpacePC**.

HACS distribution is planned after the first compatible device firmware is
released.

## Device compatibility

A compatible device must implement [SpacePC Local API v1](docs/api-v1.md) and
advertise the mDNS service described there. Existing SpacePC firmware must be
updated to that contract before it can use native discovery and this
integration.

## Development

The project targets Home Assistant 2026.7 and Python 3.14.

```bash
python -m pip install homeassistant==2026.7.2 mypy pytest pytest-asyncio ruff
ruff check .
mypy
pytest
```

## License

MIT
