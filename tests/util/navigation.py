#!/usr/bin/env python3
#
# Copyright (c) 2014 Sony Network Entertainment Intl., all rights reserved.

import conftest
import pytest
import time


from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.ui import WebDriverWait
from skynet import PSTarget, DS


@pytest.fixture(scope="module")
def pstarget(request):
    target = PSTarget(conftest.target_ip)
    target.connect()
    request.addfinalizer(target.release)
    return target


@pytest.fixture(scope="module")
def regicam_webview(pstarget, request):
    """
    Navigate to Settings -> PSN -> Account Information (regicam webview)
    """
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
        for hdl in pstarget.psdriver.window_handles:
            pstarget.psdriver.switch_to.window(hdl)
            if pstarget.psdriver.title.startswith("RegiCAM"):
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
    #         elem = pstarget.psdriver.find_element_by_id('services')
    #     WebDriverWait(pstarget.psdriver, 10).until(regicam_loaded)
    # except WebDriverException:
    #     return False
    time.sleep(10)

    def return_to_whats_new():
        pstarget.dualshock.press_button(DS.PS, timetorelease=1)
        pstarget.dualshock.press_button(DS.LEFT)
    request.addfinalizer(return_to_whats_new)

    return pstarget
