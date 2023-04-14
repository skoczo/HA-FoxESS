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
        earnings_data = await self._connector.get_earnings()
        if earnings_data is None:
            _LOGGER.error("Can't get earnings data")
            return

        self._data_set.today_generation = earnings_data["today"]["generation"]
        self._data_set.month_generation = earnings_data["month"]["generation"]
        self._data_set.year_generation = earnings_data["year"]["generation"]
        self._data_set.cumulate_generation = earnings_data["cumulate"]["generation"]
        self._data_set.current_production = earnings_data["power"]

        return self._data_set


class FoxESSStatisticsCoordinator(DataUpdateCoordinator):
    def __init__(
        self,
        hass: HomeAssistant,
        connector: FoxEssConnector,
        import_start_date: datetime,
    ):
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN + "_statistics",
            update_interval=timedelta(seconds=60 * 30),
        )
        self._connector = connector
        self._report = None
        self._statistics_updater = StatisticsUpdater(hass, self._connector)
        self._import_start_date = import_start_date

    async def _async_update_data(self) -> FoxESSDataSet:
        _LOGGER.info("FoxESSStatisticsCoordinator._update get data")
        await self._statistics_updater.update_statistics(
            self._connector, self._import_start_date
        )
