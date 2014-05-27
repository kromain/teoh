import sys
import time
from tkinter import *
from controller import Controller



class App:
    keymap = {'w':Controller.UP,
           'a':Controller.LEFT,
           's':Controller.DOWN,
           'd':Controller.RIGHT,
           'D': Controller.R1,
           'W': Controller.L1,
           'r': Controller.R2,
           'l': Controller.L2,
           'x': Controller.CROSS,
           'z': Controller.CIRCLE,
           'c': Controller.SQUARE,
           't': Controller.TRIANGLE,
           'o': Controller.OPTION,
           'h': Controller.SHARE,
           'p':Controller.PS}

    def __init__(self):
        self.root = Tk()
        self.frame = Frame(self.root, width=100, height=100)
        self.frame.bind("<Key>", self.keydown)
        self.frame.bind("<KeyRelease>", self.keyup)
        self.frame.bind("<Button-1>", self.callback)
        self.frame.pack()

        self.controller = Controller(ip=sys.argv[1])
        
    def run(self):
        self.controller.start()

        self.root.mainloop()

        self.controller.stop()

    def keyup(self,event):

        try:
            self.controller.keyup(self.keymap[event.char])
        except:
            pass # ignore bad keys

    def keydown(self,event):

        try:
            self.controller.keydown(self.keymap[event.char])
        except:
            pass # ignore bad keys

    def callback(self,event):
        self.frame.focus_set()

App().run()
