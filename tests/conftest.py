#!/usr/bin/env python3
#
# Copyright (c) 2014 Sony Network Entertainment Intl., all rights reserved.

import ipaddress
import os

# Don't remove! this makes the fixtures available to the tests without having to include them directly in here
from tests.util.navigation import pstarget, regicam_webview
from skynet.test.fixtures import *

# PENDING this global var can be removed when all tests have been migrated to SkynetTestCase
# global var
target_ip = os.getenv("SKYNET_TARGET_IP", "")

def pytest_addoption(parser):
    if not parser._anonymous.options:
        parser.addoption("--ip", action="store", required=True)

def pytest_configure(config):
    # Don't extract the --ip argument if we're running through Mantis, it's extracted in the plugin instead
    if any([plugin in config.option.plugins for plugin in ["mantis.plugin_master", "mantis.plugin_slave"]]):
        return

    # guaranteed to contain at least one entry, since the argument is marked as required above
    iparg = config.getoption("--ip")
    try:
        ipaddress.ip_address(iparg)
    except ValueError:
        raise # just pass the exception over if the ip address is invalid

    # PENDING this global var can be removed when all tests have been migrated to SkynetTestCase
    global target_ip
    target_ip = iparg
