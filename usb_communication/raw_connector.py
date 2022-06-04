import usb

from usb_communication.comm_exception import CommException


class RawConnector(object):
    """Low level class for Geiger device communication. It handles all libusb
    calls and supports all low level functions. Warning! Methods like getVoltage,
    getInterval don't return values in standard units like seconds or volts,
    but device internal representations. You should use this class wrapped by 
    some class transforming them to standard units."""
    
    VENDOR_NAME = "slomkowski.eu"
    DEVICE_NAME = "USB Geiger"
    VENDOR_ID = 0x16c0
    DEVICE_ID = 0x05df
    GET_CPI_FROM_MICRO = 10
    SET_INTERVAL_IN_MICRO = 20
    GET_INTERVAL_FROM_MICRO = 21
    SET_VOLTAGE_IN_MICRO = 30
    GET_VOLTAGE_FROM_MICRO = 31
    IS_ACKNOWLEDGE_UNCHECKED_COUNT_FROM_MICRO = 40

    def __init__(self):
        """Initiates the class and opens the device. Warning! 
        The constructor assumes that only one Geiger device is connected to the bus.
        Otherwise, it opens the first-found one."""
        self._device = None
        self._open_device()

    def _open_device(self):
        for dev in usb.core.find(idVendor=self.VENDOR_ID, idProduct=self.DEVICE_ID, find_all=True):
            vendor_name = usb.util.get_string(dev, dev.iManufacturer)
            device_name = usb.util.get_string(dev, dev.iProduct)

            if vendor_name == self.VENDOR_NAME and device_name == self.DEVICE_NAME:
                self._device = dev
                break

        if self._device is None:
            raise CommException("Geiger device not found")

    def reset_connection(self):
        """Forces the device to reset and discovers it one more time."""
        try:
            self._device.reset()
            usb.util.dispose_resources(self._device)
        except usb.core.USBError:
            pass
        self._open_device()

    def _send_message(self, request, value):
        if value > 0xffff:
            raise CommException("device doesn't support values longer than two bytes")

        request_type = usb.util.build_request_type(usb.util.ENDPOINT_OUT, usb.util.CTRL_TYPE_VENDOR,
                                                   usb.util.CTRL_RECIPIENT_DEVICE)
        try:
            self._device.ctrl_transfer(request_type, request, value)
        except usb.core.USBError:
            raise CommException("error at communication with the device")

    def _recv_message(self, request):
        request_type = usb.util.build_request_type(usb.util.ENDPOINT_IN, usb.util.CTRL_TYPE_VENDOR,
                                                   usb.util.CTRL_RECIPIENT_DEVICE)
        try:
            response = self._device.ctrl_transfer(request_type, request, 0, 0, 2)
        except usb.core.USBError:
            raise CommException("error at receiving data from the device")

        if len(response) < 2:
            raise CommException("device sent less than two bytes")

        return response[0] + response[1] * 256

    def set_raw_interval(self, raw_interval):
        """Sets the time period of counting cycle. After that time, the counts value
        is transferred to output buffer and accessible for getting. CPI value is cleared during this operation."""
        self._send_message(self.SET_INTERVAL_IN_MICRO, int(raw_interval))

    def get_raw_interval(self):
        """Returns the programmed interval."""
        return int(self._recv_message(self.GET_INTERVAL_FROM_MICRO))

    def set_raw_voltage(self, raw_voltage):
        """Sets the desired Geiger tube supply voltage."""
        self._send_message(self.SET_VOLTAGE_IN_MICRO, int(raw_voltage))

    def get_raw_voltage(self):
        """Returns the measured actual Geiger tube supply voltage."""
        return int(self._recv_message(self.GET_VOLTAGE_FROM_MICRO))

    def get_CPI(self):
        """Returns the number of counts gathered during programmed interval."""
        return float(self._recv_message(self.GET_CPI_FROM_MICRO))

    def is_count_acknowledged(self):
        """If a new count occurs, this flag is set. The flag is cleared after reading it.
         This is meant to check for counts in real-time. By checking this flag often enough, 
         you can get precise information about any new count."""
        if self._recv_message(self.IS_ACKNOWLEDGE_UNCHECKED_COUNT_FROM_MICRO) == 1:
            return True
        else:
            return False

    def __str__(self):
        """Returns the string containing all data acquired from the device: 
        actual voltage, current CPI and countAcknowledged flag."""
        return f'CPI: {str(self.get_CPI())}, supply: {str(self.get_raw_voltage())}, count acknowledged: {str(self.is_count_acknowledged())}'
