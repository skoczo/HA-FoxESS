"""Platform for FoxESSSensor integration."""
from __future__ import annotations

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.const import ENERGY_KILO_WATT_HOUR, POWER_KILO_WATT

from .const import *

from .connector import FoxEssConnector
from .coordinator import FoxESSUpdateCoordinator, FoxESSStatisticsCoordinator

import logging
from decimal import Decimal

_LOGGER = logging.getLogger(__name__)

CONNECTOR: FoxEssConnector = None


async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    async_add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    CONNECTOR = FoxEssConnector(config[USERNAME], config[PASSWORD], config[DEVICE_ID])

    coordinator = FoxESSUpdateCoordinator(hass, CONNECTOR)
    await coordinator.async_request_refresh()

    sensors = []

    for sensor_data in SENSOR_TYPES_YAML:
        entity = SENSOR_TYPES_YAML[sensor_data]
        sensors.append(
            FoxESSSensor(
                entity[NAME],
                coordinator,
                sensor_data,
                entity[STATE_CLASS],
                config[DEVICE_ID],
                entity[PROPERTY_NAME],
                entity[UNITS],
            )
        )

    statisticsCoordinator = FoxESSStatisticsCoordinator(hass, CONNECTOR)

    await statisticsCoordinator.async_request_refresh()
    statisticsCoordinator.async_add_listener(_update_statistics, "None")

    # [FoxESSSensor(name, 64, coordinator)]
    async_add_entities(sensors, True)


def _update_statistics():
    _LOGGER.info("_update_statistics: update database")


async def async_setup_entry(hass, entry: ConfigEntry, async_add_entities):
    _LOGGER.error(async_add_entities)
    # async_add_entities([FoxESSSensor("Sensor.a", 64)], True)


# TODO: add measurment units
class FoxESSSensor(SensorEntity, CoordinatorEntity):
    device_info = "FoxESS"

    def __init__(
        self,
        name: str,
        coordinator: FoxESSUpdateCoordinator,
        sensor_type: str,
        state_class: SensorStateClass,
        _device_id: str,
        property_name: str,
        units: str,
    ):
        super().__init__(coordinator)
        self._attr_native_unit_of_measurement = units
        self._client_name = name
        self._sensor_type = sensor_type
        self._device_id = _device_id
        self._state_class = state_class
        self._property_name = property_name
        self._value = None

    @property
    def device_class(self):
        return SensorDeviceClass.ENERGY

    @property
    def state_class(self):
        return self._state_class

    @property
    def native_value(self):
        return self._value

    @property
    def name(self):
        return f"{self.device_info} {self._client_name}"

    def _handle_coordinator_update(self) -> None:
        self._value = round(
            Decimal(getattr(self.coordinator.data, self._property_name)), 2
        )

        self.async_write_ha_state()

    @property
    def unique_id(self):
        """Return a unique ID."""
        return f"sfoxess-{self._device_id}-{self._sensor_type.lower()}"
