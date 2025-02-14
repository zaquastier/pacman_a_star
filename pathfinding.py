from config import *

class Node():
    def __init__(self, parent=None, pos=None, move=None):
        self.parent = parent
        self.pos = pos

        self.move = move

        self.g = 0
        self.h = 0
        self.f = 0

    def __str__(self):
        return str(self.pos)

    def __eq__(self, other):
        return self.pos == other.pos

def path_to_prize(start_pos, end_pos, map, avoid_pos=None):
    """
        Find the path from start_pos to end_pos on the map, avoiding positions in list avoid_pos if provided.
        
        Args:
        start_pos (tuple): The starting position on the map.
        end_pos (tuple): The target position on the map.
        map (Map): The map object containing the layout.
        avoid_pos (list of positions, optional): Positions to avoid during pathfinding.
        
        Returns:
        list: A list of moves representing the path from start_pos to end_pos.
    """
    open_list = []
    closed_list = []

    start_node = Node(pos=start_pos)

    open_list.append(start_node)

    while open_list:
        current_node = min_node(open_list)
        open_list = remove_node(open_list, current_node)
        closed_list.append(current_node)

        if current_node.pos == end_pos:
            path = []
            current = current_node
            while current is not None:
                path.append(current.move)
                current = current.parent
            return path[::-1]

        children_node = adjacent_nodes(current_node, map)

        for child in children_node:
            if child in closed_list:
                continue
            child.g = current_node.g + 1
            child.h = ((child.pos[0] - end_pos[0]) ** 2) + ((child.pos[1] - end_pos[1]) ** 2)

            if avoid_pos:
                for pos in avoid_pos:
                    eps = 1e-6
                    dist = ((child.pos[0] - pos[0]) ** 2) + ((child.pos[1] - pos[1]) ** 2)
                    child.h += 20 / (eps + dist)
            child.f = child.g + child.h

            for node in open_list:
                if child == node and child.g > node.g:
                    continue

            open_list.append(child)

def min_node(open_list):
    """
        Find the node with the smallest f value in the open list.
        
        Args:
        open_list (list): The list of nodes to evaluate.
        
        Returns:
        Node: The node with the smallest f value.
    """
    node = open_list[0]
    for n in open_list:
        if node.f > n.f:
            node = n

    return node

def remove_node(open_list, node):
    """
        Remove a node from the open list.
        
        Args:
        open_list (list): The list of nodes to evaluate.
        node (Node): The node to be removed.
        
        Returns:
        list: The updated open list with the node removed.
    """
    new_list = []
    for n in open_list:
        if not node.__eq__(n):
            new_list.append(n)
    return new_list

def adjacent_nodes(node, map): # could pass only adjacent cases
    """
        Get the adjacent nodes for a given node on the map.
        
        Args:
        node (Node): The current node.
        map (Map): The map object containing the layout.
        
        Returns:
        list: A list of adjacent nodes.
    """
    height = map.height
    width = map.width
    nodes = []
    x, y = node.pos[0], node.pos[1]
    if x > 0 and map.map[y, x-1] != '%':
        nodes.append(Node(parent=node, pos=(x-1, y), move=(-1, 0)))

    if x < width and map.map[y, x+1] != '%':
        nodes.append(Node(parent=node, pos=(x+1, y), move=(1, 0)))

    if y > 0 and map.map[y-1, x] != '%':
        nodes.append(Node(parent=node, pos=(x, y-1), move=(0, -1)))

    if y < height and map.map[y+1, x] != '%':
        nodes.append(Node(parent=node, pos=(x, y+1), move=(0, 1)))

    return nodes
