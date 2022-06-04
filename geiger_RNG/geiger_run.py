import signal
import sys

import configparser

from geiger_RNG import monitor
from geiger_RNG.geiger_random_number_generator import GeigerRandomNumberGenerator
from usb_communication.comm_exception import CommException
from usb_communication.connector import Connector


class Geiger:
    SIZE_OF_GENERATED_NUMBER_IN_BITS = 4
    INITIALIZATION_MESSAGE = 'Initializing Geiger device...'
    ERROR_INITIALIZATION_USB_MESSAGE = 'Error at initializing USB device: '
    ERROR_LOADING_CONFIGURATION_MESSAGE = 'Error at loading configuration file.'

    def __init__(self):
        self.__is_configuration_loaded = False
        self.__comm = None
        self.__monitor = None

        self.__initialise_usb_communication()
        self.__monitor = monitor.Monitor(usb_comm=self.__comm)
        self.__generator = GeigerRandomNumberGenerator(self.SIZE_OF_GENERATED_NUMBER_IN_BITS)

        self.__init_ctr_c_handler()

        self.__monitor.start()
        self.__main_loop()

    def __initialise_usb_communication(self):
        try:
            print(self.INITIALIZATION_MESSAGE)
            self.__comm = Connector()
        except CommException as exp:
            print(f"{self.ERROR_INITIALIZATION_USB_MESSAGE} {str(exp)}")
            sys.exit(1)

    def __init_ctr_c_handler(self):
        # register SIGINT (Ctrl-C) signal handler
        signal.signal(signal.SIGINT, self.__signal_handler)
        signal.signal(signal.SIGTERM, self.__signal_handler)

    def __main_loop(self):
        collected_readings = []
        while True:
            if self.__monitor.get_radiation is not None and self.__monitor.get_is_aknowlage:

                if len(collected_readings) == 0:
                    collected_readings.append(self.__monitor.get_radiation)
                    self.__generator.set_pulse_time()
                    if self.__generator.get_random_bits_number == self.__generator.get_number_of_bits:
                        print((str(self.__generator.get_int_number())))

                else:
                    if collected_readings[0] != self.__monitor.get_radiation:
                        collected_readings.append(self.__monitor.get_radiation)
                        self.__generator.set_pulse_time()
                        if self.__generator.get_random_bits_number == self.__generator.get_number_of_bits:
                            print((str(self.__generator.get_int_number())))

                if len(collected_readings) > 1:
                    collected_readings.pop(0)

    def __signal_handler(self, signum, frame):
        """Handles stopping signals, closes all updaters and threads and exits."""
        self.__monitor.stop()
        sys.exit(1)
