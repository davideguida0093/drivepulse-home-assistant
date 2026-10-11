"""The webhook: messages in, sensors and events out."""

from __future__ import annotations

from homeassistant.const import STATE_OFF, STATE_ON, STATE_UNAVAILABLE
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr

from custom_components.drivepulse.const import (
    DOMAIN,
    EVENT_TRIP_END,
    EVENT_TRIP_START,
    MAX_VEHICLES,
)

from .conftest import find, message


def state(hass: HomeAssistant, entry, domain: str, key: str, vehicle: str = "my_car"):
    entity_id = find(hass, entry, domain, key, vehicle)
    assert entity_id, f"no {domain} {key} for {vehicle}"
    return hass.states.get(entity_id)


async def test_live_creates_one_device_per_vehicle_without_vin(
    hass: HomeAssistant, entry, send
) -> None:
    payload = message(vin="WVWZZZAUZKW123456", latitude=45.1, longitude=9.2)
    assert await send(payload) == 200

    devices = dr.async_entries_for_config_entry(dr.async_get(hass), entry.entry_id)
    assert [d.name for d in devices] == ["My car"]
    identifiers = {i for d in devices for i in d.identifiers}
    assert identifiers == {(DOMAIN, f"{entry.entry_id}_my_car")}
    # Nothing the app might send beyond the schema lands anywhere.
    dump = repr([s.attributes for s in hass.states.async_all()])
    assert "WVWZZZ" not in dump and "45.1" not in dump


async def test_live_values_become_sensors(hass: HomeAssistant, entry, send) -> None:
    await send(message(range_km=410, fuel_level_l=33.0))
    assert state(hass, entry, "sensor", "fuel_level").state == "62.0"
    assert state(hass, entry, "sensor", "battery_voltage").state == "14.1"
    assert state(hass, entry, "sensor", "coolant_temperature").state == "88"
    assert state(hass, entry, "sensor", "range").state == "410"
    assert state(hass, entry, "sensor", "fuel_volume").state == "33.0"
    assert state(hass, entry, "binary_sensor", "adapter_connected").state == STATE_ON
    assert state(hass, entry, "binary_sensor", "trip_in_progress").state == STATE_OFF


async def test_a_missing_value_is_unavailable(hass: HomeAssistant, entry, send) -> None:
    await send(message())
    # dtc_count and odometer were null: the sensors exist and say so.
    assert state(hass, entry, "sensor", "trouble_codes").state == STATE_UNAVAILABLE
    assert state(hass, entry, "sensor", "odometer").state == STATE_UNAVAILABLE
    assert state(hass, entry, "sensor", "last_trip_distance").state == STATE_UNAVAILABLE
    # and a value that disappears from the next live goes unavailable too
    await send(message(battery_voltage=None))
    assert state(hass, entry, "sensor", "battery_voltage").state == STATE_UNAVAILABLE
    await send(message(battery_voltage=12.6))
    assert state(hass, entry, "sensor", "battery_voltage").state == "12.6"


async def test_things_that_are_not_numbers_are_unavailable(
    hass: HomeAssistant, entry, send
) -> None:
    await send(message(fuel_level_pct=50))
    for bad in (True, "62", [1], {"a": 1}):
        assert await send(message(fuel_level_pct=bad)) == 200
        assert state(hass, entry, "sensor", "fuel_level").state == STATE_UNAVAILABLE, bad
        await send(message(fuel_level_pct=50))
        assert state(hass, entry, "sensor", "fuel_level").state == "50"


async def test_nan_and_infinity_are_refused(hass: HomeAssistant, entry, send) -> None:
    """Not valid JSON: refused, and the sensor keeps what it had."""
    await send(message(fuel_level_pct=50))
    for bad in ("NaN", "Infinity", "-Infinity"):
        raw = '{"event": "live", "vehicle": "My car", "fuel_level_pct": %s}' % bad
        assert await send(None, raw=raw) == 400
        assert state(hass, entry, "sensor", "fuel_level").state == "50"


async def test_electric_car_has_charge_not_fuel(hass: HomeAssistant, entry, send) -> None:
    await send(message(vehicle="My EV", fuel_level_pct=None, hv_soc_pct=71.5))
    assert state(hass, entry, "sensor", "battery_level", "my_ev").state == "71.5"
    assert find(hass, entry, "sensor", "fuel_level", "my_ev") is None


