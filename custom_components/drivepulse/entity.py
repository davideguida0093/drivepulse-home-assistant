"""Base entity: one device per vehicle, refreshed by the hub."""

from __future__ import annotations

from homeassistant.core import callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity import Entity

from .hub import DrivePulseHub, Vehicle, device_identifier, signal


class DrivePulseEntity(Entity):
    """An entity of one vehicle."""

    _attr_has_entity_name = True
    _attr_should_poll = False

    def __init__(self, hub: DrivePulseHub, vehicle: Vehicle, key: str) -> None:
        self._hub = hub
        self._vehicle = vehicle
        self._key = key
        entry_id = hub.entry.entry_id
        self._attr_unique_id = f"{entry_id}_{vehicle.slug}_{key}"
        self._attr_translation_key = key
        self._attr_device_info = DeviceInfo(
            identifiers={device_identifier(entry_id, vehicle.slug)},
            name=vehicle.name,
            manufacturer="DrivePulse",
            model="Vehicle (OBD2)",
        )

    async def async_added_to_hass(self) -> None:
        self.async_on_remove(
            async_dispatcher_connect(
                self.hass,
                signal(self._hub.entry.entry_id, self._vehicle.slug),
                self._refresh,
            )
        )

    @callback
    def _refresh(self) -> None:
        self.async_write_ha_state()
