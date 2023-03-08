"""Update coordinator for TAURON sensors."""
import logging
import random
from datetime import timedelta

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DOMAIN
from .connector import FoxESSDataSet


_LOGGER = logging.getLogger(__name__)


class FoxESSUpdateCoordinator(DataUpdateCoordinator[FoxESSDataSet]):
    def __init__(self, hass: HomeAssistant, username, password, device_id):
        super().__init__(
            hass, _LOGGER, name=DOMAIN, update_interval=timedelta(seconds=5)
        )
        self.connector = None
        self._device_id = device_id

    async def _async_update_data(self) -> FoxESSDataSet:
        """Fetch data from API endpoint.

        This is the place to pre-process the data to lookup tables
        so entities can quickly look up their data.
        """
        _LOGGER.error("_async_update_data")

        data_set = FoxESSDataSet()
        data_set._current_production = random.random() * 100

        return data_set
