import configparser
import usbcomm
import sys
import os
import signal
import monitor






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
