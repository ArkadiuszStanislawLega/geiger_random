import datetime
import signal
import sys

import configparser
import threading
import time
from time import strftime

from geiger_RNG import monitor
from geiger_RNG.geiger_random_number_generator import GeigerRandomNumberGenerator
from geiger_RNG.geiger_simulator import GeigerSimulator
from geiger_RNG.view import RngView
from usb_communication.comm_exception import CommException
from usb_communication.connector import Connector

from xlwt import Workbook


class Geiger:
    SIZE_OF_GENERATED_NUMBER_IN_BITS = 8
    INITIALIZATION_MESSAGE = 'Initializing Geiger device...'
    ERROR_INITIALIZATION_USB_MESSAGE = 'Error at initializing USB device: '
    ERROR_LOADING_CONFIGURATION_MESSAGE = 'Error at loading configuration file.'
    EXCEL_FILE_NAME = 'wniki_pomiaru.xls'
    LEVEL_OF_RADIATION_COLUMN = 'Poziom naprowmieniowania'
    GENERATED_NUMBER_COLUMN = 'Wygenerowana cyfra'
    BITS_COLUM = 'Bity'
    TIME_ADDED_COLUMN = 'Czas dodania wpisu'
    MILLISECONDS_ADDED_COLUMN = 'Milisekundy dodania wpisu'
    COLUMN_INDEX_RADIATION = 0
    COLUMN_INDEX_GENERATED_NUMBER = 1
    COLUMN_INDEX_BITS = 2
    COLUMN_INDEX_TIME = 3
    COLUMN_INDEX_MILLISECONDS = 4

    def __init__(self):
        self.__is_configuration_loaded = False
        self.__comm = None
        self.__monitor = None
        self.__is_working = False
        self.__current_index = 0
        self.__wb = Workbook()
        self.__view = RngView(funct=self.run, controller=self)

        self.__sheet1 = self.__wb.add_sheet('Sheet 1')

        # self.__initialise_usb_communication()
        # self.__monitor = monitor.Monitor(usb_comm=self.__comm)
        self.__generator = GeigerRandomNumberGenerator(self.SIZE_OF_GENERATED_NUMBER_IN_BITS)

        self.__init_ctr_c_handler()
        self.__readings_collector = []

        # self.__monitor.start()
        # self.__main_loop()
        # self.run()
        self.__view.run_main_loop()

    def is_working(self):
        return self.__is_working

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

    def __main_loop_sim(self):
        main_loop = threading.Thread(target=self.__simulation)
        main_loop.daemon = True
        main_loop.start()

        self.__view.run_main_loop()

    def run(self):
        if self.__is_working:
            self.__is_working = False
        else:
            self.__is_working = True
        self.__main_loop_sim()

    def __excel_first_row(self):
        self.__sheet1.write(self.__current_index, self.COLUMN_INDEX_RADIATION, self.LEVEL_OF_RADIATION_COLUMN)
        self.__sheet1.write(self.__current_index, self.COLUMN_INDEX_GENERATED_NUMBER, self.GENERATED_NUMBER_COLUMN)
        self.__sheet1.write(self.__current_index, self.COLUMN_INDEX_BITS, self.BITS_COLUM)
        self.__sheet1.write(self.__current_index, self.COLUMN_INDEX_TIME, self.TIME_ADDED_COLUMN)
        self.__sheet1.write(self.__current_index, self.COLUMN_INDEX_MILLISECONDS, self.MILLISECONDS_ADDED_COLUMN)

        self.__wb.save(self.EXCEL_FILE_NAME)
        self.__current_index += 1

    def __excel(self, radiation=0, number=0, bits=''):
        date = datetime.datetime.now()
        self.__sheet1.write(self.__current_index, self.COLUMN_INDEX_RADIATION, radiation)
        self.__sheet1.write(self.__current_index, self.COLUMN_INDEX_GENERATED_NUMBER, number)
        self.__sheet1.write(self.__current_index, self.COLUMN_INDEX_BITS, bits)
        self.__sheet1.write(self.__current_index, self.COLUMN_INDEX_TIME, date.strftime("%X"))
        self.__sheet1.write(self.__current_index, self.COLUMN_INDEX_MILLISECONDS, date.strftime("%f"))

        self.__wb.save(self.EXCEL_FILE_NAME)
        self.__current_index += 1

    def __simulation(self):
        simulation = GeigerSimulator()
        self.__readings_collector = []
        self.__excel_first_row()

        while self.__is_working:
            time.sleep(0.05)
            simulation.get_values()
            if simulation.get_radiation() is not None and simulation.is_count_acknowledged():
                self.__compare_two_last_readings(simulation)
                self.__remove_oldest_reading()

    def __remove_oldest_reading(self):
        if len(self.__readings_collector) > 1:
            self.__readings_collector.pop(0)

    def __compare_two_last_readings(self, simulation):
        if len(self.__readings_collector) == 0:
            self.__readings_collector.append(simulation.get_radiation())
            self.__write_readings_to_file(simulation)

        else:
            if self.__readings_collector[0] != simulation.get_radiation():
                self.__readings_collector.append(simulation.get_radiation())
                self.__generator.set_pulse_time()
                self.__write_readings_to_file(simulation)

    def __write_readings_to_file(self, simulation):
        if self.__generator.get_random_bits_number == self.__generator.get_number_of_bits:
            self.__view.insert_to_list(radiation=simulation.get_radiation(), number=self.__generator.get_int_number(),
                                       bits=self.__generator.get_bits())
            self.__excel(radiation=simulation.get_radiation(), number=self.__generator.get_int_number(),
                         bits=self.__generator.get_bits())
            self.__generator = GeigerRandomNumberGenerator(self.SIZE_OF_GENERATED_NUMBER_IN_BITS)
            # self.__generator.remove_bits_if_size_is_max()

    def __signal_handler(self, signum, frame):
        """Handles stopping signals, closes all updaters and threads and exits."""
        self.__monitor.stop()
        sys.exit(1)
