#!/usr/bin/env python3
#
# Copyright (c) 2014 Sony Network Entertainment Intl., all rights reserved.

import unittest

from skynet.deci.dualshock import Buttons as DS
from skynet.osk.osk_graph import osk_graph, nav_path, direct_path
from skynet.osk.num_osk import NumOsk
from skynet.osk.latin_osk import LatinOsk

import string
#from lib.util.PSTestCase import PSTestCase

class oskTestCase(unittest.TestCase):
    # FIXME temporary hack, we should instead have the devkit IP(s) stored in a config file
    target_ip = "43.138.14.112"

    def test_osk_graph(self):
        """ Unit test for osk_graph """
        test_pad = osk_graph()

        test_pad.add_node("1", "none")
        test_pad.add_node("2", "lower")
        test_pad.add_node("3", "lower")
        test_pad.add_node("4", "none")
        test_pad.add_node("5", "lower")

        test_pad.add_edge("1", "2", 1, [DS.RIGHT])
        test_pad.add_edge("1", "4", 1, [DS.DOWN])
        test_pad.add_edge("4", "5", 1, [DS.RIGHT])

        self.assertEqual(test_pad.nodes, {"1", "2", "3", "4", "5"})
        
        self.assertEqual(test_pad.case["1"], "none")
        self.assertEqual(test_pad.case["2"], "lower")
        
        self.assertEqual(test_pad.direction[("1","2")], [DS.RIGHT])
        self.assertEqual(test_pad.direction[("2","1")], [DS.LEFT])
        self.assertEqual(test_pad.distances[("1","2")], 1)

        self.assertEqual(nav_path(test_pad, "15"), [DS.DOWN, DS.RIGHT, DS.CROSS])

    def test_numosk_graph(self):
        """ Unit test for init of NumOsk """
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
        """ Unit test for init of LatinOsk """
        test_pad = LatinOsk()

        chars = ["!", "#", "%", "(", ")", "~", ":", ";", "*", "+", "=", "&", "<", ">", "@", "[", "]", "{", "}", "|", "^", "`", "$"]
        chars.extend(list(string.digits))
        chars.extend(list(string.ascii_lowercase))
        chars.extend(list(string.ascii_uppercase))
        chars.extend([" ", "blank", "?", "/", "\"", "'", "-", ",", ".", "_"])
        
        char_set = set(chars)
        self.assertEqual(test_pad.nodes, char_set)


    def test_latinoosk_edge(self):
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