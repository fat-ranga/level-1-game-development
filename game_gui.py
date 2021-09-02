'''
User interface for the game, defines buttons and stuff.

Import this as 'g' for consistency.
'''
import arcade
import arcade.gui

import game_constants as c
import game_functions as f
from arcade.gui import UIManager


class StartButton(arcade.gui.UIImageButton):
    '''
    To capture a button click, subclass the button and override on_click.
    '''

    def on_click(self):
        '''Called when user lets off button'''

        # This fade initiates the transition to the intro.
        f.screen_fade.fade = True


class Reticle(arcade.Sprite):
    '''Aiming reticle used in place of the mouse cursor'''

    def __init__(self):
        # Set up parent class.
        super().__init__()

        # Start the reticle as invisible.
        self.visible = False
        self.alpha = 0

        self.texture = arcade.load_texture('resources/images/ui/reticle.png')

        # These will become the mouse position.
        self.follow_x = None
        self.follow_y = None

        # Use regular pixel scaling
        self.scaling = c.PIXEL_SCALING

    def update(self):
        # Check if visible or not, and become totally transparent if invisible.
        if self.visible:
            self.alpha = 255
        else:
            self.alpha = 0

        # Go to wherever the mouse position is.
        self.center_x = self.follow_x
        self.center_y = self.follow_y
