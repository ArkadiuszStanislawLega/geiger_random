import datetime
from tkinter import *
from tkinter.ttk import Button, Treeview

import geiger_RNG.geiger_run


class RngView:
    LP = 'lp.'
    START = 'Start'
    END = 'Koniec'
    TITLE = "Generator liczb losowych Geigera"

    def __init__(self, funct, controller):
        self.list = []
        self.__index = 0
        self.__win = Tk()
        self.__controller = controller
        self.__win.geometry('800x500+10+10')
        self.__win.wm_title(self.TITLE)

        self.__f_settings = Frame(self.__win)
        self.__f_settings.pack(side=LEFT, fill=BOTH, expand=True)

        self.__button = Button(self.__f_settings, command=self.__set_start_or_stop, text=self.START)
        self.__button.pack()

        self.__tree_view = Treeview(self.__f_settings,
                                    height=24,
                                    columns=(self.LP, geiger_RNG.geiger_run.LEVEL_OF_RADIATION_COLUMN,
                                             geiger_RNG.geiger_run.GENERATED_NUMBER_COLUMN,
                                             geiger_RNG.geiger_run.BITS_COLUM,
                                             geiger_RNG.geiger_run.TIME_ADDED_COLUMN,
                                             geiger_RNG.geiger_run.MILLISECONDS_ADDED_COLUMN))
        self.__create_tree_view()

    def run_main_loop(self):
        self.__win.mainloop()

    def __set_start_or_stop(self):
        if self.__controller.is_working():
            self.__button.config(text=self.START)
        else:
            self.__button.config(text=self.END)

        self.__win.update()
        self.__controller.run()

    def __create_tree_view(self):
        self.__tree_view.column('#0', stretch=NO, width=0)
        self.__tree_view.column(self.LP, anchor=CENTER, width=30)
        self.__tree_view.column(geiger_RNG.geiger_run.LEVEL_OF_RADIATION_COLUMN, anchor=CENTER, width=85)
        self.__tree_view.column(geiger_RNG.geiger_run.GENERATED_NUMBER_COLUMN, anchor=CENTER, width=220)
        self.__tree_view.column(geiger_RNG.geiger_run.BITS_COLUM, anchor=CENTER, width=220)
        self.__tree_view.column(geiger_RNG.geiger_run.TIME_ADDED_COLUMN, anchor=CENTER, width=80)
        self.__tree_view.column(geiger_RNG.geiger_run.MILLISECONDS_ADDED_COLUMN, anchor=CENTER, width=80)

        self.__tree_view.heading(self.LP, text=self.LP, anchor=CENTER)
        self.__tree_view.heading(geiger_RNG.geiger_run.LEVEL_OF_RADIATION_COLUMN, text=geiger_RNG.geiger_run.LEVEL_OF_RADIATION_COLUMN, anchor=CENTER)
        self.__tree_view.heading(geiger_RNG.geiger_run.GENERATED_NUMBER_COLUMN, text=geiger_RNG.geiger_run.GENERATED_NUMBER_COLUMN, anchor=CENTER)
        self.__tree_view.heading(geiger_RNG.geiger_run.BITS_COLUM, text=geiger_RNG.geiger_run.BITS_COLUM, anchor=CENTER)
        self.__tree_view.heading(geiger_RNG.geiger_run.TIME_ADDED_COLUMN, text=geiger_RNG.geiger_run.TIME_ADDED_COLUMN, anchor=CENTER)
        self.__tree_view.heading(geiger_RNG.geiger_run.MILLISECONDS_ADDED_COLUMN, text=geiger_RNG.geiger_run.MILLISECONDS_ADDED_COLUMN, anchor=CENTER)

        self.__tree_view.pack(fill=BOTH)

    def insert_to_list(self, radiation, number, bits):
        current_time = datetime.datetime.now()
        self.__tree_view.insert(parent='', index=self.__index, iid=self.__index, text='',
                                values=(self.__index, radiation, number, bits, current_time.strftime('%X'),
                                        current_time.strftime('%f')))
        self.__index += 1
