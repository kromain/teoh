#!/usr/bin/env python3
#
# Copyright (c) 2014 Sony Network Entertainment Intl., all rights reserved.
import string

from skynet.deci.dualshock import Buttons as DS
from skynet.osk.osk_type.osk_graph import osk_graph, nav_path
from skynet.osk.osk_type.locale.en_ import en_locale_basic
from skynet.osk.osk_type.locale.de_ import de_locale_basic

class BasicLatinOsk(osk_graph):
    """
    Creates basic-latin mode SDK 
    Handles mapping of basic-latin keyboard

    locale - The expected keyboard locale, default is English. 
    """
    def __init__(self, locale=None):

        super(BasicLatinOsk,self).__init__()
        self.graph = "BasicLatin"
        self.start = "g"

        if locale == None:
            osk = en_locale_basic()
        
        elif locale.startswith("de_"):
            osk = de_locale_basic()

        else:
            osk = en_locale_basic()

        lowercase = osk.lo
        uppercase = osk.up 
        l2 = osk.l2

        self.add_edge("blank_key", " ", 1, [DS.LEFT])
        self.add_edge("blank_key", ",", 1, [DS.UP])
        
        chars = [" ", "blank_key"]
        chars.extend(list(string.digits))
        for x in chars:
            self.add_node(x)

        end = [".", "?", "!"]
        self.set_node(end, "end")
        self.add_node("!", "end", "L2")

        self.set_edge(lowercase, "lowercase")
        self.set_edge(uppercase, "uppercase")
        self.set_edge(l2, "none", "L2")

        self.set_edge_overlap(lowercase, uppercase)
        self.set_edge_overlap(lowercase, l2)

if __name__ == "__main__":
    test = BasicLatinOsk()
    print(nav_path(test, "&&"))

