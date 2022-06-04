import datetime
import tkinter.messagebox
import tkinter
from tkinter import *
from tkinter.ttk import Button


class RngView:

    def __init__(self, funct, controller):
        self.list = []
        self.__controller = controller
        self.__funct = funct
        self.win = Tk()  # creating the main window and storing the window object in 'win'
        self.win.title('Welcome')  # setting title of the window
        self.win.geometry('500x200')  # setting the size of the window

        self.__f_sensors = Frame(self.win)
        self.__f_sensors.pack()

        self.__scroll = Scrollbar(self.win)
        self.__scroll.pack(side=RIGHT, fill=Y)

        self.__list = Listbox(self.win, yscrollcommand=self.__scroll.set)

        self.__list.pack(side=LEFT, fill=BOTH)

        self.__scroll.config(command=self.__list.yview)

        self.btn = Button(self.win, text='Start', width=10, command=self.__set_start_or_stop)
        self.text = Text
        self.btn.place(x=200, y=30)

    def func(self):  # function of the button
        tkinter.messagebox.showinfo("Greetings", "Hello! Welcome to PythonGeeks.")

    def run_main_loop(self):
        self.win.mainloop()

    def __set_start_or_stop(self):
        if self.__controller.get_is_run():
            self.btn.config(text='Start')
        else:
            self.btn.config(text='Stop')
        self.__funct()

    def insert_to_list(self, value):
        string = f'{str(value)} {datetime.datetime.now().time()}'
        self.__list.insert(self.__list.size()-1,  string)
        self.win.update()


