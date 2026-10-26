"""The automation examples and the dashboard card of the README, on a real Home Assistant.

The YAML is read from README.md itself (the "Automation examples" section), so the
README stays the only copy and a broken example fails here.
"""

from __future__ import annotations

import re
from datetime import timedelta
from pathlib import Path

import yaml
from homeassistant.core import HomeAssistant
from homeassistant.setup import async_setup_component
from homeassistant.util import dt as dt_util
from pytest_homeassistant_custom_component.common import (
    async_fire_time_changed,
    async_mock_service,
)

from .conftest import message

README = Path(__file__).resolve().parents[1] / "README.md"

TRIP = {
    "start": "2026-10-11T00:41:09Z",
    "end": "2026-10-11T00:55:09Z",
    "distance_km": 12.5,
    "duration_min": 14.0,
    "avg_speed_kmh": 47.5,
    "max_speed_kmh": 90.0,
    "avg_consumption_l_100km": 6.8,
    "odometer_km": 20364.8,
}


def readme_examples() -> tuple[list[dict], dict]:
    """The five automations and the dashboard card, as the README shows them."""
    text = README.read_text(encoding="utf-8")
    start = text.index("## Automation examples")
    end = text.index("\n## ", start + 1)
    blocks = re.findall(r"```yaml\n(.*?)```", text[start:end], re.DOTALL)
    assert len(blocks) == 6, len(blocks)
    automations = [yaml.safe_load(b) for b in blocks[:5]]
    return automations, yaml.safe_load(blocks[5])


def dashboard_entities(node, found: list) -> list:
    if isinstance(node, dict):
        if "entity" in node:
            found.append((node["entity"], node.get("attribute")))
        for value in node.values():
            dashboard_entities(value, found)
    elif isinstance(node, list):
        for value in node:
            dashboard_entities(value, found)
    return found


async def test_readme_automations_and_dashboard(hass: HomeAssistant, entry, send) -> None:
    """Five automations loaded from the README fire as described; the card's entities exist."""
    await hass.config.async_set_time_zone("Europe/Rome")
    calls = async_mock_service(hass, "notify", "notify")
    assert await async_setup_component(
        hass,
        "input_datetime",
        {"input_datetime": {"car_inspection": {"name": "Car inspection", "has_date": True, "has_time": False}}},
    )
    automations, dashboard = readme_examples()
    assert await async_setup_component(hass, "automation", {"automation": automations})
    await hass.async_block_till_done()
    states = hass.states.async_all("automation")
    assert len(states) == 5 and all(s.state == "on" for s in states), [(s.entity_id, s.state) for s in states]

    # first contact and a quiet trip: only the trip summary
    assert await send(message()) == 200
    await send(message("trip_start"))
    await send(message("trip_end", odometer_km=20364.8, dtc_count=0, dtc=[], obd_connected=False, trip=TRIP))
    assert len(calls) == 1, [c.data for c in calls]
    assert "12.5 km" in calls[0].data["message"]

    # 12 V battery below 12 V: nothing at once, a notice after a minute
    await send(message(battery_voltage=11.6))
    assert len(calls) == 1
    async_fire_time_changed(hass, dt_util.utcnow() + timedelta(seconds=70))
    await hass.async_block_till_done()
    assert len(calls) == 2 and "11.6 V" in calls[-1].data["message"]
    await send(message(battery_voltage=14.1))

    # inspection in 10 days, low fuel and a new code at the end of the next trip: four notices
    due = (dt_util.now() + timedelta(days=10)).date().isoformat()
    await hass.services.async_call(
        "input_datetime", "set_datetime", {"entity_id": "input_datetime.car_inspection", "date": due}, blocking=True
    )
    await send(message("trip_start", fuel_level_pct=15.0))
    await send(
        message(
            "trip_end",
            fuel_level_pct=15.0,
            odometer_km=20377.3,
            dtc_count=1,
            dtc=["P0420"],
            obd_connected=False,
            trip=dict(TRIP, odometer_km=20377.3),
        )
    )
    new = calls[2:]
    assert sorted(c.data.get("title") for c in new) == sorted(
        ["Low fuel", "New trouble code", "My car: trip finished", "Inspection coming up"]
    )
    joined = " ".join(" ".join(c.data["message"].split()) for c in new)
    assert "P0420" in joined and "15 % left" in joined and "in 10 days" in joined and "20,377 km" in joined

    # the same code again: no second notice
    await send(message("trip_end", fuel_level_pct=60.0, odometer_km=20380.0, dtc_count=1, dtc=["P0420"], trip=None))
    assert not any("P0420" in c.data["message"] for c in calls[6:]), [c.data for c in calls[6:]]

    # every entity and attribute the dashboard card shows exists
    for entity_id, attribute in dashboard_entities(dashboard, []):
        state = hass.states.get(entity_id)
        assert state is not None, entity_id
        if attribute:
            assert attribute in state.attributes, (entity_id, attribute, dict(state.attributes))
