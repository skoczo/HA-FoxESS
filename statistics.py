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
from .coordinator import FoxESSStatisticsCoordinator

import asyncio

_LOGGER = logging.getLogger(__name__)


def run_nested_until_complete(future, loop=None):
    """Run an event loop from within an executing task.

    This method will execute a nested event loop, and will not
    return until the passed future has completed execution. The
    nested loop shares the data structures of the main event loop,
    so tasks and events scheduled on the main loop will still
    execute while the nested loop is running.

    Semantically, this method is very similar to `yield from
    asyncio.wait_for(future)`, and where possible, that is the
    preferred way to block until a future is complete. The
    difference is that this method can be called from a
    non-coroutine function, even if that function was itself
    invoked from within a coroutine.
    """
    if loop is None:
        loop = asyncio.get_event_loop()

    loop._check_closed()
    if not loop.is_running():
        raise RuntimeError("Event loop is not running.")
    new_task = not isinstance(future, asyncio.futures.Future)
    task = asyncio.tasks.ensure_future(future, loop=loop)
    if new_task:
        # An exception is raised if the future didn't complete, so there
        # is no need to log the "destroy pending task" message
        task._log_destroy_pending = False
    while not task.done():
        try:
            loop._run_once()
        except:
            if new_task and future.done() and not future.cancelled():
                # The coroutine raised a BaseException. Consume the exception
                # to not log a warning, the caller doesn't have access to the
                # local task.
                future.exception()
            raise
    return task.result()


class StatisticsUpdater:
    def __init__(
        self,
        hass: HomeAssistant,
        connector: FoxEssConnector,
        coordinator: FoxESSStatisticsCoordinator,
    ) -> None:
        self._hass = hass
        self._connector = connector
        self._coordinator = coordinator

    def update_statistics(self):
        _LOGGER.error("update_statistics")

        statistic_id = "sfoxess-generation"

        generation = self._coordinator._report["2023-3-26"]

        today = datetime.today()

        yesterday = today.replace(hour=23, minute=0)
        yesterday = yesterday - timedelta(days=-1)

        stat = run_nested_until_complete(self.get_stats(statistic_id, yesterday))

        sum = stat[statistic_id][0]["sum"]
        last_stats_time = stat[statistic_id][0]["start"]

        self._update_stats(
            statistic_id, statistic_id, sum, last_stats_time, generation, today
        )

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

    async def get_stats(self, statistic_id, yesterday):
        return await get_instance(self._hass).async_add_executor_job(
            statistics_during_period,
            self._hass,
            yesterday,
            None,
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
