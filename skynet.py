#!/usr/bin/env python3
#
# Copyright (c) 2014 Sony Network Entertainment Intl., all rights reserved.

# FIXME make deci a proper module
#import deci
import psdriver
import sys

def main():
    print("[08/29/1997 02:14] Skynet becomes self-aware.")
    psd = psdriver.connectToTarget('43.138.15.55')
    psd.quit()
    return 0

if __name__ == '__main__':
    sys.exit(main())
