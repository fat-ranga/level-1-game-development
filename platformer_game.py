'''
Platformer Game, by Kael
'''
import arcade
from pyglet.gl import GL_NEAREST
from pyglet.gl import GL_LINEAR
    
# Constants.
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 650
SCREEN_TITLE = 'Platformer'

# Constants used to scale our sprites from their original size.
CHARACTER_SCALING = 4
TILE_SCALING = 4
COIN_SCALING = 4

# Size of a single map tile in pixels.
TILE_SIZE = 16

# Movement speed of player, in pixels per frame.
PLAYER_WALK_SPEED = 7
PLAYER_SPRINT_SPEED = 14

# Platformer stuff.
GRAVITY = 1
PLAYER_JUMP_SPEED = 25
WORLD_BOTTOM = -200

# How many pixels to keep as a minimum margin between the character
# and the edge of the screen.aa
LEFT_VIEWPORT_MARGIN = 250
RIGHT_VIEWPORT_MARGIN = 250
BOTTOM_VIEWPORT_MARGIN = 100
TOP_VIEWPORT_MARGIN = 200

# Index of textures, first element faces left, second faces right
TEXTURE_LEFT = 1
TEXTURE_RIGHT = 0

class Player(arcade.Sprite):
    '''The player.'''
    def __init__(self):
        super().__init__()

        self.scale = TILE_SCALING
        self.textures = []

        # Load a left facing texture and a right facing texture.
        # flipped_horizontally=True will mirror the image we load.
        texture = arcade.load_texture('resources/images/characters/PLAYER.png')
        self.textures.append(texture)
        # By default, face right.
        self.texture = texture
        texture = arcade.load_texture('resources/images/characters/PLAYER.png',
                                      flipped_horizontally=True)
        self.textures.append(texture)

    def update(self):
        
        # Figure out if we should face left or right
        if self.change_x < 0:
            self.texture = self.textures[TEXTURE_LEFT]
        elif self.change_x > 0:
            self.texture = self.textures[TEXTURE_RIGHT]

            
