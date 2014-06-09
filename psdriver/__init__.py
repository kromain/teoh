#!/usr/bin/env python3
#
# Copyright (c) 2014 Sony Network Entertainment Intl., all rights reserved.

import sys

try:
    from selenium import webdriver
except ImportError:
    print("Required module 'selenium' not found! Exiting.")
    sys.exit(-1)

class PSDriverServer(object):
    def __init__(self, server_port, server_ip):
        self.server_ip = server_ip
        self.server_port = server_port
        # TODO detect if psdriver.exe is running and start it if needed

    def connect(self, target_ip, target_port):
        chromeDriverOptions = {'debuggerAddress': "{}:{}".format(target_ip, target_port)}
        capabilities = webdriver.DesiredCapabilities.CHROME.copy()
        capabilities['chromeOptions'] = chromeDriverOptions

        # may throw a WebDriverException if connection fails
        driver = webdriver.Remote("http://{}:{}".format(self.server_ip, self.server_port), capabilities)
        # connection was successful, update target_ip and target_port
        self.target_ip = target_ip
        self.target_port = target_port

        return driver

server = PSDriverServer(9515, '127.0.0.1')

def connect(target_ip, target_port=860):
    return server.connect(target_ip, target_port)
