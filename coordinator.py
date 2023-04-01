"""Update coordinator for TAURON sensors."""
import logging
import random
from datetime import timedelta, datetime

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DOMAIN
from .connector import FoxESSDataSet, FoxEssConnector
from .statistics import StatisticsUpdater

_LOGGER = logging.getLogger(__name__)


class FoxESSUpdateCoordinator(DataUpdateCoordinator[FoxESSDataSet]):
    def __init__(self, hass: HomeAssistant, connector: FoxEssConnector):
        super().__init__(
            hass, _LOGGER, name=DOMAIN, update_interval=timedelta(seconds=60)
        )
        self._connector = connector
        self._data_set = FoxESSDataSet()

    async def _async_update_data(self) -> FoxESSDataSet:
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


class FoxESSStatisticsCoordinator(DataUpdateCoordinator):
    def __init__(self, hass: HomeAssistant, connector: FoxEssConnector):
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN + "_statistics",
            update_interval=timedelta(seconds=6),
        )
        self._connector = connector
        self._report = None
        self._statistics_updater = StatisticsUpdater(hass, self._connector)

    async def _async_update_data(self) -> FoxESSDataSet:
        _LOGGER.error("FoxESSStatisticsCoordinator._update get data")
        self._report = await self._connector.get_report()
        await self._statistics_updater.update_statistics(self._report)
