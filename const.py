"""Constants for the sFoxESS integration."""
from homeassistant.components.sensor import SensorStateClass

DOMAIN = "sfoxess"
USERNAME = "username"
PASSWORD = "password"
DEVICE_ID = "device_id"

SENSOR_TYPES_YAML = {
    "CURRENT_PRODUCTION": {
        "name": "Current production",
        "state_class": SensorStateClass.MEASUREMENT,
        "property_name": "_current_production",
    }
}
