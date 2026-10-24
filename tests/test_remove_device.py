"""Deleting a vehicle's device forgets the vehicle (review on hacs/default#11813)."""

from __future__ import annotations

from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr
from homeassistant.setup import async_setup_component

from custom_components.drivepulse.const import (
    DOMAIN,
    MAX_VEHICLES,
    MSG_TRIP_END,
    MSG_TRIP_START,
)

from .conftest import find, message


def device_of(hass: HomeAssistant, entry, slug: str) -> dr.DeviceEntry | None:
    """The device of one vehicle, by its identifier."""
    identifier = (DOMAIN, f"{entry.entry_id}_{slug}")
    return next(
        (
            d
            for d in dr.async_entries_for_config_entry(
                dr.async_get(hass), entry.entry_id
            )
            if identifier in d.identifiers
        ),
        None,
    )


async def remove(
    hass: HomeAssistant, hass_ws_client: Any, entry, device_id: str
) -> dict:
    """What the frontend does when the user presses Delete on a device."""
    # the websocket command lives in the "config" component
    assert await async_setup_component(hass, "config", {})
    client = await hass_ws_client(hass)
    # The alias with config_entry_id: it exists on every Home Assistant this
    # integration supports (2024.12 on), the newer config/device_registry/remove
    # does not.
    await client.send_json(
        {
            "id": 1,
            "type": "config/device_registry/remove_config_entry",
            "config_entry_id": entry.entry_id,
            "device_id": device_id,
        }
    )
    response = await client.receive_json()
    await hass.async_block_till_done()
    return response


async def test_deleting_the_device_forgets_the_vehicle(
    hass: HomeAssistant, entry, send, hass_ws_client, hass_storage
) -> None:
    """The old name after a rename: device, entities and stored vehicle go."""
    await send(message(vehicle="Old name"))
    await send(message(vehicle="New name"))
    old = device_of(hass, entry, "old_name")
    assert old is not None

    response = await remove(hass, hass_ws_client, entry, old.id)

    assert response["success"], response
    assert dr.async_get(hass).async_get(old.id) is None
    assert find(hass, entry, "sensor", "battery_voltage", "old_name") is None
    assert find(hass, entry, "sensor", "battery_voltage", "new_name") is not None
    assert list(entry.runtime_data.vehicles) == ["new_name"]
    saved = hass_storage[f"{DOMAIN}.{entry.entry_id}"]["data"]["vehicles"]
    assert [v["name"] for v in saved] == ["New name"]


async def test_a_forgotten_vehicle_does_not_come_back_after_a_restart(
    hass: HomeAssistant, entry, send, hass_ws_client
) -> None:
    await send(message(vehicle="Old name"))
    old = device_of(hass, entry, "old_name")
    assert (await remove(hass, hass_ws_client, entry, old.id))["success"]

    assert await hass.config_entries.async_reload(entry.entry_id)
    await hass.async_block_till_done()

    assert device_of(hass, entry, "old_name") is None
    assert entry.runtime_data.vehicles == {}


async def test_a_vehicle_in_a_trip_is_kept_until_the_trip_ends(
    hass: HomeAssistant, entry, send, hass_ws_client
) -> None:
    await send(message(MSG_TRIP_START))
    device = device_of(hass, entry, "my_car")

    response = await remove(hass, hass_ws_client, entry, device.id)

    assert not response["success"]
    assert dr.async_get(hass).async_get(device.id) is not None
    assert "my_car" in entry.runtime_data.vehicles

    await send(message(MSG_TRIP_END, trip={"distance_km": 12.5}))
    assert (await remove(hass, hass_ws_client, entry, device.id))["success"]
    assert device_of(hass, entry, "my_car") is None
    assert "my_car" not in entry.runtime_data.vehicles


async def test_a_forgotten_vehicle_frees_its_place_in_the_limit(
    hass: HomeAssistant, entry, send, hass_ws_client
) -> None:
    for index in range(MAX_VEHICLES):
        assert await send(message(vehicle=f"Car {index}")) == 200
    assert await send(message(vehicle="One more")) == 400

    first = device_of(hass, entry, "car_0")
    assert (await remove(hass, hass_ws_client, entry, first.id))["success"]

    assert await send(message(vehicle="One more")) == 200
    assert device_of(hass, entry, "one_more") is not None
    assert len(entry.runtime_data.vehicles) == MAX_VEHICLES


async def test_a_vehicle_that_comes_back_gets_a_fresh_device(
    hass: HomeAssistant, entry, send, hass_ws_client
) -> None:
    """Forgotten, then the app sends it again: a new device, as for any vehicle."""
    await send(message(vehicle="My car", range_km=410))
    device = device_of(hass, entry, "my_car")
    assert (await remove(hass, hass_ws_client, entry, device.id))["success"]

    await send(message(vehicle="My car"))

    again = device_of(hass, entry, "my_car")
    assert again is not None
    assert find(hass, entry, "sensor", "battery_voltage") is not None
    # range_km came only before: the fresh vehicle has not seen it
    assert find(hass, entry, "sensor", "range") is None
