# SpacePC Local API v1

This contract is the boundary between SpacePC firmware and clients such as
Home Assistant. Projects may expose different entities, but must use this
common transport and schema.

## Transport and discovery

- HTTP on the local network
- default port: `80`
- mDNS service: `_spacepc._tcp.local.`
- JSON request and response bodies
- API root: `/api/v1`

Required mDNS TXT records:

| Key | Description | Example |
| --- | --- | --- |
| `id` | Stable, factory/device identifier | `a4cf12ff0099` |
| `api` | Major API version | `1` |
| `project` | Firmware project identifier | `room-sensor` |
| `path` | API root | `/api/v1` |

The `id` must survive restarts, firmware updates and Wi-Fi changes. Do not use
the current IP address as an identifier.

## Authentication

`GET /api/v1/info` is available without authentication so clients can identify
the device. Its `auth_required` field tells the client whether other endpoints
require a token.

Authenticated requests use:

```text
Authorization: Bearer <device-token>
```

Tokens must never appear in mDNS records, URLs, logs or diagnostics.

## Device information

`GET /api/v1/info`

```json
{
  "api_version": 1,
  "device_id": "a4cf12ff0099",
  "name": "Living room sensor",
  "manufacturer": "SpacePC",
  "model": "ESP32 DevKit",
  "project_id": "room-sensor",
  "firmware": {
    "version": "0.2.0",
    "build_date": "2026-07-28",
    "source_commit": "0123456789abcdef"
  },
  "auth_required": false,
  "entities": [
    {
      "id": "temperature",
      "name": "Temperature",
      "platform": "sensor",
      "device_class": "temperature",
      "state_class": "measurement",
      "unit": "°C"
    }
  ]
}
```

Allowed platforms in API v1 are `sensor`, `binary_sensor`, `switch`, `light`,
`fan` and `update`. Entity IDs must remain stable across restarts.

Display devices add an optional capability object:

```json
{
  "display": {
    "width": 800,
    "height": 480,
    "max_widgets": 6,
    "max_graph_points": 48,
    "minimum_refresh_seconds": 60,
    "widget_types": ["value", "status", "graph"]
  }
}
```

## Display layout

`PUT /api/v1/display`

Home Assistant sends a complete replacement layout. E-paper devices may accept
the request immediately and coalesce it until their safe refresh interval has
elapsed.

```json
{
  "layout": {"mode": "automatic"},
  "widgets": [
    {
      "position": 0,
      "type": "value",
      "entity_id": "sensor.living_room_temperature",
      "label": "Living room",
      "value": "21.6",
      "unit": "°C",
      "available": true
    },
    {
      "position": 1,
      "type": "graph",
      "entity_id": "sensor.outside_temperature",
      "label": "Outside",
      "value": "18.2",
      "unit": "°C",
      "available": true,
      "points": [17.8, 18.0, 18.2]
    }
  ]
}
```

Supported widget types are advertised by the device. Clients must not exceed
`max_widgets` or `max_graph_points`. Successful validation returns `202
Accepted`; invalid layouts return `400` or `422`.

In automatic mode the display chooses its grid from the number of populated
widgets: one full-size tile, two half-width tiles, a 2 × 2 grid for three or
four widgets, and a 3 × 2 grid for five or six widgets.

## State

`GET /api/v1/state`

```json
{
  "entities": {
    "temperature": {
      "value": 21.6,
      "available": true
    }
  },
  "diagnostics": {
    "uptime_seconds": 86400,
    "wifi_rssi_dbm": -61,
    "free_heap_bytes": 183420
  }
}
```

Platform-specific attributes:

- `light`: `on`, optional `brightness` from `0` to `255`
- `fan`: `on`, optional `percentage` from `0` to `100`
- `switch`: `on`
- `binary_sensor`: boolean `value`
- `update`: `installed_version`, `latest_version`, `update_available`,
  optional `release_url` and `release_summary`

## Commands

`POST /api/v1/entities/{entity_id}`

The request body contains only the desired state:

```json
{"on": true}
```

```json
{"on": true, "brightness": 128}
```

```json
{"on": true, "percentage": 60}
```

Successful commands return `204 No Content`. Invalid values return `400`,
unknown entities return `404`, and missing or invalid credentials return `401`.

## Firmware updates

`POST /api/v1/update/install`

```json
{"entity_id": "firmware"}
```

The device must validate hardware compatibility, image integrity and the
SHA-256 checksum before installation. Versioned firmware artifacts are
immutable. Installation requires an explicit Home Assistant user action and
must never happen solely because the endpoint was queried.

## Errors and compatibility

Errors use JSON:

```json
{
  "error": "invalid_command",
  "message": "Percentage must be between 0 and 100"
}
```

Clients reject unsupported major `api_version` values. Additive fields may be
introduced within API v1 and must be ignored by older clients.
