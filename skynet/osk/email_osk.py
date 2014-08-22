#!/usr/bin/env python3
#
# Copyright (c) 2014 Sony Network Entertainment Intl., all rights reserved.
import string

from skynet.deci.dualshock import Buttons as DS
from skynet.osk.osk_graph import osk_graph, nav_path
from skynet.osk.en_ import en_locale_email
from skynet.osk.de_ import de_locale_email

class EmailOsk(osk_graph):
    """
    Creates email mode SDK 
    Handles mapping of email keyboard

    locale - The expected keyboard locale, default is English. 
    """
    def __init__(self, locale=None):

        super(EmailOsk,self).__init__()
        self.graph = "email"
        self.start = "g"

        if locale == None:
            osk = en_locale_email()
        
        elif locale.startswith("de_"):
            osk = de_locale_email()

        else:
            osk = en_locale_email()

        lowercase = osk.lo
        uppercase = osk.up
        l2 = osk.l2
    
        self.set_edge(lowercase, "lowercase")
        self.set_edge(uppercase, "uppercase")
        self.set_edge(l2, "none", "L2")

        self.set_edge_overlap(lowercase, uppercase)
        self.set_edge_overlap(lowercase, l2)

        chars = [" "]
        chars.extend(list(string.digits))
        for x in chars:
            self.add_node(x)

        end = [".", "?", "!"]
        self.set_node(end, "end")
        self.add_node("!", "end", "L2")

