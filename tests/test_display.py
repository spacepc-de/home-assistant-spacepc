"""Tests for Home Assistant display history handling."""

from unittest.mock import AsyncMock, MagicMock, patch

from custom_components.spacepc.const import (
    CONF_DISPLAY_HISTORY_DAYS,
    CONF_DISPLAY_WIDGETS,
)
from custom_components.spacepc.display import SpacePCDisplayManager
from custom_components.spacepc.models import DisplayCapabilities


async def test_long_term_statistics_seed_graph_immediately() -> None:
    """A 30-day graph is populated before the first periodic sample."""
    recorder = MagicMock()
    recorder.async_add_executor_job = AsyncMock(side_effect=lambda job: job())
    manager = SpacePCDisplayManager(
        MagicMock(),
        AsyncMock(),
        DisplayCapabilities(
            width=800,
            height=480,
            max_widgets=6,
            max_graph_points=3,
            minimum_refresh_seconds=300,
            widget_types=("value", "status", "graph"),
        ),
        {
            CONF_DISPLAY_HISTORY_DAYS: 30,
            CONF_DISPLAY_WIDGETS: [
                {
                    "entity_id": "sensor.outside_temperature",
                    "type": "graph",
                    "label": "Outside",
                }
            ],
        },
    )

    with (
        patch(
            "custom_components.spacepc.display.get_instance",
            return_value=recorder,
        ),
        patch(
            "custom_components.spacepc.display.statistics_during_period",
            return_value={
                "sensor.outside_temperature": [
                    {"mean": 10.0, "state": None},
                    {"mean": 11.0, "state": None},
                    {"mean": 12.0, "state": None},
                    {"mean": 13.0, "state": None},
                    {"mean": 14.0, "state": None},
                ]
            },
        ),
    ):
        await manager._async_load_graph_history()

    assert list(manager._history["sensor.outside_temperature"]) == [
        10.0,
        12.0,
        14.0,
    ]
