'''
This is where all the constants are stored.
Import these as 'c' for consistency.
'''

# Constants.
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
SCREEN_TITLE = 'Game'
WORLD_BOTTOM = -200

# Constants used to scale our sprites from their original size.
PIXEL_SCALING = 4
UI_SCALING = 4
SPRITE_PIXEL_SIZE = 128
GRID_PIXEL_SIZE = (SPRITE_PIXEL_SIZE * PIXEL_SCALING)

# Size of the map
MAP_WIDTH = 256 * PIXEL_SCALING
MAP_HEIGHT = 256 * PIXEL_SCALING

# Movement speed of player, in pixels per frame.
PLAYER_WALK_SPEED = 4.8
PLAYER_RUN_SPEED = 9.3
GRAVITY = 0.91
PLAYER_JUMP_SPEED = 25
UPDATES_PER_FRAME = 10

# How many pixels to keep as a minimum margin between
# the character and the edge of the screen.
LEFT_VIEWPORT_MARGIN = 300
RIGHT_VIEWPORT_MARGIN = 300
BOTTOM_VIEWPORT_MARGIN = 150
TOP_VIEWPORT_MARGIN = 100

PLAYER_START_X = 250
PLAYER_START_Y = 2000

# Constants used to track if the player is facing left or right.
RIGHT_FACING = 0
LEFT_FACING = 1

# Bullet speed, in pixels per frame.
BULLET_SPEED = 50

# Precalculated random numbers, used instead of random() for performance.
RANDOM_NUMBERS_8 = []