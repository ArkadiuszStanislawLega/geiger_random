import datetime
from tkinter import *
from tkinter.ttk import Button, Treeview


class RngView:
    LP = 'lp'
    RADIATION = 'Promieniowanie'
    NUMBER = 'Liczba'
    BITS = 'Bity'
    TIME = 'Czas dodania'
    MICROSECONDS = 'microseconds'
    START= 'Start'
    END = 'Koniec'

    def __init__(self, funct, controller):
        self.list = []
        self.__index = 0
        self.__win = Tk()
        self.__controller = controller
        self.__win.title('Geiger random number generator')
        self.__win.geometry('800x500+10+10')
        self.__win.wm_title("Tkinter window")

        self.__f_settings = Frame(self.__win)
        self.__f_settings.pack(side=LEFT, fill=BOTH, expand=True)

        self.__button = Button(self.__f_settings, command=self.__set_start_or_stop, text=self.START)
        self.__button.pack()

        self.__tree_view = Treeview(self.__f_settings,
                                    height=24,
                                    columns=(self.LP, self.RADIATION, self.NUMBER,
                                             self.BITS, self.TIME, self.MICROSECONDS))
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
        self.__tree_view.column(self.RADIATION, anchor=CENTER, width=85)
        self.__tree_view.column(self.NUMBER, anchor=CENTER, width=220)
        self.__tree_view.column(self.BITS, anchor=CENTER, width=220)
        self.__tree_view.column(self.TIME, anchor=CENTER, width=80)
        self.__tree_view.column(self.MICROSECONDS, anchor=CENTER, width=80)

        self.__tree_view.heading(self.LP, text=self.LP, anchor=CENTER)
        self.__tree_view.heading(self.RADIATION, text=self.RADIATION, anchor=CENTER)
        self.__tree_view.heading(self.NUMBER, text=self.NUMBER, anchor=CENTER)
        self.__tree_view.heading(self.BITS, text=self.BITS, anchor=CENTER)
        self.__tree_view.heading(self.TIME, text=self.TIME, anchor=CENTER)
        self.__tree_view.heading(self.MICROSECONDS, text=self.MICROSECONDS, anchor=CENTER)

        self.__tree_view.pack(fill=BOTH)

    def insert_to_list(self, radiation, number, bits):
        current_time = datetime.datetime.now()
        self.__tree_view.insert(parent='', index=self.__index, iid=self.__index, text='',
                                values=(self.__index, radiation, number, bits, current_time.strftime('%X'),
                                        current_time.strftime('%f')))
        self.__index += 1
