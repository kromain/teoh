#!/usr/bin/env python3
#
# Copyright (c) 2014 Sony Network Entertainment Intl., all rights reserved.

import sys

import psdriver
from deci import DualShock

class PSTarget(object):
    def __init__(self, target_ip):
        self.target_ip = target_ip
        self.psdriver = None
        self.dualshock = None
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
        if self.psdriver is None:
            self.psdriver = psdriver.server.connect(self.target_ip)
        if self.dualshock is None:
            self.dualshock = DualShock(self.target_ip)
            self.dualshock.start()

    def disconnect(self):
        if self.psdriver is not None:
            self.psdriver.quit()
            self.psdriver = None
        if self.dualshock is not None:
            self.dualshock.stop()
            self.dualshock = None

def main():
    print("[08/29/1997 02:14] Skynet becomes self-aware.")
    print("PSDriver server: {} (pid={})".format(psdriver.server.executable_path(),
                                                psdriver.server.pid()))
    print("PSDriver version: " + psdriver.__version__)
    if len(sys.argv) < 2:
        print("No Target IP address specified, exiting.")
        return 1

    print("Connecting to target at {}...".format(sys.argv[1]))
    with PSTarget('43.138.15.55') as target:
        print("URL: " + target.psdriver.current_url)
        target.dualshock.buttonpress(DualShock.DOWN)
        target.dualshock.buttonpress(DualShock.DOWN)
        target.dualshock.buttonpress(DualShock.CIRCLE)
    return 0

if __name__ == '__main__':
    sys.exit(main())
