#!/usr/bin/env python3
#
# Copyright (c) 2014 Sony Network Entertainment Intl., all rights reserved.
import string

from skynet.deci.dualshock import Buttons as DS
from skynet.osk.osk_graph import osk_graph, nav_path 

class NumOsk(osk_graph):
    """ numeric osk graph that extends from osk_graph"""

    def __init__(self):
        super(NumOsk,self).__init__()

        # Set up numeric OSK by adding nodes for each character
        num_chars = ["delete", " ", "-", ".", ","]
        num_chars.extend(list(string.digits))

        for x in num_chars:
            self.add_node(x, "none")

        num = [["1", "2", "3"], ["4", "5", "6"], ["7", "8", "9"], [".", "0", "-"], [",", " ", "delete"]]

        self.set_edge(num)



if __name__ == '__main__':
    # Print path from "1" to "5" based on numeric osk
    test_graph = NumOsk()
    print(nav_path(test_graph, "12355"))
