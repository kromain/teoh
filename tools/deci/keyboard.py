import sys
from tkinter import *

from skynet.deci.dualshock import DualShock,Buttons
from skynet.deci import deci4

deci4.enable_logging = False


class App:
    keymap = {'w':Buttons.UP,
           'a':Buttons.LEFT,
           's':Buttons.DOWN,
           'd':Buttons.RIGHT,
           'D': Buttons.R1,
           'W': Buttons.L1,
           'r': Buttons.R2,
           'l': Buttons.L2,
           'x': Buttons.CROSS,
           'z': Buttons.CIRCLE,
           'c': Buttons.SQUARE,
           't': Buttons.TRIANGLE,
           'o': Buttons.OPTION,
           'h': Buttons.SHARE,
           'p':Buttons.PS}

    def __init__(self):
        self.root = Tk()
        self.frame = Frame(self.root, width=100, height=100)
        self.frame.bind("<Key>", self.keydown)
        self.frame.bind("<KeyRelease>", self.keyup)
        self.frame.bind("<Button-1>", self.callback)
        self.frame.pack()

        try:
            self.controller = DualShock(target_ip=sys.argv[1])
        except IndexError:
            print("USAGE keyboard.py IPADDRESS")
            quit()
        
    def run(self):
        self.controller.start()

        self.root.mainloop()

        self.controller.stop()

    def keyup(self,event):

        try:
            self.controller.buttonup(self.keymap[event.char])
        except:
            if event.char == 'q':
                self.frame.quit()
            pass # ignore bad keys

    def keydown(self,event):

        try:
            self.controller.buttondown(self.keymap[event.char])
        except:
            pass # ignore bad keys

    def callback(self,event):
        self.frame.focus_set()

App().run()
