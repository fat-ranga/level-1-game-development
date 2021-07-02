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
    '''The base weapon class'''

    def __init__(self):
        # Set up parent class.
        super().__init__()

        # Scaling.
        self.scale = c.PIXEL_SCALING

        # Should we show the texture? Used for equipping/de-equipping different weapons.
        self.visible = True

        # Sprite texture.
        self.glock_17_texture = arcade.load_texture('resources/images/items/glock_17/default.png')
        self.texture = self.glock_17_texture

        # Offset - in pixels - so that the sprite is in the correct position when the animation plays.
        self.offset_x = 0
        self.offset_y = 0

        # Positions it moves according to. Set these to the player front-arm or back-arm co-ordinates.
        self.follow_x = None
        self.follow_y = None

    def update(self):
        # Go to wherever the player is.
        self.center_x = self.follow_x + (self.offset_x * c.PIXEL_SCALING)
        self.center_y = self.follow_y + (self.offset_y * c.PIXEL_SCALING)