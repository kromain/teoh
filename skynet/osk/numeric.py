#!/usr/bin/env python3
#
# Copyright (c) 2014 Sony Network Entertainment Intl., all rights reserved.

import string

from skynet.osk.osk_graph import osk_graph

class NumOsk(osk_graph):
    """
    Creates numeric mode SDK
    Handles mapping of numeric keyboard

    Locale param has no affect on numeric keyboard.
    """
    def __init__(self, locale=None):

        super(NumOsk,self).__init__()

        self.graph = "numeric"
        self.start = "5"

        num = [["1", "2", "3", "1"],
               ["4", "5", "6", "4"],
               ["7", "8", "9", "7"],
               [".", "0", "-", "."],
               [",", " ", "delete", ","]]

        self.set_edge(num)

