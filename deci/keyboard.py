import sys
from tkinter import *

from deci.dualshock import DualShock


class App:
    keymap = {'w':DualShock.UP,
           'a':DualShock.LEFT,
           's':DualShock.DOWN,
           'd':DualShock.RIGHT,
           'D': DualShock.R1,
           'W': DualShock.L1,
           'r': DualShock.R2,
           'l': DualShock.L2,
           'x': DualShock.CROSS,
           'z': DualShock.CIRCLE,
           'c': DualShock.SQUARE,
           't': DualShock.TRIANGLE,
           'o': DualShock.OPTION,
           'h': DualShock.SHARE,
           'p':DualShock.PS}

    def __init__(self):
        self.root = Tk()
        self.frame = Frame(self.root, width=100, height=100)
        self.frame.bind("<Key>", self.keydown)
        self.frame.bind("<KeyRelease>", self.keyup)
        self.frame.bind("<Button-1>", self.callback)
        self.frame.pack()

        self.controller = DualShock(ip=sys.argv[1])
        
    def run(self):
        self.controller.start()

        self.root.mainloop()

        self.controller.stop()

    def keyup(self,event):

        try:
            self.controller.buttonup(self.keymap[event.char])
        except:
            pass # ignore bad keys

    def keydown(self,event):

        try:
            self.controller.buttondown(self.keymap[event.char])
        except:
            pass # ignore bad keys

    def callback(self,event):
        self.frame.focus_set()

App().run()
