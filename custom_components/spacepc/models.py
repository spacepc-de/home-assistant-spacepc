"""Data models for the SpacePC local API."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


class SpacePCDataError(ValueError):
    """Raised when a device returns an invalid API payload."""


@dataclass(frozen=True, slots=True)
class FirmwareInfo:
    """Firmware metadata reported by a SpacePC device."""

    version: str
    build_date: str | None = None
    source_commit: str | None = None


@dataclass(frozen=True, slots=True)
class EntityDefinition:
    """Definition of one entity exposed by a SpacePC device."""

    entity_id: str
    name: str
    platform: str
    device_class: str | None = None
    state_class: str | None = None
    unit: str | None = None
    icon: str | None = None


@dataclass(frozen=True, slots=True)
class DisplayCapabilities:
    """Display capabilities advertised by a SpacePC device."""

    width: int
    height: int
    max_widgets: int
    max_graph_points: int
    minimum_refresh_seconds: int
    widget_types: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class DeviceInfo:
    """Static device information."""

    api_version: int
    device_id: str
    name: str
    manufacturer: str
    model: str
    project_id: str
    firmware: FirmwareInfo
    auth_required: bool
    entities: tuple[EntityDefinition, ...]
    display: DisplayCapabilities | None = None


@dataclass(frozen=True, slots=True)
class EntityState:
    """Runtime state of an entity."""

    value: Any = None
    available: bool = True
    attributes: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class DeviceState:
    """Runtime state and diagnostics returned by a device."""

    entities: dict[str, EntityState]
    diagnostics: dict[str, Any]


def _require_mapping(value: object, field_name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        msg = f"{field_name} must be an object"
        raise SpacePCDataError(msg)
    return value


def _require_string(data: dict[str, Any], field_name: str) -> str:
    value = data.get(field_name)
    if not isinstance(value, str) or not value:
        msg = f"{field_name} must be a non-empty string"
        raise SpacePCDataError(msg)
    return value


def parse_device_info(payload: object) -> DeviceInfo:
    """Validate and parse a device information payload."""
    data = _require_mapping(payload, "response")
    api_version = data.get("api_version")
    if not isinstance(api_version, int):
        raise SpacePCDataError("api_version must be an integer")

    firmware_data = _require_mapping(data.get("firmware"), "firmware")
    raw_entities = data.get("entities")
    if not isinstance(raw_entities, list):
        raise SpacePCDataError("entities must be an array")

    entities: list[EntityDefinition] = []
    for raw_entity in raw_entities:
        entity = _require_mapping(raw_entity, "entity")
        entities.append(
            EntityDefinition(
                entity_id=_require_string(entity, "id"),
                name=_require_string(entity, "name"),
                platform=_require_string(entity, "platform"),
                device_class=_optional_string(entity.get("device_class")),
                state_class=_optional_string(entity.get("state_class")),
                unit=_optional_string(entity.get("unit")),
                icon=_optional_string(entity.get("icon")),
            )
        )

    display = _parse_display_capabilities(data.get("display"))
    return DeviceInfo(
        api_version=api_version,
        device_id=_require_string(data, "device_id"),
        name=_require_string(data, "name"),
        manufacturer=_require_string(data, "manufacturer"),
        model=_require_string(data, "model"),
        project_id=_require_string(data, "project_id"),
        firmware=FirmwareInfo(
            version=_require_string(firmware_data, "version"),
            build_date=_optional_string(firmware_data.get("build_date")),
            source_commit=_optional_string(firmware_data.get("source_commit")),
        ),
        auth_required=bool(data.get("auth_required", False)),
        entities=tuple(entities),
        display=display,
    )


def parse_device_state(payload: object) -> DeviceState:
    """Validate and parse a device state payload."""
    data = _require_mapping(payload, "response")
    raw_entities = _require_mapping(data.get("entities"), "entities")
    diagnostics = _require_mapping(data.get("diagnostics", {}), "diagnostics")

    entities: dict[str, EntityState] = {}
    for entity_id, raw_state in raw_entities.items():
        state = _require_mapping(raw_state, f"entities.{entity_id}")
        attributes = {
            key: value for key, value in state.items() if key not in {"value", "available"}
        }
        entities[entity_id] = EntityState(
            value=state.get("value"),
            available=bool(state.get("available", True)),
            attributes=attributes,
        )

    return DeviceState(entities=entities, diagnostics=diagnostics)


def _optional_string(value: object) -> str | None:
    return value if isinstance(value, str) and value else None


def _parse_display_capabilities(value: object) -> DisplayCapabilities | None:
    if value is None:
        return None
    data = _require_mapping(value, "display")
    widget_types = data.get("widget_types")
    if not isinstance(widget_types, list) or not all(
        isinstance(widget_type, str) for widget_type in widget_types
    ):
        raise SpacePCDataError("display.widget_types must be an array of strings")
    return DisplayCapabilities(
        width=_require_positive_int(data, "width"),
        height=_require_positive_int(data, "height"),
        max_widgets=_require_positive_int(data, "max_widgets"),
        max_graph_points=_require_positive_int(data, "max_graph_points"),
        minimum_refresh_seconds=_require_positive_int(
            data, "minimum_refresh_seconds"
        ),
        widget_types=tuple(widget_types),
    )


def _require_positive_int(data: dict[str, Any], field_name: str) -> int:
    value = data.get(field_name)
    if not isinstance(value, int) or value <= 0:
        msg = f"display.{field_name} must be a positive integer"
        raise SpacePCDataError(msg)
    return value
