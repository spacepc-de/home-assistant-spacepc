<p align="center">
  <a href="https://spacepc.dev">
    <img src="assets/spacepc-logo.png" alt="SpacePC.dev" width="520">
  </a>
</p>

<h1 align="center">SpacePC for Home Assistant</h1>

Local-first Home Assistant integration for SpacePC devices.

[![HACS validation](https://github.com/spacepc-de/home-assistant-spacepc/actions/workflows/hacs.yml/badge.svg)](https://github.com/spacepc-de/home-assistant-spacepc/actions/workflows/hacs.yml)
[![Hassfest](https://github.com/spacepc-de/home-assistant-spacepc/actions/workflows/hassfest.yml/badge.svg)](https://github.com/spacepc-de/home-assistant-spacepc/actions/workflows/hassfest.yml)

SpacePC devices are discovered over mDNS and communicate with Home Assistant
through the versioned local SpacePC HTTP API. MQTT remains available as an
optional interface for users and systems outside Home Assistant, but it is not
required by this integration.

## Status

Version 0.1.x is the first stable SpacePC Local API v1 integration series.

## Features

- automatic discovery via `_spacepc._tcp.local.`
- automatic recovery after Wi-Fi reconnects or DHCP address changes
- manual setup by hostname or IP address
- sensors and binary sensors
- switches, lights and fans
- device and connection diagnostics
- firmware update entities
- configurable e-paper dashboards with value, status and graph widgets
- selectable 5, 10, 15, 30 or 60 minute display refresh interval
- optional bearer-token authentication
- English and German setup text

The entities exposed for a device come from its API capabilities. A temperature
sensor firmware therefore uses the same integration as a fan or e-paper
project, without project-specific Home Assistant code.

Display-capable firmware advertises its dimensions and widget limits through
the same API. Use **Configure** on the SpacePC device to select Home Assistant
entities and choose their widget types in one six-slot editor. Empty slots are
ignored; the display automatically uses one full tile, two halves, four
quarters or six tiles. A custom dashboard title can be shown beside the local
time of the latest Home Assistant update. Ten minutes is the recommended default for the supported
full-refresh e-paper panel. Graph widgets are seeded from the last 24 hours of
Home Assistant recorder history and continue collecting new samples in memory.

Discovered devices are stored by their stable mDNS hostname instead of their
current DHCP address. If discovery updates connection data, the integration
rebuilds its API client and requests fresh state without restarting Home
Assistant.

## Installation with HACS

Open the repository directly in HACS:

[Add SpacePC to HACS](https://my.home-assistant.io/redirect/hacs_repository/?owner=spacepc-de&repository=home-assistant-spacepc&category=integration)

Alternatively, add this repository as a custom HACS integration repository,
install SpacePC, restart Home Assistant and add **SpacePC** from
**Settings → Devices & services**.

## Manual installation

Copy `custom_components/spacepc` to the `custom_components` directory in your
Home Assistant configuration and restart Home Assistant. Then open
**Settings → Devices & services → Add integration → SpacePC**.

## Device compatibility

A compatible device must implement [SpacePC Local API v1](docs/api-v1.md) and
advertise the mDNS service described there. Existing SpacePC firmware must be
updated to that contract before it can use native discovery and this
integration.

## Development

The integration supports Home Assistant 2026.5 or newer. Development and CI
currently target Home Assistant 2026.7 and Python 3.14.

```bash
python -m pip install pytest-homeassistant-custom-component==0.13.348 mypy ruff
ruff check .
mypy
pytest
```

## License

MIT
