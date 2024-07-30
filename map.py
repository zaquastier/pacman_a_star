import numpy as np
from time import time

from config import *

class Entity():
    """
        A class to represent an entity in the game.

        Attributes:
        pos (tuple): The position of the entity on the map.
        symbol (str): The symbol representing the entity.
        category (str): The category of the entity (e.g., player, enemy).

        Methods:
        __init__(pos, symbol, category): Initializes the entity with position, symbol, and category.
        __eq__(other): Checks if two entities are at the same position.
        __str__(): Returns the string representation of the entity.
        dist(other): Calculates the squared distance to another entity.
    """
    def __init__(self, pos, symbol, category):
        self.pos = pos
        self.symbol = symbol
        self.category = category

    def __eq__(self, other):
        """
            Checks if two entities are at the same position.

            Args:
            other (Entity): The other entity to compare with.

            Returns:
            bool: True if both entities are at the same position, False otherwise.
        """
        return other.pos[0] == self.pos[0] and other.pos[1] == self.pos[1]
    
    def __str__(self):
        # for debugging
        return self.category + ' at:' + str(self.pos) + ' with ' + self.symbol
    
    def dist(self, other):
        """
            Calculates the squared distance to another entity.

            Args:
            other (Entity): The other entity to calculate the distance to.

            Returns:
            float: The squared distance to the other entity.
        """
        return ((self.pos[0] - other.pos[0]) ** 2) + ((self.pos[1] - other.pos[1]) ** 2)
    
class Map():
    """
        A class to represent the game map and its operations.

        Attributes:
        map (numpy array): The game map.
        width (int): The width of the map.
        height (int): The height of the map.
        player_id (str): The ID of the player entity.
        entities (dict): The dictionary of entities on the map.
        entities_counter (int): Counter for assigning unique IDs to entities.
        powered (bool): Indicates if power mode is active.
        dur (int): Duration of the power mode.

        Methods:
        __init__(map_path): Initializes the map with the specified map file.
        load_map(map_path): Loads the map from a file.
        add_entity(category, symbol, id): Adds a new entity to the map.
        closest_to_eat(player_id, avoid_category, eps): Finds the closest entity to eat.
        update_map(entity_id, move): Updates the map based on the entity's move.
        show_idles(): Shows idle entities on the map.
        power(): Activates the power mode.
        reactivate(scared_id): Reactivates a scared entity to enemy.
        reactivate_enemies(): Reactivates all scared entities to enemies.
        get_entity_category(category): Gets all entities of a specific category.
        lost(player_pos, enemy_pos): Checks if the player has lost.
        won(): Sets the game state to won.
        move(entity_id, current_pos, new_pos): Moves an entity on the map.
        is_valid(entity_id, move): Checks if a move is valid.
        get_player(): Gets the player entity.
        get_house(): Gets the house entity.
    """
    def __init__(self, map_path=None):
        self.load_map(map_path=map_path)
        self.player_id = None
        self.entities = {} 
        self.entities_counter = 0 # for ID
        self.powered = False
        self.dur = POWER_DURATION

    def load_map(self, map_path: str):
        """
            Loads the map from a file.

            Args:
            map_path (str): The path to the map file.
        """
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
        """
            Adds a new entity to the map.

            Args:
            category (str): The category of the entity.
            symbol (str): The symbol representing the entity.
            id (str, optional): The ID of the entity.

            Returns:
            int: Status code indicating success.
        """
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
        """
            Finds the best to eat for the player, avoiding specific categories if provided (check report for details)

            Args:
            player_id (str): The ID of the player entity.
            avoid_category (str, optional): The category of entities to avoid.
            eps (float, optional): A small value to prevent division by zero.

            Returns:
            tuple: The ID and the closest entity to eat.
        """
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
        """
            Updates the map based on the entity's move.

            Args:
            entity_id (str): The ID of the entity to move.
            move (tuple): The move to apply to the entity.

            Returns:
            int: Status code indicating the result of the move.
        """
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
        """
            Shows idle entities on the map.
        """
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
        """
            Activates the power mode.

            Returns:
            int: Status code indicating the activation of power mode.
        """
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
        """
            Reactivates a scared entity to enemy.

            Args:
            scared_id (str): The ID of the scared entity.
        """
        scared = self.entities[scared_id]
        enemy = Entity(scared.pos, '#', category='enemy')
        x, y = scared.pos
        self.map[y, x] = '#'
        self.entities[scared_id] = enemy
    
    def reactivate_enemies(self):
        """
            Reactivates all scared entities to enemies.

            Returns:
            int: Status code indicating the enemies are reactivated.
        """
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
        """
            Gets all entities of a specific category.

            Args:
            category (str): The category of entities to get.

            Returns:
            list: List of entity IDs in the specified category.
        """
        entities = []
        for k, v in self.entities.items():
            if v.category == category:
                entities.append(k)
        return entities

    def lost(self, player_pos, enemy_pos):
        """
            Checks if the player has lost (i.e., caught by an enemy).

            Args:
            player_pos (tuple): The position of the player.
            enemy_pos (tuple): The position of the enemy.

            Returns:
            bool: True if the player is caught, False otherwise.
        """
        if player_pos == enemy_pos:
            self.entities[self.player_id].symbol = '!'
            x, y = player_pos
            self.map[y, x] = '!'
            return True
        return False
    
    def won(self):
        """
            Sets the game state to won.

            Returns:
            int: Status code indicating the game is won.
        """
        self.entities[self.player_id].symbol = 'W'
        _, player = self.get_player()
        x, y = player.pos
        self.map[y, x] = 'W'
        return WON
        
    def move(self, entity_id, current_pos, new_pos):
        """
            Moves an entity on the map.

            Args:
            entity_id (str): The ID of the entity to move.
            current_pos (tuple): The current position of the entity.
            new_pos (tuple): The new position of the entity.
        """
        entity = self.entities[entity_id]
        x, y = current_pos
        self.map[y, x] = '-'
        self.entities[entity_id].pos = new_pos
        x, y = new_pos
        self.map[y, x] = entity.symbol
        
    def is_valid(self, entity_id, move):
        """
            Checks if a move is valid.

            Args:
            entity_id (str): The ID of the entity to move.
            move (tuple): The move to validate.

            Returns:
            tuple: A boolean indicating if the move is valid, and the new position.
        """
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
        """
            Gets the player entity.

            Returns:
            tuple: The player ID and the player entity.
        """
        return self.player_id, self.entities[self.player_id]
    
    def get_house(self):
        """
            Gets the house entity.

            Returns:
            Entity: The house entity.
        """
        return self.entities[self.get_entity_category('house')[0]]
