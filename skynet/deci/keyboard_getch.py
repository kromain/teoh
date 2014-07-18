import getch
import sys
import threading

from skynet.deci.dualshock import DualShock, Buttons
from skynet.deci.console import Console

class ConsoleThread(threading.Thread):

    def run(self):
        self.stop = False
        with Console(ip=sys.argv[1]) as console:
            while not self.stop:
                line = console.read()
                if line:
                    print (line)

thread = ConsoleThread()

with DualShock(target_ip=sys.argv[1], force=True) as controller:

    thread.start()
    while True:
        ch = getch.getch()

        if ch == 'q':
            thread.stop = True
            thread.join()
            break

        button =  {'w':Buttons.UP,
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
               'p':Buttons.PS} [ ch ]

        controller.buttonpress(button)




