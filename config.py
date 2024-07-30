# RUN WITH CURSES
CURSES = False

# Number of prizes on the map
N_PRIZES = 10

# Number of enemies on the map
N_ENEMIES = 4

# Number of power-ups on the map
N_POWERS = 3

# Initial number of lives for the player
LIVES = 3

# Number of frames between enemy updates
ENEMY_FRAME = 4

# Duration of the power-up effect in seconds
POWER_DURATION = 5

# Sleep duration between frames in the game loop
SLEEP = 0.1

# Status codes for various game events
PRIZE = 0    # Code for collecting a prize
WON = 1        # Code for winning the level
OK = 2         # Code for a normal move
SCORE = 3      # Code for scoring points
LOST = 4       # Code for losing a life or the game
POWER = 5      # Code for activating a power-up
NORMAL = 6     # Code for normal status
EAT = 7        # Code for eating an enemy
