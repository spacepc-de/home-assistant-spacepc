"""Push selected Home Assistant entities to a SpacePC display."""

from __future__ import annotations

from collections import defaultdict, deque
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import timedelta
from functools import partial
from typing import Any

from homeassistant.components.recorder.history import get_significant_states
from homeassistant.core import Event, HomeAssistant
from homeassistant.helpers.event import async_track_state_change_event, async_track_time_interval
from homeassistant.helpers.recorder import get_instance
from homeassistant.util import dt as dt_util

from .api import SpacePCClient, SpacePCError
from .const import (
    CONF_DISPLAY_INTERVAL,
    CONF_DISPLAY_TITLE,
    CONF_DISPLAY_WIDGETS,
    DEFAULT_DISPLAY_INTERVAL_SECONDS,
)
from .models import DisplayCapabilities


@dataclass(slots=True)
class SpacePCDisplayManager:
    """Collect states and periodically render them on the physical display."""

    hass: HomeAssistant
    client: SpacePCClient
    capabilities: DisplayCapabilities
    options: dict[str, Any]
    _history: dict[str, deque[float]] = field(init=False)
    _unsubscribers: list[Callable[[], None]] = field(init=False, default_factory=list)

    def __post_init__(self) -> None:
        self._history = defaultdict(
            lambda: deque(maxlen=self.capabilities.max_graph_points)
        )

    async def async_start(self) -> None:
        """Start subscriptions and send the initial layout."""
        entity_ids = {
            widget["entity_id"]
            for widget in self._widgets
            if isinstance(widget.get("entity_id"), str)
        }
        if entity_ids:
            self._unsubscribers.append(
                async_track_state_change_event(
                    self.hass,
                    entity_ids,
                    self._async_state_changed,
                )
            )
        interval = max(
            self.capabilities.minimum_refresh_seconds,
            int(
                self.options.get(
                    CONF_DISPLAY_INTERVAL,
                    DEFAULT_DISPLAY_INTERVAL_SECONDS,
                )
            ),
        )
        self._unsubscribers.append(
            async_track_time_interval(
                self.hass,
                self._async_periodic_update,
                timedelta(seconds=interval),
            )
        )
        await self._async_load_graph_history()
        self._sample_graphs()
        await self._async_push()

    def async_stop(self) -> None:
        """Stop all display listeners."""
        for unsubscribe in self._unsubscribers:
            unsubscribe()
        self._unsubscribers.clear()

    @property
    def _widgets(self) -> list[dict[str, Any]]:
        widgets = self.options.get(CONF_DISPLAY_WIDGETS, [])
        return widgets if isinstance(widgets, list) else []

    async def _async_state_changed(self, event: Event[Any]) -> None:
        self._sample_entity(event.data["entity_id"])

    async def _async_periodic_update(self, _now: object) -> None:
        self._sample_graphs()
        await self._async_push()

    def _sample_graphs(self) -> None:
        for widget in self._widgets:
            if widget.get("type") == "graph":
                self._sample_entity(widget.get("entity_id"))

    async def _async_load_graph_history(self) -> None:
        """Seed graph widgets from the last 24 hours of recorder history."""
        entity_ids = {
            widget["entity_id"]
            for widget in self._widgets
            if widget.get("type") == "graph"
            and isinstance(widget.get("entity_id"), str)
        }
        if not entity_ids:
            return
        try:
            states_by_entity = await get_instance(self.hass).async_add_executor_job(
                partial(
                    get_significant_states,
                    self.hass,
                    dt_util.utcnow() - timedelta(hours=24),
                    entity_ids=list(entity_ids),
                    significant_changes_only=False,
                    no_attributes=True,
                )
            )
        except KeyError:
            return

        for entity_id, states in states_by_entity.items():
            values: list[float] = []
            for state in states:
                if not hasattr(state, "state"):
                    continue
                try:
                    values.append(float(state.state))
                except ValueError:
                    continue
            if len(values) > self.capabilities.max_graph_points:
                last_index = len(values) - 1
                values = [
                    values[
                        round(
                            index
                            * last_index
                            / (self.capabilities.max_graph_points - 1)
                        )
                    ]
                    for index in range(self.capabilities.max_graph_points)
                ]
            self._history[entity_id].extend(values)

    def _sample_entity(self, entity_id: object) -> None:
        if not isinstance(entity_id, str):
            return
        state = self.hass.states.get(entity_id)
        if state is None:
            return
        try:
            value = float(state.state)
        except ValueError:
            return
        self._history[entity_id].append(value)

    async def _async_push(self) -> None:
        widgets = []
        for position, configured in enumerate(self._widgets):
            entity_id = configured.get("entity_id")
            if not isinstance(entity_id, str):
                continue
            state = self.hass.states.get(entity_id)
            widget_type = configured.get("type", "value")
            widget: dict[str, Any] = {
                "position": position,
                "type": widget_type,
                "entity_id": entity_id,
                "label": configured.get("label")
                or (state.name if state is not None else entity_id),
                "value": state.state if state is not None else "unknown",
                "unit": state.attributes.get("unit_of_measurement", "")
                if state is not None
                else "",
                "available": state is not None
                and state.state not in {"unavailable", "unknown"},
            }
            if widget_type == "graph":
                widget["points"] = list(self._history[entity_id])
            widgets.append(widget)
        try:
            await self.client.async_update_display(
                {
                    "layout": {
                        "mode": "automatic",
                        "title": self.options.get(CONF_DISPLAY_TITLE, "Home"),
                        "updated_at": dt_util.as_local(dt_util.utcnow()).strftime(
                            "%H:%M"
                        ),
                    },
                    "widgets": widgets,
                }
            )
        except SpacePCError:
            # The normal coordinator reports reachability; retry at the next interval.
            return
