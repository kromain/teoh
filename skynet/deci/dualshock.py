import sys
import threading
import time
from enum import IntEnum

from .deci4 import NetmpManager, Netmp


class Buttons(IntEnum):
    """
    Represents the DualShock4 buttons.

    Used by the :class:`Dualshock` methods, for example :meth:`pressbutton`
    """
    UP = 0x10  #:
    LEFT = 0x80  #:
    RIGHT = 0x20  #:
    DOWN = 0x40  #:
    R1 = 0x800  #:
    L1 = 0x400  #:
    R2 = 0x200  #:
    L2 = 0x100  #:
    R3 = 0x00000004 #:
    L3 = 0x00000002 #:
    CROSS = 0x4000  #:
    CIRCLE = 0x2000  #:
    SQUARE = 0x8000  #:
    TRIANGLE = 0x1000  #:
    OPTION = 0x8  #:
    SHARE = 0x1  #:
    PS = 0x10000  #:


class DualShock(NetmpManager):
    """
    The interface to a DualShock controller on the target.

    This class emulates a DualShock controller connected to the remote target, and is able to send key presses
    in a way that is identical to a real controller. It is therefore not limited to sending input on a webview,
    instead this can be used to control the UI as a whole, including logging in and out, accessing settings, etc.

    You can also use the :class:`DualShock` class with the 'with' operator.
    In this case the connection is automatically handled at the scope level, for example::

        with DualShock("123.123.123.123") as controller:
            # controller is automatically connected to the target at 123.123.123.123 here
            controller.buttonpress(Buttons.CROSS)
        # controller is automatically disconnected then destroyed at the end of the 'with' block above
        print("bla")

    :param String target_ip: the IP address of the target, e.g. "43.138.12.123"
    """

    class _KeyThread(threading.Thread):
        """ Thread that sends the current button state to the device once every 10 msecs. """

        def run(self):

            self.buttonstate = 0x0
            self.stop = False

            while not self.stop:
                self.ctrlp.play_data([self.buttonstate] * 8)
                time.sleep(0.1)

    def __init__(self, target_ip, force=False):
        self.target_ip = target_ip
        self.force = force
        """The remote target IP address

        :type: String
        """

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, type, value, traceback):
        self.stop()

    def start(self):
        """
        Connect to the remote target and prepare to send events

        :TODO: Add exception handling for connection errors and such
        """

        self.netmp = super(DualShock, self).startnetmp(self.target_ip)

        try:
            self.ctrlp = self.netmp.register_ctrlp()
        except Netmp.InUseException:

            if self.force:
                print("Device in use, forcing disconnection");
                self.netmp.force_disconnect()

                self.ctrlp = self.netmp.register_ctrlp()
            else:
                raise

        self.ctrlp.play_start()

        self.thread = self._KeyThread()
        self.thread.ctrlp = self.ctrlp

        self.thread.ready = False
        self.thread.start()

        time.sleep(0.1)

    def stop(self):
        """
        Disconnect from the remote target
        """
        self.thread.stop = True
        self.thread.join()

        self.ctrlp.play_stop()

        self.netmp.unregister_ctrlp()

        self.netmp = super(DualShock, self).stopnetmp(self.target_ip)

    def buttondown(self, button):
        """
        Set *button* in the 'pressed' state, leaving other buttons as-is.

        :param button: The button to set in pressed state
        :type button: :class:`Buttons`
        """
        self.thread.buttonstate |= button

    def buttonup(self, button):
        """
        Set *button* in the 'released' state, leaving other buttons as-is.

        :param button: The button to set in released state
        :type button: :class:`Buttons`
        """
        self.thread.buttonstate &= ~button

    def buttonpress(self, button, timetopress=0.2, timetorelease=0.2):
        print(" Deprecated: please use buttonpress " )
        self.press_button(button, timetopress, timetorelease)

    def press_button(self, button, timetopress=0.2, timetorelease=0.2):
        """
        Simulate a button press (click) by setting *button* in the 'pressed' state for
        *timetopress* seconds, then back to the 'released' state for *timetorelease* seconds.
            
        Buttons already in 'pressed' state when invoked will be switched to 'released' state when done.
        All other buttons are left as-is.

        Note that if there are two calls for the same button without a non-zero *timetorelease*,
        the console will see only one event

        :param button: The button to press (click)
        :type button: :class:`Buttons`
        :param float timetopress: Time to keep the button in 'pressed' state, by default 200ms
        :param float timetorelease: Time to keep the button in 'released' state, by default 200ms
        """

        self.buttondown(button)
        time.sleep(timetopress)
        self.buttonup(button)
        time.sleep(timetorelease)

    def press_buttons(self, buttonlist, timetopress=0.2, timetorelease=0.2):
        """
        Simulate a series of button presses by iterating through *buttonList*

        Starting with the first button in the list, each button is set in the 'pressed' state for *timetopress* seconds
        before reverting it back to the 'released' state, then waiting for *post_delay* seconds before
        processing the next button in the list.

        Buttons already in 'pressed' state when invoked will be switched to 'released' state when done.
        All other buttons are left as-is.

        :param buttonlist: The list of buttons to press (click)
        :type buttonlist: [:class:`Buttons`]
        :param float timetopress: Time to keep the button in 'pressed' state, by default 200ms
        :param float timetorelease: Time to wait between two instances of the same button, by default 200ms.  Also used after all buttons pressed.  Only used if timetodelay is 0.
        """
        lastbutton = 0
        for x in buttonlist:

            if x == lastbutton:
                time.sleep(timetorelease)
            else:
                lastbutton = x

            self.press_button(x, timetopress, 0)

            time.sleep(timetorelease)

        