async def test_petrol_car_has_no_battery_level(hass: HomeAssistant, entry, send) -> None:
    await send(message())
    assert find(hass, entry, "sensor", "battery_level") is None


async def test_sticky_values_survive_a_message_without_them(
    hass: HomeAssistant, entry, send
) -> None:
    await send(
        message("trip_end", odometer_km=20364.8, dtc_count=2, dtc=["P0420", "P0171"],
                range_km=380)
    )
    assert state(hass, entry, "sensor", "odometer").state == "20364.8"
    codes = state(hass, entry, "sensor", "trouble_codes")
    assert codes.state == "2" and codes.attributes["codes"] == ["P0420", "P0171"]

    # the next live does not carry them: they keep their last good value
    await send(message(odometer_km=None, dtc_count=None, dtc=None, range_km=None))
    assert state(hass, entry, "sensor", "odometer").state == "20364.8"
    assert state(hass, entry, "sensor", "trouble_codes").state == "2"
    assert state(hass, entry, "sensor", "range").state == "380"
    # while the fast ones follow the car
    await send(message(rpm=None, coolant_temp_c=None))
    assert state(hass, entry, "sensor", "coolant_temperature").state == STATE_UNAVAILABLE


async def test_trip_start_and_end(hass: HomeAssistant, entry, send) -> None:
    events = []
    hass.bus.async_listen(EVENT_TRIP_START, events.append)
    hass.bus.async_listen(EVENT_TRIP_END, events.append)

    await send(message("trip_start", vin="X", latitude=1.0, address="Via Roma"))
    assert state(hass, entry, "binary_sensor", "trip_in_progress").state == STATE_ON
    assert [e.event_type for e in events] == [EVENT_TRIP_START]
    start = events[0].data
    assert start["vehicle"] == "My car"
    assert start["fuel_level_pct"] == 62.0
    # fields the car did not give are present and empty, never missing
    assert start["odometer_km"] is None and start["dtc_count"] is None
    assert start["device_id"]
    # no position, no VIN, no address, whatever the sender added
    assert not {"vin", "latitude", "address", "extended", "rpm"} & set(start)

    trip = {"id": 5, "start": "2026-10-11T00:41:09Z", "end": "2026-10-11T00:42:51Z",
            "distance_km": 12.5, "duration_min": 14.0, "avg_speed_kmh": 47.5,
            "max_speed_kmh": 90.0, "avg_consumption_l_100km": 6.8,
            "odometer_km": 20364.8, "route": "secret"}
    await send(message("trip_end", odometer_km=20364.8, obd_connected=False, trip=trip))
    assert state(hass, entry, "binary_sensor", "trip_in_progress").state == STATE_OFF
    assert state(hass, entry, "binary_sensor", "adapter_connected").state == STATE_OFF
    last = state(hass, entry, "sensor", "last_trip_distance")
    assert last.state == "12.5"
    assert last.attributes["duration_min"] == 14.0
    assert last.attributes["avg_consumption_l_100km"] == 6.8
    assert "route" not in last.attributes and "id" not in last.attributes

    assert [e.event_type for e in events] == [EVENT_TRIP_START, EVENT_TRIP_END]
    end = events[1].data
    assert end["trip"]["distance_km"] == 12.5 and "route" not in end["trip"]
    assert end["odometer_km"] == 20364.8


async def test_trip_end_without_a_trip_object(hass: HomeAssistant, entry, send) -> None:
    await send(message("trip_end"))
    assert state(hass, entry, "sensor", "last_trip_distance").state == STATE_UNAVAILABLE
    assert state(hass, entry, "binary_sensor", "trip_in_progress").state == STATE_OFF


async def test_two_vehicles_two_devices(hass: HomeAssistant, entry, send) -> None:
    await send(message(vehicle="Golf"))
    await send(message(vehicle="Panda", battery_voltage=12.2))
    names = sorted(
        d.name for d in dr.async_entries_for_config_entry(dr.async_get(hass), entry.entry_id)
    )
    assert names == ["Golf", "Panda"]
    assert state(hass, entry, "sensor", "battery_voltage", "panda").state == "12.2"
    assert state(hass, entry, "sensor", "battery_voltage", "golf").state == "14.1"


