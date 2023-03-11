"""Constants for the sFoxESS integration."""
from homeassistant.components.sensor import SensorStateClass

DOMAIN = "sfoxess"
USERNAME = "username"
PASSWORD = "password"
DEVICE_ID = "device_id"

CURRENT_PRODUCTION = "CURRENT_PRODUCTION"
TODAY_GENERATION = "TODAY_GENERATION"
MONTH_GENERATION = "MONTH_GENERATION"
YEAR_GENERATION = "YEAR_GENERATION"
CUMULATIVE_GENERATION = "CUMULATIVE_GENERATION"

NAME = "name"
STATE_CLASS = "state_class"
PROPERTY_NAME = "property_name"

SENSOR_TYPES_YAML = {
    CURRENT_PRODUCTION: {
        NAME: "Current production",
        STATE_CLASS: SensorStateClass.MEASUREMENT,
        PROPERTY_NAME: "current_production",
    },
    TODAY_GENERATION: {
        NAME: "Today generation",
        STATE_CLASS: SensorStateClass.MEASUREMENT,
        PROPERTY_NAME: "today_generation",
    },
    MONTH_GENERATION: {
        NAME: "Month generation",
        STATE_CLASS: SensorStateClass.MEASUREMENT,
        PROPERTY_NAME: "month_generation",
    },
    YEAR_GENERATION: {
        NAME: "Year generation",
        STATE_CLASS: SensorStateClass.MEASUREMENT,
        PROPERTY_NAME: "year_generation",
    },
    CUMULATIVE_GENERATION: {
        NAME: "Cumulate generation",
        STATE_CLASS: SensorStateClass.MEASUREMENT,
        PROPERTY_NAME: "cumulate_generation",
    },
}
