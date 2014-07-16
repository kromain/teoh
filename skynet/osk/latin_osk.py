#!/usr/bin/env python3
#
# Copyright (c) 2014 Sony Network Entertainment Intl., all rights reserved.
import string

from skynet.deci.dualshock import Buttons as DS
from skynet.osk.osk_graph import osk_graph

class LatinOsk(osk_graph):
    """ basic latin osk graph that extends from osk_graph"""

    def __init__(self):
        super(LatinOsk,self).__init__()

        chars = [" ", "blank_key"]
        chars.extend(list(string.digits))

        lower_chars = ["_", "-", ".", "?"]
        lower_chars.extend(list(string.ascii_lowercase))

        upper_chars = ["/", "\"", ",", "'"]
        upper_chars.extend(list(string.ascii_uppercase))
        
        l2_chars = ["!", "#", "%", "(", ")", "~", ":", ";", "*", "+", "=", "&", "<", ">", "@", "[", "]", "{", "}", "|", "^", "`", "$"]

        for x in chars:
            self.add_node(x)
            
        for x in lower_chars:
            self.add_node(x, "lower")

        for x in upper_chars:
            self.add_node(x, "upper")
        
        for x in l2_chars:
            self.add_node(x, "l2_chars")


        # Lower case letters
        lower_tab = [["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"],
                    ["q", "w", "e", "r", "t", "y", "u", "i", "o", "p"],
                    ["a", "s", "d", "f", "g", "h", "j", "k", "l", "'"],
                    ["z", "x", "c", "v", "b", "n", "m", ",", ".", "?"]]

        # Upper case letters
        upper_tab = [["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"],
                    ["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"],
                    ["A", "S", "D", "F", "G", "H", "J", "K", "L", "\""],
                    ["Z", "X", "C", "V", "B", "N", "M", "-", "_", "/"]]

        # L2 Characters    
        l2_tab = ["!", "#", "%", "(", ")", "~", ":", ";", "*", "+", "=", "&", "<", ">", "@", "[", "]", "{", "}", "|", "^", "`", "$"]
        l2_rel = ["1", "5", "6", "7", "8", "9", "t", "y", "u", "i", "o", "p", "a", "s", "d", "f", "g", "h", "j", "l", "\"", "z", "x"]


        self.set_edge(lower_tab)
        self.set_edge(upper_tab)

        self.set_edge_overlap(lower_tab, upper_tab)
        self.set_edge_overlap(l2_tab, l2_rel)

        # Characters with special edges
        table = {
            "#" : [("%", [DS.RIGHT]), (":", [DS.DOWN])],
            "%" : [("(", [DS.RIGHT]), (";", [DS.DOWN])],
            "(" : [(")", [DS.RIGHT]), ("*", [DS.DOWN])],
            ")" : [("~", [DS.RIGHT]), ("+", [DS.DOWN])],

            "~" : [("=", [DS.DOWN])],
            ":" : [(";", [DS.RIGHT]), ("]", [DS.DOWN])],
            ";" : [("*", [DS.RIGHT]), ("{", [DS.DOWN])],
            "*" : [("+", [DS.RIGHT]), ("}", [DS.DOWN])],
            "+" : [("=", [DS.RIGHT]), ("\\", [DS.DOWN])],
            "=" : [("&", [DS.RIGHT]), ("|", [DS.DOWN])],
            "&" : [("^", [DS.DOWN])],    

            "<" : [(">", [DS.RIGHT]), ("`", [DS.DOWN])],
            ">" : [("@", [DS.RIGHT]), ("$", [DS.DOWN])],
            "@" : [("[", [DS.RIGHT])],
            "[" : [("]", [DS.RIGHT])],
            "]" : [("{", [DS.RIGHT])],
            "{" : [("}", [DS.RIGHT])],
            "}" : [("\\", [DS.RIGHT])],
            "\\" : [("|", [DS.RIGHT])],

            "|" : [("^", [DS.RIGHT])],
            "`" : [("$", [DS.RIGHT])], 
            " " : [("blank_key", [DS.RIGHT])],
            "," : [("blank_key", [DS.DOWN])]
        }

        self.set_edge_table(table)

