"""Update coordinator for TAURON sensors."""
import logging
import random
from datetime import timedelta

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DOMAIN
from .connector import FoxESSDataSet, FoxEssConnector


_LOGGER = logging.getLogger(__name__)


class FoxESSUpdateCoordinator(DataUpdateCoordinator[FoxESSDataSet]):
    def __init__(self, hass: HomeAssistant, username, password, device_id):
        super().__init__(
            hass, _LOGGER, name=DOMAIN, update_interval=timedelta(seconds=5)
        )
        self._connector = FoxEssConnector()
        self._connector.username = username
        self._connector.password = password
        self._connector.device_id = device_id

        self._device_id = device_id
        self._data_set = FoxESSDataSet()

    async def _async_update_data(self) -> FoxESSDataSet:
        """Fetch data from API endpoint.

        This is the place to pre-process the data to lookup tables
        so entities can quickly look up their data.
        """
        _LOGGER.error("_async_update_data")

        earnings_data = await self.hass.async_add_executor_job(self._update)
        if earnings_data is None:
            _LOGGER.error("Can't get earnings data")
            return

        self._data_set.today_generation = earnings_data["today"]["generation"]
        self._data_set.month_generation = earnings_data["month"]["generation"]
        self._data_set.year_generation = earnings_data["year"]["generation"]
        self._data_set.cumulate_generation = earnings_data["cumulate"]["generation"]
        self._data_set.current_production = earnings_data["power"]

        return self._data_set

    def _update(self):
        return self._connector.get_earnings()
