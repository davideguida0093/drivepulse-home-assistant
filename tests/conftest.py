"""Fixtures for the DrivePulse tests."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import pytest
from homeassistant.const import CONF_WEBHOOK_ID
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from homeassistant.setup import async_setup_component
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.drivepulse.const import DOMAIN

WEBHOOK_ID = "drivepulse_test_webhook"


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations: None) -> None:
    """Let Home Assistant load custom_components/ in every test."""


@pytest.fixture(autouse=True)
async def webhook_ready(hass: HomeAssistant) -> None:
    """The webhook integration is a dependency: set it up once."""
    assert await async_setup_component(hass, "webhook", {})


@pytest.fixture
async def entry(hass: HomeAssistant) -> MockConfigEntry:
    """A set-up DrivePulse entry with a known webhook id."""
    config_entry = MockConfigEntry(
        domain=DOMAIN,
        title="DrivePulse",
        data={CONF_WEBHOOK_ID: WEBHOOK_ID},
    )
    config_entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()
    return config_entry


@pytest.fixture
def send(hass: HomeAssistant, hass_client_no_auth: Any) -> Callable[..., Any]:
    """POST a message to the webhook, wait for the entities to settle."""

    async def _send(payload: Any, *, raw: str | None = None) -> int:
        client = await hass_client_no_auth()
        if raw is not None:
            response = await client.post(
                f"/api/webhook/{WEBHOOK_ID}",
                data=raw,
                headers={"Content-Type": "application/json"},
            )
        else:
            response = await client.post(f"/api/webhook/{WEBHOOK_ID}", json=payload)
        await hass.async_block_till_done()
        return response.status

    return _send


def message(event: str = "live", **fields: Any) -> dict[str, Any]:
    """A message shaped like the app's (schema 1), with the given values."""
    body: dict[str, Any] = {
        "source": "drivepulse",
        "schema": 1,
        "event": event,
        "sent_at": "2026-10-11T00:41:59.418857Z",
        "units": "metric",
        "vehicle": "My car",
        "obd_connected": True,
        "rpm": 1000,
        "speed_kmh": 50,
        "coolant_temp_c": 88,
        "battery_voltage": 14.1,
        "fuel_level_pct": 62.0,
        "hv_soc_pct": None,
        "range_km": None,
        "odometer_km": None,
        "dtc_count": None,
        "dtc": None,
        "fuel_level_l": None,
        "extended": {},
    }
    body.update(fields)
    return body


def find(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    domain: str,
    key: str,
    vehicle: str = "my_car",
) -> str | None:
    """The entity id of a vehicle's entity, by its unique id."""
    return er.async_get(hass).async_get_entity_id(
        domain, DOMAIN, f"{entry.entry_id}_{vehicle}_{key}"
    )
