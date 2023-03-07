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

from .const import USERNAME, PASSWORD, DEVICE_ID

from .connector import FoxEssConnector
from .coordinator import FoxESSUpdateCoordinator

import logging

_LOGGER = logging.getLogger(__name__)

CONNECTOR = FoxEssConnector()


async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    async_add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    CONNECTOR._username = config[USERNAME]
    CONNECTOR._password = config[PASSWORD]
    CONNECTOR._device_id = config[DEVICE_ID]

    coordinator = FoxESSUpdateCoordinator(
        hass, config[USERNAME], config[PASSWORD], config[DEVICE_ID]
    )
    await coordinator.async_request_refresh()

    async_add_entities([FoxESSSensor("Sensor.a", 64, coordinator)], True)


async def async_setup_entry(hass, entry: ConfigEntry, async_add_entities):
    _LOGGER.error(async_add_entities)
    # async_add_entities([FoxESSSensor("Sensor.a", 64)], True)


class FoxESSSensor(SensorEntity, CoordinatorEntity):
    """Representation of a Sensor."""

    _attr_has_entity_name = True
    _attr_device_class = SensorDeviceClass.ENERGY
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, name, value, coordinator):
        super().__init__(coordinator)
        self._value = value
        self._attr_name = name
        _LOGGER.info(f"Sensor name: {name}")

    def _handle_coordinator_update(self) -> None:
        _LOGGER.error("_handle_coordinator_update")

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._attr_name

    @property
    def native_value(self):
        """Return the state of the sensor."""
        return self._value
