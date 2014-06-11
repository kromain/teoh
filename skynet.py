#!/usr/bin/env python3
#
# Copyright (c) 2014 Sony Network Entertainment Intl., all rights reserved.

# FIXME make deci a proper module
#import deci
import psdriver
import sys

def main():
    print("[08/29/1997 02:14] Skynet becomes self-aware.")
    print("PSDriver server: {} (pid={})".format(psdriver.server.executable_path(),
                                                psdriver.server.pid()))
    print("PSDriver version: " + psdriver.__version__)
    if len(sys.argv) < 2:
        print("No Target IP address specified, exiting.")
        return 1

    print("Connecting to target at {}...".format(sys.argv[1]))
    psd = psdriver.server.connect(sys.argv[1])
    psd.quit()
    return 0

if __name__ == '__main__':
    sys.exit(main())
