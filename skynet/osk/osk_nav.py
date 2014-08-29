#!/usr/bin/env python3
#
# Copyright (c) 2014 Sony Network Entertainment Intl., all rights reserved.
#
# Djikstra algorithm implementation based on code from: http://www.dainf.ct.utfpr.edu.br/~kaestner/MatematicaDiscreta/Conteudo/Algoritmos/dijkstra2-exemplo6.2-pg290.py

from skynet.deci.dualshock import Buttons as DS

def dijkstra(graph, init_node):
    """
    Implementation of dijkstra to find shortest path
    """
    visited = {init_node: 0}
    curr_node = init_node
    path = {}
    nodes = set(graph.nodes)

    while nodes:
        min_node = None
        for node in nodes:
            if node in visited:
                if min_node is None:
                    min_node = node
                elif visited[node] < visited[min_node]:
                    min_node = node

        if min_node is None:
            break

        nodes.remove(min_node)
        curr_weight = visited[min_node]

        for edge in graph.edges[min_node]:
            weight = graph.distances[(min_node, edge)] + curr_weight
            if edge not in visited or weight < visited[edge]:
                visited[edge] = weight
                path[edge] = min_node

    return visited, path

def shortest_path(graph, init_node, final_node):
    """
    Returns shortest character path between two chars, *init_node* to *final_node*
    Part of dijstra implementation.

    :param graph: Specify the graph map
    :type osk_graph: :class:`osk_graph`
    :param init_node: Starting key node
    :param final_node: Destination key node
    """
    track = [final_node]
    distances, paths = dijkstra(graph, init_node)

    while final_node != init_node:
        track.append(paths[final_node])
        final_node = paths[final_node]

    track.reverse()
    return track


def nav_path(g, string):
    """
    Returns navigation path of string for osk entry

    :param g: Specify the graph map
    :type osk_graph: :class:`osk_graph`
    :param string: Text to be entered
    """
    nav_list = []
    string_List = []
    string_List = string
    text_case = True

    for x in range(len(string_List)-1):
        if string_List[x+1] == " " or string_List[x+1] == "\u3000":
            nav_list.extend([DS.TRIANGLE])
            string_List[x+1] = string_List[x]
        else:
            if text_case == True and g.graph == "text":
                nav_list.extend([DS.L2])
                text_case = False

            nav_list.extend(direct_path(g, string_List[x], string_List[x+1]))

    return nav_list

def direct_path_(g, direct_list, start, end):
    """
    Returns navigation pation between two chars for osk entry

    :param g: Specify the graph map
    :type osk_graph: :class:`osk_graph`
    :param direct_list: List of navigation buttons
    :param start: Starting char
    :param end: Destination char
    """
    path = shortest_path(g, start, end)
    for x in range(len(path)-1):
        direct_list.extend(g.direction[(path[x], path[x+1])])

    if g.case[end] == "uppercase":
        direct_list.extend([DS.L2])

    direct_list.extend([DS.CROSS])


def direct_path(g, start, end):
    """
    Returns navigational directions of shortest path beween two keys, *start* to *end*.
    Handles shift casing (i.e., press shift for uppercase letters) and types (e.g., L2 + Triangle, L3).

    :param g: Specify the graph map
    :type osk_graph: :class:`osk_graph`
    :param start: Starting key node
    :param end: Destination key node
    """
    direct_list = []

    if g.graph == "text":
        if g.lang.startswith("ja_"):
            return direct_path_text_japanese(g, start, end)
        else:
            return direct_path_text(g, start, end)

    if (g.type[end] == "L2" or g.type[start] == "L2_") and (g.type[start] != "L2" and g.type[start] != "L2_"):
        direct_list.extend([DS.L2 | DS.TRIANGLE])

    if (g.type[start] == "L2" or g.type[start] == "L2_") and (g.type[end] != "L2" and g.type[end] != "L2_"):
        direct_list.extend([DS.L2 | DS.TRIANGLE])

    direct_path_(g, direct_list, start, end)

    return direct_list

def direct_path_text(g, start, end):
    """
    Corner cases for text OSK
    Returns navigational directions of shortest path beween two keys, *start* to *end*.
    Handles shift casing (i.e., press shift for uppercase letters) and types (e.g., L2 + Triangle, L3).

    :param g: Specify the graph map
    :type osk_graph: :class:`osk_graph`
    :param start: Starting key node
    :param end: Destination key node
    """
    direct_list = []

    if g.lang.startswith("ru_"):
        if g.type[start] == "L3" and g.type[end] == "L1":
            direct_list.extend(direct_path_text(g, start, "L3key"))
            start = "L3key"

        if g.type[start] == "L1" and g.type[end] == "L3":
            direct_list.extend(direct_path_text(g, start, "L3key"))
            start = "L3key"


    else:
        if not(g.type[start] == "L3") and g.type[end] == "L3":
            direct_list.extend(direct_path_text(g, start, "L3key"))
            start = "L3key"

        if g.type[start] == "L3":
            start = "L3key"
            if g.type[end] == "L3":
                direct_list.extend([DS.L3])


    if g.type[end] == "L2_" and g.type[start] != "L2_":
        direct_list.extend(direct_path_text(g, start, "page"))
        start = "page"

    if end != "page" and g.type[end] == "L2":
        if g.type[start] == "L2_":
            direct_list.extend(direct_path_text(g, start, "page"))
            start = "page"

    if (g.type[end] == "L2" or g.type[end] == "L2_") and (g.type[start] != "L2" and g.type[start] != "L2_"):
        if g.lang.startswith("ru_"):
            direct_list.extend(direct_path_text(g, start, "L2key"))
            start = "L2key"
        else:
            direct_list.extend([DS.L2 | DS.TRIANGLE])

    if (g.type[start] == "L2" or g.type[start] == "L2_") and (g.type[end] != "L2" and g.type[end] != "L2_"):
        direct_list.extend([DS.L2 | DS.TRIANGLE])

    if g.case[start] == "end" and g.case[end] != "end":
        direct_list.extend([DS.L2])

    if start == "L3key" or start == "page" or start == "L2key":
        direct_list.extend(["DELAY"])

    direct_path_(g, direct_list, start, end)

    return direct_list


