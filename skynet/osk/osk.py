#!/usr/bin/env python3
#
# Copyright (c) 2014 Sony Network Entertainment Intl., all rights reserved.

import skynet.deci as deci

from skynet.deci.dualshock import Buttons as DS
from skynet.osk.osk_graph import osk_graph, nav_path
from skynet.osk.num_osk import NumOsk
from skynet.osk.latin_osk import LatinOsk


class OskEntry():
    """ entry methods for different types of on-screen keyboards """
    
    NUM_START = "5"
    LATIN_START = "g"
    DONE = DS.R2

    def __init__(self, ds):
        self.dualshock = ds

    def entry_osk(self, string, osk_type):
        """ passes string to appropriate type of osk

            osk_type - Type of osk (e.g numeric)
        """
        if not(type(string) == str):
            raise self.InvalidString(string)

        if osk_type == "numeric":
            num_map = NumOsk()
            self.entry_numeric(num_map, self.NUM_START + string)

        if osk_type == "latin_basic":
            latin_map = LatinOsk()
            self.entry_numeric(latin_map, self.LATIN_START + string)


    def entry_numeric(self, g, string):
        """ takes in string and stimulates on numeric osk """
        stringList = list(string)

        self.check_invalid(g, stringList)
        
        nav = nav_path(g, stringList)
        
        self.dualshock.press_buttons(nav, postdelay=0.2)   
        self.dualshock.buttonpress(self.DONE)   

    
    def check_invalid(self, g, string):
        stringset = set(string)
        if not(stringset < g.nodes):
            invalid_keys = stringset - g.nodes
            raise self.InvalidKey(invalid_keys)


    class Error(Exception):
        """ base class for other exceptions """
        pass


    class InvalidKey(Error):
        """ raised when input value is not in OSK """
        def __init__(self, msg):
            self.msg = msg

        def __str__(self):
            return "Entry is not valid OSK key: %s" % self.msg


    class InvalidString(Error):
        """ raised when input value is not a string """
        def __init__(self, msg):
            self.msg = msg

        def __str__(self):
            return "Entry is not valid string: %s" % self.msg