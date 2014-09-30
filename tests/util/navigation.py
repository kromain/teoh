#!/usr/bin/env python3
#
# Copyright (c) 2014 Sony Network Entertainment Intl., all rights reserved.

import time

from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.ui import WebDriverWait
from skynet.deci.dualshock import Buttons as DS


class Navigation:
    """
    Represents the Navigation class
    """

    def __init__(self, dualshock, psdriver):
        self.ds = dualshock
        self.browser = psdriver

    def go_to_account_mgmt(self):
        """
        Navigate to RegiCam page
        """
        self.ds.press_button(DS.PS, timetorelease=1)
        self.ds.press_button(DS.UP, timetorelease=1)

        self.ds.press_button(DS.RIGHT, timetopress=1)

        self.ds.press_button(DS.LEFT, timetorelease=1)
        self.ds.press_button(DS.CROSS, timetorelease=1)
        self.ds.press_button(DS.CROSS, timetorelease=1)
        self.ds.press_button(DS.CROSS, timetorelease=1)

        # Wait up to 10s for the RegiCAM page to load
        foundregicam = False
        for i in range(10):
            for hdl in self.browser.window_handles:
                self.browser.switch_to.window(hdl)
                if self.browser.title.startswith("RegiCAM"):
                    foundregicam = True
                    break
            if foundregicam:
                break
            time.sleep(1)

        if not foundregicam:
            return False

        # FIXME waiting on some page elements isn't enough, as they are available before regicam starts showing.
        #       Find the right condition that reflects that regicam has really finished loading.
        #       In the meantime just use an explicit 10s sleep to give it enough time to load
        #
        # try:
        #     def regicam_loaded(driver):
        #         elem = self.browser.find_element_by_id('services')
        #     WebDriverWait(self.browser, 10).until(regicam_loaded)
        # except WebDriverException:
        #     return False
        time.sleep(10)

        return True

    def return_to_whats_new(self):
        self.ds.press_button(DS.PS, timetorelease=1)
        self.ds.press_button(DS.LEFT)