class MyGame(arcade.Window):
    '''
    Main application class.
    '''

    def __init__(self):

        # Call the parent class and set up the window.
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, False, True)

        # These are 'lists' that keep track of our sprites.
        # Each sprite should go into a list.
        self.coin_list = None
        self.wall_list = None
        self.player_list = None
        self.foreground_decoration_list = None
        self.gem_list = None
        self.key_list = None
        self.door_list = None

        # Separate variable that holds the player sprite.
        self.player_sprite = None

        # Our physics engine.
        self.physics_engine = None
        
        # Used to keep track of our scrolling
        self.view_bottom = 0
        self.view_left = 0
        
        # Keep track of the score
        self.score = 0
        
        # Where are the edges of the map?
        self.end_of_map = 0
        self.start_of_map = 0

        # Level
        self.level = 1
        
         # Load sounds
        self.collect_coin_sound = arcade.load_sound(":resources:sounds/coin1.wav")
        self.jump_sound = arcade.load_sound(":resources:sounds/jump1.wav")
        
        arcade.set_background_color(arcade.csscolor.CORNFLOWER_BLUE)

    def setup(self, level):
        '''Set up the game here. Call this function to COMPLETELY restart the game.'''

        # Score.
        self.score = 0
        
        # Create the sprite lists.
        self.player_list = arcade.SpriteList()
        
        # Set up the player, specifically placing it at these coordinates.
        self.player_sprite = Player()
        self.player_sprite.center_x = 32
        self.player_sprite.center_y = 1600

        # Set the player sprint to false.
        self.player_sprite.is_sprinting = False
        
        # Add player sprite to the list.
        self.player_list.append(self.player_sprite)


        # --- Load in a map from the tiled editor ---


        # Name of map file to load
        map_name = f'resources/platformer_map_{level}.tmx'
        # Name of the layer in the file that has our platforms/walls
        platforms_layer_name = 'Walls'
        # Name of the layer that has items for pick-up
        coins_layer_name = 'Coins'
        # Name of the layer for foreground decorations
        foreground_decorations_layer_name = 'Foreground_Decorations'
        # Gems
        gems_layer_name = 'Gems'
        # Background decorations
        background_decorations_layer_name = 'Background_Decorations'
        # Doors
        doors_layer_name = 'Doors'
        # Keys
        keys_layer_name = 'Keys'

        
        # Read in the tiled map
        my_map = arcade.tilemap.read_tmx(map_name)

        # Calculate the right edge of the my_map in pixels
        self.end_of_map = my_map.map_size.width * TILE_SIZE * TILE_SCALING
        print(self.end_of_map)
        self.start_of_map = 0 + (my_map.map_size.width * (self.level - 1)) * TILE_SIZE * TILE_SCALING
        print(self.start_of_map)
        # -- Background decorations
        self.background_decoration_list = arcade.tilemap.process_layer(map_object=my_map,
                                                                       layer_name=background_decorations_layer_name,
                                                                       scaling=TILE_SCALING,
                                                                       use_spatial_hash=True)
        
        # -- Platforms
        self.wall_list = arcade.tilemap.process_layer(map_object=my_map,
                                                      layer_name=platforms_layer_name,
                                                      scaling=TILE_SCALING,
                                                      use_spatial_hash=True)

        # -- Coins
        self.coin_list = arcade.tilemap.process_layer(my_map, coins_layer_name, TILE_SCALING)

        # -- Gems
        self.gem_list = arcade.tilemap.process_layer(map_object=my_map,
                                                     layer_name=gems_layer_name,
                                                     scaling=TILE_SCALING,
                                                     use_spatial_hash=True)
        # -- Foreground decorations
        self.foreground_decoration_list = arcade.tilemap.process_layer(map_object=my_map,
                                                                       layer_name=foreground_decorations_layer_name,
                                                                       scaling=TILE_SCALING,
                                                                       use_spatial_hash=True)

        # -- Doors
        self.door_list = arcade.tilemap.process_layer(map_object=my_map,
                                                      layer_name=doors_layer_name,
                                                      scaling=TILE_SCALING,
                                                      use_spatial_hash=True)
        # -- Keys
        self.key_list = arcade.tilemap.process_layer(map_object=my_map,
                                                     layer_name=keys_layer_name,
                                                     scaling=TILE_SCALING,
                                                     use_spatial_hash=True)
        
        # --- Other stuff
        # Set the background color
        if my_map.background_color:
            arcade.set_background_color(my_map.background_color)
        
        # Create the 'physics engine'.
        self.physics_engine = arcade.PhysicsEnginePlatformer(self.player_sprite,
                                                             self.wall_list,
                                                             GRAVITY,
                                                             )
    def reload(self):
        '''Reload the game here. Call this function to restart the game. Doesn't load wall layer/decorations etc.'''

        # Score.
        self.score = 0
        
        # Create the sprite lists.
        self.player_list = arcade.SpriteList()
        self.gem_list = arcade.SpriteList(use_spatial_hash=True)
        self.key_list = arcade.SpriteList(use_spatial_hash=True)
        self.door_list = arcade.SpriteList(use_spatial_hash=True)
        
       # Set up the player, specifically placing it at these coordinates.
        self.player_sprite = Player()
        self.player_sprite.center_x = 32
        self.player_sprite.center_y = 1600

        # Set the player sprint to false.
        self.player_sprite.is_sprinting = False
        
        # Add player sprite to the list.
        self.player_list.append(self.player_sprite)


        # --- Load in a map from the tiled editor ---


        # Name of map file to load
        map_name = 'resources/platformer_map.tmx'
        # Name of the layer that has items for pick-up
        coins_layer_name = 'Coins'
        # Name of the layer for foreground decorations
        foreground_decorations_layer_name = 'Foreground_Decorations'
        # Gems
        gems_layer_name = 'Gems'
        # Background decorations
        background_decorations_layer_name = 'Background_Decorations'
        # Doors
        doors_layer_name = 'Doors'
        # Keys
        keys_layer_name = 'Keys'
        
        # Read in the tiled map
        my_map = arcade.tilemap.read_tmx(map_name)

        # -- Coins
        self.coin_list = arcade.tilemap.process_layer(my_map, coins_layer_name, TILE_SCALING)

         # -- Gems
        self.gem_list = arcade.tilemap.process_layer(map_object=my_map,
                                                      layer_name=gems_layer_name,
                                                      scaling=TILE_SCALING,
                                                      use_spatial_hash=True)

        # -- Doors
        self.door_list = arcade.tilemap.process_layer(map_object=my_map,
                                                      layer_name=doors_layer_name,
                                                      scaling=TILE_SCALING,
                                                      use_spatial_hash=True)
        # -- Keys
        self.key_list = arcade.tilemap.process_layer(map_object=my_map,
                                                     layer_name=keys_layer_name,
                                                     scaling=TILE_SCALING,
                                                     use_spatial_hash=True)
        
        # --- Other stuff
        # Set the background color
        if my_map.background_color:
            arcade.set_background_color(my_map.background_color)
        
        # Create the 'physics engine'.
        self.physics_engine = arcade.PhysicsEnginePlatformer(self.player_sprite,
                                                             self.wall_list,
                                                             GRAVITY,
                                                             )
    def on_draw(self):
        '''Render the screen.'''

        # Clear the screen to the background colour.
        arcade.start_render()

        # Draw our sprites.
        self.background_decoration_list.draw(filter=GL_NEAREST)
        self.wall_list.draw(filter=GL_NEAREST)
        self.coin_list.draw(filter=GL_NEAREST)
        self.gem_list.draw(filter=GL_NEAREST)
        self.key_list.draw(filter=GL_NEAREST)
        self.player_list.draw(filter=GL_NEAREST)
        self.door_list.draw(filter=GL_NEAREST)
        self.foreground_decoration_list.draw(filter=GL_NEAREST)
        
        
        # Draw our score on the screen, scrolling it with the viewport
        score_text = f"Score: {self.score}"
        arcade.draw_text(score_text, 10 + self.view_left, 10 + self.view_bottom,
                         arcade.csscolor.WHITE, 18)
        
    def on_key_press(self, key, modifiers):
        '''Called whenever a key is pressed.'''

        # Check if sprinting.
        if key == arcade.key.LSHIFT:
            self.player_sprite.is_sprinting = True

        # Jumping stuff.
        if key == arcade.key.W:
            if self.physics_engine.can_jump():
                self.player_sprite.change_y = PLAYER_JUMP_SPEED

        # Horizontal movement.
        elif key == arcade.key.A:
            if self.player_sprite.is_sprinting:
                self.player_sprite.change_x = -PLAYER_SPRINT_SPEED
            else:
                self.player_sprite.change_x = -PLAYER_WALK_SPEED
        elif key == arcade.key.D:
            if self.player_sprite.is_sprinting:
                self.player_sprite.change_x = PLAYER_SPRINT_SPEED
            else:
                self.player_sprite.change_x = PLAYER_WALK_SPEED

    def on_key_release(self, key, modifiers):
        '''Called when the user releases a key.'''

        # Check if the player is no longer sprinting.
        if key == arcade.key.LSHIFT:
            self.player_sprite.is_sprinting = False

        
        if key == arcade.key.A:
            self.player_sprite.change_x = 0
        elif key == arcade.key.D:
            self.player_sprite.change_x = 0

    def on_update(self, delta_time):
        '''Movement and game logic'''

        # Reset the game if the player falls through the world.
        if self.player_sprite.center_y < WORLD_BOTTOM:
            self.reload()

        self.player_list.update()
        
        # Move the player with the physics engine.
        self.physics_engine.update()

        # See if we hit any coins
        coin_hit_list = arcade.check_for_collision_with_list(self.player_sprite,
                                                             self.coin_list)

        # Loop through each coin we hit (if any) and remove it
        for coin in coin_hit_list:
            # Remove the coin
            coin.remove_from_sprite_lists()
            # Play a sound
            arcade.play_sound(self.collect_coin_sound)
            # Add one to the score
            self.score += 1

        # See if we hit any gems
        gem_hit_list = arcade.check_for_collision_with_list(self.player_sprite,
                                                             self.gem_list)

        # Loop through each gem we hit (if any) and remove it
        for gem in gem_hit_list:
            # Remove the coin
            gem.remove_from_sprite_lists()
            # Play a sound
            arcade.play_sound(self.collect_coin_sound)
            # Add one to the score
            self.score += 5

        # See if we hit any keys
        key_hit_list = arcade.check_for_collision_with_list(self.player_sprite,
                                                             self.key_list)

        # Loop through each key we hit and delete it
        for key in key_hit_list:
            # Remove the key
            key.remove_from_sprite_lists()
            # Check if there
            if len(self.key_list) < 1:
                # Remove all the door tiles
                for door in self.door_list:
                    # Remove the door
                    door.remove_from_sprite_lists()
            else:
                pass

        # See if the user got to the end of the level
        if self.player_sprite.center_x >= self.end_of_map:
            # Advance to the next level
            self.level += 1

            # Load the next level
            self.setup(self.level)
            
            self.player_sprite.center_x += 32
            
            # Set the camera to the start
            self.view_left = 0
            self.view_bottom = 0
            changed_viewport = True

        # See if the user went back to the start of the level.
        if self.player_sprite.center_x <= self.start_of_map:
            # Go back to the previous level
            self.level -= 1

            # Load the next level
            self.setup(self.level)

            self.player_sprite.center_x += 32

            # Set the camera to the start
            self.view_left = 0
            self.view_bottom = 0
            changed_viewport = True
        
            
        # --- Manage Scrolling --- #

        # Track if we need to change the viewport.

        changed = False

        # Scroll left.
        left_boundary = self.view_left + LEFT_VIEWPORT_MARGIN
        if self.player_sprite.left < left_boundary:
            self.view_left -= left_boundary - self.player_sprite.left
            changed = True

        # Scroll right.
        right_boundary = self.view_left + SCREEN_WIDTH - RIGHT_VIEWPORT_MARGIN
        if self.player_sprite.right > right_boundary:
            self.view_left += self.player_sprite.right - right_boundary
            changed = True

        # Scroll up.
        top_boundary = self.view_bottom + SCREEN_HEIGHT - TOP_VIEWPORT_MARGIN
        if self.player_sprite.top > top_boundary:
            self.view_bottom += self.player_sprite.top - top_boundary
            changed = True

        # Scroll down.
        bottom_boundary = self.view_bottom + BOTTOM_VIEWPORT_MARGIN
        if self.player_sprite.bottom < bottom_boundary:
            self.view_bottom -= bottom_boundary - self.player_sprite.bottom
            changed = True

        if changed:
            # Only scroll to integers. Otherwise we end up with
            # pixels that don't line up on the screen.
            self.view_bottom = int(self.view_bottom)
            self.view_left = int(self.view_left)

            # Do the scrolling.
            arcade.set_viewport(self.view_left,
                                SCREEN_WIDTH + self.view_left,
                                self.view_bottom,
                                SCREEN_HEIGHT + self.view_bottom)




def main():
    '''Main method'''
    window = MyGame()
    window.setup(window.level)
    arcade.run()


if __name__ == '__main__':
    main()
