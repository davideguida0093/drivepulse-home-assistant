"""Binary sensors of a DrivePulse vehicle."""

from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import DrivePulseConfigEntry
from .entity import DrivePulseEntity
from .hub import DrivePulseHub, Vehicle

TRIP_IN_PROGRESS = BinarySensorEntityDescription(
    key="trip_in_progress",
    translation_key="trip_in_progress",
    device_class=BinarySensorDeviceClass.RUNNING,
)
ADAPTER_CONNECTED = BinarySensorEntityDescription(
    key="adapter_connected",
    translation_key="adapter_connected",
    device_class=BinarySensorDeviceClass.CONNECTIVITY,
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: DrivePulseConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Create the binary sensors of the known vehicles, and of the ones to come."""
    hub = entry.runtime_data

    def vehicle_entities(vehicle: Vehicle) -> list[DrivePulseBinarySensor]:
        return [
            DrivePulseBinarySensor(hub, vehicle, TRIP_IN_PROGRESS),
            DrivePulseBinarySensor(hub, vehicle, ADAPTER_CONNECTED),
        ]

    async_add_entities(
        entity for vehicle in hub.vehicles.values() for entity in vehicle_entities(vehicle)
    )
    hub.listen_new_vehicle(lambda vehicle: async_add_entities(vehicle_entities(vehicle)))


class DrivePulseBinarySensor(DrivePulseEntity, BinarySensorEntity):
    """Trip in progress / adapter connected."""

    def __init__(
        self,
        hub: DrivePulseHub,
        vehicle: Vehicle,
        description: BinarySensorEntityDescription,
    ) -> None:
        super().__init__(hub, vehicle, description.key)
        self.entity_description = description

    @property
    def is_on(self) -> bool | None:
        if self._key == "trip_in_progress":
            return self._vehicle.in_trip
        return self._vehicle.adapter_connected

    @property
    def available(self) -> bool:
        return self._key == "trip_in_progress" or self.is_on is not None
