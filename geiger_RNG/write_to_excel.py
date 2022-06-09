import datetime

from xlwt import Workbook
from geiger_RNG import constants


class WriteToExcel:

    def __init__(self):
        self.__wb = Workbook()
        self.__sheet1 = self.__wb.add_sheet(constants.EXCEL_SHIT_TITLE)
        self.__current_index = 0
        self.__excel_first_row()

    def __excel_first_row(self):
        self.__sheet1.write(self.__current_index, constants.COLUMN_INDEX_RADIATION, constants.LEVEL_OF_RADIATION_COLUMN)
        self.__sheet1.write(self.__current_index, constants.COLUMN_INDEX_GENERATED_NUMBER,
                            constants.GENERATED_NUMBER_COLUMN)
        self.__sheet1.write(self.__current_index, constants.COLUMN_INDEX_BITS, constants.BITS_COLUM)
        self.__sheet1.write(self.__current_index, constants.COLUMN_INDEX_TIME, constants.TIME_ADDED_COLUMN)
        self.__sheet1.write(self.__current_index, constants.COLUMN_INDEX_MILLISECONDS,
                            constants.MILLISECONDS_ADDED_COLUMN)

        self.__wb.save(constants.EXCEL_FILE_NAME)
        self.__current_index += 1

    def write_row(self, radiation=0, number=0, bits=''):
        print(f'{radiation}, {number}, {bits}')
        date = datetime.datetime.now()
        self.__sheet1.write(self.__current_index, constants.COLUMN_INDEX_RADIATION, radiation)
        self.__sheet1.write(self.__current_index, constants.COLUMN_INDEX_GENERATED_NUMBER, number)
        self.__sheet1.write(self.__current_index, constants.COLUMN_INDEX_BITS, bits)
        self.__sheet1.write(self.__current_index, constants.COLUMN_INDEX_TIME, date.strftime("%X"))
        self.__sheet1.write(self.__current_index, constants.COLUMN_INDEX_MILLISECONDS, date.strftime("%f"))

        self.__wb.save(constants.EXCEL_FILE_NAME)
        self.__current_index += 1
