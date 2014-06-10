#!/usr/bin/env python3
#
# Copyright (c) 2014 Sony Network Entertainment Intl., all rights reserved.

# kept in sync with the chromedriver version used as base for psdriver
__version__ = "2.10.267521"

try:
    from selenium import webdriver
except ImportError:
    print("Required module 'selenium' not found! Aborting.")
    sys.exit(-1)

from .psdriver import PSDriverError, connect_to_target, server
