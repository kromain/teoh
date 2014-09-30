#!/usr/bin/env python3
#
# Copyright (c) 2014 Sony Network Entertainment Intl., all rights reserved.

import os

from skynet.deci.dualshock import Buttons as DS
from tests.util.navigation import Navigation
from tests.util.PSTestCase import PSTestCase


class OskEntryTestCase(PSTestCase):
    def setUp(self):
        assert Navigation(self.target.dualshock, self.target.psdriver).go_to_account_mgmt()

        # Replace the regicam app with the test page
        testfile = os.path.join(os.path.dirname(os.path.realpath(__file__)), "keyevent.html")
        html = ''.join([x[:-1] for x in open(testfile).readlines()])
        self.target.psdriver.execute_script("document.getElementsByTagName('html')[0].innerHTML = \'%s\';" % html)

    def tearDown(self):
        Navigation(self.target.dualshock, self.target.psdriver).return_to_whats_new()

    def test_osk_input(self):
        """ Basic test for entry_osk """
        ps = self.target.osk
        ds = self.target.dualshock
        browser = self.target.psdriver

        en_basic = browser.find_element_by_id("1")
        en_text = browser.find_element_by_id("2")
        en_email = browser.find_element_by_id("11")
        en_password = browser.find_element_by_id("12")
        en_numeric = browser.find_element_by_id("13")
        de_basic = browser.find_element_by_id("3")
        de_text = browser.find_element_by_id("4")
        ru_basic = browser.find_element_by_id("5")
        ru_text = browser.find_element_by_id("6")
        ja_basic = browser.find_element_by_id("7")
        ja_text = browser.find_element_by_id("8")
        es_basic = browser.find_element_by_id("9")
        es_text = browser.find_element_by_id("10")

        text1 = "Default BASIC test"
        text2 = "Default TEXT test"
        text11 = "name@email.com"
        text12 = "password123"
        text13 = "5105553854"
        text3 = "Wie geht's dir/ Ihnen?"
        text4 = "Wie geht's dir/ Ihnen?"
        text5 = "Kak pazhivayesh?"
        text6 = "Как поживаешь?"
        text7 = "Ogenki desuka?"
        text8 = "こんばんは。おですか？"
        text9 = "Mucho gusto Encantado"
        text10 = "Cómo está usted?"

        en_basic.click()
        ds.press_button(DS.CROSS, timetorelease=1)
        ps.entry_osk(text1, "latin_basic", "en_")
        assert en_basic.get_attribute('value') == text1

        en_text.click()
        ds.press_button(DS.CROSS, timetorelease=1)
        ps.entry_osk(text2, "text", "en_")
        assert en_text.get_attribute('value') == text2

        en_email.click()
        ds.press_button(DS.CROSS, timetorelease=1)
        ps.entry_osk(text11, "email", "en_")
        assert en_email.get_attribute('value') == text11

        en_password.click()
        ds.press_button(DS.CROSS, timetorelease=1)
        ps.entry_osk(text12, "password", "en_")
        assert en_password.get_attribute('value') == text12

        en_numeric.click()
        ds.press_button(DS.CROSS, timetorelease=1)
        ps.entry_osk(text13, "numeric")
        assert en_numeric.get_attribute('value') == text13

        de_basic.click()
        ds.press_button(DS.CROSS, timetorelease=1)
        ps.entry_osk(text3, "latin_basic", "de_")
        assert de_basic.get_attribute('value') == text3

        de_text.click()
        ds.press_button(DS.CROSS, timetorelease=1)
        ps.entry_osk(text4, "text", "de_")
        assert de_text.get_attribute('value') == text4

        ru_basic.click()
        ds.press_button(DS.CROSS, timetorelease=1)
        ps.entry_osk(text5, "latin_basic", "ru_")
        assert ru_basic.get_attribute('value') == text5

        ru_text.click()
        ds.press_button(DS.CROSS, timetorelease=1)
        ps.entry_osk(text6, "text", "ru_")
        assert ru_text.get_attribute('value') == text6

        ja_basic.click()
        ds.press_button(DS.CROSS, timetorelease=1)
        ps.entry_osk(text7, "latin_basic", "ja_")
        assert ja_basic.get_attribute('value') == text7

        ja_text.click()
        ds.press_button(DS.CROSS, timetorelease=1)
        ps.entry_osk(text8, "text", "ja_")
        assert ja_text.get_attribute('value') == text8

        es_basic.click()
        ds.press_button(DS.CROSS, timetorelease=1)
        ps.entry_osk(text9, "latin_basic", "es_")
        assert es_basic.get_attribute('value') == text9

        es_text.click()
        ds.press_button(DS.CROSS, timetorelease=1)
        ps.entry_osk(text10, "text", "es_")
        assert es_text.get_attribute('value') == text10
