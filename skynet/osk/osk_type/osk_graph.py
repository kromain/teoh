#!/usr/bin/env python3
#
# Copyright (c) 2014 Sony Network Entertainment Intl., all rights reserved.
#
# Djikstra algorithm implementation based on code from: http://www.dainf.ct.utfpr.edu.br/~kaestner/MatematicaDiscreta/Conteudo/Algoritmos/dijkstra2-exemplo6.2-pg290.py

from skynet.deci.dualshock import Buttons as DS

class osk_graph(object):
    """
    Serves as base class for all on-screen keyboard types. 

    Handles the interface mapping and navigation of on-screen keyboards. 
    """
    def __init__(self):
        self.graph = {}
        self.start = {}
        self.nodes = set()
        self.edges = {}
        self.direction = {}
        self.distances = {}
        self.case = {}
        self.type = {}


    def add_node(self, key, case="none", kind="none"):
        """
        Add *key* (node) to keyboard graph with attributes *case* and *kind*. 

        :param string key: The key value to be added 
        :param string case: The letter case of the key (e.g., lowercase, uppercase), default is none
        :param string kind: The type of key (e.g., L3, L2+TRIANGLE), default is none
        """
        self.nodes.add(key)
        self.case[key] = case
        self.type[key] = kind

    def add_edge(self, start, end, distance, direction):
        """ 
        Specifies distance and direction between two keys, *start* and *end*. 

        :param string start: Starting node
        :param string end: Destination node
        :param int distance: Distance weight between two keys; 0 if same node or 1 if neighbor. 
        :param direction: Direction from *start* to *end* (e.g., RIGHT, LEFT, UP, DOWN)
        :type button: :class:`Buttons`
        """
        self._add_edge(start, end, distance, direction)
        self._add_edge(end, start, distance, self.rev_direction(direction))

    def rev_direction(self, d):
        """
        Reverses direction to have two-way edges between keys
        """
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
        """
        Helper method for add_edge.
        Sets direction between two nodes. 
        Sets distance between two nodes. 
        """
        self.edges.setdefault(start, [])
        self.edges[start].append(end)
        self.direction[(start, end)] = direction
        self.distances[(start, end)] = distance

    def set_node(self, node_list, case="none", kind="none"):
        """
        Add multiple nodes from a list, specifying case and kind

        :param list node_list: list of nodes
        """
        for y in range(len(node_list)):
            if (len(node_list)) > 0:
                for x in range(len(node_list[y])):
                    self.add_node(node_list[y][x], case, kind)
            else:
                self.add_node(node_list[y], case, kind)



    def set_edge(self, map_array, case="none", kind="none"):
        """ 
        Set distance and direction between adjacent nodes on a list

        :param list map_array: A list mapping of keyboard layout
        """
        for node in self.nodes:
            self.add_edge(node, node, 0, [])
        
        self.set_node(map_array, case, kind)

        for y in range(len(map_array)-1):
            for x in range(len(map_array[y])-1):
                self.add_edge(map_array[y][x], map_array[y][x+1], 1, [DS.RIGHT])
                self.add_edge(map_array[y][x], map_array[y+1][x], 1, [DS.DOWN])

        bot_row = map_array[-1]
        for x in range(len(bot_row)-1):
            self.add_edge(bot_row[x], bot_row[x+1], 1, [DS.RIGHT])

    def set_edge_overlap(self, layer1, layer2):
        """ 
        Set distance and direction between two overlapping key layouts
        Distance is set to 0 and direction is empty. 

        Note that the size of layer1 must be smaller or equal to layer2. 

        :param list layer1: First layer to overlap. (e.g., lowercase layout)
        :param list layer2: Second layer to overlap. (e.g., uppercase layout)
        """
        for y in range(len(layer1)):
            for x in range(len(layer1[y])):
                self.add_edge(layer1[y][x], layer2[y][x], 0, [])  

    def set_edge_table(self, table, weight=1):
        """ 
        Set distance and direction between two nodes in table. 
        *table* is a dictionary, where the key represents the attributes of that key. 

        :param dict table: Table with keys to specify edges between neighbors
        :param int weight: Distance weight between two nodes, default is 1. 
        """
        for key in table.keys():
            self.add_edge(key, key, 0, [])
            for keydef in table[key]:
                target_key = keydef[0]
                direction = keydef[1]
                self.add_edge(key, target_key, weight, direction)

        for node in self.nodes:
            for nodex in self.nodes:
                if node.lower() == nodex.lower():
                    self.add_edge(node, node, 0, [])


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
    Returns shortest path between two nodes, *init_node* to *final_node*

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

    # Check corner cases
    if g.graph == "text":
        if g.type[start] == "L3":
            #direct_list.extend(direct_path(g, start, "L3key"))
            start = "L3key"

        if g.type[end] == "L2_" and g.type[start] != "L2_":
            direct_list.extend(direct_path(g, start, "page"))
            start = "page"
    
        if end != "page" and g.type[end] == "L2" :
            if g.type[start] == "L2_":
                direct_list.extend(direct_path(g, start, "page"))
                start = "page"

    if (g.type[end] == "L2" or g.type[start] == "L2_") and (g.type[start] != "L2" and g.type[start] != "L2_"):
        direct_list.extend([DS.L2 | DS.TRIANGLE])

    if (g.type[start] == "L2" or g.type[start] == "L2_") and (g.type[end] != "L2" and g.type[end] != "L2_"):
        direct_list.extend([DS.L2 | DS.TRIANGLE])


    if g.type[end] == "L3":
        direct_list.extend([DS.L3])

    if g.case[end] == "uppercase":
        direct_list.extend([DS.L2])


    path = shortest_path(g, start, end)
    for x in range(len(path)-1):
        direct_list.extend(g.direction[(path[x], path[x+1])])

    direct_list.extend([DS.CROSS])

    if g.graph == "text":
        # Handling case change after punctuation ending
        if g.case[end] == "end":
            direct_list.extend([DS.L2])
        if g.case[start] == "end" and end == " ":
            direct_list.extend([DS.L2])

    return direct_list


def nav_path(g, string):
    """
    Returns navigation path of a string for osk entry

    :param g: Specify the graph map 
    :type osk_graph: :class:`osk_graph`
    :param string: Text to be entered
    """
    nav_list = []
    string_List = []
    string_List = string

    if g.graph == "text":
        nav_list.extend([DS.L2])
    for x in range(len(string_List)-1):
            nav_list.extend(direct_path(g, string_List[x], string_List[x+1]))

    return nav_list