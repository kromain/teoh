#!/usr/bin/env python3
#
# Copyright (c) 2014 Sony Network Entertainment Intl., all rights reserved.

import unittest
import string

from skynet.deci.dualshock import Buttons as DS
from skynet.osk.osk_graph import osk_graph, nav_path
from skynet.osk.num_osk import NumOsk
from skynet.osk.latin_osk import LatinOsk


class oskTestCase(unittest.TestCase):

    def test_osk_graph(self):
        """ unit test for osk_graph """
        test_pad = osk_graph()

        test_pad.add_node("1")
        test_pad.add_node("2", "lower")
        test_pad.add_node("3")
        test_pad.add_node("4")

        test_map = [["1", "2"], ["3", "4"]]

        test_pad.set_edge(test_map)

        self.assertEqual(test_pad.nodes, {"1", "2", "3", "4"})
        
        self.assertEqual(test_pad.case["1"], "none")
        self.assertEqual(test_pad.case["2"], "lower")

        self.assertEqual(nav_path(test_pad, "14"), [DS.DOWN, DS.RIGHT, DS.CROSS])

    def test_numosk_graph(self):
        """ unit test for init and edges of NumOsk """
        test_pad = NumOsk()

        digits = list(string.digits)
        digits.extend([" ", "-", ".", ",", "delete"])
        numeric_chars = set(digits)


        self.assertEqual(test_pad.nodes, numeric_chars)

        # Test letter case
        for node in test_pad.nodes:
            self.assertEqual(test_pad.case[node], "none")

        # Test distance is 0 between same node
        for node in test_pad.nodes:
            self.assertEqual(test_pad.distances[(node, node)], 0)

    def test_latinosk_graph(self):
        """ unit test for init of LatinOsk """
        test_pad = LatinOsk()

        chars = ["!", "#", "%", "(", ")", "~", ":", ";", "*", "+", "=", "&", "<", ">", "@", "[", "]", "{", "}", "|", "^", "`", "$"]
        chars.extend(list(string.digits))
        chars.extend(list(string.ascii_lowercase))
        chars.extend(list(string.ascii_uppercase))
        chars.extend([" ", "blank_key", "?", "/", "\"", "'", "-", ",", ".", "_"])
        
        char_set = set(chars)
        self.assertEqual(test_pad.nodes, char_set)

    def test_latinoosk_edge(self):
        """ unit test for edges of LatinOsk """
        test_pad = LatinOsk()

        lower = list(string.ascii_lowercase)
        upper = list(string.ascii_uppercase)

        for low in lower:
            self.assertEqual(test_pad.case[low], "lower")

        for up in upper:
            self.assertEqual(test_pad.case[up], "upper")

        for (low, up) in zip(lower, upper):
            self.assertEqual(test_pad.distances[(low, up)], 0)

        for node in test_pad.nodes:
            if node != "L3" and node != "square":
                self.assertEqual(test_pad.distances[(node, node)], 0)


if __name__ == '__main__':
    unittest.main()