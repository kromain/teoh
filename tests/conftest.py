#!/usr/bin/env python3
#
# Copyright (c) 2014 Sony Network Entertainment Intl., all rights reserved.

import os
import re

from tests.util.navigation import pstarget, regicam_webview

# global var: target Target IP
target_ip = os.getenv("SKYNET_TARGET_IP", "")
all_target_ips = [target_ip]

def safe_target_ip():
    if target_ip:
        return  target_ip
    raise PytestOptionException("Target IP Address Not Configured! Please Use\"--ip=1.2.3.4\" to set Target IP!")


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
    global all_target_ips

    ip_matching = [opt for opt in args if "--ip" in opt]
    if  not ip_matching:
        return

    all_target_ips.clear()
    # ipv4 format ***.***.***.***
    p = re.compile('^--ip=(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$)')
    for ip_opt in ip_matching:
        ip_matched = p.match(ip_opt)
        if (ip_matched == None):
            raise  PytestOptionException( "Target IP Address is invalid!")
        # target_ip only matches one --ip option, but default the last one
        target_ip = ip_matched.groups()[0]
        all_target_ips.append(target_ip)

