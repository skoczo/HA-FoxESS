import logging

from homeassistant.core import HomeAssistant
from .connector import FoxEssConnector

_LOGGER = logging.getLogger(__name__)


class StatisticsUpdater:
    def __init__(self, hass: HomeAssistant, connector: FoxEssConnector) -> None:
        self._hass = hass
        self._connector = connector

    def update_statistics(self):
        _LOGGER.error("update_statistics")
