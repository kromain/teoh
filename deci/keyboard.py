import sys
import time
import threading
from Tkinter import *
from deci4 import Netmp, Controller

class KeyThread(threading.Thread):

    def run(self):
        self.buttonstate = 0x0
        self.stop = False
        self.blocks = []

        netmp = Netmp(ip=sys.argv[1])

        netmp.connect()

        ctrlp = netmp.register_ctrlp()

        ctrlp.play_start()

        while not self.stop:
            ctrlp.play_data([self.buttonstate] * 8)
            time.sleep(0.01)

        ctrlp.play_stop()

        netmp.unregister_ctrlp()

        netmp.disconnect()


thread = KeyThread()

root = Tk()


def keyup(event):
    global thread

    if event.char == 'w':
        thread.buttonstate &= ~Controller.UP
    elif event.char == 'a':
        thread.buttonstate &= ~Controller.LEFT
    elif event.char == 's':
        thread.buttonstate &= ~Controller.DOWN
    elif event.char == 'd':
        thread.buttonstate &= ~Controller.RIGHT
    elif event.char == 'D': 
        thread.buttonstate &= ~Controller.R1
    elif event.char == 'W': 
        thread.buttonstate &= ~Controller.L1
    elif event.char == 'r': 
        thread.buttonstate &= ~Controller.R2
    elif event.char == 'l': 
        thread.buttonstate &= ~Controller.L2
    elif event.char == 'x': 
        thread.buttonstate &= ~Controller.CROSS
    elif event.char == 'z': 
        thread.buttonstate &= ~Controller.CIRCLE
    elif event.char == 'c': 
        thread.buttonstate &= ~Controller.SQUARE
    elif event.char == 't': 
        thread.buttonstate &= ~Controller.TRIANGLE
    elif event.char == 'o': 
        thread.buttonstate &= ~Controller.OPTION
    elif event.char == 'h': 
        thread.buttonstate &= ~Controller.SHARE
    elif event.char == 'p':
        thread.buttonstate &= ~Controller.PS

def keydown(event):
    global thread

    if event.char == 'w':
        thread.buttonstate |= Controller.UP
    elif event.char == 'a':
        thread.buttonstate |= Controller.LEFT
    elif event.char == 's':
        thread.buttonstate |= Controller.DOWN
    elif event.char == 'd':
        thread.buttonstate |= Controller.RIGHT
    elif event.char == 'D': 
        thread.buttonstate |= Controller.R1
    elif event.char == 'W': 
        thread.buttonstate |= Controller.L1
    elif event.char == 'r': 
        thread.buttonstate |= Controller.R2
    elif event.char == 'l': 
        thread.buttonstate |= Controller.L2
    elif event.char == 'x': 
        thread.buttonstate |= Controller.CROSS
    elif event.char == 'z': 
        thread.buttonstate |= Controller.CIRCLE
    elif event.char == 'c': 
        thread.buttonstate |= Controller.SQUARE
    elif event.char == 't': 
        thread.buttonstate |= Controller.TRIANGLE
    elif event.char == 'o': 
        thread.buttonstate |= Controller.OPTION
    elif event.char == 'h': 
        thread.buttonstate |= Controller.SHARE
    elif event.char == 'p':
        thread.buttonstate |= Controller.PS


def callback(event):
    frame.focus_set()

frame = Frame(root, width=100, height=100)
frame.bind("<Key>", keydown)
frame.bind("<KeyRelease>", keyup)
frame.bind("<Button-1>", callback)
frame.pack()

thread.start()
root.mainloop()
thread.stop = True
thread.join()
