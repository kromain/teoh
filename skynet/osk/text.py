#!/usr/bin/env python3
#
# Copyright (c) 2014 Sony Network Entertainment Intl., all rights reserved.
import string

from skynet.deci.dualshock import Buttons as DS
from skynet.osk.osk_graph import osk_graph, nav_path
from skynet.osk.en_ import en_locale_text
from skynet.osk.de_ import de_locale_text

class TextOsk(osk_graph):
    """
    Creates text mode SDK 
    Handles mapping of text keyboard

    locale - The expected keyboard locale, default is English. 
    """
    def __init__(self, locale=None):

        super(TextOsk,self).__init__()
        self.graph = "text"
        self.start = "G"

        if locale == None:
            osk = en_locale_text()
        
        elif locale.startswith("de_"):
            osk = de_locale_text()

        else:
            osk = en_locale_text()

        lowercase = osk.lo
        uppercase = osk.up
        l2 = osk.l2
        l2_ = osk.l2_
        acc_uppercase = osk.ac
        acc_lowercase = osk.ac_

        self.add_node("L3key", "none", "none")
        self.add_edge("L3key", "c", 1, [DS.UP])
        self.add_edge("L3key", " ", 1, [DS.RIGHT])
        self.add_edge("L3key", "ż", 1, [DS.UP])

        self.set_edge(lowercase, "lowercase")
        self.set_edge(uppercase, "uppercase")
        self.set_edge(l2, "none", "L2")
        self.set_edge(l2_, "none", "L2_")
        self.set_edge(acc_uppercase, "uppercase", "L3")
        self.set_edge(acc_lowercase, "lowercase", "L3")
        
        self.set_edge_overlap(lowercase, uppercase)
        self.set_edge_overlap(lowercase, l2)
        self.set_edge_overlap(l2, l2_)
        self.set_edge_overlap(acc_uppercase, acc_lowercase)

        chars = [" "]
        chars.extend(list(string.digits))
        for x in chars:
            self.add_node(x)

        end = [".", "?", "!"]
        self.add_node("!", "end", "L2")
        for x in end:
            self.case[x] = "end"

