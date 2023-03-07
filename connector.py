"""FoxEss connector class"""

import hashlib
import requests
import logging
import json

_LOGGER = logging.getLogger(__name__)


class FoxEssConnector(object):
    def __init__(self):
        self._password: str = None
        self._username: str = None
        self._device_id: str = None

    @property
    def device_id(self):
        return self._device_id

    @device_id.setter
    def set_device_id(self, device_id):
        self._device_id = device_id

    @property
    def password(self):
        return self._password

    @password.setter
    def set_password(self, password):
        self._password = password

    @property
    def username(self):
        return self._username

    @username.setter
    def set_username(self, username):
        self._username = username

    def login(self):
        password_hash = hashlib.md5(self._password.encode("utf-8")).hexdigest()

        payload = {"user": self._username, "password": password_hash}
        headers = {
            "contentType": "application/json",
            "Content-Type": "application/json;charset=utf-8",
        }
        """response = requests.post(
            "https://www.foxesscloud.com/c/v0/user/login",
            json=payload,
            timeout=120,
            headers=headers,
        )"""

        return False

    """
        response_json = response.json()
        errno = response_json["errno"]
        access = response_json["result"]["access"]
        if access == 0:
            _LOGGER.error(f"Login failed. Response: {str(response.content)}")
            return False

        self._token = response_json["result"]["token"]
        _LOGGER.info(f"Login response: {str(response.content)}")

        return True"""

    def earnings(self):
        headers = {
            "contentType": "application/json",
            "Content-Type": "application/json;charset=utf-8",
            # "token": self._token,
        }

        response = requests.get(
            "https://www.foxesscloud.com/c/v0/device/earnings?deviceID="
            & self._device_id,
            headers=headers,
        )

        if response.status_code == 200:
            response.json


class FoxESSDataSet:
    def __init__(self) -> None:
        self._current_production = None
