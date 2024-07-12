import numpy as np
import curses

class Game:
    def __init__(self, map_path: str):
        self.load(map_path)

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

    def update_user(self, stdscr):
        while True:
            self.print_map(stdscr)

            x, y = self.x, self.y
            
            user_input = stdscr.getkey()
            if user_input == 'p':
                break
            elif user_input == 'q':
                if x > 0 and self.map[y, x-1] == '*':
                    break
                if x > 0 and self.map[y, x-1] == '-':
                    self.update_map(x-1, y)
            elif user_input == 'd':
                if x < self.width and self.map[y, x+1] == '*':
                    break
                if x < self.width and self.map[y, x+1] == '-':
                    self.update_map(x+1, y)
            elif user_input == 's':
                if y < self.height and self.map[y+1, x] == '*':
                    break
                if y < self.height and self.map[y+1, x] == '-':
                    self.update_map(x, y+1)
            elif user_input == 'z':
                if y > 0 and self.map[y-1, x] == '*':
                    break
                if y > 0 and self.map[y-1, x] == '-':
                    self.update_map(x, y-1)

    def update_map(self, x, y):
        old_x, old_y = self.x, self.y
        self.map[old_y, old_x] = '-'
        self.x = x
        self.y = y
        self.map[y, x] = self.symbol

    def print_map(self, stdscr):
        stdscr.clear()
        for y, line in enumerate(self.map):
            line_str = ''.join(line) if isinstance(line, np.ndarray) else line
            stdscr.addstr(y, 0, line_str)
        stdscr.refresh()

if __name__ == '__main__':
    game = Game('maps/test_map.txt')
    curses.wrapper(game.start)
