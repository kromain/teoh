#!/usr/bin/env python3
#
# Copyright (c) 2014 Sony Network Entertainment Intl., all rights reserved.

import unittest
import sys
import pytest
import time

from skynet.deci.dualshock import Buttons as DS
from skynet.osk.osk import OskEntry
from tests.util.PSTestCase import PSTestCase
from selenium import webdriver
from tests.osk.osk_setup import test_set_up

class oskTestCase(PSTestCase):

      test_set_up()

      def test_osk_input(self):

            """ Basic test for entry_osk """
            ps = self.target.osk
            ds = self.target.dualshock


            browser = self.target.psdriver

            exit = False
            while not exit:
                for hdl in browser.window_handles:
                    browser.switch_to.window(hdl)
                    if browser.title[:14] == "https://regcam":
                        exit = True;
                        break

            browser.switch_to.window(hdl)

            Text = browser.find_element_by_id("1")
            Num = browser.find_element_by_id("2")
            Latin = browser.find_element_by_id("3")
            De = browser.find_element_by_id("4")
            En = browser.find_element_by_id("5")
            Pass = browser.find_element_by_id("11")
            Email = browser.find_element_by_id("12")


            text = "Test default text"
            num = "1234567890"
            latin = "Text basic-latin"
            de = "Text test with locale: de"
            en = "Text test with locale: en"
            password = "Test default password"
            email = "Test default email"

            Text.click()
            ds.press_button(DS.CROSS, timetorelease=2.0)           
            ps.entry_osk(text , "text", "en_")

            Num.click()
            ds.press_button(DS.CROSS, timetorelease=2.0)           
            ps.entry_osk(num , "numeric")

            Latin.click()
            ds.press_button(DS.CROSS, timetorelease=2.0)           
            ps.entry_osk(latin , "latin_basic", "en_us")

            De.click()
            ds.press_button(DS.CROSS, timetorelease=2.0)           
            ps.entry_osk(de , "text", "de_")

            En.click()
            ds.press_button(DS.CROSS, timetorelease=2.0)           
            ps.entry_osk(en , "text", "en_us")

            Pass.click()
            ds.press_button(DS.CROSS, timetorelease=2.0)           
            ps.entry_osk(password , "password", "en_")

            Email.click()
            ds.press_button(DS.CROSS, timetorelease=2.0)           
            ps.entry_osk(email , "email", "en_")
            
            assert Text.get_attribute('value') == text
            assert Num.get_attribute('value') == num
            assert Latin.get_attribute('value') == latin
            assert De.get_attribute('value') == de
            assert En.get_attribute('value') == en
            assert Pass.get_attribute('value') == password
            assert Email.get_attribute('value') == email    
