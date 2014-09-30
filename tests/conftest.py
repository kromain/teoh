#!/usr/bin/env python3
#
# Copyright (c) 2014 Sony Network Entertainment Intl., all rights reserved.

import pytest
import re

from tests.util.navigation import pstarget, regicam_webview

# global var: target Target IP
target_ip=""

class PytestOptionException(Exception):
    def __init__(self, err_msg):
        self.err_msg = str(err_msg)
    def __str__(self):
        return repr(self.err_msg)
        
def pytest_addoption(parser):
    parser.addoption("--ip", action="store" )
    
def pytest_cmdline_preparse(args):
    '''
    The function aa=request.config.getoption("--ip") does not work properly
    So change to parse all argv
    Recognize option "--ip=***.***.***.***" and return valid IP
    :return:  Target IP (target_ip)
    :rtype:   String
    :raises:  PytestOptionException: no input option --IP
    :raises:  PytestOptionException: invalid IP address
    '''
    global target_ip
    # ipv4 format ***.***.***.***
    p = re.compile('^--ip=(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$)')
    ip_matching = [opt for opt in args if "--ip" in opt]
    if (len(ip_matching)<1):
        raise  PytestOptionException( "Target IP Address Not Configured!\
                            Please Use\"--ip=1.2.3.4\" to set Target IP!")
 
    # No matter how many "--ip=" options recognized
    # Just get the first the First one
    ip_opt = str(ip_matching[0])
    ip_matched = p.match(ip_opt)
    if (ip_matched == None):
        raise  PytestOptionException( "Target IP Address is invalid!")
    target_ip = ip_matched.groups()[0]
    return target_ip
