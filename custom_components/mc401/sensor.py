import logging
import voluptuous as vol
import serial
from time import sleep

from homeassistant.components.sensor import (
    PLATFORM_SCHEMA,
    SensorEntity
)
import homeassistant.helpers.config_validation as cv
from homeassistant.const import (
    CONF_PATH,
    CONF_NAME,
    CONF_SCAN_INTERVAL,
    CONF_RESOURCES
)
from homeassistant.util import Throttle
from .const import (
    DOMAIN,
    DEFAULT_NAME,
    DEFAULT_SCAN_INTERVAL,
    SENSOR_TYPES,
)

_LOGGER = logging.getLogger(__name__)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
    vol.Required(CONF_PATH): cv.string,
    vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): cv.time_period,
    vol.Required(CONF_RESOURCES, default=[]):
        vol.All(cv.ensure_list, [vol.In(SENSOR_TYPES)]),
})

def setup_platform(hass, config, add_entities, discovery_info=None):
    """Setup the sensors."""
    name = config.get(CONF_NAME)
    path = config.get(CONF_PATH)

    try:
        reader = MC401Reader(path)
    except RuntimeError:
        _LOGGER.error("Unable to connect to %s", path)
        return False

    entities = []

    for resource in config[CONF_RESOURCES]:
        sensor_type = resource.lower()

        if sensor_type in SENSOR_TYPES:
            entities.append(MC401Sensor(name, reader, sensor_type))

    add_entities(entities)


class MC401Reader(object):
    """Reader object that communicates with the MC401."""

    def __init__(self, path):
        """Initialize the serial reader."""
        self._path = path
        self.data = None

    @Throttle(DEFAULT_SCAN_INTERVAL)
    def read(self):
        """Read data from the serial port."""
        # See page 33-36 in 5511- 634 GB Rev C1.qxd.pdf -  4. Data communication.
        MC401 = serial.Serial(port=self._path,
                              bytesize=serial.SEVENBITS,
                              parity=serial.PARITY_EVEN,
                              stopbits=serial.STOPBITS_TWO,
                              timeout=2)
        MC401.baudrate = 300
        MC401.write("/#1".encode("utf-8"))
        MC401.flush()
        sleep(1)
        MC401.baudrate = 1200
        MC401.flushInput()
        reading = MC401.read(87).split()
        MC401.close()

        self.validateAndSetData(reading)

    def validateAndSetData(self, reading):
        """New data needs validation before we continue."""
        data = []

        num_fields = len(reading)
        if num_fields is 10:
            _LOGGER.info("Successfully fetched new data: %s", reading)

            try:
                for c in reading:
                    if (len(c)) != 7:
  	                    raise Exception('Received invalid datafield length')

                data.append(int((reading[0]).decode("utf-8")) / 1000) # energy
                data.append(round(int((reading[0]).decode("utf-8")) / 1000 * 32.68, 3)) # gas_equivalent_m³ according to Vattenfall
                data.append(int((reading[1]).decode("utf-8")) / 100) # volume
                data.append(int((reading[2]).decode("utf-8"))) # operating_hours
                data.append(int((reading[3]).decode("utf-8")) / 100) # temperature_supply
                data.append(int((reading[4]).decode("utf-8")) / 100) # temperature_return
                data.append(int((reading[5]).decode("utf-8")) / 100) # temperature_delta
                data.append(int((reading[6]).decode("utf-8")) / 10) # power
                data.append(int((reading[7]).decode("utf-8"))) # flow
                data.append(int((reading[8]).decode("utf-8"))) # peak_flow
                data.append(int((reading[9]).decode("utf-8"))) # info_code

                # Only setting the data at the end, if parsing fails for one or more sensors, the data was corrupt and this reading should be skipped.
                self.data = data
            except Exception as error:
                _LOGGER.info("Error=%s parsing data=%s", error, reading)
        else:
            _LOGGER.info("Skipping, received %s fields, this should be 10. Data: %s", num_fields, reading)


class MC401Sensor(SensorEntity):
    """Representation of a sensor."""

    def __init__(self, name, reader, sensor_type):
        """Initialize the sensor."""
        super().__init__()
        self.reader = reader
        self.type = sensor_type
        self._data_position = SENSOR_TYPES[self.type][0]

        self._attr_name = "{} {}".format(name, SENSOR_TYPES[self.type][1])
        self._attr_entity_description = self._attr_name
        self._attr_device_class = SENSOR_TYPES[self.type][2]
        self._attr_native_unit_of_measurement = SENSOR_TYPES[self.type][3]
        self._attr_state_class = SENSOR_TYPES[self.type][4]
        self._attr_icon = SENSOR_TYPES[self.type][5]
        self._attr_unique_id = "{}_{}_{}".format(DOMAIN, name, self.type).lower().replace(" ", "_")

        self.update()

    def update(self):
        """Get the data and use it to update our sensor state."""
        self.reader.read()

        if self.reader.data is not None:
            new_state = self.reader.data[self._data_position]
            
            if (
                self._attr_native_value is not None and 
                self._data_position in [0, 1, 2]  and 
                abs(new_state - self._attr_native_value) / self._attr_native_value > 1
            ):
                _LOGGER.info("Skipping update; new value: %s is too different than previous: %s", new_state, self._attr_native_value)
            else:
                _LOGGER.info("Set %s to %s", self.type, new_state)
                self._attr_native_value = new_state