def direct_path_text_japanese(g, start, end):
    """
    Corner cases for japanese text OSK
    Returns navigational directions of shortest path beween two keys, *start* to *end*.
    Handles shift casing (i.e., press shift for uppercase letters) and types (e.g., L2 + Triangle, L3).

    Handles hiragana and diagraph chars

    :param g: Specify the graph map
    :type osk_graph: :class:`osk_graph`
    :param start: Starting key node
    :param end: Destination key node
    """

    direct_list = []


    if g.type[start] == "L3":
        if g.type[end] == "L1":
            direct_list.extend(direct_path_text_japanese(g, start, "L3key"))
            start = "L3key"

        elif g.type[end] == "L2_j":
            direct_list.extend([DS.L2 | DS.TRIANGLE])

        elif g.type[end] == "L2":
            direct_list.extend(direct_path_text_japanese(g, start, "L2key"))
            direct_list.extend([DS.L2 | DS.TRIANGLE])
            direct_list.extend([DS.CROSS])
            start = "L2key"  

    if g.type[start] == "L1":
        if g.type[end] == "L3":
            direct_list.extend(direct_path_text_japanese(g, start, "L3key"))
            start = "L3key"            
        elif g.type[end] == "L2":
            direct_list.extend([DS.L2 | DS.TRIANGLE])

        elif g.type[end] == "L2_j":
            direct_list.extend(direct_path_text_japanese(g, start, "L2key"))
            direct_list.extend([DS.L2 | DS.TRIANGLE])
            direct_list.extend([DS.CROSS])
            start = "L2key"  
    
    if g.type[start] == "L2":
        if g.type[end] == "L1":
            direct_list.extend([DS.L2 | DS.TRIANGLE])
        if g.type[end] == "L3":
            direct_list.extend(direct_path_text_japanese(g, start, "L2key"))
            start = "L2key"
            direct_list.extend([DS.L2 | DS.TRIANGLE])
    
    if g.type[start] == "L2_j":
        if g.type[end] == "L3":
            direct_list.extend([DS.L2 | DS.TRIANGLE])
        if g.type[end] == "L1": 
            direct_list.extend(direct_path_text_japanese(g, start, "L2key"))
            start = "L2key"
            direct_list.extend([DS.L2 | DS.TRIANGLE])



    hiragana = ["が", "ざ", "だ", "ば", "ぱ",
                "ぎ", "じ", "ぢ", "び", "ぴ",
                "ぐ", "ず", "づ", "ぶ", "ぷ",
                "げ", "ぜ", "で", "べ", "ぺ",
                "ご", "ぞ", "ど", "ぼ", "ぽ"]

    hiragana_ = ["ぱ", "ぴ", "ぷ", "ぺ", "ぽ"]

    orig_hiragana = ["か", "さ", "た", "は", "は",
                 "き", "し", "ち", "ひ", "ひ",
                 "く", "す", "つ", "ふ", "ふ",
                 "け", "せ", "て", "へ", "へ",
                 "こ", "そ", "と", "ほ", "ほ"]

    diagraph = ["ゃ", "ゅ", "ょ"]
    orig_diagraph = ["や", "ゆ", "よ"]

    hiragana_flag = False
    flag_ = False

    if end in hiragana:
        index = hiragana.index(end)
        if end in hiragana_:
            flag_ = True
        end = orig_hiragana[index]
        hiragana_flag = True

    diagraph_flag = False
    if end in diagraph:
        index = diagraph.index(end)
        end = orig_diagraph[index]
        diagraph_flag = True

    if start in hiragana:
        start = "small_key"
    if start in diagraph:
        start = "small_key"

    if start == "L3key" or start == "page":
        direct_list.extend(["DELAY"])


    direct_path_(g, direct_list, start, end)

    if hiragana_flag == True:
        direct_list.extend(direct_path_text_japanese(g, end, "small_key"))
        if flag_ == True:
            direct_list.extend([DS.CROSS])

    if diagraph_flag == True:
        direct_list.extend(direct_path_text_japanese(g, end, "small_key"))

    return direct_list

