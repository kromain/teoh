#!/usr/bin/env python3
#
# Copyright (c) 2014 Sony Network Entertainment Intl., all rights reserved.

import unittest
import skynet
import conftest
 
class PSTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        #get target IP from pytest's conftest
        self.target_ip = conftest.target_ip
        self.target = skynet.PSTarget(self.target_ip)
        self.target.psdriver.implicitly_wait(30)
    @classmethod
    def tearDownClass(self):
        self.target.disconnect()
