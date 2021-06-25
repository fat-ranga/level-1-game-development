'''
For all of the game's audio files, these are all loaded
into the game using the load_audio function.

Import these as a for consistency
'''
import arcade

audio_list = ['ak_47_reload', 'clip_load', 'glock_17_fire', 'glock_17_reload',
              'gun_pickup_1', 'gun_pickup_2', 'jump_1', 'jump_2']

def load_audio():
    '''Loads all of the game's audio files in __init__.'''
    for i in audio_list:
        arcade.load_sound(f'resources/audio/{i}.wav')
        print({i})