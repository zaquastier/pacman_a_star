import numpy as np
import curses
from time import sleep

from pathfinding import *

    
class Game:
    def __init__(self, map_path: str):
        self.prizes = []
        self.n_prizes = 10
        self.load(map_path)
        self.lost = False
        self.won = False
        # self.mode = 'renew'
        self.mode = 'capture'

    def dist(self, other):
        return ((self.x - other[0]) ** 2) + ((self.y - other[1]) ** 2)

    def closest_prize(self):
        closest = self.prizes[0]
        index = 0
        for i in range(1, len(self.prizes)):
            if self.dist(self.prizes[i]) < self.dist(closest):
                index = i
                closest = self.prizes[i]
        return index, closest


    def a_star(self, stdscr):
    # def a_star(self):
        counter = 0

        while True:

            self.print_map(stdscr)
            
            while self.won:
                continue
            while(self.lost):
                continue

            char_pos = (self.x, self.y)
            prize_index, prize_pos = self.closest_prize() # shouldnt be closest but the one with lowest distance
            enemy_pos = (self.enemy_x, self.enemy_y)


            path = path_to_prize(char_pos, prize_pos, self.map, avoid_pos=enemy_pos)[1:]
            # print(char_pos)
            # print(self.prizes)
            # print(prize_index, prize_pos)
            # print(enemy_pos)
            # print('\n')
            move = path[0]
            x, y = move[0], move[1]


            if self.map[self.y + y, self.x + x] == self.prize:
                if self.mode == 'renew':
                    self.load_prize(prize_index)
                elif self.mode == 'capture':
                    self.prizes.pop(prize_index)

            self.update_map(self.x + x, self.y + y)

            if counter % 5 == 0:
                current_player_pos = (self.x, self.y)
                path_to_enemy = path_to_prize(enemy_pos, current_player_pos, self.map)[1:]

                x_move = path_to_enemy[0][0]
                y_move = path_to_enemy[0][1]

                if self.enemy_x + x_move > 0 \
                and self.enemy_x + x_move < self.width \
                and self.enemy_y + y_move > 0 \
                and self.enemy_y + y_move < self.height \
                and self.map[self.enemy_y + y_move, self.enemy_x + x_move] != '%':
                    self.update_map(self.enemy_x + x_move, self.enemy_y + y_move, 'enemy')
                counter = 0

            counter +=1 
            sleep(0.05)

    def start(self, stdscr):
        self.update_user(stdscr)

    def load(self, map_path):
        self.load_map(map_path)
        self.load_character()
        self.load_enemy()
        self.init_prizes()

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

    def load_enemy(self):
        self.enemy = '#'
        while True:
            x, y = np.random.randint(self.width), np.random.randint(self.height)
            if self.map[y, x] == '-':
                break
        self.enemy_x = x
        self.enemy_y = y
        self.map[y, x] = self.enemy

    def init_prizes(self,):
        self.prize = 'A'
        for _ in range(self.n_prizes):
            while True:
                x, y = np.random.randint(self.width), np.random.randint(self.height)
                if self.map[y, x] == '-':
                    break
            self.prizes.append((x, y))
            self.map[y, x] = self.prize

    def load_prize(self, index):
        self.prize = 'A'
        while True:
            x, y = np.random.randint(self.width), np.random.randint(self.height)
            if self.map[y, x] == '-':
                break
        self.prizes[index] = (x, y)
        self.map[y, x] = self.prize
    
    def update_user(self, stdscr):

        counter = 0
        while True:
            self.print_map(stdscr)
            while(self.lost):
                continue

            x, y = self.x, self.y
            
            user_input = stdscr.getkey()
            if user_input == 'p':
                break
            elif user_input == 'q':
                if x > 0 and self.map[y, x-1] == self.prize:
                    self.update_map(x-1, y)
                    self.load_prize()
                if x > 0 and self.map[y, x-1] != '%':
                    self.update_map(x-1, y)
            elif user_input == 'd':
                if x < self.width and self.map[y, x+1] == self.prize:
                    self.update_map(x+1, y)
                    self.load_prize()
                if x < self.width and self.map[y, x+1] != '%':
                    self.update_map(x+1, y)
            elif user_input == 's':
                if y < self.height and self.map[y+1, x] == self.prize:
                    self.load_prize()
                    self.update_map(x, y+1)
                if y < self.height and self.map[y+1, x] != '%':
                    self.update_map(x, y+1)
            elif user_input == 'z':
                if y > 0 and self.map[y-1, x] == self.prize:
                    self.load_prize()
                    self.update_map(x, y-1)
                if y > 0 and self.map[y-1, x] != '%':
                    self.update_map(x, y-1)

            if counter % 1e1 == 0:
                x_move = np.random.randint(-1, 2)
                y_move = np.random.randint(-1, 2) if x_move == 0 else 0
                if self.enemy_x + x_move > 0 \
                and self.enemy_x + x_move < self.width \
                and self.enemy_y + y_move > 0 \
                and self.enemy_y + y_move < self.height \
                and self.map[self.enemy_y + y_move, self.enemy_x + x_move] == '-':
                    self.update_map(self.enemy_x + x_move, self.enemy_y + y_move, 'enemy')
                counter = 0
            counter +=1 

    def update_map(self, x, y, entity='player'):
        for prize_x, prize_y in self.prizes:
            self.map[prize_y, prize_x] = self.prize

        if not self.prizes:
            self.symbol = 'W'
            self.won = True

        if entity == 'enemy':
            old_x, old_y = self.enemy_x, self.enemy_y
            if x == self.enemy_x and y == self.enemy_y:
                self.symbol = '!'
                self.lost = True
            self.map[old_y, old_x] = '-'
            self.enemy_x = x
            self.enemy_y = y
            self.map[y, x] = self.enemy

            
        if entity == 'player':
            old_x, old_y = self.x, self.y
            if x == self.enemy_x and y == self.enemy_y:
                self.symbol = '!'
                self.lost = True
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
    game = Game('maps/simple_walls.txt')
    curses.wrapper(game.a_star)
    # game.a_star()
