'''
The stuff for the parallax environment backgrounds.

Import this as 'b' for consistency.
'''
import arcade
import game_constants as c


class Background(arcade.Sprite):
    '''Parallax background environment sprite.'''

    def __init__(self):
        # Set up parent class.
        super().__init__()

        # Scaling.
        self.scale = c.PIXEL_SCALING

        # Sprite texture.
        self.mountains_texture = arcade.load_texture('resources/images/backgrounds/test.png')
        self.texture = self.mountains_texture

        # Set the default values for parallax. At 1, it moves at the same rate as the player.
        self.parallax_multiplier_x = 0.9
        self.parallax_multiplier_y = 0.9

        # Positions it moves according to. Set these to the player co-ordinates.
        self.follow_x = None
        self.follow_y = None

    def update(self):
        # Go to wherever the player is.
        self.center_x = self.follow_x * self.parallax_multiplier_x
        self.center_y = self.follow_y * self.parallax_multiplier_y
