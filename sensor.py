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

from .const import USERNAME, PASSWORD, DEVICE_ID

from .connector import FoxEssConnector

import logging

_LOGGER = logging.getLogger(__name__)

CONNECTOR = FoxEssConnector()


def setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up the sensor platform."""
    add_entities(
        [
            FoxESSSensor("Sensor.a", 64),
        ]
    )

    CONNECTOR._username = config[USERNAME]
    CONNECTOR._password = config[PASSWORD]
    CONNECTOR._device_id = config[DEVICE_ID]


def setup_entry(hass, entry: ConfigEntry, async_add_entities):
    _LOGGER.error(async_add_entities)


class FoxESSSensor(SensorEntity):
    """Representation of a Sensor."""

    _attr_has_entity_name = True
    _attr_device_class = SensorDeviceClass.ENERGY
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, name, value):
        self._value = value
        self._attr_name = name
        _LOGGER.info(f"Sensor name: {name}")

    def update(self) -> None:
        """Fetch new state data for the sensor.
        This is the only method that should fetch new data for Home Assistant.
        """
        if CONNECTOR.login():
            _LOGGER.info("Successfull login")
        else:
            _LOGGER.info("Login failed")

        self._attr_native_value = self._value

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._attr_name

    @property
    def native_value(self):
        """Return the state of the sensor."""
        return self._value
