#!/usr/bin/env python3
import time

import skynet.psdriver as psdriver
from skynet.deci.dualshock import DualShock,Buttons
import skynet
import conftest

test_ip = conftest.target_ip

def test_set_up():

    target_ip = test_ip

    browser = psdriver.server.connect(target_ip)

    for x in range(0, 5):
        for hdl in browser.window_handles:
            browser.switch_to.window(hdl)
            if browser.title.startswith("RegiCAM"):
                break
        time.sleep(1)

    browser.switch_to.window(hdl)

    time.sleep(3)

    html = ''.join([x[:-1] for x in open("keyevent.html").readlines()])

    # Replace the regicam app with the test app
    browser.execute_script( "document.getElementsByTagName('html')[0].innerHTML = \'%s\';" % html)

test_set_up()