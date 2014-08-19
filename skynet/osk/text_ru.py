#!/usr/bin/env python3
#
# Copyright (c) 2014 Sony Network Entertainment Intl., all rights reserved.

import string

from skynet.deci.dualshock import Buttons as DS
from skynet.osk.osk_graph import osk_graph
from skynet.osk.osk_nav import nav_path

from skynet.osk.ru_ import ru_dict_text

class TextOsk_ru(osk_graph):
    """
    Creates text mode SDK
    Handles mapping of text keyboard based on locale "ru"
    """
    def __init__(self):

        super(TextOsk_ru,self).__init__()
        self.graph = "text"
        self.start = "Е"
        self.lang = "ru_"

        osk = ru_dict_text()

        lowercase = osk.lo
        uppercase = osk.up
        l2 = osk.l2
        l2_ = osk.l2_
        l3 = osk.l3
        l3_ = osk.l3_

        self.add_node("L2key", "none", "none")
        self.add_edge("L2key", "Ч", 1, [DS.UP])
        self.add_edge("L2key", "x", 1, [DS.UP])

        self.add_node(" ")
        self.add_node("L3key", "none", "none")
        self.add_edge("L3key", "c", 1, [DS.UP])
        self.add_edge("L3key", "С", 1, [DS.UP])

        self.set_edge(lowercase, "lowercase", "L1")
        self.set_edge(uppercase, "uppercase", "L1")
        self.set_edge(l2, "none", "L2")
        self.set_edge(l2_, "none", "L2_")
        self.set_edge(l3, "uppercase", "L3")
        self.set_edge(l3_, "lowercase", "L3")

        self.set_edge_overlap(lowercase, uppercase)
        self.set_edge_overlap(lowercase, l2)
        self.set_edge_overlap(l2, l2_)
        self.set_edge_overlap(l3, l3_)

        end = [".", "?", "!"]
        for x in end:
            self.add_node(x, "end", "L3")

