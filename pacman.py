import numpy as np
import curses
from time import sleep

from pathfinding import *
from map import *

class Game:
    def __init__(self, map_path: str):
        self.prizes = []
        self.ennemies = []
        self.n_prizes = 10
        self.n_enemies = 10
        self.load(map_path)
        self.lost = False
        self.won = False
        self.mode = 'renew'
        self.status = OK
        # self.mode = 'capture'



    def a_star(self, stdscr=None):
        counter = 0

        while True:

            self.map.print_map(stdscr)
            print(f'STATUS {self.status}')

            
            while self.status == WON or self.status == LOST:
                continue

            player_id, player = self.map.get_player()
            prize_id, closest_prize = self.map.closest_prize()
            enemies = []
            enemy_ids = self.map.get_entity_category('enemy')
            for enemy_id in enemy_ids:
                enemies.append(self.map.entities[enemy_id])

            enemy_pos = []
            for enemy in enemies:
                enemy_pos.append(enemy.pos)

            path = path_to_prize(player.pos, closest_prize.pos, self.map, avoid_pos=enemy_pos)[1:]

            move = path[0]

            self.status = self.map.update_map(player_id, move)

            # if status == SCORE:
            #     if self.mode == 'renew':
            #         self.map.load_prize(prize_id)

            # self.update_map(player_id, move)

            if counter % 5 == 0:
                for enemy_id, enemy in zip(enemy_ids, enemies):
                    path_to_player = path_to_prize(enemy.pos, player.pos, self.map)[1:]
                    enemy_move = path_to_player[0]
                    enemy_status = self.map.update_map(enemy_id, enemy_move)

                    if enemy_status == LOST:
                        self.status = LOST

                    counter = 0
                    

            counter +=1 
            sleep(0.05)

    def start(self, stdscr):
        self.update_user(stdscr)

    def load(self, map_path):
        self.map = Map(map_path)
        self.map.add_entity('player', '@')
        for _ in range(self.n_enemies):
            self.map.add_entity('enemy', '#')
        for _ in range(self.n_prizes):
            self.map.add_entity('prize', 'A')

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
    game = Game('maps/simple_walls.txt')
    # curses.wrapper(game.a_star)
    game.a_star()
