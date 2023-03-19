"""Constants for the sFoxESS integration."""
from homeassistant.components.sensor import SensorStateClass
from homeassistant.const import ENERGY_KILO_WATT_HOUR, POWER_KILO_WATT

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
UNITS = "units"

SENSOR_TYPES_YAML = {
    CURRENT_PRODUCTION: {
        NAME: "Current production",
        STATE_CLASS: SensorStateClass.MEASUREMENT,
        PROPERTY_NAME: "current_production",
        UNITS: POWER_KILO_WATT,
    },
    TODAY_GENERATION: {
        NAME: "Today generation",
        STATE_CLASS: SensorStateClass.TOTAL_INCREASING,
        PROPERTY_NAME: "today_generation",
        UNITS: ENERGY_KILO_WATT_HOUR,
    },
    MONTH_GENERATION: {
        NAME: "Month generation",
        STATE_CLASS: SensorStateClass.TOTAL_INCREASING,
        PROPERTY_NAME: "month_generation",
        UNITS: ENERGY_KILO_WATT_HOUR,
    },
    YEAR_GENERATION: {
        NAME: "Year generation",
        STATE_CLASS: SensorStateClass.TOTAL_INCREASING,
        PROPERTY_NAME: "year_generation",
        UNITS: ENERGY_KILO_WATT_HOUR,
    },
    CUMULATIVE_GENERATION: {
        NAME: "Cumulate generation",
        STATE_CLASS: SensorStateClass.TOTAL_INCREASING,
        PROPERTY_NAME: "cumulate_generation",
        UNITS: ENERGY_KILO_WATT_HOUR,
    },
}
