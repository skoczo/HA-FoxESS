import logging
import pytz
from datetime import timedelta, datetime

from homeassistant.components.recorder import get_instance
from homeassistant.util.dt import get_time_zone
from homeassistant.core import HomeAssistant
from homeassistant.components.recorder.statistics import (
    async_add_external_statistics,
    statistics_during_period,
)
from homeassistant.components.recorder.models import StatisticMetaData
from homeassistant.const import UnitOfEnergy

from .connector import FoxEssConnector

_LOGGER = logging.getLogger(__name__)


class StatisticsUpdater:
    def __init__(self, hass: HomeAssistant, connector: FoxEssConnector) -> None:
        self._hass = hass
        self._connector = connector

    async def update_statistics(
        self, connector: FoxEssConnector, import_start_date: datetime
    ):
        _LOGGER.info("Integration sfoxess statistics import started")
        statistic_id = "sfoxess:import_generation"

        local_tz = pytz.timezone("Europe/Warsaw")
        current_date = local_tz.localize(datetime.today())
        current_date = current_date.replace(minute=0, second=0)

        """
        state: generation sum value at specific point of time
        sum: generation sum from statistics period time
        """

        import_date = import_start_date
        generation_state = await connector.get_earnings()
        _LOGGER.debug(generation_state)
        stats = list()

        earnings = await connector.get_earnings()
        _LOGGER.debug(earnings)
        generation_sum = 0
        generation_state = 0

        stat_entity = {
            "start": import_date - timedelta(hours=1),
            "end": import_date,
            "state": None,
            "sum": 0,
        }

        stats.insert(0, stat_entity)

        while import_date <= current_date:
            current_date = current_date.replace(minute=0, second=0, microsecond=0)
            generation_daily = await connector.get_report_daily(import_date)
            generation_monthly = await connector.get_report_monthly(import_date)

            _LOGGER.debug(import_date)
            _LOGGER.debug(generation_daily)

            end_time = import_date.replace(hour=23, minute=59)

            statistics = await self.get_stats(statistic_id, import_date, end_time)
            _LOGGER.debug(statistics)

            # day generation value from monthly report
            day_generation = self._get_day_generation(
                import_date.day, generation_monthly
            )

            correction = self._calculate_correction(generation_daily, day_generation)

            tmp_stats = list()

            for i in range(23):
                if generation_daily[i]["value"] != 0:
                    generation_sum += correction
                    generation_state += correction

                generation_sum = generation_sum + generation_daily[i]["value"]
                generation_state = generation_state + generation_daily[i]["value"]
                stat_entity = {
                    "start": import_date,
                    "end": import_date + timedelta(hours=1),
                    "state": generation_state,
                    "sum": generation_sum,
                }

                tmp_stats.insert(0, stat_entity)

                import_date = import_date + timedelta(hours=1)

            stats += tmp_stats

            import_date = import_date.replace(hour=0)
            import_date = import_date + timedelta(hours=1)

        self._update_stats(statistic_id, statistic_id, stats)
        _LOGGER.info("Integration sfoxess statistics import finished")

    def _calculate_correction(self, generation_daily, day_generation):
        hours = 0
        sum_of_values = 0

        for entity in generation_daily:
            if entity["value"] != 0:
                sum_of_values += entity["value"]
                hours += 1

        if hours == 0:
            return 0

        return (day_generation - sum_of_values) / hours

    def _get_day_generation(self, day, generation_monthly):
        for item in generation_monthly:
            if item["index"] == day:
                return item["value"]

        return None

    def _update_stats(self, statistic_id, statistic_name, statistic_data):
        metadata: StatisticMetaData = {
            "has_mean": False,
            "has_sum": True,
            "name": None,
            "statistic_id": statistic_id,
            "source": "sfoxess",
            "unit_of_measurement": UnitOfEnergy.KILO_WATT_HOUR,
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
