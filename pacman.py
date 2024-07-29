import numpy as np
import curses
from time import sleep
import os
from pathlib import Path

from config import *
from pathfinding import *
from map import *

DEBUG = True

class Game:
    def __init__(self, map_folder: str):
        self.map_folder = map_folder
        self.levels = np.sort(os.listdir(self.map_folder))
        self.n_levels = len(self.levels)
        self.level = 0
        self.load()
        self.status = OK
        self.score = 0
        self.enemy_frame = 2
        self.lives = 3

    def a_star(self, stdscr=None):
        counter = 0 # to update enemy position

        while True:
            self.print_map(stdscr)
            
            while self.level == self.n_levels + 1 or self.lives <= 0:
                continue

            if self.status == WON:
                self.level += 1
                self.load()

            if self.status == LOST:
                self.lives =- 1
                if self.score < 100: self.score = 0
                else: self.score -= 100
                self.load()
            

            player_id, player = self.map.get_player()
            _, closest_prize = self.map.closest_to_eat(player_id, avoid_category='enemy')

            enemies = []
            enemy_ids = self.map.get_entity_category('enemy')
            for enemy_id in enemy_ids:
                enemies.append(self.map.entities[enemy_id])

            enemy_pos = []
            for enemy in enemies:
                enemy_pos.append(enemy.pos)
            
            # calculate path to prize while avoiding enemies
            path = path_to_prize(player.pos, closest_prize.pos, self.map, avoid_pos=enemy_pos)[1:] 
            if path: # only use first move of the provided path
                move = path[0]
            else:
                move = (0, 0)

            self.status = self.map.update_map(player_id, move)

            if self.status == WON: continue

            if self.status == SCORE: self.score += 1
            if self.status == POWER: self.score += 5
            if self.status == EAT: self.score += 10

            # update enemies
            if counter % self.enemy_frame == 0:

                for enemy_id, enemy in zip(enemy_ids, enemies):
                    # chase down the player
                    path_to_player = path_to_prize(enemy.pos, player.pos, self.map)[1:]
                    if path_to_player:
                        enemy_move = path_to_player[0]
                    else:
                        enemy_move = (0, 0)
                    enemy_status = self.map.update_map(enemy_id, enemy_move)

                    if enemy_status == LOST:
                        self.status = LOST
                        break

                # send scared enemies to the house
                scareds = []
                scared_ids = self.map.get_entity_category('scared')
                for scared_id in scared_ids:
                    scareds.append(self.map.entities[scared_id])

                for scared_id, scared in zip(scared_ids, scareds):
                    house = self.map.get_house()
                    path_to_house = path_to_prize(scared.pos, house.pos, self.map, avoid_pos=[player.pos])[1:]
                    scared_move = (0, 0)
                    if path_to_house:
                        scared_move = path_to_house[0]
                    scared_status = self.map.update_map(scared_id, scared_move)

                    if scared_status == LOST:
                        self.status = LOST

                    
                counter = 0

            counter +=1 
            sleep(SLEEP)


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
            for line in self.map.map:
                print(''.join(line))
            print(f'LEVEL: {self.level} \t SCORE: {self.score} \t {self.lives}UP')

    def load(self):
        
        map_path = Path(self.map_folder, self.levels[self.level])
        self.map = Map(map_path)
        self.map.add_entity('player', '@')
        self.map.add_entity('house', 'H')
        for _ in range(N_ENEMIES):
            self.map.add_entity('enemy', '#')
        for _ in range(N_PRIZES):
            self.map.add_entity('prize', '.')
        for _ in range(N_POWERS):
            self.map.add_entity('power', 'O')


if __name__ == '__main__':
    game = Game('maps/levels')
    if DEBUG == True:
        game.a_star()
    else:
        curses.wrapper(game.a_star)
