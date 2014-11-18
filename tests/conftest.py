#!/usr/bin/env python3
#
# Copyright (c) 2014 Sony Network Entertainment Intl., all rights reserved.

import ipaddress

# DO NOT DELETE - this makes the fixtures available to the tests without having to include them directly in here
from skynet.test.fixtures import *
from tests.util.navigation import *


# DO NOT DELETE - this allows running the tests with py.test directly as an alternative to mantis-run
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
        raise  # just pass the exception over if the ip address is invalid

    # attach the ip to config the same way Mantis does it
    config.target_ip = iparg
