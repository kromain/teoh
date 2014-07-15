#!/usr/bin/env python3
#
# Copyright (c) 2014 Sony Network Entertainment Intl., all rights reserved.
#
# Djikstra algorithm implementation based on code from: http://www.dainf.ct.utfpr.edu.br/~kaestner/MatematicaDiscreta/Conteudo/Algoritmos/dijkstra2-exemplo6.2-pg290.py

from skynet.deci.dualshock import Buttons as DS

class osk_graph(object):
    """ generic graph for mapping OSKs """

    def __init__(self):
        self.nodes = set()
        self.edges = {}
        self.direction = {}
        self.distances = {}
        self.case = {}

    def add_node(self, value, case):
        self.nodes.add(value)
        self.add_case(value, case)

    def add_case(self, node, case):
        self.case[node] = case

    def add_edge(self, start, end, distance, direction):
        """ edge between two nodes, specifying distance and direction """
        self._add_edge(start, end, distance, direction)
        self._add_edge(end, start, distance, self.rev_direction(direction))

    def rev_direction(self, d):
        if d == [DS.DOWN]:
            return [DS.UP]
        elif d == [DS.UP]:
            return [DS.DOWN]
        elif d == [DS.RIGHT]:
            return [DS.LEFT]
        elif d == [DS.LEFT]:
            return [DS.RIGHT]
        elif d == []:
            return []

    def _add_edge(self, start, end, distance, direction):
        self.edges.setdefault(start, [])
        self.edges[start].append(end)
        self.direction[(start, end)] = direction
        self.distances[(start, end)] = distance

    def set_edge(self, map_array):
        """ set distance and direction between adjacent nodes in 2D map array """
        for node in self.nodes:
            self.add_edge(node, node, 0, [])

        for y in range(len(map_array)-1):
            for x in range(len(map_array[y])-1):
                self.add_edge(map_array[y][x], map_array[y][x+1], 1, [DS.RIGHT])
                self.add_edge(map_array[y][x], map_array[y+1][x], 1, [DS.DOWN])

        bot_row = map_array[-1]
        for x in range(len(bot_row)-1):
            self.add_edge(bot_row[x], bot_row[x+1], 1, [DS.RIGHT])

    def set_edge_overlap(self, layer1, layer2):
        """ Set distance and direction between two overlapping osk layers """

        for y in range(len(layer1)):
            for x in range(len(layer1[y])):
                self.add_edge(layer1[y][x], layer2[y][x], 0, [])  

    def set_edge_table(self, table):
        """ Set distance and direction between two nodes in table """
        
        for key in table.keys():
            self.add_edge(key, key, 0, [])
            for keydef in table[key]:
                target_key = keydef[0]
                direction = keydef[1]
                self.add_edge(key, target_key, 1, direction)

        for node in self.nodes:
            for nodex in self.nodes:
                if node.lower() == nodex.lower():
                    self.add_edge(node, node, 0, [])


def dijkstra(graph, init_node):
    """ implementation of dijkstra to find shortest path"""
    # dictionary of visited nodes with distance
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
                # If distance is less than previously recorded distance
                elif visited[node] < visited[min_node]:
                    min_node = node
 
        if min_node is None:
            break
        
        # Remove and return best node
        nodes.remove(min_node)
        curr_weight = visited[min_node]
        
        for edge in graph.edges[min_node]:
            weight = graph.distances[(min_node, edge)] + curr_weight
            # If shorter path has been found
            if edge not in visited or weight < visited[edge]:
                visited[edge] = weight
                path[edge] = min_node

    return visited, path
 
def shortest_path(graph, init_node, final_node):
    track = [final_node]
    distances, paths = dijkstra(graph, init_node)

    while final_node != init_node:
        track.append(paths[final_node])
        final_node = paths[final_node]
 
    track.reverse()
    return track

def direct_path(g, start, end):
    """ return list of directions of path between start and end nodes
        (e.g [DS.LEFT, DS.RIGHT]) 
    """
    direct_list = []
    path = shortest_path(g, start, end)

    # Iterate through shortest path from start to end
    for x in range(len(path)-1):
        # Continuously add directions between next nodes 
        direct_list.extend(g.direction[(path[x], path[x+1])])

    # Check for upper case letters
    # Click shift (DS.L2) to capitalize
    if g.case[end] == "upper":
        direct_list.extend([DS.L2])

    if (g.case[end] == "l2_chars") and (g.case[start] != "l2_chars"):
        direct_list.extend([DS.L2 | DS.TRIANGLE])

    if (g.case[start] == "l2_chars") and (g.case[end] != "l2_chars"):
        direct_list.extend([DS.L2 | DS.TRIANGLE])

    # Select final node by adding cross button to end of list
    direct_list.extend([DS.CROSS])

    # Check for ending punctuation marks
    if g.case[end] == "end":
        direct_list.extend([DS.L2])

    return direct_list

def nav_path(g, string):
    """ return list of directions for path of string """
    nav_list = []
    string_List = []
    string_List = string

    for x in range(len(string_List)-1):
            nav_list.extend(direct_path(g, string_List[x], string_List[x+1]))

    return nav_list