"""Shared SpacePC entity implementation."""

from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo as HADeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import SpacePCDataUpdateCoordinator
from .models import EntityDefinition, EntityState


class SpacePCEntity(CoordinatorEntity[SpacePCDataUpdateCoordinator]):
    """Base class for a SpacePC entity."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: SpacePCDataUpdateCoordinator,
        definition: EntityDefinition,
    ) -> None:
        super().__init__(coordinator)
        self.definition = definition
        self._attr_unique_id = f"{coordinator.device_info.device_id}_{definition.entity_id}"
        self._attr_name = definition.name
        self._attr_icon = definition.icon
        info = coordinator.device_info
        self._attr_device_info = HADeviceInfo(
            identifiers={(DOMAIN, info.device_id)},
            name=info.name,
            manufacturer=info.manufacturer,
            model=info.model,
            sw_version=info.firmware.version,
        )

    @property
    def state_data(self) -> EntityState | None:
        """Return the current state for this entity."""
        return self.coordinator.data.entities.get(self.definition.entity_id)

    @property
    def available(self) -> bool:
        """Return whether the entity and device are available."""
        state = self.state_data
        return super().available and state is not None and state.available
