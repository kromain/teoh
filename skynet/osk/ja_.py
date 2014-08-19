#!/usr/bin/env python3
#
# Copyright (c) 2014 Sony Network Entertainment Intl., all rights reserved.

"""
Contains list mappings of various keyboards for the Japanese language, or locale ja_*.
Main difference between locales en_ and ja_ exist in the text OSK.

Note: Keys that begin with X followed by a char are dummy keys.
"""

class ja_dict_basic:

    lo = [["1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "1"],
          ["q", "w", "e", "r", "t", "y", "u", "i", "o", "p", "q"],
          ["a", "s", "d", "f", "g", "h", "j", "k", "l", "'", "a"],
          ["z", "x", "c", "v", "b", "n", "m", ",", ".", "?", "z"]]

    up = [["1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "1"],
          ["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P", "Q"],
          ["A", "S", "D", "F", "G", "H", "J", "K", "L", "\"", "A"],
          ["Z", "X", "C", "V", "B", "N", "M", "-", "_", "/", "Z"]]

    l2 = [["!", "X?", "X\"", "X'", "#", "%", "(", ")", "~", "X/", "!"],
          ["X-", "X_", "X,", "X.", ":", ";", "*", "+", "=", "&", "X-"],
          ["<", ">", "@", "[", "]", "{", "}", "\\", "|", "^", "<"],
          ["`", "$", "X1", "X2", "X3", "X4", "X5", "X6", "X7", "X8", "`"]]


class ja_dict_text:

    lo = [["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"],
          ["q", "w", "e", "r", "t", "y", "u", "i", "o", "p"],
          ["a", "s", "d", "f", "g", "h", "j", "k", "l", "'"],
          ["z", "x", "c", "v", "b", "n", "m", ",", ".", "?"]]

    up = [["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"],
          ["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"],
          ["A", "S", "D", "F", "G", "H", "J", "K", "L", "\""],
          ["Z", "X", "C", "V", "B", "N", "M", "-", "_", "/"]]

    l2 = [["!", "X1", "X2", "X3", "#", "%", "(", ")", "()", "X4"],
          ["X5", "X6", "X7", "X8", ":", ";", "*", "+", "=", "&"],
          ["<", ">", "@", "[", "]", "[]", "{", "}", "{}", "page"],
          ["\\", "|", "^", "`", "$", "¥", "´", "‘", "X’", "X9"]]

    l2_ = [["‚","“", "X”", "„", "~", "¡", "s1", "¿", "X10", "‹"],
           ["›", "«", "»", "°", "ª", "º", "×", "÷", "¤", "¢"],
           ["€", "£", "₩", "§", "¦", "µ", "¬", "¹", "²", "X11"],
           ["³", "¼", "½", "¾", "№", "·", "X12", "X13", "X14", "X15"]]

    l3 = [["わ", "ら", "や", "ま", "は", "な", "た", "さ", "か", "あ", "わ"],
         ["を", "り", "ゆ", "み", "ひ", "に", "ち", "し", "き", "い", "を"],
         ["ん", "る", "よ", "む", "ふ", "ぬ", "つ", "す", "く", "う", "ん"],
         ["ー", "れ", "、", "め", "へ", "ね", "て", "せ", "け", "え", "ー"],
         ["small", "ろ", "？", "も", "ほ", "の", "と", "そ", "こ", "お", "small"]]

    l2_j = [["！", "X？", "”", "’", "＃", "％", "（", "）","（）", "／", "！"],
          ["－", "＿", "，", "．", "：", "；", "＊", "＋", "＝", "＆", "－"],
          ["＜", "＞", "＠", "［", "］", "［］", "｛", "｝", "｛｝", "＼", "＜"],
          ["｜", "＾", "｀", "＄", "￥", "「", "」", "「」", "X、", "。", "｜"],
          ["Xー", "・", "～", "X16", "X17", "X18", "X19", "X20", "X21", "X22", "Xー"]]

    hiragana = ["が", "ざ", "だ", "ば", "ぱ",
                "ぎ", "じ", "ぢ", "び", "ぴ",
                "ぐ", "ず", "づ", "ぶ", "ぷ",
                "げ", "ぜ", "で", "べ", "ぺ",
                "ご", "ぞ", "ど", "ぼ", "ぽ"]

    hiragana_ = ["か", "さ", "た", "は", "は",
                 "き", "し", "ち", "ひ", "ひ",
                 "く", "す", "つ", "ふ", "ふ",
                 "け", "せ", "て", "へ", "へ",
                 "こ", "そ", "と", "ほ", "ほ"]

    diagraph = ["ゃ", "ゅ", "ょ"]
    diagraph_ = ["や", "ゆ", "よ"]


class ja_dict_email:

    lo = [["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"],
          ["q", "w", "e", "r", "t", "y", "u", "i", "o", "p"],
          ["a", "s", "d", "f", "g", "h", "j", "k", "l", "-"],
          ["z", "x", "c", "v", "b", "n", "m", "@", ".", "_"]]

    up = [["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"],
          ["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"],
          ["A", "S", "D", "F", "G", "H", "J", "K", "L", "\""],
          ["Z", "X", "C", "V", "B", "N", "M", ",", "'", "/"]]

    l2 = [["!", "?", "X\"", "X'", "#", "%", "(", ")", "~", "X/"],
          ["X-", "X_", "X,", "X.", ":", ";", "*", "+", "=", "&"],
          ["<", ">", "X@", "[", "]", "{", "}", "\\", "|", "^"],
          ["`", "$", "X1", "X2", "X3", "X4", "X5", "X6", "X7", "X8"]]


