#!/usr/bin/env python3
#
# Copyright (c) 2014 Sony Network Entertainment Intl., all rights reserved.

import skynet.deci as deci

from skynet.deci.dualshock import Buttons as DS
from skynet.osk.osk_type.osk_graph import osk_graph, nav_path

from skynet.osk.osk_type.numeric import NumOsk
from skynet.osk.osk_type.latin_basic import BasicLatinOsk
from skynet.osk.osk_type.email_osk import EmailOsk
from skynet.osk.osk_type.text import TextOsk
from skynet.osk.osk_type.password import PasswordOsk


class OskEntry():
    """ entry methods for different types of on-screen keyboards """
    def __init__(self, ds):
        self.dualshock = ds

    def entry_osk(self, text, osk_type, locale=None):
        """
        Simulate an on-screen keyboard entry by specifying *text*, *osk_type*, and *locale*.
        
        Method must be called when on-screen keyboard is opened and cursor is at default
        starting position.
        After *text* is entered, keyboard will close. 

        :param string text: Text to be entered
        :param osk_type: Type of keyboard
        :type osk_graph: :class:`osk_graph`
        :param string locale: Type of locale, default is English language

        :raises InvalidType exception: if *osk_type* is not a valid keyboard
        :raises InvalidString: if text entered is not a valid string
        :raises InvalidKey: if characters of entered text is not a specified keyboard character
        """

        if type(text) != str:
            raise self.InvalidString(string)

        if osk_type == "numeric":
            osk_map = NumOsk(locale)

        elif osk_type == "latin_basic":
            osk_map = BasicLatinOsk(locale)

        elif osk_type == "email":
            osk_map = EmailOsk(locale)

        elif osk_type == "password":
            osk_map = PasswordOsk(locale)

        elif osk_type == "text":
            osk_map = TextOsk(locale)

        else:
            raise self.InvalidType(osk_type)

        self._entry_osk(osk_map, osk_map.start + text)

    def _entry_osk(self, g, text):
        """
        Helper method for entry_osk. 
        Simulates button-presses for keyboard navigation to enter text. 

        :param string text: Text to be entered
        :param g: Type of keyboard
        :type osk_graph: :class:`osk_graph`
        """
        stringList = list(text)

        self.check_valid(g, stringList)
        
        nav = nav_path(g, stringList)
        
        self.dualshock.press_buttons(nav, timetorelease=0.13)   
        self.dualshock.press_button(DS.R2)   

    def check_valid(self, g, text):
        """
        Checks if characters of *text* are valid keys of keyboard *g*. 
        Raises InvalidKey exception and returns invalid chars. 

        :param g: Type of keyboard
        :type osk_graph: :class:`osk_graph`
        :param string text: Text to be entered
        """

        stringset = set(text)
        if not(stringset < g.nodes):
            invalid_keys = stringset - g.nodes
            raise self.InvalidKey(invalid_keys)


    class Error(Exception):
        """ 
        Base class for exeptions related to OskEntry
        """
        pass

    class InvalidKey(Error):
        """ 
        Represents an osk entry error when input value is not part of OSK 
        """
        def __init__(self, msg):
            self.msg = msg

        def __str__(self):
            return "Entry is not valid OSK key: %s" % self.msg

    class InvalidString(Error):
        """ 
        Represents an osk entry error when input text is not a valid string 
        """
        def __init__(self, msg):
            self.msg = msg

        def __str__(self):
            return "Entry is not valid string: %s" % self.msg


    class InvalidType(Error):
        """ 
        Represents an osk entry error when input arg osk_type is not a valid OSK type 
        """
        def __init__(self, msg):
            self.msg = msg

        def __str__(self):
            return "Entry is not valid type: %s" % self.msg