import logging
import asyncio
import time
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

        current_date = datetime.today()
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
        stats = {statistic_id: list()}

        earnings = await connector.get_earnings()
        _LOGGER.info(earnings)
        sum = None
        state = earnings["cumulate"]["generation"]

        while import_date <= current_date:
            current_date = current_date.replace(minute=0, second=0, microsecond=0)
            generation = await connector.get_report(current_date)

            end_time = import_date.replace(hour=23, minute=59)

            # stats = await self.get_stats(statistic_id, import_date, end_time)
            # _LOGGER.info(stats)

            for i in range(23):
                stat_entity = {
                    "start": import_date,
                    "end": import_date + timedelta(hours=1),
                    "state": state,
                    "sum": sum,
                }

                stats[statistic_id].insert(0, stat_entity)

                state -= generation[i]["value"]

                import_date = import_date - timedelta(hours=1)

            import_date = import_date.replace(hour=0)
            import_date = import_date - timedelta(hours=1)

            # TODO: if not found skip and try next time
            sum = stats[statistic_id][0]["sum"]
            last_stats_time = stats[statistic_id][0]["start"]

            # self._update_stats(
            #    statistic_id, statistic_id, sum, last_stats_time, generation, today
            # )

    def _update_stats(
        self,
        statistic_id,
        statistic_name,
        initial_sum,
        last_stats_time,
        generation,
        date: datetime,
    ):
        current_sum = initial_sum
        metadata: StatisticMetaData = {
            "has_mean": False,
            "has_sum": True,
            "name": statistic_name,
            "source": STATISTICS_DOMAIN,
            "statistic_id": statistic_id,
            "unit_of_measurement": ENERGY_KILO_WATT_HOUR,
        }
        statistic_data = []
        for raw_hour in generation:
            start = date.replace(hour=raw_hour["index"])

            if last_stats_time is not None and start <= last_stats_time:
                continue
            usage = float(raw_hour["value"])

            current_sum += usage
            stats = {"start": start, "state": usage, "sum": current_sum}
            statistic_data.append(stats)
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
