import numpy as np
import curses
from time import sleep

class Node():
    def __init__(self, parent=None, x=None, y=None, move_x=0, move_y=0):
        self.parent = parent
        self.x = x
        self.y = y

        self.move_x = move_x
        self.move_y = move_y

        self.g = 0
        self.h = 0
        self.f = 0

    def __str__(self):
        return f'{self.x}, {self.y}'

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y
    
class Game:
    def __init__(self, map_path: str):
        self.load(map_path)

    def a_star(self, stdscr):

        while True:
            path = self.path_to_prize()
            path = path[:-1]
            
            for move in path:
                x, y = move[0], move[1]
                self.print_map(stdscr)

                if self.map[self.y + y, self.x + x] == '*':
                        self.update_map(self.x + x, self.y + y)
                        self.load_prize()
                if self.map[self.y + y, self.x + x] == '-':
                    self.update_map(self.x + x, self.y + y)
                sleep(0.5)

            self.print_map(stdscr)

    def start(self, stdscr):
        self.update_user(stdscr)

    def load(self, map_path):
        self.load_map(map_path)
        self.load_character()
        self.load_prize()

    def load_map(self, map_path: str):
        with open(map_path, 'r') as f:
            map = []
            height = 0
            for l in f:
                line = l.strip()
                if line:
                    width = len(line)
                    height += 1
                    map.append(list(line))

        self.map = np.array(map, dtype='<U1')
        self.width = width
        self.height = height

    def load_character(self):
        self.symbol = '@'
        while True:
            x, y = np.random.randint(self.width), np.random.randint(self.height)
            if self.map[y, x] == '-':
                break
        self.x = x
        self.y = y
        self.map[y, x] = self.symbol

    def load_prize(self):
        self.prize = '*'
        while True:
            x, y = np.random.randint(self.width), np.random.randint(self.height)
            if self.map[y, x] == '-':
                break
        self.prize_x = x
        self.prize_y = y
        self.map[y, x] = self.prize

    def path_to_prize(self):
        open_list = []
        closed_list = []

        start_node = Node(x=self.x, y=self.y)

        open_list.append(start_node)

        while open_list:
            current_node = self.min_node(open_list)
            open_list = self.remove_node(open_list, current_node)
            closed_list.append(current_node)

            print(f"current node: {current_node}")
            
            if current_node.x == self.prize_x and current_node.y == self.prize_y:
                path = []
                current = current_node
                while current is not None:
                    path.append((current.move_x, current.move_y))
                    current = current.parent
                return path

            children_node = self.adjacent_nodes(current_node)

            for child in children_node:
                print(f'child: {child}')
                if child in closed_list:
                    continue
                child.g = current_node.g + 1
                child.h = ((child.x - self.prize_x) ** 2) + ((child.y - self.prize_y) ** 2)
                child.f = child.g + child.h

                for node in open_list:
                    if child == node and child.g > node.g:
                        continue

                open_list.append(child)

    def min_node(self, open_list):
        node = open_list[0]
        for n in open_list:
            if node.f > n.f:
                node = n

        return node

    def remove_node(self, open_list, node):
        new_list = []
        for n in open_list:
            if not node.__eq__(n):
                new_list.append(n)

        return new_list

    def adjacent_nodes(self, node):
        nodes = []
        x, y = node.x, node.y
        if x > 0 and (self.map[y, x-1] == '-' or self.map[y, x-1] == self.prize):
            nodes.append(Node(parent=node, x=x-1, y=y, move_x=-1, move_y=0))
        if x < self.width and (self.map[y, x+1] == '-' or self.map[y, x+1] == self.prize):
            nodes.append(Node(parent=node, x=x+1, y=y, move_x=1, move_y=0))
        if y > 0 and (self.map[y-1, x] == '-' or self.map[y-1, x] == self.prize):
            nodes.append(Node(parent=node, x=x, y=y-1, move_x=0, move_y=-1))
        if y < self.height and (self.map[y+1, x] == '-' or self.map[y+1, x] == self.prize):
            nodes.append(Node(parent=node, x=x, y=y+1, move_x=0, move_y=1))

        return nodes
    
    def update_user(self, stdscr):
        while True:
            self.print_map(stdscr)

            x, y = self.x, self.y
            
            user_input = stdscr.getkey()
            if user_input == 'p':
                break
            elif user_input == 'q':
                if x > 0 and self.map[y, x-1] == '*':
                    self.update_map(x-1, y)
                    self.load_prize()
                if x > 0 and self.map[y, x-1] == '-':
                    self.update_map(x-1, y)
            elif user_input == 'd':
                if x < self.width and self.map[y, x+1] == '*':
                    self.update_map(x+1, y)
                    self.load_prize()
                if x < self.width and self.map[y, x+1] == '-':
                    self.update_map(x+1, y)
            elif user_input == 's':
                if y < self.height and self.map[y+1, x] == '*':
                    self.load_prize()
                    self.update_map(x, y+1)
                if y < self.height and self.map[y+1, x] == '-':
                    self.update_map(x, y+1)
            elif user_input == 'z':
                if y > 0 and self.map[y-1, x] == '*':
                    self.load_prize()
                    self.update_map(x, y-1)
                if y > 0 and self.map[y-1, x] == '-':
                    self.update_map(x, y-1)

    def update_map(self, x, y):
        old_x, old_y = self.x, self.y
        self.map[old_y, old_x] = '-'
        self.x = x
        self.y = y
        self.map[y, x] = self.symbol

    def print_map(self, stdscr, opt='', offset=0):
        stdscr.clear()
        stdscr.addstr(0, 0, opt)
        for y, line in enumerate(self.map):
            line_str = ''.join(line) if isinstance(line, np.ndarray) else line
            stdscr.addstr(y + offset, 0, line_str)
        stdscr.refresh()

if __name__ == '__main__':
    game = Game('maps/simple_map.txt')
    curses.wrapper(game.a_star)
