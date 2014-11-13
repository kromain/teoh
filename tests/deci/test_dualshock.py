#!/usr/bin/env python3
#
# Copyright (c) 2014 Sony Network Entertainment Intl., all rights reserved.

import os
import time
import pytest

from skynet.deci import Buttons


def _set_event(browser, elem, event, handler):
    browser.execute_script("document.getElementById('%s').%s=%s" % (elem, event, handler))


@pytest.fixture(scope="module")
def dualshock_test_setup(regicam_webview):
    # Replace the regicam app with the test page
    testfile = os.path.join(os.path.dirname(os.path.realpath(__file__)), "keyevent.html")
    html = ''.join([x[:-1] for x in open(testfile).readlines()])
    regicam_webview.webview.execute_script("document.getElementsByTagName('html')[0].innerHTML = \'%s\';" % html)

    bhtml = ""
    buttonset = (
                 (Buttons.UP, 38, "up"),
                 (Buttons.RIGHT, 39, "right"),
                 (Buttons.DOWN, 40, "down"),
                 (Buttons.CROSS, 13, "cross"),
                 (Buttons.CIRCLE, 27, "circle"),
                 (Buttons.TRIANGLE, 112, "triangle"),
                 (Buttons.LEFT, 37, "left"),
                 (Buttons.SQUARE, 113, "square"),
                 (Buttons.OPTION, 114, "option"),
                 (Buttons.L1, 116, "L1"),
                 (Buttons.R1, 117, "R1"),
                 (Buttons.L2, 118, "L2"),
                 (Buttons.R2, 119, "R2"),
                 (Buttons.L3, 120, "L3"),
                 (Buttons.R3, 121, "R3"))
    for button, val, name in buttonset:
        bhtml += '<input id="%s" type="text"/><br>' % name
    regicam_webview.webview.execute_script("document.getElementById('buttons').innerHTML = \'%s\';" % bhtml)

    class TestContext:
        def __init__(self, _pstarget, _buttonset):
            self.pstarget = _pstarget
            self.buttonset = _buttonset
    return TestContext(regicam_webview, buttonset)


def test_press_button(dualshock_test_setup):
    browser = dualshock_test_setup.pstarget.webview
    ds = dualshock_test_setup.pstarget.dualshock
    buttonset = dualshock_test_setup.buttonset

    _set_event(browser, 'root', 'onkeydown',
               """function(event) { document.getElementById('target').value=event.keyCode; };""")

    # Browser can't detect Share or PS
    target_el = browser.find_element_by_id('target')
    for button, val, name in buttonset:
        ds.press_button(button)
        assert target_el.get_attribute('value') == str(val)


def test_press_buttons(dualshock_test_setup):
    browser = dualshock_test_setup.pstarget.webview
    ds = dualshock_test_setup.pstarget.dualshock
    buttonset = dualshock_test_setup.buttonset

    _set_event(browser, 'root', 'onkeydown',
               """function(event) { document.getElementById('target').value++; };""")

    target_el = browser.find_element_by_id('target')
    for button, val, name in buttonset:
        browser.execute_script("document.getElementById('target').value=0;")
        ds.press_buttons([button]*5)
        assert target_el.get_attribute('value') == "5"

    browser.execute_script("document.getElementById('target').value=0;")
    ds.press_buttons([b[0] for b in buttonset])
    assert target_el.get_attribute('value') == str(len(buttonset))


def test_up_down_single(dualshock_test_setup):
    """ Test buttondown/buttonup for each single button at a time """
    browser = dualshock_test_setup.pstarget.webview
    ds = dualshock_test_setup.pstarget.dualshock
    buttonset = dualshock_test_setup.buttonset

    bswitch = "switch(event.keyCode) {"
    for button, val, name in buttonset:
        bswitch += "case %s: target = '%s'; break;" % (val, name)
    bswitch += "}"
    _set_event(browser, 'root', 'onkeydown',
               """function(event) {
                   var target=null;
                   %s
                   document.getElementById(target).value++;
               };""" % bswitch)

    for button, val, name in buttonset:
        browser.execute_script("document.getElementById('%s').value=0;" % name)
        button_el = browser.find_element_by_id(name)
        ds.buttondown(button)
        time.sleep(1)  # wait for auto-repeat to kick in
        assert int(button_el.get_attribute('value')) > 1, "%s not seen as down" % name
        ds.buttonup(button)
        time.sleep(0.1)  # make sure auto-repeat is off
        lastvalue = int(button_el.get_attribute('value'))
        time.sleep(1)
        assert int(button_el.get_attribute('value')) == lastvalue, "%s not seen as up" % name


def test_up_down_multiple(dualshock_test_setup):
    """ Test buttondown/buttonup for CROSS/CIRCLE/TRIANGLE/SQUARE at the same time """
    browser = dualshock_test_setup.pstarget.webview
    ds = dualshock_test_setup.pstarget.dualshock
    buttonset = dualshock_test_setup.buttonset

    bswitch = "switch(event.keyCode) {"
    for button, val, name in buttonset:
        bswitch += "case %s: target = '%s'; break;" % (val, name)
    bswitch += "}"
    _set_event(browser, 'root', 'onkeydown',
               """function(event) {
                   var target=null;
                   %s
                   document.getElementById(target).value++;
               };""" % bswitch)

    for button, val, name in buttonset[4:8]:
        browser.execute_script("document.getElementById('%s').value=0;" % name)
        ds.buttondown(button)

    buttonvalues = {}

    for button, val, name in buttonset[4:8]:
        button_el = browser.find_element_by_id(name)
        value = int(button_el.get_attribute('value'))
        assert value > 1, "%s not seen as down" % name
        ds.buttonup(button)
        time.sleep(0.2)  # make sure auto-repeat is off
        buttonvalues[name] = int(button_el.get_attribute('value'))

    time.sleep(1)

    for button, val, name in buttonset[4:8]:
        button_el = browser.find_element_by_id(name)
        value = int(button_el.get_attribute('value'))
        assert value == buttonvalues[name]


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
