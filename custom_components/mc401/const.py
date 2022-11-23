"""The mc401 component."""

from datetime import timedelta

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorStateClass
)

from homeassistant.const import (
    UnitOfEnergy,
    UnitOfVolume,
    UnitOfTemperature,
    UnitOfPower,
    TIME_HOURS
)

DOMAIN = "mc401"
DEFAULT_NAME = "Multical 401"
DEFAULT_SCAN_INTERVAL = timedelta(seconds=60)

SENSOR_TYPES = {
    "energy": [0, "Energy usage", SensorDeviceClass.ENERGY, UnitOfEnergy.GIGA_JOULE, SensorStateClass.TOTAL, "mdi:radiator"],
    "gas_equivalent_m3": [1, "Gas equivalent energy usage in m³", SensorDeviceClass.GAS, UnitOfVolume.CUBIC_METERS, SensorStateClass.TOTAL, "mdi:radiator"],
    "volume": [2, "Supply water volume used", SensorDeviceClass.VOLUME, UnitOfVolume.CUBIC_METERS, SensorStateClass.MEASUREMENT, "mdi:water"],
    "operating_hours": [3, "Lifetime operating hours", SensorDeviceClass.DURATION ,TIME_HOURS, SensorStateClass.MEASUREMENT, "mdi:timer-sand"],
    "temperature_supply": [4, "Supply water temperature", SensorDeviceClass.TEMPERATURE ,UnitOfTemperature.CELSIUS, SensorStateClass.MEASUREMENT, "mdi:coolant-temperature"],
    "temperature_return": [5, "Return water temperature", SensorDeviceClass.TEMPERATURE, UnitOfTemperature.CELSIUS, SensorStateClass.MEASUREMENT, "mdi:coolant-temperature"],
    "temperature_delta": [6, "Temperature difference", SensorDeviceClass.TEMPERATURE, UnitOfTemperature.CELSIUS, SensorStateClass.MEASUREMENT, "mdi:coolant-temperature"],
    "power": [7, "Power consumption", SensorDeviceClass.POWER, UnitOfPower.KILO_WATT, SensorStateClass.MEASUREMENT, "mdi:flash"],
    "flow": [8, "Supply water flow", SensorDeviceClass.WATER, "l/h", SensorStateClass.MEASUREMENT, "mdi:water"],
    "peak_flow": [9, "Supply water flow - peak", SensorDeviceClass.WATER, "l/h", SensorStateClass.MEASUREMENT, "mdi:water"],
    "info_code": [10, "Info code", "", "", "", "mdi:alert-outline"]
}
