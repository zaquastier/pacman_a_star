import numpy as np
import curses
from time import sleep

from pathfinding import *
from map import *

DEBUG = False

class Game:
    def __init__(self, map_path: str):
        self.prizes = []
        self.ennemies = []
        self.n_prizes = 20
        self.n_enemies = 8
        self.n_powers = 10
        self.map_path = map_path
        self.load(map_path)
        self.lost = False
        self.won = False
        self.mode = 'capture'
        self.status = OK
        self.player = 'auto'
        self.score = 0

    def print_map(self, stdscr=None, opt='', offset=0):
        if stdscr:
            stdscr.clear()
            stdscr.addstr(0, 0, opt)
            for y, line in enumerate(self.map.map):
                line_str = ''.join(line) if isinstance(line, np.ndarray) else line
                stdscr.addstr(y + offset, 0, line_str)
            stdscr.addstr(y + offset + 1, 0, f'SCORE: {self.score}')
            stdscr.refresh()
        else:
            for line in self.map:
                print(''.join(line))
            print(f'SCORE: {self.score}')


    def a_star(self, stdscr=None):
        counter = 0

        while True:
            self.print_map(stdscr)
            
            while self.status == WON or self.status == LOST:
                continue
            # if self.status == WON:
            #     self.load('maps/simple_map.txt')
            
            if self.status == LOST or self.status == WON:
                self.load(self.map_path)

            player_id, player = self.map.get_player()
            prize_id, closest_prize = self.map.closest_to_eat(player_id, avoid_category='enemy')
            enemies = []
            enemy_ids = self.map.get_entity_category('enemy')
            for enemy_id in enemy_ids:
                enemies.append(self.map.entities[enemy_id])

            enemy_pos = []
            for enemy in enemies:
                enemy_pos.append(enemy.pos)
            
            if self.player == 'auto':
                path = path_to_prize(player.pos, closest_prize.pos, self.map, avoid_pos=enemy_pos)[1:]
                if path:
                    move = path[0]
                else:
                    move = (0, 0)

            elif self.player == 'manual':
                user_input = stdscr.getkey()
                if user_input == 'p':
                    break
                elif user_input == 'q':
                    move = (-1, 0)
                elif user_input == 'd':
                    move = (1, 0)
                elif user_input == 's':
                    move = (0, 1)
                elif user_input == 'z':
                    move = (0, -1)

            self.status = self.map.update_map(player_id, move)

            if self.status == SCORE: self.score += 1
            if self.status == POWER: self.score += 5
            if self.status == EAT: self.score += 10

            if self.status == SCORE:
                if self.mode == 'renew':
                    self.map.add_entity('prize', '.', prize_id)

            if counter % 4 == 0:
                for enemy_id, enemy in zip(enemy_ids, enemies):
                    path_to_player = path_to_prize(enemy.pos, player.pos, self.map)[1:]
                    enemy_move = path_to_player[0]
                    enemy_status = self.map.update_map(enemy_id, enemy_move)

                    if enemy_status == LOST:
                        self.status = LOST

                scareds = []
                scared_ids = self.map.get_entity_category('scared')
                for scared_id in scared_ids:
                    scareds.append(self.map.entities[scared_id])

                for scared_id, scared in zip(scared_ids, scareds):
                    house_id, closest_house = self.map.closest_category(scared_id, 'house')
                    path_to_house = path_to_prize(scared.pos, closest_house.pos, self.map, avoid_pos=[player.pos])[1:]
                    scared_move = (0, 0)
                    if path_to_house:
                        scared_move = path_to_house[0]
                    scared_status = self.map.update_map(scared_id, scared_move)

                    if scared_status == LOST:
                        self.status = LOST

                    
                counter = 0

            counter +=1 
            sleep(0.3)

    def start(self, stdscr):
        self.update_user(stdscr)

    def load(self, map_path):
        self.map = Map(map_path)
        self.map.add_entity('player', '@')
        self.map.add_entity('house', 'H')
        for _ in range(self.n_enemies):
            self.map.add_entity('enemy', '#')
        for _ in range(self.n_prizes):
            self.map.add_entity('prize', '.')
        for _ in range(self.n_powers):
            self.map.add_entity('power', 'O')

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

if __name__ == '__main__':
    game = Game('maps/map1.txt')
    if DEBUG == True:
        game.a_star()
    else:
        curses.wrapper(game.a_star)
