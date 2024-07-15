import numpy as np

from config import *

class Entity():
    def __init__(self, pos, symbol, category):
        self.pos = pos
        self.symbol = symbol
        self.category = category

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

    def add_entity(self, category, symbol):
        while True:
            x, y = np.random.randint(self.width), np.random.randint(self.height)
            if self.map[y, x] == '-':
                break
        self.map[y, x] = symbol

        entity = Entity((x, y), symbol, category)
        index = str(self.entities_counter)
        self.entities_counter += 1
        self.entities[index] = entity

        if category == 'player':
            self.player_id = index

        return OK
        
    def update_map(self, entity_id, move):
        is_valid_move, new_pos = self.is_valid(entity_id, move)

        status = OK

        if not is_valid_move:
            return status

        entity = self.entities[entity_id]
        current_pos = entity.pos

        if entity.category == 'enemy':
            player_pos = self.entities[self.player_id].pos
            if self.lost(player_pos, new_pos):
                return LOST

            self.move(entity_id, current_pos, new_pos)

            
        if entity.category == 'player':
            for index in self.get_entity_category('enemy'):
                enemy = self.entities[index]
                if self.lost(new_pos, enemy.pos):
                    return LOST
            
            self.move(entity_id, current_pos, new_pos)

            for index in self.get_entity_category('prize'):
                prize = self.entities[index]
                if new_pos == prize.pos:
                    del self.entities[index]
                    if not self.get_entity_category('prize'):
                        return self.won()
                    return SCORE
        


        for index in self.get_entity_category('prize'): # in case enemy leaves price
            prize = self.entities[index]
            x, y = prize.pos
            self.map[y, x] = prize.symbol

        return OK

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

        return is_within_map and is_case_valid, new_pos

    def closest_prize(self):
        player = self.entities[self.player_id]
        prize_ids = self.get_entity_category('prize')
        index = prize_ids[0]
        closest_prize = self.entities[index]
        for prize_id in prize_ids:
            prize = self.entities[prize_id]
            if player.dist(prize) < player.dist(closest_prize):
                index = prize_id
                closest_prize = prize
        return index, closest_prize
    
    def get_player(self):
        return self.player_id, self.entities[self.player_id]
    
    def print_map(self, stdscr=None, opt='', offset=0):
        if stdscr:
            stdscr.clear()
            stdscr.addstr(0, 0, opt)
            for y, line in enumerate(self.map):
                line_str = ''.join(line) if isinstance(line, np.ndarray) else line
                stdscr.addstr(y + offset, 0, line_str)
            stdscr.refresh()
        else:
            for line in self.map:
                print(''.join(line))