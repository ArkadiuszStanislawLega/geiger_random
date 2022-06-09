import signal
import sys

import threading
import time

from geiger_RNG import monitor, constants
from geiger_RNG.write_to_excel import WriteToExcel
from geiger_RNG.geiger_random_number_generator import GeigerRandomNumberGenerator
from geiger_RNG.geiger_simulator import GeigerSimulator
from geiger_RNG.view import RngView
from usb_communication.comm_exception import CommException
from usb_communication.connector import Connector


class Geiger:

    def __init__(self, simulation=False):
        self.__write_to_file = WriteToExcel()
        self.__generator = GeigerRandomNumberGenerator(constants.SIZE_OF_GENERATED_NUMBER_IN_BITS)
        self.__view = RngView(self)

        self.__comm = None
        self.__monitor = None

        self.__is_simulation = simulation  # <<<!!!!Jeżeli podłączone jest urządzenie tą flagę trzeba dać na False!!!!!
        self.__is_working = False
        self.__is_should_be_set_pulse_time = False
        self.__is_should_be_data_save = False

        self.__readings_collector = []
        self.__current_radiation = None

        self.__initialise_connection()
        self.__init_ctr_c_handler()
        self.__start_readings()

        # self.run_with_GUI()
        self.run()

    def __initialise_connection(self):
        if not self.__is_simulation:
            self.__initialise_usb_communication()
            self.__monitor = monitor.Monitor(usb_comm=self.__comm)

    def __initialise_usb_communication(self):
        try:
            print(constants.INITIALIZATION_MESSAGE)
            self.__comm = Connector()
        except CommException as exp:
            print(f"{constants.ERROR_INITIALIZATION_USB_MESSAGE} {str(exp)}")
            sys.exit(1)

    def __init_ctr_c_handler(self):
        # register SIGINT (Ctrl-C) signal handler
        signal.signal(signal.SIGINT, self.__signal_handler)
        signal.signal(signal.SIGTERM, self.__signal_handler)

    def __signal_handler(self, signum, frame):
        """Handles stopping signals, closes all updaters and threads and exits."""
        self.__monitor.stop()
        sys.exit(1)

    def __start_readings(self):
        if not self.__is_simulation:
            self.__monitor.start()
            # self.__main_loop_new()

    def run_with_GUI(self):
        main_loop = threading.Thread(target=self.run)
        main_loop.daemon = True
        main_loop.start()

        self.__view.run_main_loop()

    def run(self):
        if self.__is_working:
            self.__is_working = False
        else:
            self.__is_working = True

        if self.__is_simulation:
            self.__main_loop_sim()
        else:
            self.__main_loop()

    def is_working(self):
        return self.__is_working

    def __main_loop(self):
        while self.__is_working:
            if self.__monitor.get_radiation is not None:
                self.__update_current_radiation()
                if self.__monitor.is_count_acknowledged:
                    self.__set_pulse_time_to_generator()
                    if self.__is_data_should_be_save():
                        self.__write_readings_to_file()
                        self.__show_result_in_GUI()
                        self.__clear_bits_in_generator()

    def __update_current_radiation(self):
        if self.__is_current_radiation_should_be_updated():
            self.__current_radiation = self.__monitor.get_radiation
            self.__is_should_be_set_pulse_time = True
        else:
            self.__current_radiation = self.__monitor.get_radiation

    def __is_current_radiation_should_be_updated(self):
        return self.__current_radiation is not None \
                and self.__current_radiation != self.__monitor.get_radiation

    def __set_pulse_time_to_generator(self):
        if self.__is_should_be_set_pulse_time:
            self.__generator.set_pulse_time()
            self.__is_should_be_set_pulse_time = False

    def __is_data_should_be_save(self):
        return self.__generator.get_current_size_of_bits == constants.SIZE_OF_GENERATED_NUMBER_IN_BITS

    def __write_readings_to_file(self):
        self.__write_to_file.write_row(radiation=self.__current_radiation,
                                       number=self.__generator.get_int_number(),
                                       bits=self.__generator.get_bits())

    def __show_result_in_GUI(self):
        self.__view.insert_to_list(radiation=self.__current_radiation,
                                   number=self.__generator.get_int_number(),
                                   bits=self.__generator.get_bits())

    def __clear_bits_in_generator(self):
        # self.__generator = GeigerRandomNumberGenerator(self.SIZE_OF_GENERATED_NUMBER_IN_BITS)
        self.__generator.remove_bits_if_size_is_max()

    # def __remove_oldest_reading(self):
    #     if len(self.__readings_collector) > 1:
    #         print(f'usuwam pierwszy{self.__readings_collector[0]} len = {len(self.__readings_collector)}')
    #         self.__readings_collector.pop(0)

    # region SIMULATION
    def __main_loop_sim(self):
        main_loop = threading.Thread(target=self.__simulation)
        main_loop.daemon = True
        main_loop.start()

        self.__view.run_main_loop()

    def __simulation(self):
        simulation = GeigerSimulator()
        self.__readings_collector = []
        self.__excel_first_row()

        while self.__is_working:
            time.sleep(0.05)
            simulation.get_values()
            if simulation.get_radiation() is not None and simulation.is_count_acknowledged():
                self.__compare_two_simulated_last_readings(simulation)
                self.__remove_oldest_reading()

    def __compare_two_simulated_last_readings(self, simulation):
        if len(self.__readings_collector) == 0:
            self.__readings_collector.append(simulation.get_radiation())
            self.__write_simulated_readings_to_file(simulation)

        else:
            if self.__readings_collector[0] != simulation.get_radiation():
                self.__readings_collector.append(simulation.get_radiation())
                self.__generator.set_pulse_time()
                self.__write_simulated_readings_to_file(simulation)

    def __write_simulated_readings_to_file(self, simulation):
        if self.__generator.get_current_size_of_bits == self.__generator.get_number_of_bits:
            # self.__view.insert_to_list(radiation=simulation.get_radiation(), number=self.__generator.get_int_number(),
            #                            bits=self.__generator.get_bits())
            self.__write_to_file.write_row(radiation=simulation.get_radiation(),
                                           number=self.__generator.get_int_number(),
                                           bits=self.__generator.get_bits())
            self.__generator = GeigerRandomNumberGenerator(self.SIZE_OF_GENERATED_NUMBER_IN_BITS)
            # self.__generator.remove_bits_if_size_is_max()
    # endregion Endsimulation
