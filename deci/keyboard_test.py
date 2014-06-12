import getch
import sys
import threading

from deci.dualshock import DualShock
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

with DualShock(ip=sys.argv[1]) as controller:

    thread.start()
    while True:
        ch = getch.getch()

        if ch == 'q':
            thread.stop = True
            thread.join()
            break

        try:
            button =  {'w':DualShock.UP,
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
                   'p':DualShock.PS} [ ch ]

            controller.buttonpress(button)
        except:
            pass




