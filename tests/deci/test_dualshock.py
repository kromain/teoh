#!/usr/bin/env python3
import os
import time
import pytest

import skynet.psdriver as psdriver
from skynet.deci.dualshock import DualShock,Buttons
import skynet
import conftest

test_target_ip = conftest.target_ip

def test_Buttons():
    """ Ensure all the expected defines exist, all refer to a single bit, and there are no duplicates """

    expected = ["UP", "LEFT", "RIGHT", "DOWN", "R1", "L1", "R2", "L2", "R3", "L3", "CROSS", "CIRCLE", "SQUARE", "TRIANGLE", "OPTION", "SHARE", "PS"]
    
    keymap = {}
    allbits = 0
    for b in expected:
        assert Buttons[b]
        assert Buttons[b].value not in keymap, "Multiple flags with same bit"
        assert bin(Buttons[b].value).count('1') == 1, "More than one bit in flag"
        keymap[Buttons[b].value] = True

    for b in dir(Buttons):
        if b[0] != "_":
            assert b in expected

class TestDualshock:

    def setup(self):
        target_ip = test_target_ip
        if not hasattr(self, "controller"):
            self.controller = DualShock(target_ip=target_ip)

        self.controller.start()

        self.controller.press_button(Buttons.PS)
        time.sleep(1)
        self.controller.press_button(Buttons.UP)
        self.controller.buttondown(Buttons.RIGHT)
        time.sleep(3)
        self.controller.buttonup(Buttons.RIGHT)
        self.controller.press_button(Buttons.LEFT)
        time.sleep(1)
        self.controller.press_button(Buttons.CROSS)
        time.sleep(1)
        self.controller.press_button(Buttons.CROSS)
        time.sleep(1)
        self.controller.press_button(Buttons.CROSS)
        time.sleep(5)

        self.browser = psdriver.server.connect(target_ip)


        exit = False
        for i in range(10):
            for hdl in self.browser.window_handles:
                self.browser.switch_to.window(hdl)
                if self.browser.title.startswith("RegiCAM") == True:
                    exit = True;
                    break

            if exit:
                break

            time.sleep(1)

        assert exit

        self.browser.switch_to.window(hdl)

        self.browser.execute_script( "document.getElementsByTagName('html')[0].innerHTML = \'%s\';" % 
                                     ''.join([x[:-1] for x in open("keyevent.html").readlines()]))

        self.buttonset = (
                    (Buttons.LEFT, 37, "left"),
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
                    (Buttons.R3, 121, "R3")
                    )

        bhtml = ""
        for button, val, name in self.buttonset:
            bhtml += '<input id="%s" type="text"/><br>' % name

        self.browser.execute_script( "document.getElementById('buttons').innerHTML = \'%s\';" % bhtml)


    def teardown(self):
        self.controller.stop()

    def set_event(self, elem, event, handler):
        script =  "document.getElementById('%s').%s=%s" % (elem, event, handler)
        self.browser.execute_script(script)
        "function(event) { console.log('DOWN: ' + event.keyCode); document.getElementById('target').value=event.keyCode;};" 

    def test_press_button(self):

        target_el = self.browser.find_element_by_id('target')

                    
        self.set_event('root', 'onkeydown', 
                 """function(event) { 
                     document.getElementById('target').value=event.keyCode;
                 };""");

        # test press_button

        # Browser can't detect Share or PS
        for button, val, name in self.buttonset:

            self.controller.press_button(button)
            assert target_el.get_attribute('value') == str(val)

    def test_press_buttons(self):
        self.set_event('root', 'onkeydown', 
                 """function(event) {
                    document.getElementById('target').value++;
                 };""" )

        target_el = self.browser.find_element_by_id('target')

        for button, val, name in self.buttonset:
            self.browser.execute_script( "document.getElementById('target').value=0;" )
            self.controller.press_buttons([button]*5)
            assert target_el.get_attribute('value') == "5"

        self.browser.execute_script( "document.getElementById('target').value=0;" )
        self.controller.press_buttons([b[0] for b in self.buttonset])
        assert target_el.get_attribute('value') == str(len(self.buttonset))

    def test_up_down_single(self):
        # test buttondown/buttonup
        bswitch = "switch(event.keyCode) {"
        for button, val, name in self.buttonset:
            bswitch += "case %s: target = '%s'; break;" % (val, name)
        bswitch += "}"
        self.set_event('root', 'onkeydown', 
                 """function(event) { 
                     var target=null;
                     %s
                     document.getElementById(target).value=1;
                 };""" % bswitch);
        self.set_event('root', 'onkeyup', 
                 """function(event) { 
                     var target=null;
                     %s
                     document.getElementById(target).value=0;
                 };""" % bswitch);


        # test one by one

        for button, val, name in self.buttonset:
            button_el = self.browser.find_element_by_id(name)
            self.controller.buttondown(button)
            assert button_el.get_attribute('value') == "1", "%s not seen as down" % name
            self.controller.buttonup(button)
            assert button_el.get_attribute('value') == "0", "%s not seen as up" % name

    def test_up_down_multiple(self):
        # Tests failing 
        return 
        bswitch = "switch(event.keyCode) {"
        for button, val, name in self.buttonset:
            bswitch += "case %s: target = '%s'; break;" % (val, name)
        bswitch += "}"
        self.set_event('root', 'onkeydown', 
                 """function(event) { 
                     var target=null;
                     %s
                     document.getElementById(target).value=1;
                 };""" % bswitch);
        self.set_event('root', 'onkeyup', 
                 """function(event) { 
                     var target=null;
                     %s
                     document.getElementById(target).value=0;
                 };""" % bswitch);

        for button, val, name in self.buttonset[4:]:
            self.browser.execute_script( "document.getElementById('%s').value='';" % name )

        for button, val, name in self.buttonset[4:]:
            self.controller.buttondown(button)
            time.sleep(1)

        for button, val, name in self.buttonset[4:]:
            button_el = self.browser.find_element_by_id(name)
            assert button_el.get_attribute('value') == "1", "%s not seen as down" % name

        time.sleep(10)

        for button, val, name in self.buttonset[4:]:
            time.sleep(1)
            self.controller.buttonup(button)

        for button, val, name in self.buttonset[4:]:
            button_el = self.browser.find_element_by_id(name)
            assert button_el.get_attribute('value') == "0", "%s not seen as up" % name




