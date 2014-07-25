#!/usr/bin/env python3
#
# Copyright (c) 2014 Sony Network Entertainment Intl., all rights reserved.

import sys

import skynet.deci as deci
import skynet.psdriver as psdriver
import skynet.osk as osk


class PSTarget(object):
    """
    Handles the remote connection to a PlayStation target (DevKit/TestKit).

    The PSTarget class mainly exposes two objects to control the target remotely:

    * :attr:`dualshock`: allows emulating DualShock keys on the target
    * :attr:`psdriver` allows introspecting webviews and executing JavaScript code on the target

    The remote connection to *target_ip* is handled automatically:
    :meth:`connect` is called from the constructor, and :meth:`disconnect` from the destructor.

    You can also use the :class:`PSTarget` class with the 'with' operator, for example::

        with PSTarget("123.123.123.123") as target:
            print("Target WebView URL: " + target.psdriver.current_url)
        # target is automatically disconnected then destroyed at the end of the 'with' block above
        print("bla")

    :param String target_ip: the IP address of the target, e.g. "43.138.12.123"
    :raises PSDriverError: if the connection to *target_ip* fails
    """
    def __init__(self, target_ip):
        self.target_ip = target_ip
        """The remote target IP address

        :type: String
        """
        self.psdriver = None
        """The Webview introspection interface

        :type: :class:`selenium.webdriver.Remote`
        """
        self.dualshock = None
        """The Dualshock emulator interface

        :type: :class:`skynet.deci.dualshock.DualShock`
        """
        self.osk = None
        # self.tty = None
        self.connect()

    def __del__(self):
        self.disconnect()

    def __enter__(self):
        # self.connect() is called in __init__() instead
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()
        # PENDING figure out if exceptions should be suppressed or not
        return False

    def connect(self):
        """
        Connects to the target at the IP address specified in the constructor.

        Does nothing if the target is already connected.

        You normally don't need to call this method explicitely, as it is automatically called by the constructor.
        """
        if self.psdriver is None:
            self.psdriver = psdriver.server.connect(self.target_ip)
        if self.dualshock is None:
            self.dualshock = deci.DualShock(self.target_ip)
            self.dualshock.start()
        if self.osk is None:
            self.osk = osk.OskEntry(self.dualshock)

    def disconnect(self):
        """
        Disconnects from the target at the IP address specified in the constructor.

        Does nothing if the target is already disconnected.

        This method is automatically called when the PSTarget object is GC'd or at the end of a 'with' block,
        but you may still want to call it explicitely to ensure the target connection is released as soon as possible.
        """
        if self.psdriver is not None:
            self.psdriver.quit()
            self.psdriver = None
        if self.dualshock is not None:
            self.dualshock.stop()
            self.dualshock = None
        if self.osk is not None:
            self.osk = None


def main():
    """
    Simple checks, and prints out important words

    :return: zero if Skynet started successfully, non-zero otherwise
    """
    print("[08/29/1997 02:14] Skynet becomes self-aware.")
    print("PSDriver server: {} (pid={})".format(psdriver.server.executable_path(),
                                                psdriver.server.pid()))
    print("PSDriver version: " + psdriver.__version__)
    if len(sys.argv) < 2:
        print("No Target IP address specified, exiting.")
        return 1

    print("Connecting to target at {}...".format(sys.argv[1]))
    with PSTarget(sys.argv[1]) as target:
        print("Target WebView URL: " + target.psdriver.current_url)
    return 0

if __name__ == '__main__':
    sys.exit(main())
