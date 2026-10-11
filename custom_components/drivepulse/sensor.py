"""Sensors of a DrivePulse vehicle."""

from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import (
    PERCENTAGE,
    REVOLUTIONS_PER_MINUTE,
    UnitOfElectricPotential,
    UnitOfLength,
    UnitOfSpeed,
    UnitOfTemperature,
    UnitOfVolume,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import DrivePulseConfigEntry
from .entity import DrivePulseEntity
from .hub import DrivePulseHub, Vehicle

LAST_TRIP = "last_trip_distance"

DESCRIPTIONS: dict[str, SensorEntityDescription] = {
    d.key: d
    for d in (
        SensorEntityDescription(
            key="fuel_level",
            translation_key="fuel_level",
            native_unit_of_measurement=PERCENTAGE,
            state_class=SensorStateClass.MEASUREMENT,
        ),
        SensorEntityDescription(
            key="battery_level",
            translation_key="battery_level",
            device_class=SensorDeviceClass.BATTERY,
            native_unit_of_measurement=PERCENTAGE,
            state_class=SensorStateClass.MEASUREMENT,
        ),
        SensorEntityDescription(
            key="range",
            translation_key="range",
            device_class=SensorDeviceClass.DISTANCE,
            native_unit_of_measurement=UnitOfLength.KILOMETERS,
            state_class=SensorStateClass.MEASUREMENT,
        ),
        SensorEntityDescription(
            key="odometer",
            translation_key="odometer",
            device_class=SensorDeviceClass.DISTANCE,
            native_unit_of_measurement=UnitOfLength.KILOMETERS,
            state_class=SensorStateClass.TOTAL_INCREASING,
            suggested_display_precision=1,
        ),
        SensorEntityDescription(
            key="battery_voltage",
            translation_key="battery_voltage",
            device_class=SensorDeviceClass.VOLTAGE,
            native_unit_of_measurement=UnitOfElectricPotential.VOLT,
            state_class=SensorStateClass.MEASUREMENT,
            suggested_display_precision=1,
        ),
        SensorEntityDescription(
            key="coolant_temperature",
            translation_key="coolant_temperature",
            device_class=SensorDeviceClass.TEMPERATURE,
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            state_class=SensorStateClass.MEASUREMENT,
        ),
        SensorEntityDescription(
            key="trouble_codes",
            translation_key="trouble_codes",
            state_class=SensorStateClass.MEASUREMENT,
        ),
        SensorEntityDescription(
            key="fuel_volume",
            translation_key="fuel_volume",
            native_unit_of_measurement=UnitOfVolume.LITERS,
            state_class=SensorStateClass.MEASUREMENT,
        ),
        SensorEntityDescription(
            key="speed",
            translation_key="speed",
            device_class=SensorDeviceClass.SPEED,
            native_unit_of_measurement=UnitOfSpeed.KILOMETERS_PER_HOUR,
            state_class=SensorStateClass.MEASUREMENT,
            entity_registry_enabled_default=False,
        ),
        SensorEntityDescription(
            key="engine_speed",
            translation_key="engine_speed",
            native_unit_of_measurement=REVOLUTIONS_PER_MINUTE,
            state_class=SensorStateClass.MEASUREMENT,
            entity_registry_enabled_default=False,
        ),
    )
}

LAST_TRIP_DESCRIPTION = SensorEntityDescription(
    key=LAST_TRIP,
    translation_key=LAST_TRIP,
    device_class=SensorDeviceClass.DISTANCE,
    native_unit_of_measurement=UnitOfLength.KILOMETERS,
    suggested_display_precision=1,
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: DrivePulseConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Create the sensors of the known vehicles, and of the ones to come."""
    hub = entry.runtime_data

    def vehicle_entities(vehicle: Vehicle) -> list[DrivePulseSensor]:
        found: list[DrivePulseSensor] = [DrivePulseLastTrip(hub, vehicle)]
        found += [
            DrivePulseSensor(hub, vehicle, DESCRIPTIONS[key])
            for key in sorted(vehicle.keys)
            if key in DESCRIPTIONS
        ]
        return found

    async_add_entities(
        entity for vehicle in hub.vehicles.values() for entity in vehicle_entities(vehicle)
    )
    hub.listen_new_vehicle(lambda vehicle: async_add_entities(vehicle_entities(vehicle)))

    def optional_sensor(vehicle: Vehicle, key: str) -> None:
        """A sensor that appears when the car first sends its number."""
        if key in DESCRIPTIONS:
            async_add_entities([DrivePulseSensor(hub, vehicle, DESCRIPTIONS[key])])

    hub.listen_new_key(optional_sensor)


class DrivePulseSensor(DrivePulseEntity, SensorEntity):
    """A number read from the car."""

    def __init__(
        self,
        hub: DrivePulseHub,
        vehicle: Vehicle,
        description: SensorEntityDescription,
    ) -> None:
        super().__init__(hub, vehicle, description.key)
        self.entity_description = description

    @property
    def native_value(self) -> float | int | None:
        return self._vehicle.values.get(self._key)

    @property
    def available(self) -> bool:
        """'Unavailable' while the car has not given this value."""
        return self.native_value is not None

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        if self._key == "trouble_codes" and self._vehicle.codes is not None:
            return {"codes": list(self._vehicle.codes)}
        return None


class DrivePulseLastTrip(DrivePulseSensor):
    """Distance of the last finished trip, with its summary as attributes."""

    def __init__(self, hub: DrivePulseHub, vehicle: Vehicle) -> None:
        super().__init__(hub, vehicle, LAST_TRIP_DESCRIPTION)

    @property
    def native_value(self) -> float | int | None:
        trip = self._vehicle.last_trip
        value = trip.get("distance_km") if trip else None
        return value if isinstance(value, (int, float)) else None

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        trip = self._vehicle.last_trip
        return (
            {k: v for k, v in trip.items() if k != "distance_km"} if trip else None
        )
