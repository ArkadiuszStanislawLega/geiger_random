import sys
import threading
import _thread
import time
import configparser
import logging

from geiger_RNG import usbcomm


class Monitor(object):
    _interval = None
    _usbcomm = None
    _log = False
    _configuration = None

    _timer = None

    _updatersList = []

    _radiation = None

    def __init__(self, configuration, usbcomm):
        self._log = logging.getLogger("geiger.monitor")
        self._usbcomm = usbcomm
        self._configuration = configuration
        confFileSection = 'monitor'
        try:
            self._interval = configuration.getint(confFileSection, 'interval')
        except configparser.Error as e:
            self._log.critical("Measuring interval wrong or not provided: %s.", str(e))
            sys.exit(1)

        self._log.info("Setting programmed voltage and interval to %d seconds.", self._interval)

        usbcomm.setVoltageFromConfigFile()
        usbcomm.setInterval(self._interval)

    def start(self):
        """Enables cyclic monitoring. The first measurement cycle has the 1.5 length of the given interval
		in order to collect data by the device.
		"""
        self._timer = threading.Timer(self._interval, self._update)
        self._timer.setDaemon(True)
        self._timer.start()

    def stop(self):
        """Stops measuring cycle and closes all updaters."""
        self._timer.cancel()

        self._log.info("Stopping all updaters.")

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
            cpm, self._radiation = self._usbcomm.getCPMandRadiation()
        except usbcomm.CommException as e:
            self._log.error("USB device error: %s. Forcing device reset and wait of 1.5 cycle length.", str(e))
            self._log.info("Resetting device.")
            try:
                self._usbcomm.resetConnection()
                self._log.info("Setting programmed voltage and interval to %d seconds.", self._interval)
                self._usbcomm.setVoltageFromConfigFile()
                self._usbcomm.setInterval(self._interval)
            except usbcomm.CommException as e:
                self._log.critical("Error at reinitializing device: %s", str(e))
                self.stop()
                # close entire application
                _thread.interrupt_main()

            self._timer.cancel()
            self._timer = threading.Timer(1.5 * self._interval, self._update)
            self._timer.setDaemon(True)
            self._timer.start()
            return

        self._log.info(f"pushing data: {cpm} CPM, {self._radiation} uSv/h")
