#!/usr/bin/env python3
#
# Copyright (c) 2014 Sony Network Entertainment Intl., all rights reserved.

import unittest

import skynet

class PSTestCase(unittest.TestCase):
    def setUp(self):
        self.target = skynet.PSTarget(self.__class__.target_ip)
        self.target.psdriver.implicitly_wait(30)

    def tearDown(self):
        self.target.disconnect()