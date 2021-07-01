'''
For all the items, including weapons, present in the game.

Import this as 'i' for consistency.
'''

import arcade
import os
import random
from pyglet.gl import GL_NEAREST
import math
import game_constants as c
import game_player as p
import game_functions as f
import game_audio as a


class Weapon(arcade.Sprite):
    '''The base weapon class.'''
    def __init__(self):
        # Set up parent class.
        super().__init__()