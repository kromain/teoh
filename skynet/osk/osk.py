#!/usr/bin/env python3
#
# Copyright (c) 2014 Sony Network Entertainment Intl., all rights reserved.

from skynet.deci.dualshock import Buttons as DS
from skynet.osk.osk_graph import osk_graph, nav_path
from skynet.osk.num_osk import NumOsk
from skynet.osk.latin_osk import LatinOsk

import skynet.deci as deci

class OskEntry():
    """ entry methods for different types of on-screen keyboards """
    
    NUM_OSK_START = "5"
    LATIN_OSK_START = "g"
    DONE = DS.R2

    def __init__(self, ds):
        self.dualshock = ds

    def entry_osk(self, string, osk_type):
        """ passes string to appropriate type of osk

            osk_type - Type of osk (e.g numeric)
        """
        nav = []

        if osk_type == "numeric":
            nav = self.entry_numeric(string)
        if osk_type == "latin_basic":
            nav = self.entry_latin_basic(string)

        self.dualshock.press_buttons(nav)   
        self.dualshock.buttonpress(DONE)   

    def entry_numeric(self, string):
        """ takes in string and stimulates on numeric osk """
        num_map = NumOsk()

        string_list = [self.NUM_OSK_START]
        string_list.extend(list(string))

        return nav_path(num_map, string_list)

    def entry_latin_basic(self, string):
        """ takes in string and stimulates on basic-latin osk """
        latin_map = LatinOsk()

        string_list = [self.LATIN_OSK_START]
        string_list.extend(list(string))

        return nav_path(latin_map, string_list)