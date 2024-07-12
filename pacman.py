import numpy as np
import curses
import time
import keyboard

class Character:
    def __init__(self, x, y, symbol='@'):
        self.x = x
        self.y = y
        self.symbol = symbol

    def set_pos(self, x, y):
        self.x = x
        self.y = y

    def get_pos(self):
        return self.x, self.y

class Map:
    def __init__(self, map, width, height):
        self.map = np.array(map, dtype='<U1')
        self.width = width
        self.height = height

    def start_map(self, character):
        x, y = character.get_pos()
        self.x = x
        self.y = y
        self.map[y, x] = character.symbol

    def update_map(self, character):
        old_x, old_y = self.x, self.y
        self.map[old_y, old_x] = '-'
        x, y = character.get_pos()
        self.x = x
        self.y = y
        self.map[y, x] = character.symbol

class Game:
    def __init__(self, map_path: str):
        self.load_map(map_path)

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

        self.map = Map(map, width, height)

    def start(self, stdscr):
        x_start, y_start = self.start_pos()
        character = Character(x_start, y_start)

        self.map.start_map(character)
        self.print_map(stdscr)

        while True:
            x, y = character.get_pos()
            
            user_input = stdscr.getkey()
            if user_input == 'p':
                break
            elif user_input == 'q':
                if x > 0 and self.map.map[y, x-1] == '-':
                    character.set_pos(x-1, y)
            elif user_input == 'd':
                if x < self.map.width and self.map.map[y, x+1] == '-':
                    character.set_pos(x+1, y)
            elif user_input == 's':
                if y < self.map.height and self.map.map[y+1, x] == '-':
                    character.set_pos(x, y+1)
            elif user_input == 'z':
                if y > 0 and self.map.map[y-1, x] == '-':
                    character.set_pos(x, y-1)

            self.map.update_map(character)
            self.print_map(stdscr)

    def start_pos(self):
        while True:
            x, y = np.random.randint(self.map.width), np.random.randint(self.map.height)
            if self.map.map[y, x] == '-':
                return x, y

    def print_map(self, stdscr):
        stdscr.clear()
        for y, line in enumerate(self.map.map):
            line_str = ''.join(line) if isinstance(line, np.ndarray) else line
            stdscr.addstr(y, 0, line_str)
        stdscr.refresh()

if __name__ == '__main__':
    game = Game('maps/test_map.txt')
    curses.wrapper(game.start)
