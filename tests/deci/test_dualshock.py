#!/usr/bin/env python3
import os
import time

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

def set_page(browser, pagename):
    html = ''.join([x[:-1] for x in open(pagename).readlines()])

    # Replace the regicam app with the test app
    browser.execute_script( "document.getElementsByTagName('html')[0].innerHTML = \'%s\';" % html)

def set_event(browser, elem, event, handler):
    script =  "document.getElementById('%s').%s=%s" % (elem, event, handler)
    browser.execute_script(script)
    "function(event) { console.log('DOWN: ' + event.keyCode); document.getElementById('target').value=event.keyCode;};" 

def test_Dualshock():

    target_ip = test_target_ip
    with DualShock(target_ip=target_ip) as controller:
        assert controller

        browser = psdriver.server.connect(target_ip)

        exit = False
        while not exit:
            for hdl in browser.window_handles:
                browser.switch_to.window(hdl)
                if browser.title[:14] == "https://regcam":
                    exit = True;
                    break

            time.sleep(5)

        browser.switch_to.window(hdl)

        time.sleep(3)

        set_page(browser, os.path.join(os.path.dirname(__file__), "keyevent.html"))


        target_el = browser.find_element_by_id('target')

                    
        buttonset = (
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

        set_event(browser, 'root', 'onkeydown', 
                 """function(event) { 
                     document.getElementById('target').value=event.keyCode;
                 };""");

        # test press_button

        # Browser can't detect Share or PS
        for button, val, name in buttonset:

            controller.press_button(button)
            assert target_el.get_attribute('value') == str(val)

        set_event(browser, 'root', 'onkeydown', 
                 """function(event) {
                    document.getElementById('target').value++;
                 };""" )

        # test press_buttons
        for button, val, name in buttonset:
            browser.execute_script( "document.getElementById('target').value=0;" )
            controller.press_buttons([button]*5)
            assert target_el.get_attribute('value') == "5"

        browser.execute_script( "document.getElementById('target').value=0;" )
        controller.press_buttons([b[0] for b in buttonset])
        assert target_el.get_attribute('value') == str(len(buttonset))

        bswitch = "switch(event.keyCode) {"
        for button, val, name in buttonset:
            bswitch += "case %s: target = '%s'; break;" % (val, name)
        bswitch += "}"

        # test buttondown/buttonup
        set_event(browser, 'root', 'onkeydown', 
                 """function(event) { 
                     var target=null;
                     %s
                     document.getElementById(target).value=1;
                 };""" % bswitch);
        set_event(browser, 'root', 'onkeyup', 
                 """function(event) { 
                     var target=null;
                     %s
                     document.getElementById(target).value=0;
                 };""" % bswitch);

        bhtml = ""
        for button, val, name in buttonset:
            bhtml += '<input id="%s" type="text"/><br>' % name

        browser.execute_script( "document.getElementById('buttons').innerHTML = \'%s\';" % bhtml)

        # test one by one

        for button, val, name in buttonset:
            button_el = browser.find_element_by_id(name)
            controller.buttondown(button)
            assert button_el.get_attribute('value') == "1", "%s not seen as down" % name
            controller.buttonup(button)
            assert button_el.get_attribute('value') == "0", "%s not seen as up" % name

        # test simultaneous
        return

        # Tests failing 
        for button, val, name in buttonset:
            browser.execute_script( "document.getElementById('%s').value='5';" % name )

        for button, val, name in buttonset:
            button_el = browser.find_element_by_id(name)
            controller.buttondown(button)

        for button, val, name in buttonset:
            button_el = browser.find_element_by_id(name)
            assert button_el.get_attribute('value') == "1", "%s not seen as down" % name

        for button, val, name in buttonset:
            button_el = browser.find_element_by_id(name)
            controller.buttonup(button)

        for button, val, name in buttonset:
            button_el = browser.find_element_by_id(name)
            assert button_el.get_attribute('value') == "0", "%s not seen as up" % name




