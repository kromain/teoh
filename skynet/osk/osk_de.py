#!/usr/bin/env python3
#
# Copyright (c) 2014 Sony Network Entertainment Intl., all rights reserved.

"""
Contains mappings of various keyboards for the German language, or locale de_*.

Difference between en_* and de_*: Z and Y keys are swapped.

Each list represents a keyboard layer (e.g. 'lo' represents the lower-case keyboard chars).

Note: Keys that begin with X followed by a number are stand-in keys. These keys replace 
duplicate characters and help to avoid confusion with navigation.
dummy_key serves as placeholder for setting up keyboard map and will be removed from final mapping. 
"""

class de_dict_basic:

    lo = [["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"],
          ["q", "w", "e", "r", "t", "z", "u", "i", "o", "p"],
          ["a", "s", "d", "f", "g", "h", "j", "k", "l", "'"],
          ["y", "x", "c", "v", "b", "n", "m", ",", ".", "?"]]

    up = [["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"],
          ["Q", "W", "E", "R", "T", "Z", "U", "I", "O", "P"],
          ["A", "S", "D", "F", "G", "H", "J", "K", "L", "\""],
          ["Y", "X", "C", "V", "B", "N", "M", "-", "_", "/"]]

    L2 = [["!", "X?", "X\"", "X'", "#", "%", "(", ")", "~", "X/"],
          ["X-", "X_", "X,", "X.", ":", ";", "*", "+", "=", "&"],
          ["<", ">", "@", "[", "]", "{", "}", "\\", "|", "^"],
          ["`", "$", "X1", "X2", "X3", "X4", "X5", "X6", "X7", "X8"]]


class de_dict_text():

    lo = [["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"],
          ["q", "w", "e", "r", "t", "z", "u", "i", "o", "p"],
          ["a", "s", "d", "f", "g", "h", "j", "k", "l", "'"],
          ["y", "x", "c", "v", "b", "n", "m", ",", ".", "?"]]

    up = [["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"],
          ["Q", "W", "E", "R", "T", "Z", "U", "I", "O", "P"],
          ["A", "S", "D", "F", "G", "H", "J", "K", "L", "\""],
          ["Y", "X", "C", "V", "B", "N", "M", "-", "_", "/"]]

    L2 = [["!",   "X1", "X2", "X3", "#", "%", "(", ")", "()", "X4"],
          ["X5", "X6", "X7", "X8", ":", ";", "*", "+", "=", "&"],
          ["<", ">", "@", "[", "]", "[]", "{", "}", "{}", "page"],
          ["\\", "|", "^", "`", "$", "¥", "´", "‘", "’", "dummy_key"]]

    L2_ = [["‚","“", "”", "„", "~", "¡", "s1", "¿", "X10", "‹"],
           ["›", "«", "»", "°", "ª", "º", "×", "÷", "¤", "¢"],
           ["€", "£", "₩", "§", "¦", "µ", "¬", "¹", "²", "X11"],
           ["³", "¼", "½", "¾", "№", "·", "X12", "X13", "X14", "X15"]]

    L3 = [["À", "Á", "Â", "Ã", "Ä", "Å", "Ą", "Æ", "Ç", "Ć"],
          ["È", "É", "Ê", "Ë", "Ę", "Ğ", "Ì", "Í", "Î", "Ï"],
          ["İ", "Ł", "Ñ", "Ń", "Ò", "Ó", "Ô", "Õ", "Ö", "Ø"],
          ["Œ", "Ś", "Ş", "Š", "ß", "Ù", "Ú", "Û", "Ü", "Ý"],
          ["Ÿ", "Ź", "Ż", "Ž", "Ɖ", "Þ", "X16", "X17", "X18", "X19"]]

    L3_ = [["à", "á", "â", "ã", "ä", "å", "ą", "æ", "ç", "ć"],
           ["è", "é", "ê", "ë", "ę", "ğ", "ì", "í", "î", "ï"],
           ["ı", "ł", "ñ", "ń", "ò", "ó", "ô", "õ", "ö", "ø"],
           ["œ", "ś", "ş", "š", "ß", "ù", "ú", "û", "ü", "ý"],
           ["ÿ", "ź", "ż", "ž", "đ", "þ", "X20", "X21", "X22", "X23"]]

class de_dict_email():

    lo = [["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"],
          ["q", "w", "e", "r", "t", "z", "u", "i", "o", "p"],
          ["a", "s", "d", "f", "g", "h", "j", "k", "l", "-"],
          ["y", "x", "c", "v", "b", "n", "m", "@", ".", "_"]]

    up = [["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"],
          ["Q", "W", "E", "R", "T", "Z", "U", "I", "O", "P"],
          ["A", "S", "D", "F", "G", "H", "J", "K", "L", "\""],
          ["Y", "X", "C", "V", "B", "N", "M", ",", "'", "/"]]

    L2 = [["!", "?", "X\"", "X'", "#", "%", "(", ")", "~", "X/"],
          ["X-", "X_", "X,", "X.", ":", ";", "*", "+", "=", "&"],
          ["<", ">", "X@", "[", "]", "{", "}", "\\", "|", "^"],
          ["`", "$", "X1", "X2", "X3", "X4", "X5", "X6", "X7", "X8"]]
