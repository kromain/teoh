#!/usr/bin/env python3
#
# Copyright (c) 2014 Sony Network Entertainment Intl., all rights reserved.

import string

from skynet.osk.osk_graph import osk_graph
from skynet.osk.numeric import NumOsk
from skynet.osk.latin_basic import BasicLatinOsk
from skynet.osk.text import TextOsk


def test_osk_graph():
    """ unit test for osk_graph """
    test_pad = osk_graph()

    test_map = [["1", "2"], ["3", "4"]]

    test_pad.set_edge(test_map)
    test_pad.add_node("2", case="lower")

    assert test_pad.nodes == {"1", "2", "3", "4"}

    assert test_pad.case["1"] == "none"
    assert test_pad.case["2"] == "lower"


def test_numosk_graph():
    """ unit test for init and edges of NumOsk """
    test_pad = NumOsk()

    digits = list(string.digits)
    digits.extend([" ", "-", ".", ",", "delete"])
    numeric_chars = set(digits)

    assert test_pad.nodes == numeric_chars

    # Test letter case
    for node in test_pad.nodes:
        assert test_pad.case[node] == "none"

    # Test distance is 0 between same node
    for node in test_pad.nodes:
        if node != " ":
            assert test_pad.distances[(node, node)] == 0


def test_basiclatin_graph():
    """ unit test for init of LatinOsk """
    test_pad = BasicLatinOsk()

    chars = ["!", "#", "%", "(", ")", "~", ":", ";", "*", "+", "=", "&",
             "<", ">", "@", "[", "]", "{", "}", "|", "^", "`", "$"]
    chars.extend(list(string.digits))
    chars.extend(list(string.ascii_lowercase))
    chars.extend(list(string.ascii_uppercase))
    chars.extend(["?", "/", "\"", "'", "-", ",", ".", "_"])

    char_set = set(chars)


def test_basiclatin_edge():
    """ unit test for mapping of LatinOsk """
    test_pad = BasicLatinOsk()

    lower = list(string.ascii_lowercase)
    upper = list(string.ascii_uppercase)

    for low in lower:
        assert test_pad.case[low] == "lowercase"

    for up in upper:
        assert test_pad.case[up] == "uppercase"

    for (low, up) in zip(lower, upper):
        assert test_pad.distances[(low, up)] == 0

    for node in test_pad.nodes:
        if node != "L3" and node != "square" and node != " ":
            assert test_pad.distances[(node, node)] == 0


def test_text_edge():
    test_pad = TextOsk()

    lower = list(string.ascii_lowercase)
    upper = list(string.ascii_uppercase)

    for low in lower:
        assert test_pad.case[low] == "lowercase"

    for up in upper:
        assert test_pad.case[up] == "uppercase"

    for (low, up) in zip(lower, upper):
        assert test_pad.distances[(low, up)] == 0

    for node in test_pad.nodes:
        if node != "L3" and node != "square":
            assert test_pad.distances[(node, node)] == 0
