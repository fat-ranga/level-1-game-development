'''
Where all the game's general functions are stored.

Import this as 'f' for consistency.
'''

import arcade
import os
import random
from pyglet.gl import GL_NEAREST
import math
import game_constants as c


def load_texture_pair(filename):
    '''Loads a texture pair, with the second being a mirror image.'''
    return [
        arcade.load_texture(filename),
        arcade.load_texture(filename, flipped_horizontally=True)
    ]


def load_texture_pair_vertical_flip(filename):
    '''Loads a texture pair, with the second being a vertical mirror image.
        Used for sprites that both rotate with angles and face left or right.'''
    return [
        arcade.load_texture(filename),
        arcade.load_texture(filename, flipped_vertically=True)
    ]

# TODO: end_of_animation function to detect the end of an animation.
# TODO: Make get_offset function for each frame, which will somehow have a value attached. List, perhaps?