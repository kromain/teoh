#!/usr/bin/env python3
#
# Copyright (c) 2014 Sony Network Entertainment Intl., all rights reserved.

import unittest
import string

from skynet.deci.dualshock import Buttons as DS
from skynet.osk.osk import OskEntry

from skynet.lib.util.PSTestCase import PSTestCase


class oskTestCase(PSTestCase):
      # FIXME temporary hack, we should instead have the devkit IP(s) stored in a config file

      target_ip = "43.138.14.112"

      def test_osk_input(self):
            """ Basic test for entry_osk """
            ps = self.target.osk
            ps.entry_osk(" Testing Testing " , "latin_basic")
            browser = self.target.psdriver
            ds = self.target.dualshock

            #titleInfo = browser.find_elements_by_xpath("text")
            #titleInfoLabel = titleInfo.find_element_by_class_name('title')
            #print(titleInfo)

if __name__ == '__main__':
    unittest.main()