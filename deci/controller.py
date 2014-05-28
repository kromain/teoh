import time
import sys
import threading
from deci4 import Netmp, NetmpManager

class Controller(NetmpManager):
    """ Input at the controller level.  
    
        While in operation, sends constant events to the device even if no
        keys pressed.
    """
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
        """ Thread that sends the current button state to the device once every 10 msecs. """

        def run(self):

            self.buttonstate = 0x0
            self.stop = False

            while not self.stop:
                self.ctrlp.play_data([self.buttonstate] * 8)
                time.sleep(0.1)


    def __init__(self, ip):
        self.ip = ip

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, type, value, traceback):
        self.stop()

    def start(self):
        """ Connect to the device and prepare to send events """

        self.netmp = super(Controller,self).startnetmp(self.ip)

        self.ctrlp = self.netmp.register_ctrlp()

        self.ctrlp.play_start()

        self.thread = self.KeyThread()
        self.thread.ctrlp = self.ctrlp

        self.thread.ready = False
        self.thread.start()

        time.sleep(0.1)

    def stop(self):
        """ stop sending events. """
        self.thread.stop = True
        self.thread.join()

        self.ctrlp.play_stop()

        self.netmp.unregister_ctrlp()

        self.netmp = super(Controller, self).stopnetmp(self.ip)

    def keydown(self,button):
        """ sets button in the key down state, leaving other buttons as is. 
        
            button - bitfield of buttons to set in down state.
                     ex Controller.UP | Controller.RIGHT
        """
        self.thread.buttonstate |= button

    def keyup(self,button):
        """ sets button in the key up state, leaving other buttons as is. 
        
            button - bitfield of buttons to set in up state.
                     ex Controller.UP | Controller.RIGHT
        """
        self.thread.buttonstate &= ~button

    def buttonpress(self, button, timetopress=0.2):
        """ sets a button or buttons in the down state, waits for a period of time,
            then sets them back in the up state. 
            
            Buttons already down when invoked will be in up state when done.
            All other buttons left as is.


            timetopress - Time to wait between states.
                          defaults to 0.2, which seems to reliably be seen by
                          console as keypress
        """

        self.keydown(button)
        time.sleep(timetopress)
        self.keyup(button)
        time.sleep(0.1)
        
if __name__ ==  "__main__":
    
    with Controller(ip=sys.argv[1]) as controller:

        for i in range(10):
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
            controller.buttonpress(Controller.PS, 0.2)
            time.sleep(1)
