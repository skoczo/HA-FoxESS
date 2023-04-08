import logging
import asyncio
import time
import pytz
from datetime import timedelta, datetime

from homeassistant.components.recorder import get_instance
from homeassistant.util.dt import get_time_zone
from homeassistant.core import HomeAssistant
from homeassistant.components.recorder.statistics import (
    async_add_external_statistics,
    get_last_statistics,
    statistics_during_period,
)
from homeassistant.components.recorder.models import StatisticMetaData
from homeassistant.const import ENERGY_KILO_WATT_HOUR

from .connector import FoxEssConnector
from .const import STATISTICS_DOMAIN

_LOGGER = logging.getLogger(__name__)


class StatisticsUpdater:
    def __init__(self, hass: HomeAssistant, connector: FoxEssConnector) -> None:
        self._hass = hass
        self._connector = connector

    async def update_statistics(
        self, connector: FoxEssConnector, import_start_date: datetime
    ):
        _LOGGER.error("update_statistics")

        statistic_id = "sensor.foxess_cumulate_generation"

        local_tz = pytz.timezone("Europe/Warsaw")
        current_date = local_tz.localize(datetime.today())
        current_date = current_date.replace(minute=0, second=0)

        _LOGGER.error(
            "first stats: %s",
            await self.get_stats(
                statistic_id,
                datetime(year=2023, month=4, day=1, hour=0, minute=0),
                datetime(year=2023, month=4, day=1, hour=23, minute=59),
            ),
        )

        """
        state: generation sum value at specific point of time
        sum: generation sum from statistics period time
        """

        import_date = import_start_date
        sum = 0
        state = await connector.get_earnings()
        _LOGGER.info(state)
        stats = list()

        earnings = await connector.get_earnings()
        _LOGGER.info(earnings)
        sum = 0
        state = 0

        stat_entity = {
            "start": import_date - timedelta(hours=1),
            "end": import_date,
            "state": None,
            "sum": 0,
        }

        stats.insert(0, stat_entity)

        while import_date <= current_date:
            current_date = current_date.replace(minute=0, second=0, microsecond=0)
            generation = await connector.get_report(import_date)

            _LOGGER.info(import_date)
            _LOGGER.info(generation)

            end_time = import_date.replace(hour=23, minute=59)

            statistics = await self.get_stats(statistic_id, import_date, end_time)
            _LOGGER.info(statistics)

            for i in range(23):
                sum = sum + generation[i]["value"]
                state = state + generation[i]["value"]
                stat_entity = {
                    "start": import_date,
                    "end": import_date + timedelta(hours=1),
                    "state": state,
                    "sum": sum,
                }

                stats.insert(0, stat_entity)

                import_date = import_date + timedelta(hours=1)

            import_date = import_date.replace(hour=0)
            import_date = import_date + timedelta(hours=1)

        self._update_stats(statistic_id, statistic_id, stats)

    def _update_stats(self, statistic_id, statistic_name, statistic_data):
        metadata: StatisticMetaData = {
            "has_mean": False,
            "has_sum": True,
            "name": None,
            "statistic_id": "sfoxess:import_generation",
            "source": "sfoxess",
            "unit_of_measurement": ENERGY_KILO_WATT_HOUR,
        }

        async_add_external_statistics(self._hass, metadata, statistic_data)

    async def get_stats(self, statistic_id, start, end):
        return await get_instance(self._hass).async_add_executor_job(
            statistics_during_period,
            self._hass,
            start,
            end,
            [statistic_id],
            "hour",
            None,
            {"state", "sum"},
        )

    @staticmethod
    def get_time(raw_hour):
        zone = get_time_zone("Europe/Warsaw")
        date = raw_hour["Date"]
        hour = int(raw_hour["Hour"]) - 1
        return datetime.datetime.strptime(
            f"{date} {hour}:00", "%Y-%m-%d %H:%M"
        ).replace(tzinfo=zone)
