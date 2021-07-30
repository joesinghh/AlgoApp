from ttkwidgets.autocomplete import AutocompleteCombobox
from tkinter import *
from threading import Thread

def demo():
    def d():
        print("hello")

    t2 = Thread(target=d,args=())
    t2.start()

demo()