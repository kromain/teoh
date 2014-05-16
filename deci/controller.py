import time
import sys
import threading
from deci4 import Netmp

class Controller:
    UP = 0x10
    LEFT = 0x80
    RIGHT = 0x20
    DOWN = 0x40
    R1 = 0x400
    L1 = 0x800
    R2 = 0x200
    L2 = 0x100
    CROSS = 0x4000
    CIRCLE = 0x2000
    SQUARE = 0x8000
    TRIANGLE = 0x1000
    OPTION = 0x8
    SHARE = 0x1
    PS = 0x10000

    class KeyThread(threading.Thread):

        def run(self):

            self.buttonstate = 0x0
            self.stop = False

            while not self.stop:
                self.ctrlp.play_data([self.buttonstate] * 8)
                time.sleep(0.1)

    def start(self):

        self.netmp = Netmp(ip=sys.argv[1])

        self.netmp.connect()

        self.ctrlp = self.netmp.register_ctrlp()

        self.ctrlp.play_start()

        self.thread = self.KeyThread()
        self.thread.ctrlp = self.ctrlp

        self.thread.ready = False
        self.thread.start()

        time.sleep(0.1)

    def stop(self):
        self.thread.stop = True
        self.thread.join()

        self.ctrlp.play_stop()

        self.netmp.unregister_ctrlp()

        self.netmp.disconnect()

    def keydown(self,button):
        self.thread.buttonstate |= button

    def keyup(self,button):
        self.thread.buttonstate &= ~button

    def buttonpress(self, button, timetopress=0.1):
        print "press %x" % button
        self.keydown(button)
        time.sleep(timetopress)
        self.keyup(button)
        time.sleep(0.1)
        
if __name__ ==  "__main__":
    
    controller = Controller()

    controller.start()
    controller.buttonpress(Controller.RIGHT)
    controller.buttonpress(Controller.RIGHT)
    controller.buttonpress(Controller.RIGHT)
    controller.buttonpress(Controller.RIGHT)
    controller.buttonpress(Controller.UP)
    controller.buttonpress(Controller.DOWN)
    controller.buttonpress(Controller.LEFT, 1.0)
    controller.buttonpress(Controller.RIGHT, 1.0)
    controller.buttonpress(Controller.PS, 1.0)
    time.sleep(1)
    controller.buttonpress(Controller.CIRCLE)
