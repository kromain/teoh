#!/usr/bin/env python3
#
# Copyright (c) 2014 Sony Network Entertainment Intl., all rights reserved.

import string

from skynet.deci.dualshock import Buttons as DS
from skynet.osk.osk_graph import osk_graph
from skynet.osk.osk_nav import nav_path

from skynet.osk.en_ import en_dict_text
from skynet.osk.de_ import de_dict_text
from skynet.osk.es_ import es_dict_text
from skynet.osk.fr_ import fr_dict_text

from skynet.osk.text_ja import TextOsk_ja

class TextOsk(osk_graph):
    """
    Represents text mode SDK
    Handles mapping of text keyboard based on locale.

    Default keyboard locale is English.
    """

    def __init__(self, lang=None):

        super(TextOsk,self).__init__()
        self.graph = "text"
        self.start = "G"
        self.lang = lang

        if lang == None:
            osk = en_dict_text()
        else:         
            for x in ["pt_", "it_", "da_", "nl_", "sv_", "no_", "fi_"]:
                if lang.startswith(x):
                    osk = en_dict_text()
                    break
            if lang.startswith("de_"):
                osk = de_dict_text()
            elif lang.startswith("es_"):
                osk = es_dict_text()
            elif lang.startswith("fr_"):
                osk = fr_dict_text()
            elif lang.startswith("ru_"):
                osk = ru_dict_text()
                self.start = "Е"
            else:
                osk = en_dict_text()

        lowercase = osk.lo
        uppercase = osk.up
        L2_keys = osk.L2
        L2_keys_ = osk.L2_
        L3_keys = osk.L3
        L3_keys_ = osk.L3_

        self.add_node(" ")
        self.add_node("L3key", "none", "none")
        self.add_edge("L3key", "c", 1, [DS.UP])
        self.add_edge("L3key", "ż", 1, [DS.UP])

        self.set_edge(lowercase, "lowercase", "L1")
        self.set_edge(uppercase, "uppercase", "L1")
        self.set_edge(L2_keys, "none", "L2")
        self.set_edge(L2_keys_, "none", "L2_")
        self.set_edge(L3_keys, "uppercase", "L3")
        self.set_edge(L3_keys_, "lowercase", "L3")

        self.set_edge_overlap(lowercase, uppercase)
        self.set_edge_overlap(lowercase, L2_keys)
        self.set_edge_overlap(L2_keys, L2_keys_)
        self.set_edge_overlap(L3_keys, L3_keys_)

        for i in self.nodes.copy():
            if i == "dummy_key":
                self.nodes.remove(i)


        end = [".", "?", "!"]
        for x in end:
            self.add_node(x, "end", "L1")

        self.add_node("!", "end", "L2")

        chars = list(string.digits)
        for x in chars:
            self.add_node(x, "none", "L1")

