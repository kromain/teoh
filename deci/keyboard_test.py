import getch
import sys
import threading

from deci.controller import Controller
from deci.console import Console

class ConsoleThread(threading.Thread):

    def run(self):
        self.stop = False
        with Console(ip=sys.argv[1]) as console:
            while not self.stop:
                line = console.read()
                if line:
                    print (line)

thread = ConsoleThread()

with Controller(ip=sys.argv[1]) as controller:

    thread.start()
    while True:
        ch = getch.getch()

        if ch == 'q':
            thread.stop = True
            thread.join()
            break

        try:
            button =  {'w':Controller.UP,
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
                   'p':Controller.PS} [ ch ]

            controller.buttonpress(button)
        except:
            pass




