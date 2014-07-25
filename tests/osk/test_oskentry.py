#!/usr/bin/env python3
#
# Copyright (c) 2014 Sony Network Entertainment Intl., all rights reserved.

import unittest

from skynet.deci.dualshock import Buttons as DS
from skynet.osk.osk import OskEntry
from tests.util.PSTestCase import PSTestCase
from selenium import webdriver


class oskTestCase(PSTestCase, unittest.TestCase):
      
      # FIXME temporary hack, we should instead have the devkit IP(s) stored in a config file
      target_ip = "43.138.15.41"

      def test_invalid_string(self):
            """ Basic test for entry_osk """
            ps = self.target.osk
            ds = self.target.dualshock

            self.assertRaises(OskEntry.InvalidString, ps.entry_osk, None, "numeric")
            self.assertRaises(OskEntry.InvalidString, ps.entry_osk, None, "latin_basic")

            text = 123

            self.assertRaises(OskEntry.InvalidString, ps.entry_osk, text, "numeric")
            self.assertRaises(OskEntry.InvalidString, ps.entry_osk, text, "latin_basic")

      def test_invalid_key(self):
            ps = self.target.osk
            ds = self.target.dualshock

            self.assertRaises(OskEntry.InvalidKey, ps.entry_osk, "123 abc", "numeric")
            self.assertRaises(OskEntry.InvalidKey, ps.entry_osk, "áéíóúüñ", "latin_basic")

            self.assertRaises(OskEntry.InvalidKey, ps.entry_osk, "abc123", "numeric")
            self.assertRaises(OskEntry.InvalidKey, ps.entry_osk, "abcáéíóúüñ123", "latin_basic")           

      def test_osk_input(self):
            """ Basic test for entry_osk """
            ps = self.target.osk
            ds = self.target.dualshock

            #Select window
            browser = self.target.psdriver
            browserList = browser.window_handles
            # print(browserList)
            browser.switch_to.window(browserList[-1])
            
            NumText = browser.find_element_by_id("2")
            LatinText = browser.find_element_by_id("3")

            numString = "111111111123"
            latinString = "Skynet Test!"

            NumText.click()
            ds.press_buttons([DS.CROSS], postdelay=.5)
            ps.entry_osk(numString , "numeric")

            LatinText.click()
            ds.press_buttons([DS.CROSS], postdelay=.5)
            ps.entry_osk(latinString , "latin_basic")
            

            assert LatinText.get_attribute('value') == latinString
            assert NumText.get_attribute('value') == numString

            NumText.click()
            ds.press_buttons([DS.CROSS], postdelay=.5)
            for char in list(numString):
                  ds.press_buttons([DS.SQUARE], postdelay=.2)
            ds.press_buttons([DS.R2])

            LatinText.click()
            ds.press_buttons([DS.CROSS], postdelay=.5)
            for char in list(latinString):
                  ds.press_buttons([DS.SQUARE], postdelay=.2)
            ds.press_buttons([DS.R2])


if __name__ == '__main__':
    unittest.main()