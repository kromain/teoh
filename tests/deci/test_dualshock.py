#!/usr/bin/env python3
#
# Copyright (c) 2014 Sony Network Entertainment Intl., all rights reserved.

import os
import time
import unittest

import skynet.psdriver as psdriver
from skynet.deci.dualshock import DualShock, Buttons
from tests.util.navigation import Navigation

import conftest
test_target_ip = conftest.target_ip


def test_buttons_enum():
    """ Ensure all the expected defines exist, all refer to a single bit, and there are no duplicates """

    expected = ["UP", "LEFT", "RIGHT", "DOWN", "R1", "L1", "R2", "L2", "R3", "L3",
                "CROSS", "CIRCLE", "SQUARE", "TRIANGLE", "OPTION", "SHARE", "PS"]
    
    keymap = {}
    for b in expected:
        assert Buttons[b]
        assert Buttons[b].value not in keymap, "Multiple flags with same bit"
        assert bin(Buttons[b].value).count('1') == 1, "More than one bit in flag"
        keymap[Buttons[b].value] = True

    for b in dir(Buttons):
        if b[0] != "_":
            assert b in expected


class TestDualshock(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.controller = DualShock(test_target_ip)
        cls.controller.start()

        cls.browser = psdriver.server.connect(test_target_ip)

        assert Navigation(cls.controller, cls.browser).go_to_account_mgmt()

        testfile = os.path.join(os.path.dirname(os.path.realpath(__file__)), "keyevent.html")
        html = ''.join([x[:-1] for x in open(testfile).readlines()])

        cls.browser.execute_script("document.getElementsByTagName('html')[0].innerHTML = \'%s\';" % html)

        cls.buttonset = ((Buttons.LEFT, 37, "left"),
                         (Buttons.UP, 38, "up"),
                         (Buttons.RIGHT, 39, "right"),
                         (Buttons.DOWN, 40, "down"),
                         (Buttons.CROSS, 13, "cross"),
                         (Buttons.CIRCLE, 27, "circle"),
                         (Buttons.TRIANGLE, 112, "triangle"),
                         (Buttons.SQUARE, 113, "square"),
                         (Buttons.OPTION, 114, "option"),
                         (Buttons.L1, 116, "L1"),
                         (Buttons.R1, 117, "R1"),
                         (Buttons.L2, 118, "L2"),
                         (Buttons.R2, 119, "R2"),
                         (Buttons.L3, 120, "L3"),
                         (Buttons.R3, 121, "R3"))

        bhtml = ""
        for button, val, name in cls.buttonset:
            bhtml += '<input id="%s" type="text"/><br>' % name

        cls.browser.execute_script("document.getElementById('buttons').innerHTML = \'%s\';" % bhtml)

    @classmethod
    def tearDownClass(cls):
        Navigation(cls.controller, cls.browser).return_to_whats_new()

        cls.browser.quit()
        cls.controller.stop()

    def _set_event(self, elem, event, handler):
        script = "document.getElementById('%s').%s=%s" % (elem, event, handler)
        self.browser.execute_script(script)

    def test_press_button(self):
        self._set_event('root', 'onkeydown',
                        """function(event) { document.getElementById('target').value=event.keyCode; };""")

        # Browser can't detect Share or PS
        target_el = self.browser.find_element_by_id('target')
        for button, val, name in self.buttonset:
            self.controller.press_button(button)
            assert target_el.get_attribute('value') == str(val)

    def test_press_buttons(self):
        self._set_event('root', 'onkeydown',
                        """function(event) { document.getElementById('target').value++; };""")

        target_el = self.browser.find_element_by_id('target')
        for button, val, name in self.buttonset:
            self.browser.execute_script("document.getElementById('target').value=0;")
            self.controller.press_buttons([button]*5)
            assert target_el.get_attribute('value') == "5"

        self.browser.execute_script("document.getElementById('target').value=0;")
        self.controller.press_buttons([b[0] for b in self.buttonset])
        assert target_el.get_attribute('value') == str(len(self.buttonset))

    @unittest.skip
    def test_up_down_single(self):
        bswitch = "switch(event.keyCode) {"
        for button, val, name in self.buttonset:
            bswitch += "case %s: target = '%s'; break;" % (val, name)
        bswitch += "}"
        self._set_event('root', 'onkeydown',
                        """function(event) {
                            var target=null;
                            %s
                            document.getElementById(target).value++;
                        };""" % bswitch)

        for button, val, name in self.buttonset:
            self.browser.execute_script("document.getElementById('%s').value=0;" % name)
            button_el = self.browser.find_element_by_id(name)
            self.controller.buttondown(button)
            assert int(button_el.get_attribute('value')) == 1, "%s not seen as down" % name
            time.sleep(1) # wait for auto-repeat to kick in
            assert int(button_el.get_attribute('value')) > 1, "%s not triggering auto-repeat" % name
            self.controller.buttonup(button)
            lastvalue = int(button_el.get_attribute('value'))
            time.sleep(0.1) # make sure auto-repeat is off
            assert int(button_el.get_attribute('value')) == lastvalue, "%s not seen as up" % name

    @unittest.skip
    def test_up_down_multiple(self):
        # We need to rework this test using a different approach, since the webview doesn't send onkeyup events
        # test multiple buttondown/buttonup at the same time
        bswitch = "switch(event.keyCode) {"
        for button, val, name in self.buttonset:
            bswitch += "case %s: target = '%s'; break;" % (val, name)
        bswitch += "}"
        self._set_event('root', 'onkeydown',
                        """function(event) {
                            var target=null;
                            %s
                            document.getElementById(target).value++;
                        };""" % bswitch)

        for button, val, name in self.buttonset[4:]:
            self.browser.execute_script("document.getElementById('%s').value=0;" % name)
            self.controller.buttondown(button)

        buttonvalues = {}

        for button, val, name in self.buttonset[4:]:
            button_el = self.browser.find_element_by_id(name)
            value = int(button_el.get_attribute('value'))
            assert value >=1, "%s not seen as down" % name
            buttonvalues[name] = value

        time.sleep(1)

        for button, val, name in self.buttonset[4:]:
            button_el = self.browser.find_element_by_id(name)
            value = int(button_el.get_attribute('value'))
            assert value > buttonvalues[name], "%s not triggering auto-repeat" % name
            buttonvalues[name] = value
            self.controller.buttonup(button)

        time.sleep(0.1)

        for button, val, name in self.buttonset[4:]:
            button_el = self.browser.find_element_by_id(name)
            value = int(button_el.get_attribute('value'))
            assert value == buttonvalues[name], "%s not seen as up" % name
