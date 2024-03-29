""" code to login """
import hashlib
import requests
import logging
import datetime
from homeassistant.exceptions import HomeAssistantError
from enum import Enum
from .config_flow import InvalidAuth

_LOGGER = logging.getLogger(__name__)


class Action(Enum):
    LOGIN = 1
    SUCCESS = 2
    FAIL = 3
    AUTH_FAIL = 4
    SERVER_FAIL = 5


MESSAGE = "message"
ACTION = "action"

KNOWN_ERRORS = {
    41808: {MESSAGE: "Token expired", ACTION: Action.LOGIN},
    0: {MESSAGE: "Success", ACTION: Action.SUCCESS},
    41807: {MESSAGE: "Bad credentials", ACTION: Action.AUTH_FAIL},
    41930: {MESSAGE: "Bad device id", ACTION: Action.FAIL},
    30000: {MESSAGE: "Server under maintenance", ACTION: Action.SERVER_FAIL},
}


def execute_post(url, payload, headers):
    return requests.post(url=url, json=payload, headers=headers, timeout=120)


def execute_get(url, headers, timeout):
    return requests.get(url=url, headers=headers)


class FoxEssConnector(object):
    def __init__(self, username, password, device_id, hass):
        self._password: str = password
        self._username: str = username
        self._device_id: str = device_id
        self._token: str = None
        self._earnings = None
        self._report = None
        self._hass = hass

    @property
    def earnings(self):
        return self._earnings

    @property
    def device_id(self):
        return self._device_id

    @device_id.setter
    def device_id(self, device_id):
        self._device_id = device_id

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, password):
        self._password = password

    @property
    def username(self):
        return self._username

    @username.setter
    def username(self, username):
        self._username = username

    async def get_token(self):
        password_hash = hashlib.md5(self._password.encode("utf-8")).hexdigest()

        payload = {"user": self._username, "password": password_hash}
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/110.0",
            "contentType": "application/json",
            "Content-Type": "application/json;charset=utf-8",
            "Origin": "https://www.foxesscloud.com",
            "Referer": "https://www.foxesscloud.com/login",
            "Host": "www.foxesscloud.com",
            "Accept": "application/json, text/plain",
        }

        response = await self._hass.async_add_executor_job(
            execute_post,
            "https://www.foxesscloud.com/c/v0/user/login",
            payload,
            headers,
        )

        response_json = response.json()
        errno = response_json["errno"]

        await self.check_errno(errno)

        access = response_json["result"]["access"]
        if access == 0:
            _LOGGER.error("Login failed. Response: %s", str(response.content))
            return False

        self._token = response_json["result"]["token"]

    async def check_errno(self, errno: str):
        if errno not in KNOWN_ERRORS:
            _LOGGER.error("Unsupported error from foxess: %s", errno)
            raise HomeAssistantError(f"Unsupported error from foxess: {errno}")

        known = KNOWN_ERRORS[errno]
        if known["action"] == Action.LOGIN:
            _LOGGER.warning(known["message"])
            await self.get_token()

        if known["action"] == Action.SUCCESS:
            _LOGGER.debug(known["message"])

        if known["action"] == Action.AUTH_FAIL:
            _LOGGER.error(known["message"])
            raise InvalidAuth

        if known["action"] == Action.FAIL:
            raise HomeAssistantError(known["message"])

        if known["action"] == Action.SERVER_FAIL:
            raise HomeAssistantError(known["message"])

    async def login(self):
        if self._token is None:
            await self.get_token()

        return True

    async def get_report_daily(self, report_date: datetime):
        await self.login()
        report_type = "day"

        return await self._get_report(report_date, report_type)

    async def get_report_monthly(self, report_date: datetime):
        await self.login()
        report_type = "month"

        return await self._get_report(report_date, report_type)

    async def _get_report(self, report_date, report_type):
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/110.0",
            "contentType": "application/json",
            "Content-Type": "application/json;charset=utf-8",
            "contentType": "application/json",
            "token": self._token,
        }

        payload = {
            "deviceID": self._device_id,
            "reportType": report_type,
            "variables": ["generation"],
            "queryDate": {
                "year": report_date.year,
                "month": report_date.month,
                "day": report_date.day,
            },
        }
        report_response = await self._hass.async_add_executor_job(
            execute_post,
            "https://www.foxesscloud.com/c/v0/device/history/report",
            payload,
            headers,
        )

        if report_response.status_code == 200:
            report_data = report_response.json()
            await self.check_errno(report_data["errno"])

            self._report = report_data["result"][0]["data"]

        return self._report

    async def get_earnings(self):
        await self.login()

        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/110.0",
            "contentType": "application/json",
            "Content-Type": "application/json;charset=utf-8",
            "contentType": "application/json",
            "token": self._token,
        }

        response = await self._hass.async_add_executor_job(
            execute_get,
            f"https://www.foxesscloud.com/c/v0/device/earnings?deviceID={self._device_id}",
            headers,
            60,
        )

        if response.status_code == 200:
            await self.check_errno(response.json()["errno"])

            return response.json()["result"]

        _LOGGER.error(
            "Wrong response. Status code: %s, data: %s",
            response.status_code,
            str(response.content),
        )
        return None


class FoxESSDataSet:
    def __init__(self) -> None:
        self.current_production = None
        self.today_generation = None
        self.month_generation = None
        self.year_generation = None
        self.cumulate_generation = None
