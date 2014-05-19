import sys
import time
from tkinter import *
from controller import Controller


root = Tk()

def keyup(event):
    global thread

    if event.char == 'w':
        controller.keyup(Controller.UP)
    elif event.char == 'a':
        controller.keyup(Controller.LEFT)
    elif event.char == 's':
        controller.keyup(Controller.DOWN)
    elif event.char == 'd':
        controller.keyup(Controller.RIGHT)
    elif event.char == 'D': 
        controller.keyup(Controller.R1)
    elif event.char == 'W': 
        controller.keyup(Controller.L1)
    elif event.char == 'r': 
        controller.keyup(Controller.R2)
    elif event.char == 'l': 
        controller.keyup(Controller.L2)
    elif event.char == 'x': 
        controller.keyup(Controller.CROSS)
    elif event.char == 'z': 
        controller.keyup(Controller.CIRCLE)
    elif event.char == 'c': 
        controller.keyup(Controller.SQUARE)
    elif event.char == 't': 
        controller.keyup(Controller.TRIANGLE)
    elif event.char == 'o': 
        controller.keyup(Controller.OPTION)
    elif event.char == 'h': 
        controller.keyup(Controller.SHARE)
    elif event.char == 'p':
        controller.keyup(Controller.PS)

def keydown(event):
    global thread

    if event.char == 'w':
        controller.keydown(Controller.UP)
    elif event.char == 'a':
        controller.keydown(Controller.LEFT)
    elif event.char == 's':
        controller.keydown(Controller.DOWN)
    elif event.char == 'd':
        controller.keydown(Controller.RIGHT)
    elif event.char == 'D': 
        controller.keydown(Controller.R1)
    elif event.char == 'W': 
        controller.keydown(Controller.L1)
    elif event.char == 'r': 
        controller.keydown(Controller.R2)
    elif event.char == 'l': 
        controller.keydown(Controller.L2)
    elif event.char == 'x': 
        controller.keydown(Controller.CROSS)
    elif event.char == 'z': 
        controller.keydown(Controller.CIRCLE)
    elif event.char == 'c': 
        controller.keydown(Controller.SQUARE)
    elif event.char == 't': 
        controller.keydown(Controller.TRIANGLE)
    elif event.char == 'o': 
        controller.keydown(Controller.OPTION)
    elif event.char == 'h': 
        controller.keydown(Controller.SHARE)
    elif event.char == 'p':
        controller.keydown(Controller.PS)


def callback(event):
    frame.focus_set()

frame = Frame(root, width=100, height=100)
frame.bind("<Key>", keydown)
frame.bind("<KeyRelease>", keyup)
frame.bind("<Button-1>", callback)
frame.pack()

controller = Controller()
controller.start()

root.mainloop()

controller.stop()
