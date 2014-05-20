import sys
import getch
import threading
from deci4 import Netmp

class ConsoleThread(threading.Thread):

    def init(self, ttyp):
        self.ttyp = ttyp
        self.stop = False

    def run(self):
        while not self.stop:
            res = ttyp.read()
            if res:
                if len(res["message"]) > 1:
                    print ("%s" % res["message"])

netmp = Netmp(ip=sys.argv[1])

netmp.connect()

ctrlp = netmp.register_ctrlp()

ttyp = netmp.register_ttyp()

thread = ConsoleThread()

thread.init(ttyp)
thread.start()

ctrlp.play_start()

def dobutton(ctrlp, button):
    for i in range(10):
        ctrlp.play_data([button] * 8)

    for i in range(10):
        ctrlp.play_data([0x0] * 8)

while True:
    ch = getch.getch()

    if ch == 'q':
        thread.stop = True
        break
    elif ch == 'w':
        dobutton(ctrlp,0x10)
    elif ch == 'a':
        dobutton(ctrlp,0x80)
    elif ch == 's':
        dobutton(ctrlp,0x40)
    elif ch == 'd':
        dobutton(ctrlp,0x20)
    elif ch == 'D': #r1
        dobutton(ctrlp,0x400)
    elif ch == 'W': #l1
        dobutton(ctrlp,0x800)
    elif ch == 'r': #r2
        dobutton(ctrlp,0x200)
    elif ch == 'l': #l2
        dobutton(ctrlp,0x100)
    elif ch == 'x': # cross
        dobutton(ctrlp,0x4000)
    elif ch == 'z': #circle
        dobutton(ctrlp,0x2000)
    elif ch == 'c': #square
        dobutton(ctrlp,0x8000)
    elif ch == 't': #triangle
        dobutton(ctrlp,0x1000)
    elif ch == 'o': #option
        dobutton(ctrlp,0x8)
    elif ch == 'h': #share - doesn't seem to work
        dobutton(ctrlp,0x100000)
    elif ch == 'p':
        dobutton(ctrlp,0x10000)


ctrlp.play_stop()

thread.join()

netmp.unregister_ttyp()

netmp.unregister_ctrlp()

netmp.disconnect()


