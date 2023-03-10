import hashlib
import requests
import logging
import json
from homeassistant.exceptions import HomeAssistantError

from enum import Enum

from .config_flow import InvalidAuth

_LOGGER = logging.getLogger(__name__)


class Action(Enum):
    LOGIN = 1
    SUCCESS = 2
    FAIL = 3
    AUTH_FAIL = 4


MESSAGE = "message"
ACTION = "action"

KNOWN_ERRORS = {
    41808: {MESSAGE: "Token expired", ACTION: Action.LOGIN},
    0: {MESSAGE: "Success", ACTION: Action.SUCCESS},
    41807: {MESSAGE: "Bad credentials", ACTION: Action.AUTH_FAIL},
    41930: {MESSAGE: "Bad device id", ACTION: Action.FAIL},
}


class FoxEssConnector(object):
    def __init__(self):
        self._password: str = None
        self._username: str = None
        self._device_id: str = None
        self._token: str = None
        self._earnings = None

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

    def get_token(self):
        password_hash = hashlib.md5(self._password.encode("utf-8")).hexdigest()

        payload = {"user": self._username, "password": password_hash}
        headers = {
            "contentType": "application/json",
            "Content-Type": "application/json;charset=utf-8",
        }
        response = requests.post(
            "https://www.foxesscloud.com/c/v0/user/login",
            json=payload,
            timeout=120,
            headers=headers,
        )

        response_json = response.json()
        errno = response_json["errno"]

        self.check_errno(errno)

        access = response_json["result"]["access"]
        if access == 0:
            _LOGGER.error(f"Login failed. Response: {str(response.content)}")
            return False

        self._token = response_json["result"]["token"]
        _LOGGER.info(f"Login response: {str(response.content)}")

    def check_errno(self, errno: str):
        if errno not in KNOWN_ERRORS:
            _LOGGER.error("Unsupported error from foxess: %s", errno)
            raise Exception(f"Unsupported error from foxess: {errno}")

        known = KNOWN_ERRORS[errno]
        if known["action"] == Action.LOGIN:
            _LOGGER.warning(known["message"])
            self.get_token()

        if known["action"] == Action.SUCCESS:
            _LOGGER.info(known["message"])

        if known["action"] == Action.AUTH_FAIL:
            _LOGGER.error(known["message"])
            raise InvalidAuth

        if known["action"] == Action.FAIL:
            raise HomeAssistantError(known["message"])

    def login(self):
        if self._token is None:
            self.get_token()

        return True

    def get_earnings(self):
        self.login()

        headers = {
            "contentType": "application/json",
            "token": self._token,
        }

        response = requests.get(
            f"https://www.foxesscloud.com/c/v0/device/earnings?deviceID={self._device_id}",
            headers=headers,
            timeout=60,
        )

        if response.status_code == 200:
            self.check_errno(response.json()["errno"])

            return response.json()["result"]


class FoxESSDataSet:
    def __init__(self) -> None:
        self.current_production = None
        self.today_generation = None
        self.month_generation = None
        self.year_generation = None
        self.cumulate_generation = None
