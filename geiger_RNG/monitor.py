import threading
import time

from usb_communication.comm_exception import CommException


class Monitor(object):
    INTERVAL = 1

    def __init__(self, usb_comm):
        self._timer = None
        self._radiation = None
        self._usb_communication = usb_comm
        self.__is_count_acknowledged = False

        self._usb_communication.set_voltage_from_config_file()
        self._usb_communication.set_interval(self.INTERVAL)

    def start(self):
        """Enables cyclic monitoring. The first measurement cycle
        has the 1.5 length of the given interval in order to collect data by the device."""
        self._timer = threading.Timer(self.INTERVAL, self._update)
        self._timer.setDaemon(True)
        self._timer.start()

    def stop(self):
        """Stops measuring cycle and closes all updaters."""
        self._timer.cancel()

        print("Stopping all updaters.")

    @property
    def get_radiation(self):
        return self._radiation

    @property
    def is_count_acknowledged(self):
        return  self.__is_count_acknowledged

    def _update(self):
        """This method is called by the internal timer every 'interval'
        time to gather measurements and send them to specified updaters.
        The first cycle has 1.5*interval length to give the Geiger device
        time to collect counts. Then, update takes place in the middle of
        the next measuring cycle."""
        self._timer = threading.Timer(0.01, self._update)
        self._timer.setDaemon(True)
        self._timer.start()
        try:
            cpm, self._radiation = self._usb_communication.get_CP_mand_radiation()
            self.__is_count_acknowledged = self._usb_communication.is_count_acknowledged()
        except CommException as e:
            print(f'USB device error: {str(e)}. Forcing device reset and wait of 1.5 cycle length.')
            print("Resetting device.")
            try:
                self._usb_communication.reset_connection()
                print(f'Setting programmed voltage and interval to {self.INTERVAL} seconds.')
                self._usb_communication.set_voltage_from_config_file()
                self._usb_communication.set_interval(self.INTERVAL)
            except CommException as e:
                print(f'Error at reinitializing device: {str(e)}')
                self.stop()
                self._thread.interrupt_main()

            self._timer.cancel()
            self._timer = threading.Timer(1.5 * self.INTERVAL, self._update)
            self._timer.setDaemon(True)
            self._timer.start()
            return

        if self._usb_communication.get_radiation() is not None and self.is_count_acknowledged:
            print(f'{self._usb_communication.get_radiation()} uSv/h')
