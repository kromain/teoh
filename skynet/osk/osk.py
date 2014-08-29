#!/usr/bin/env python3
#
# Copyright (c) 2014 Sony Network Entertainment Intl., all rights reserved.

import skynet.deci as deci
import time

from skynet.deci.dualshock import Buttons as DS
from skynet.osk.osk_graph import osk_graph
from skynet.osk.osk_nav import nav_path

from skynet.osk.numeric import NumOsk
from skynet.osk.latin_basic import BasicLatinOsk
from skynet.osk.email_osk import EmailOsk
from skynet.osk.text import TextOsk
from skynet.osk.password import PasswordOsk
from skynet.osk.text_ja import TextOsk_ja
from skynet.osk.text_ru import TextOsk_ru

class OskEntry():
    """ entry methods for different types of on-screen keyboards """
    def __init__(self, ds):
        self.dualshock = ds

    def entry_osk(self, text, osk_type, lang=None):
        """
        Simulate an on-screen keyboard entry by specifying *text*, *osk_type*, and *lang*.

        Method must be called when on-screen keyboard is opened and cursor is at default
        starting position.
        After *text* is entered, keyboard will close.

        :param string text: Text to be entered
        :param osk_type: Type of keyboard
        :type osk_graph: :class:`osk_graph`
        :param string lang: Type of lang, default is English language

        :raises InvalidType exception: if *osk_type* is not a valid keyboard
        :raises InvalidString: if text entered is not a valid string
        :raises InvalidKey: if characters of entered text is not a specified keyboard character
        """

        if type(text) != str:
            raise self.InvalidString(string)

        if osk_type == "numeric":
            osk_map = NumOsk(lang)

        elif osk_type == "latin_basic":
            osk_map = BasicLatinOsk(lang)

        elif osk_type == "email":
            osk_map = EmailOsk(lang)

        elif osk_type == "password":
            osk_map = PasswordOsk(lang)

        elif osk_type == "text":
            if lang.startswith("ja_"):
                osk_map = TextOsk_ja()
            elif lang.startswith("ru_"):
                osk_map = TextOsk_ru()
            else:
                osk_map = TextOsk(lang)

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

        self.osk_press_buttons(nav)

        self.dualshock.press_button(DS.R2)
        self.dualshock.press_button(DS.R2)

    def osk_press_buttons(self, buttonlist):
        """
        Revised press_buttons method with delays between button presses
        Simulates button-presses for keyboard navigation to enter text.

        :param buttonlist: list of buttons to be pressed
        """

        button_delay = [DS.L2, DS.L3, DS.L2 | DS.TRIANGLE]

        lastbutton = 0

        for x in buttonlist:
            if x == lastbutton:
                time.sleep(0.1)

            else:
                lastbutton = x

            if x == "DELAY":
                time.sleep(.2)

            elif x in button_delay:
                self.dualshock.press_button(x, 0.09, 0.4)

            else:
                self.dualshock.press_button(x, 0.09, 0.06)


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
            raise self.InvalidKey(g.graph, invalid_keys)


    class Error(Exception):
        """
        Base class for exeptions related to OskEntry
        """
        pass

    class InvalidKey(Error):
        """
        Represents an osk entry error when input value is not part of OSK
        """
        def __init__(self, osk, msg):
            self.osk = osk
            self.msg = msg

        def __str__(self):
            return "Entry is not valid %s key: %s" % (self.osk, self.msg)

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

