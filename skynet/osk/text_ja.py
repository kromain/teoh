#!/usr/bin/env python3
#
# Copyright (c) 2014 Sony Network Entertainment Intl., all rights reserved.

import string

from skynet.deci.dualshock import Buttons as DS
from skynet.osk.osk_graph import osk_graph
from skynet.osk.osk_nav import nav_path

from skynet.osk.ja_ import ja_dict_text

class TextOsk_ja(osk_graph):
    """
    Creates text mode SDK
    Handles mapping of the text keyboard based on locale "ja"
    """
    def __init__(self):

        super(TextOsk_ja,self).__init__()
        self.graph = "text"
        self.start = "ふ"
        self.lang = "ja_"

        osk = ja_dict_text()

        lowercase = osk.lo
        uppercase = osk.up
        L2_keys = osk.L2
        L2_keys_ = osk.L2_
        L2_ja_keys = osk.L2_j
        L3_keys = osk.L3
        hiragana = osk.hiragana
        hiragana_ = osk.hiragana_
        diagraph = osk.diagraph
        diagraph_ = osk.diagraph_

        for x in hiragana:
            self.add_node(x, "hiragana", "L3")

        for x in diagraph:
            self.add_node(x, "diagraph", "L3")

        self.add_node(" ")
        self.add_node("\u3000")
        self.add_node("L3key", "none", "none")
        self.add_edge("L3key", "c", 1, [DS.UP])
        self.add_edge("L3key", "？", 1, [DS.UP])

        self.add_node("L2key", "none", "none")
        self.add_edge("L2key", "そ", 1, [DS.UP])

        self.set_edge(lowercase, "lowercase", "L1")
        self.set_edge(uppercase, "uppercase", "L1")
        self.set_edge(L2_keys, "none", "L2")
        self.set_edge(L2_keys_, "none", "L2_")
        self.set_edge(L3_keys, "none", "L3")
        self.set_edge(L2_ja_keys, "none", "L2_j")

        self.set_edge_overlap(lowercase, uppercase)
        self.set_edge_overlap(lowercase, L2_keys)
        self.set_edge_overlap(L2_keys, L2_keys_)
        self.set_edge_overlap(L3_keys, L2_ja_keys)
        self.set_edge_overlap(hiragana, hiragana_)
        self.set_edge_overlap(diagraph, diagraph_)

        for i in self.nodes.copy():
            if i == "dummy_key":
                self.nodes.remove(i)

        chars = list(string.digits)
        for x in chars:
            self.add_node(x, "none", "L1")

        end = [".", "?", "!"]
        for x in end:
            self.add_node(x, "end", "L1")
        self.add_node("!", "end", "L2")

