'''
For all npcs, enemies and effects.

Import this as 'e' for consistency.
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


class Explosion(arcade.Sprite):
    '''This class creates an explosion animation.'''

    def __init__(self, texture_list):
        super().__init__()

        # Start at the first frame
        self.current_texture = 0
        self.textures = texture_list

    def update(self):

        # Update to the next frame of the animation. If we are at the end
        # of our frames, then delete this sprite.
        self.current_texture += 1
        if self.current_texture < len(self.textures * c.EFFECT_UPDATES_PER_FRAME):
            frame = self.current_texture // c.EFFECT_UPDATES_PER_FRAME
            self.set_texture(frame)
        else:
            self.remove_from_sprite_lists()
