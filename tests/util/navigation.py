#!/usr/bin/env python3
#
# Copyright (c) 2014 Sony Network Entertainment Intl., all rights reserved.

import pytest
import time

from skynet import DS
from skynet.deci import Netmp
from skynet.deci.info import Info


@pytest.fixture(scope="module")
def netmp(request):
    netmp = Netmp(ip=request.config.target_ip)
    netmp.connect()
    request.addfinalizer(netmp.disconnect)
    return netmp


@pytest.fixture(scope="module")
def info(request):
    i = Info(ip=request.config.target_ip)
    i.start()
    request.addfinalizer(i.stop)
    return i


@pytest.fixture(scope="module")
def regicam_webview(pstarget_module, request):
    """
    Navigate to Settings -> PSN -> Account Information (regicam webview)
    """
    pstarget = pstarget_module
    pstarget.dualshock.press_button(DS.UP, timetorelease=1)
    pstarget.dualshock.press_button(DS.PS, timetorelease=1)
    pstarget.dualshock.press_button(DS.UP, timetorelease=1)

    pstarget.dualshock.press_button(DS.RIGHT, timetopress=1)

    pstarget.dualshock.press_button(DS.LEFT, timetorelease=1)
    pstarget.dualshock.press_button(DS.CROSS, timetorelease=1)
    pstarget.dualshock.press_button(DS.CROSS, timetorelease=1)
    pstarget.dualshock.press_button(DS.CROSS, timetorelease=1)

    # Wait up to 10s for the RegiCAM page to load
    foundregicam = False
    for i in range(10):
        for hdl in pstarget.webview.window_handles:
            pstarget.webview.switch_to.window(hdl)
            if pstarget.webview.title.startswith("RegiCAM"):
                foundregicam = True
                break
        if foundregicam:
            break
        time.sleep(1)

    if not foundregicam:
        return None

    # FIXME waiting on some page elements isn't enough, as they are available before regicam starts showing.
    #       Find the right condition that reflects that regicam has really finished loading.
    #       In the meantime just use an explicit 10s sleep to give it enough time to load
    #
    # try:
    #     def regicam_loaded(driver):
    #         elem = pstarget.webview.find_element_by_id('services')
    #     WebDriverWait(pstarget.webview, 10).until(regicam_loaded)
    # except WebDriverException:
    #     return False
    time.sleep(10)

    def return_to_whats_new():
        pstarget.dualshock.press_button(DS.PS, timetorelease=1)
        pstarget.dualshock.press_button(DS.LEFT)
    request.addfinalizer(return_to_whats_new)

    return pstarget