async def test_vehicle_without_a_name_gets_the_default(hass, entry, send) -> None:
    await send(message(vehicle=None))
    await send(message(vehicle="   "))
    names = [
        d.name for d in dr.async_entries_for_config_entry(dr.async_get(hass), entry.entry_id)
    ]
    assert names == ["DrivePulse"]


async def test_vehicle_limit(hass: HomeAssistant, entry, send) -> None:
    for i in range(MAX_VEHICLES):
        assert await send(message(vehicle=f"Car {i}")) == 200
    assert await send(message(vehicle="One too many")) == 400
    devices = dr.async_entries_for_config_entry(dr.async_get(hass), entry.entry_id)
    assert len(devices) == MAX_VEHICLES


async def test_bad_bodies_are_refused_and_change_nothing(
    hass: HomeAssistant, entry, send
) -> None:
    assert await send(None, raw="this is not json") == 400
    assert await send(None, raw="[1, 2]") == 400
    assert await send(None, raw='"text"') == 400
    assert not dr.async_entries_for_config_entry(dr.async_get(hass), entry.entry_id)


async def test_test_and_unknown_events_are_accepted_and_ignored(
    hass: HomeAssistant, entry, send
) -> None:
    assert await send(message("test")) == 200
    assert await send(message("something_new")) == 200
    assert await send({"no": "event"}) == 200
    assert not dr.async_entries_for_config_entry(dr.async_get(hass), entry.entry_id)


async def test_a_newer_schema_still_works(hass: HomeAssistant, entry, send) -> None:
    await send(message(schema=2, brand_new_field="x"))
    assert state(hass, entry, "sensor", "battery_voltage").state == "14.1"


async def test_restart_keeps_the_vehicle_and_the_slow_values(
    hass: HomeAssistant, entry, send
) -> None:
    await send(message("trip_end", odometer_km=1000.5, dtc_count=1, dtc=["P0300"]))
    await send(message("trip_start"))
    assert await hass.config_entries.async_unload(entry.entry_id)
    await hass.async_block_till_done()
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    assert state(hass, entry, "sensor", "odometer").state == "1000.5"
    assert state(hass, entry, "sensor", "trouble_codes").attributes["codes"] == ["P0300"]
    assert state(hass, entry, "binary_sensor", "trip_in_progress").state == STATE_ON
    # a live value from before the restart is not shown as if it were fresh
    assert state(hass, entry, "sensor", "battery_voltage").state == STATE_UNAVAILABLE
    # and the first live after the restart fills it again
    await send(message(battery_voltage=13.9))
    assert state(hass, entry, "sensor", "battery_voltage").state == "13.9"
    devices = dr.async_entries_for_config_entry(dr.async_get(hass), entry.entry_id)
    assert len(devices) == 1


async def test_optional_sensors_come_back_after_restart(
    hass: HomeAssistant, entry, send
) -> None:
    await send(message(fuel_level_pct=40))
    assert await hass.config_entries.async_unload(entry.entry_id)
    await hass.async_block_till_done()
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    assert state(hass, entry, "sensor", "fuel_level").state == STATE_UNAVAILABLE


async def test_a_long_vehicle_name_is_cut_at_64(hass: HomeAssistant, entry, send) -> None:
    await send(message(vehicle="x" * 100))
    names = [
        d.name for d in dr.async_entries_for_config_entry(dr.async_get(hass), entry.entry_id)
    ]
    assert names == ["x" * 64]


async def test_adapter_flag_that_is_not_a_boolean_is_ignored(
    hass: HomeAssistant, entry, send
) -> None:
    await send(message(obd_connected="yes"))
    assert state(hass, entry, "binary_sensor", "adapter_connected").state == STATE_UNAVAILABLE
    await send(message(obd_connected=True))
    assert state(hass, entry, "binary_sensor", "adapter_connected").state == STATE_ON


async def test_no_more_than_fifty_trouble_codes_are_kept(
    hass: HomeAssistant, entry, send
) -> None:
    codes = [f"P{i:04d}" for i in range(60)]
    await send(message("trip_end", dtc_count=60, dtc=codes))
    kept = state(hass, entry, "sensor", "trouble_codes").attributes["codes"]
    assert kept == codes[:50]
