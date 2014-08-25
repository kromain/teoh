#!/usr/bin/env python3
#
# Copyright (c) 2014 Sony Network Entertainment Intl., all rights reserved.

from skynet.deci.dualshock import Buttons as DS

class osk_graph(object):
    """
    Serves as base class for all on-screen keyboard types.

    Handles the interface mapping and navigation of on-screen keyboards.
    """
    def __init__(self):
        self.graph = {}
        self.lang = "en_"
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

        self.set_node(map_array, case, kind)

        for y in range(len(map_array)):
            for x in range(len(map_array[y])-1):
                self.add_edge(map_array[y][x], map_array[y][x+1], 1, [DS.RIGHT])
        
        for y in range(len(map_array)-1):
            for x in range(len(map_array[y])):
                self.add_edge(map_array[y][x], map_array[y+1][x], 1, [DS.DOWN])


        for node in self.nodes:
            self.add_edge(node, node, 0, [])

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

