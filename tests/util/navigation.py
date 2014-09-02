#!/usr/bin/env python3
#
# Copyright (c) 2014 Sony Network Entertainment Intl., all rights reserved.

import time
from skynet.deci.dualshock import Buttons as DS

class Navigation:
      """
      Represents the Navigation class
      """
      def __init__(self, target):
            self.target = target
            self.ds = self.target.dualshock
            self.browser = self.target.psdriver

      def go_to_account_mgmt(self):
            """
            Navigate to RegiCam page  
            """
            self.ds.press_button(DS.PS, timetorelease=1)
            self.ds.press_button(DS.UP, timetorelease=1)
            
            self.ds.buttondown(DS.RIGHT)
            time.sleep(1)
            self.ds.buttonup(DS.RIGHT)

            self.ds.press_button(DS.LEFT, timetorelease=1)
            self.ds.press_button(DS.CROSS, timetorelease=1)
            self.ds.press_button(DS.CROSS, timetorelease=1)
            self.ds.press_button(DS.CROSS, timetorelease=1)

            for x in range(0, 5):
                  for hdl in self.browser.window_handles:
                        self.browser.switch_to.window(hdl)
                        if self.browser.title.startswith("RegiCAM"):
                              break
                              return True
                  time.sleep(1)

