from usb_communication.comm_exception import CommException
from usb_communication.raw_connector import RawConnector


class Connector(RawConnector):
    """This class wraps a RawCommunicator class to provide human-readable interface in standard units."""
    TUBE_SENSITIVITY = 25.0
    TUBE_VOLTAGE = 395
    UPPER_RESISTOR = 2000
    VOLTAGE_DIVIDER_UPPER_RESISTOR = 2000
    VOLTAGE_DIVIDER_LOWER_RESISTOR = 4.7
    TIMER_TICKS_PER_SECOND = 100
    MIN_VOLTAGE = 50
    MAX_VOLTAGE = 450

    def __init__(self):
        """Optional parameter is ConfigParser instance."""
        super(Connector, self).__init__()

        self._tube_sensitivity = self.TUBE_SENSITIVITY
        self._tube_voltage = self.TUBE_VOLTAGE

        self._volt_divider_factor = self.VOLTAGE_DIVIDER_LOWER_RESISTOR / (
                self.VOLTAGE_DIVIDER_LOWER_RESISTOR + self.VOLTAGE_DIVIDER_UPPER_RESISTOR)

    def set_voltage_from_config_file(self):
        """Sets the tube voltage basing on the value written in the config file."""
        self.set_voltage(self._tube_voltage)

    def get_CP_mand_radiation(self):
        """Returns a tuple containing CPM and Radiation in respective order."""

        cpm = self.get_CPM()
        radiation = self.get_radiation(cpm)
        return cpm, radiation

    def get_CPM(self):
        """Returns radiation in counts per minute."""
        return self.get_CPI() / self.get_interval() * 60.0

    def get_radiation(self, cpm=None):
        """Returns radiation in uSv/h."""
        # if cpm is None:
        #     cpm = self.get_CPM()
        # value = (cpm / 60.0) * 10.0 / self._tube_sensitivity
        if self.get_CPI() > 0:
            # print(str(self.get_CPI()))
            return self.get_CPI()

    def get_interval(self):
        """Returns measuring interval in seconds."""
        return self.get_raw_interval() / self.TIMER_TICKS_PER_SECOND

    def set_interval(self, seconds):
        """Sets the measuring interval in seconds."""
        if seconds < 1 or seconds > (0xffff / self.TIMER_TICKS_PER_SECOND):
            raise CommException(f'interval has to be between 1 and {str(0xffff / self.TIMER_TICKS_PER_SECOND)} seconds')
        self.set_raw_interval(self.TIMER_TICKS_PER_SECOND * seconds)

    def get_voltage(self):
        """Returns the measured Geiger tube supply voltage in volts."""
        return int(round(1.1 * self.get_raw_voltage() / (self._volt_divider_factor * 1024.0)))

    def set_voltage(self, volts):
        """Sets the desired Geiger tube supply voltage in volts."""
        if volts < self.MIN_VOLTAGE or volts > self.MAX_VOLTAGE:
            raise CommException(f'voltage has to have value between {str(self.MIN_VOLTAGE)} and {str(self.MAX_VOLTAGE)} volts')
        self.set_raw_voltage(int(self._volt_divider_factor * volts * 1024.0 / 1.1))

    def __str__(self):
        """Returns a string containing all data from the device: CPM, current radioactivity, voltage etc."""
        return f'Radiation: {str(self.get_radiation())} uS/h, CPM: {str(self.get_CPM())} int. {str(self.get_interval())} s, supply: {str(self.get_voltage())}V, count acknowledged: {str(self.is_count_acknowledged())} '