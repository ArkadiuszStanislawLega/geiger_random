import configparser
import usbcomm
import sys
import os
import signal
import monitor

import datetime


class GeigerRandomNumberGenerator:
    """
    A class that intercepts the moments when radiation is extracted from a Geiger sensor.
    As a result of the radiation detection times taken and the permutations performed,
    a list of bits is generated. The sequence of bits can be used to generate numbers.
    """
    NUMBER_OF_TICKS = 3

    def __init__(self, number_of_bits=8):
        self.__number_of_bits = number_of_bits
        self.__random_bits = []
        self.__pulses_times = []

    @property
    def get_random_bits_number(self):
        """
        :return: Number of collected bits.
        """
        return len(self.__random_bits)

    @property
    def get_number_of_bits(self):
        return self.__number_of_bits

    def set_pulse_time(self):
        """
        Adds a new pulse time to the list, and then adds the bit to the list of bits
        in the string of numbers returned as a string of random numbers.
        :return: None
        """
        self.__remove_first_pulse_time()
        self.__pulses_times.append(datetime.datetime.now())

        self.__add_bit_to_list()

    def __remove_first_pulse_time(self):
        """
        Removes the first pulse reading time from the list.
        :return: None
        """
        if len(self.__pulses_times) == self.NUMBER_OF_TICKS:
            self.__pulses_times.pop(0)

    def __add_bit_to_list(self):
        """
        Adds a bit to the random bit string list as long as the bit limit is not exceeded.
        :return: None
        """
        self.__remove_bits_if_size_is_max()
        self.__append_bits_to_list()

    def __remove_bits_if_size_is_max(self):
        """
        Clears the bit list when the number of bits equals the reached limit.
        :return: None
        """
        if len(self.__random_bits) == self.__number_of_bits:
            self.__random_bits.clear()

    def __append_bits_to_list(self):
        """
        Adds a bit when the number of required ticks is reached.
        :return: None
        """
        if len(self.__pulses_times) == self.NUMBER_OF_TICKS:
            first_time = self.__pulses_times[1] - self.__pulses_times[0]
            second_time = self.__pulses_times[2] - self.__pulses_times[1]

            self.__random_bits.append((0x00, 0x01)[first_time > second_time])

    def get_int_number(self):
        """
        Convert bits from random bits to integer.
        :return: A decimal number calculated from the bits of the random bit list.
        """
        if len(self.__random_bits) > 0:
            all_random_bits = ''

            for bit in self.__random_bits:
                all_random_bits += str(bit)

            return int(all_random_bits, 2)

        return None


class Geiger:
    CONFIG_FILE_NAME = 'configuration.ini'

    def __init__(self):
        self.__config_path = [".", os.path.dirname(__file__), os.path.expanduser("~/.geiger"), "/etc/geiger"]
        self.__config_path = [os.path.realpath(os.path.join(directory, self.CONFIG_FILE_NAME)) for directory in
                              self.__config_path]
        self.__is_configuration_loaded = False
        self.__conf = configparser.ConfigParser()
        self.__comm = None
        self.__monitor = None
        self.__generator = GeigerRandomNumberGenerator(2)

        self.read_conf()
        self.__monitor = monitor.Monitor(configuration=self.__conf, usbcomm=self.__comm)

        # register SIGINT (Ctrl-C) signal handler
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

        self.__monitor.start()
        self.main_loop()

    def main_loop(self):
        last = []
        while True:
            if self.__monitor.get_radiation is not None and self.__monitor.get_radiation > 0:
                last.append(self.__monitor.get_radiation)
                if last[0] != self.__monitor.get_radiation:
                    self.__generator.set_pulse_time()
                    if self.__generator.get_random_bits_number == self.__generator.get_number_of_bits:
                        print((str(self.__generator.get_int_number())))

                if len(last) > 1:
                    last.pop(0)


    # print(self.__comm)

    # default config file name

    def signal_handler(self, signum, frame):
        """Handles stopping signals, closes all updaters and threads and exits."""
        self.__monitor.stop()
        sys.exit(1)

    def read_conf(self):
        for filePath in self.__config_path:
            try:
                self.__conf.read_file(open(filePath))
                self.__is_configuration_loaded = True
                break
            except IOError:
                self.__is_configuration_loaded = False

        if not self.__is_configuration_loaded:
            print >> sys.stderr, ("Error at loading configuration file.")
            sys.exit(1)

        try:
            print("Initializing Geiger device...")
            self.__comm = usbcomm.Connector(self.__conf)
        except usbcomm.CommException as exp:
            print("Error at initializing USB device: %s", str(exp))
            sys.exit(1)


if __name__ == "__main__":
    Geiger()
