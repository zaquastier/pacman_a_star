import numpy as np
import curses
from time import sleep

from pathfinding import *
from map import *

DEBUG = True

class Game:
    def __init__(self, map_path: str):
        self.prizes = []
        self.ennemies = []
        self.n_prizes = 2
        self.n_enemies = 2
        self.n_powers = 1
        self.map_path = map_path
        self.load(map_path)
        self.lost = False
        self.won = False
        self.mode = 'renew'
        self.status = OK
        # self.mode = 'capture'



    def a_star(self, stdscr=None):
        counter = 0

        while True:
            
            for k, v in self.map.entities.items():
                print(k, v)
            self.map.print_map(stdscr)
            
            while self.status == WON or self.status == LOST:
                continue
            # if self.status == WON:
            #     self.load('maps/simple_map.txt')
            
            # if self.status == LOST:
            #     self.load(self.map_path)

            player_id, player = self.map.get_player()
            prize_id, closest_prize = self.map.closest_category(player_id, 'power')
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

            if self.status == POWER:
                if self.mode == 'renew':
                    self.map.add_entity('power', 'O', prize_id)

            if counter % 3 == 0:
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
                    path_to_house = path_to_prize(scared.pos, closest_house.pos, self.map)[1:]
                    scared_move = path_to_house[0]
                    scared_status = self.map.update_map(scared_id, scared_move)

                    if scared_status == LOST:
                        self.status = LOST

                    
                counter = 0

            counter +=1 
            sleep(0.25)

    def start(self, stdscr):
        self.update_user(stdscr)

    def load(self, map_path):
        self.map = Map(map_path)
        self.map.add_entity('player', '@')
        self.map.add_entity('house', 'H')
        for _ in range(self.n_enemies):
            self.map.add_entity('enemy', '#')
        for _ in range(self.n_prizes):
            self.map.add_entity('prize', 'A')
        for _ in range(self.n_powers):
            self.map.add_entity('power', 'O')

if __name__ == '__main__':
    game = Game('maps/simple_walls.txt')
    if DEBUG == True:
        game.a_star()
    else:
        curses.wrapper(game.a_star)
