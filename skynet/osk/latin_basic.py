#!/usr/bin/env python3
#
# Copyright (c) 2014 Sony Network Entertainment Intl., all rights reserved.
import string

from skynet.deci.dualshock import Buttons as DS
from skynet.osk.osk_graph import osk_graph

from skynet.osk.en_ import en_dict_basic
from skynet.osk.de_ import de_dict_basic
from skynet.osk.es_ import es_dict_basic
from skynet.osk.fr_ import fr_dict_basic
from skynet.osk.ja_ import ja_dict_basic
from skynet.osk.ru_ import ru_dict_basic

class BasicLatinOsk(osk_graph):
    """
    Represents basic-latin mode SDK
    Handles mapping of basic-latin keyboard based on locale.

    Default keyboard locale is English.
    """
    def __init__(self, lang=None):

        super(BasicLatinOsk,self).__init__()
        self.graph = "basic-latin"
        self.start = "g"
        self.lang = lang

        if lang == None:
            osk = en_dict_basic()
        else:   
            for x in ["pt_", "it_", "da_", "nl_", "sv_", "no_", "fi_"]:
                if lang.startswith(x):
                    osk = en_dict_basic()
                    break
            if lang.startswith("de_"):
                osk = de_dict_basic()
            elif lang.startswith("es_"):
                osk = es_dict_basic()
            elif lang.startswith("fr_"):
                osk = fr_dict_basic()
            elif lang.startswith("ja_"):
                osk = ja_dict_basic()
            elif lang.startswith("ru_"):
                osk = ru_dict_basic()
            else:
                osk = en_dict_basic()

        lowercase = osk.lo
        uppercase = osk.up
        L2_keys = osk.L2

        self.set_edge(lowercase, "lowercase", "L1")
        self.set_edge(uppercase, "uppercase", "L1")
        self.set_edge(L2_keys, "none", "L2")

        self.set_edge_overlap(lowercase, uppercase)
        self.set_edge_overlap(lowercase, L2_keys)

        chars = [" "]
        chars.extend(list(string.digits))
        for x in chars:
            self.add_node(x, "none", "none")

