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


def fade_black(time, opacity):
    '''Uses a black image to create a fading effect.'''
    # Change opacity of this to create fading to and from black effect.
    black_fade = arcade.Sprite()
    black_fade.texture = 'resources/'
    black_fade.alpha = 255 # TODO: This.

# TODO: end_of_animation function to detect the end of an animation.


# -- PLAYER AND ENEMIES SPRITE STUFF -- #


# List of all the names of the human sprite animation frames in the game.
frame_list = []

# Dictionary that contains the names of the frames and their respective head positions.
# This is what is accessed whenever the head is repositioned.
frame_head_position = {}

# Contains all the x, y values for all the different animation frames.
head_positions = []

# x, y co-ordinates for the different frames. Contents added to 'head_positions' afterwards.
head_positions_idle_to_jump = [[1, 24], [2, 25], [3, 20], [3, 16], [3, 17], [2, 24], [2, 30], [1, 26],
                               [1, 24], [0, 25], [-1, 26], [-1, 26], [1, 25], [-1, 23], [-1, 22], [-1, 22]]

head_positions_idle_to_walk = [[1, 23], [1, 23], [1, 23], [1, 22], [1, 21], [2, 23]]

head_positions_run = [[9, 23], [10, 20], [16, 23], [8, 24], [8, 22]]

head_positions_walk = [[-2, 24], [-2, 25], [-2, 24], [-2, 22], [-2, 24], [-2, 25], [-2, 24], [-2, 22], [-2, 23]]


def add_frames_to_list():
    '''Loads all the names of the frame files and puts them into frame_list.
        Also compiles all the 'head_positions_(x)' lists into one big list.
        MUST ALL BE IN SAME ORDER!'''

    # Compiling positions into big list.
    for i in head_positions_idle_to_jump:
        head_positions.append(i)
    for i in head_positions_idle_to_walk:
        head_positions.append(i)
    for i in head_positions_run:
        head_positions.append(i)
    for i in head_positions_walk:
        head_positions.append(i)

    # Adding all the names.
    for i in range(16):
        frame_list.append(f'idle_to_jump_{i}')
    for i in range(6):
        frame_list.append(f'idle_to_walk_{i}')
    for i in range(5):
        frame_list.append(f'run_{i}')
    for i in range(9):
        frame_list.append(f'walk_{i}')
    print(head_positions)

    return frame_list


def load_frames_and_positions():
    # For all the frames of the animations.
    counter = -1
    for i in frame_list:
        counter += 1
        # Load the audio into the dictionary.
        frame_head_position[f'{i}'.format(i)] = head_positions[counter]
        print(len(i))
    print(frame_head_position)


def get_head_offset_x(frame):
    '''Returns the x co-ordinates for where the centre of the head
        should be from an animation frame.'''
    # Head position.
    head_x = frame_head_position[f'{frame}']

    return head_x[0]


def get_head_offset_y(frame):
    '''Returns the y co-ordinates for where the centre of the head
        should be from an animation frame.'''
    # Head position.
    head_y = frame_head_position[f'{frame}']

    return head_y[1]
