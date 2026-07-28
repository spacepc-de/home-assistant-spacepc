"""Helpers shared by SpacePC entity platforms."""

from __future__ import annotations

from collections.abc import Callable

from .coordinator import SpacePCDataUpdateCoordinator
from .models import EntityDefinition


def entities_for_platform[EntityT](
    coordinator: SpacePCDataUpdateCoordinator,
    platform: str,
    factory: Callable[[SpacePCDataUpdateCoordinator, EntityDefinition], EntityT],
) -> list[EntityT]:
    """Create all device entities for a Home Assistant platform."""
    return [
        factory(coordinator, definition)
        for definition in coordinator.device_info.entities
        if definition.platform == platform
    ]
