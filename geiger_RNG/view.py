import datetime
from tkinter import *
from tkinter.ttk import Button, Treeview

from geiger_RNG import constants


class RngView:

    def __init__(self, model):
        self.list = []
        self.__index = 0
        self.__win = Tk()
        self.__model = model
        self.__win.geometry('800x500+10+10')
        self.__win.wm_title(constants.TITLE)

        self.__f_settings = Frame(self.__win)
        self.__f_settings.pack(side=LEFT, fill=BOTH, expand=True)

        self.__button = Button(self.__f_settings, command=self.__set_start_or_stop, text=constants.START)
        self.__button.pack()

        self.__tree_view = Treeview(self.__f_settings,
                                    height=24,
                                    columns=(constants.LP, constants.LEVEL_OF_RADIATION_COLUMN,
                                             constants.GENERATED_NUMBER_COLUMN,
                                             constants.BITS_COLUM,
                                             constants.TIME_ADDED_COLUMN,
                                             constants.MILLISECONDS_ADDED_COLUMN))
        self.__create_tree_view()

    def run_main_loop(self):
        self.__win.mainloop()

    def __set_start_or_stop(self):
        if self.__model.is_working():
            self.__button.config(text=constants.START)
        else:
            self.__button.config(text=constants.END)

        self.__win.update()
        self.__model.run()

    def __create_tree_view(self):
        self.__tree_view.column('#0', stretch=NO, width=0)
        self.__tree_view.column(constants.LP, anchor=CENTER, width=30)
        self.__tree_view.column(constants.LEVEL_OF_RADIATION_COLUMN, anchor=CENTER, width=85)
        self.__tree_view.column(constants.GENERATED_NUMBER_COLUMN, anchor=CENTER, width=220)
        self.__tree_view.column(constants.BITS_COLUM, anchor=CENTER, width=220)
        self.__tree_view.column(constants.TIME_ADDED_COLUMN, anchor=CENTER, width=80)
        self.__tree_view.column(constants.MILLISECONDS_ADDED_COLUMN, anchor=CENTER, width=80)

        self.__tree_view.heading(constants.LP, text=constants.LP, anchor=CENTER)
        self.__tree_view.heading(constants.LEVEL_OF_RADIATION_COLUMN, text=constants.LEVEL_OF_RADIATION_COLUMN,
                                 anchor=CENTER)
        self.__tree_view.heading(constants.GENERATED_NUMBER_COLUMN, text=constants.GENERATED_NUMBER_COLUMN,
                                 anchor=CENTER)
        self.__tree_view.heading(constants.BITS_COLUM, text=constants.BITS_COLUM, anchor=CENTER)
        self.__tree_view.heading(constants.TIME_ADDED_COLUMN, text=constants.TIME_ADDED_COLUMN, anchor=CENTER)
        self.__tree_view.heading(constants.MILLISECONDS_ADDED_COLUMN, text=constants.MILLISECONDS_ADDED_COLUMN,
                                 anchor=CENTER)

        self.__tree_view.pack(fill=BOTH)

    def insert_to_list(self, radiation, number, bits):
        current_time = datetime.datetime.now()
        self.__tree_view.insert(parent='', index=self.__index, iid=self.__index, text='',
                                values=(self.__index, radiation, number, bits, current_time.strftime('%X'),
                                        current_time.strftime('%f')))
        self.__index += 1
