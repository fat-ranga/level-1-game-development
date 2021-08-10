'''
User interface for the game, defines buttons and stuff.

Import this as 'g' for consistency.
'''
import arcade
import arcade.gui
import game_functions as f
from arcade.gui import UIManager


class StartButton(arcade.gui.UIImageButton):
    '''
    To capture a button click, subclass the button and override on_click.
    '''

    def on_click(self):
        '''Called when user lets off button'''
        print('Click flat button.')

        # This fade initiates the transition to the intro
        f.screen_fade.fade = True


