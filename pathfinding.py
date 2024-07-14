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
    open_list = []
    closed_list = []

    start_node = Node(pos=start_pos)

    open_list.append(start_node)

    while open_list:
        current_node = min_node(open_list)
        open_list = remove_node(open_list, current_node)
        closed_list.append(current_node)
        # print(current_node, end_pos)
        # print('open')
        # for node in open_list:
        #     print(node, sep=', ')
        # print('closed')
        # for node in closed_list:
        #     print(node, sep=', ')

        if current_node.pos == end_pos:
            # print("here")
            path = []
            current = current_node
            while current is not None:
                path.append(current.move)
                current = current.parent
            return path[::-1]

        children_node = adjacent_nodes(current_node, map)
        # print('children')
        # for node in children_node:
        #     print(node, sep=', ')
        # print('\n')
        # print('\n')

        for child in children_node:
            if child in closed_list:
                continue
            child.g = current_node.g + 1
            child.h = ((child.pos[0] - end_pos[0]) ** 2) + ((child.pos[1] - end_pos[1]) ** 2)

            if avoid_pos:
                for pos in avoid_pos:
                    eps = 1e-6
                    dist = ((child.pos[0] - pos[0]) ** 2) + ((child.pos[1] - pos[1]) ** 2)
                    child.h += 1 / (eps + dist)
            child.f = child.g + child.h

            for node in open_list:
                if child == node and child.g > node.g:
                    continue

            open_list.append(child)

def min_node(open_list):
    node = open_list[0]
    for n in open_list:
        if node.f > n.f:
            node = n

    return node

def remove_node(open_list, node):
    new_list = []
    for n in open_list:
        if not node.__eq__(n):
            new_list.append(n)
    return new_list

def adjacent_nodes(node, map): # could pass only adjacent cases
    height = len(map)
    width = len(map[0])
    nodes = []
    x, y = node.pos[0], node.pos[1]
    if x > 0 and map[y, x-1] != '%':
        nodes.append(Node(parent=node, pos=(x-1, y), move=(-1, 0)))

    if x < width and map[y, x+1] != '%':
        nodes.append(Node(parent=node, pos=(x+1, y), move=(1, 0)))

    if y > 0 and map[y-1, x] != '%':
        nodes.append(Node(parent=node, pos=(x, y-1), move=(0, -1)))

    if y < height and map[y+1, x] != '%':
        nodes.append(Node(parent=node, pos=(x, y+1), move=(0, 1)))

    return nodes
