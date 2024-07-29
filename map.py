import numpy as np
from time import time

from config import *

class Entity():
    def __init__(self, pos, symbol, category):
        self.pos = pos
        self.symbol = symbol
        self.category = category
        self.power_timer = time()

    def __eq__(self, other):
        return other.pos[0] == self.pos[0] and other.pos[1] == self.pos[1]
    
    def __str__(self):
        return self.category + ' at:' + str(self.pos) + ' with ' + self.symbol
    
    def dist(self, other):
        return ((self.pos[0] - other.pos[0]) ** 2) + ((self.pos[1] - other.pos[1]) ** 2)
    
class Map():
    def __init__(self, map_path=None):
        self.load_map(map_path=map_path)
        self.player_id = None
        self.entities = {} 
        self.entities_counter = 0 # for ID
        self.powered = False
        self.dur = 10

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

    def add_entity(self, category, symbol, id=None):
        while True:
            x, y = np.random.randint(self.width), np.random.randint(self.height)
            if self.map[y, x] == '-':
                break
        self.map[y, x] = symbol

        entity = Entity((x, y), symbol, category)
        if id:
            index = id
        index = str(self.entities_counter)
        self.entities_counter += 1
        self.entities[index] = entity

        if category == 'player':
            self.player_id = index

        return OK
    
    def closest_to_eat(self, player_id, avoid_category=None, eps=1e-6):
        player = self.entities[player_id]

        categories = ['prize', 'power', 'scared']
        ids = [] 
        for category in categories:
            ids += self.get_entity_category(category)

        avoid_ids = self.get_entity_category(avoid_category)

        index = ids[0]
        closest = self.entities[index]
        dist_to_closest = player.dist(closest)
        for avoid_id in avoid_ids:
                avoid_entity = self.entities[avoid_id]
                dist_to_closest += 20 / (avoid_entity.dist(closest) + eps)

        for id in ids:
            other = self.entities[id]
            dist_to_other = player.dist(other)
            if other.category == 'scared':
                dist_to_other /= 10
            for avoid_id in avoid_ids:
                avoid_entity = self.entities[avoid_id]
                dist_to_other += 20 / (avoid_entity.dist(other) + eps)
            if dist_to_other < dist_to_closest:
                index = id
                closest = other
                dist_to_closest = dist_to_other
        return index, closest
        
    def update_map(self, entity_id, move):
        is_valid_move, new_pos = self.is_valid(entity_id, move)

        status = OK

        if not is_valid_move:
            return status

        self.show_idles()

        entity = self.entities[entity_id]
        current_pos = entity.pos

        if entity.category == 'enemy':
            player_pos = self.entities[self.player_id].pos
            if self.lost(player_pos, new_pos):
                return LOST

            self.move(entity_id, current_pos, new_pos)


        if entity.category == 'scared':

            player_pos = self.entities[self.player_id].pos
            if new_pos == player_pos:
                del self.entities[entity_id]
                return EAT
            
            for index in self.get_entity_category('house'):
                house = self.entities[index]
                if new_pos == house.pos:
                    self.reactivate(entity_id)

            else:
                self.move(entity_id, current_pos, new_pos)

            
        if entity.category == 'player':
            for index in self.get_entity_category('enemy'):
                enemy = self.entities[index]
                if self.lost(new_pos, enemy.pos):
                    return LOST
            for index in self.get_entity_category('scared'):
                scared = self.entities[index]
                if new_pos == scared.pos:
                    del self.entities[index]
                    self.move(entity_id, current_pos, new_pos)
                    return EAT
            

            for index in self.get_entity_category('prize'):
                prize = self.entities[index]
                if new_pos == prize.pos:
                    self.move(entity_id, current_pos, new_pos)
                    del self.entities[index]
                    if not self.get_entity_category('prize'):
                        return self.won()
                    return SCORE
            
                            
            for index in self.get_entity_category('power'):
                power = self.entities[index]
                if new_pos == power.pos:
                    del self.entities[index]
                    self.move(entity_id, current_pos, new_pos)
                    return self.power()
        
            self.move(entity_id, current_pos, new_pos)

        if self.powered and time() - self.time > self.dur:
            self.reactivate_enemies()

        return OK
    
    def show_idles(self):
        idle_categories = ['house', 'prize', 'power']
        idle_ids = []
        for category in idle_categories:
            idle_ids += self.get_entity_category(category)
        for idle_id in idle_ids:
            idle = self.entities[idle_id]
            occupied = False
            for entity_id, entity in self.entities.items():
                if entity.pos == idle.pos and entity_id != idle_id:
                    occupied = True
            if not occupied:
                x, y = idle.pos
                self.map[y, x] = idle.symbol

    def power(self):
        self.powered = True
        self.time = time()
        enemy_ids = self.get_entity_category('enemy')
        for enemy_id in enemy_ids:
            enemy = self.entities[enemy_id]
            scared = Entity(enemy.pos, '&', category='scared')
            x, y = enemy.pos
            self.map[y, x] = '&'
            self.entities[enemy_id] = scared
        return POWER
    
    def reactivate(self, scared_id):
        scared = self.entities[scared_id]
        enemy = Entity(scared.pos, '#', category='enemy')
        x, y = scared.pos
        self.map[y, x] = '#'
        self.entities[scared_id] = enemy
    
    def reactivate_enemies(self):
        self.powered = False
        scared_ids = self.get_entity_category('scared')
        for scared_id in scared_ids:
            scared = self.entities[scared_id]
            enemy = Entity(scared.pos, '#', category='enemy')
            x, y = scared.pos
            self.map[y, x] = '#'
            self.entities[scared_id] = enemy
        return NORMAL

    def get_entity_category(self, category):
        entities = []
        for k, v in self.entities.items():
            if v.category == category:
                entities.append(k)
        return entities

    def lost(self, player_pos, enemy_pos):
        if player_pos == enemy_pos:
            self.entities[self.player_id].symbol = '!'
            x, y = player_pos
            self.map[y, x] = '!'
            return True
        return False
    
    def won(self):
        self.entities[self.player_id].symbol = 'W'
        _, player = self.get_player()
        x, y = player.pos
        self.map[y, x] = 'W'
        return WON
        
    def move(self, entity_id, current_pos, new_pos):
        entity = self.entities[entity_id]
        x, y = current_pos
        self.map[y, x] = '-'
        self.entities[entity_id].pos = new_pos
        x, y = new_pos
        self.map[y, x] = entity.symbol
        
    def is_valid(self, entity_id, move):
        entity = self.entities[entity_id]
        x, y = entity.pos
        delta_x, delta_y = move

        new_pos = x + delta_x, y + delta_y

        is_within_map = new_pos[0] > 0 and new_pos[0] < self.width and new_pos[1] > 0 and new_pos[1] < self.height
        is_case_valid = self.map[new_pos[1], new_pos[0]] != '%'

        if entity.category == 'enemy':
            is_case_valid &= self.map[new_pos[1], new_pos[0]] != entity.symbol

        if entity.category == 'scared':
            is_case_valid &= self.map[new_pos[1], new_pos[0]] != entity.symbol

        return is_within_map and is_case_valid, new_pos
    
    def get_player(self):
        return self.player_id, self.entities[self.player_id]
    
    def get_house(self):
        return self.entities[self.get_entity_category('house')[0]]
