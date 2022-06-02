import threading
import _thread
import time

from usb_communication.comm_exception import CommException


class Monitor(object):
    INTERVALS = 1

    _interval = None
    _usbcomm = None
    _log = False

    _timer = None

    _updatersList = []

    _radiation = None

    def __init__(self, usbcomm):
        self._usbcomm = usbcomm
        self._interval = self.INTERVALS

        usbcomm.set_voltage_from_config_file()
        usbcomm.set_interval(self._interval)

    def start(self):
        """Enables cyclic monitoring. The first measurement cycle
        has the 1.5 length of the given interval in order to collect data by the device."""
        self._timer = threading.Timer(self._interval, self._update)
        self._timer.setDaemon(True)
        self._timer.start()

    def stop(self):
        """Stops measuring cycle and closes all updaters."""
        self._timer.cancel()

        print("Stopping all updaters.")

    @property
    def get_radiation(self):
        return self._radiation

    def _update(self):
        """This method is called by the internal timer every 'interval' time to gather measurements
		and send them to specified updaters. The first cycle has 1.5*interval length to give the
		Geiger device time to collect counts. Then, update takes place in the middle of the next
		measuring cycle.
		"""
        self._timer = threading.Timer(0.001, self._update)
        self._timer.setDaemon(True)
        # start new cycle here to prevent shifting next update time stamp
        self._timer.start()

        timestamp = time.gmtime()

        try:
            cpm, self._radiation = self._usbcomm.get_CP_mand_radiation()
        except CommException as e:
            print("USB device error: %s. Forcing device reset and wait of 1.5 cycle length.", str(e))
            print("Resetting device.")
            try:
                self._usbcomm.reset_connection()
                print("Setting programmed voltage and interval to %d seconds.", self._interval)
                self._usbcomm.set_voltage_from_config_file()
                self._usbcomm.set_interval(self._interval)
            except CommException as e:
                print("Error at reinitializing device: %s", str(e))
                self.stop()
                # close entire application
                _thread.interrupt_main()

            self._timer.cancel()
            self._timer = threading.Timer(1.5 * self._interval, self._update)
            self._timer.setDaemon(True)
            self._timer.start()
            return

        print(f"pushing data: {cpm} CPM, {self._radiation} uSv/h")
