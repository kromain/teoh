#!/usr/bin/env python3
import time

import skynet.psdriver as psdriver
from skynet.deci.dualshock import DualShock,Buttons
import skynet

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

def test_Dualshock():

    target_ip = "172.31.1.144"
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

    html = ''.join([x[:-1] for x in open("keyevent.html").readlines()])

    # Replace the regicam app with the test app
    browser.execute_script( "document.getElementsByTagName('html')[0].innerHTML = \'%s\';" % html)

    browser.execute_script( "document.getElementById('root').onkeydown=function(event) { console.log('DOWN: ' + event.keyCode); document.getElementById('target').value=event.keyCode;};" )
    target_el = browser.find_element_by_id('target')

    controller = DualShock(target_ip=target_ip)
    assert controller

    controller.start()
                
    buttonset = (
                (Buttons.LEFT, 37),
                (Buttons.UP, 38),
                (Buttons.RIGHT, 39),
                (Buttons.DOWN, 40),
                (Buttons.CROSS, 13),
                (Buttons.CIRCLE, 27),
                (Buttons.TRIANGLE, 112),
                (Buttons.SQUARE, 113),
                (Buttons.OPTION, 114),
                (Buttons.L1, 116),
                (Buttons.R1, 117),
                (Buttons.L2, 118),
                (Buttons.R2, 119),
                (Buttons.L3, 120),
                (Buttons.R3, 121)
                )
    try:
        # Browser can't detect Share or PS
        for button, val in buttonset:

            controller.press_button(button)
            assert int(target_el.get_attribute('value')) == val

        browser.execute_script( "document.getElementById('target').value=0;" )
        browser.execute_script( "document.getElementById('root').onkeydown=function(event) { console.log('DOWN: ' + event.keyCode); document.getElementById('target').value++;};" )

        for button, val in buttonset:
            browser.execute_script( "document.getElementById('target').value=0;" )
            controller.press_buttons([button]*5)
            assert int(target_el.get_attribute('value')) == 5
    except Exception as e:
        print (e)


    controller.stop()

