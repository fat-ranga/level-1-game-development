'''
Platformer game, by Kael.
'''
import arcade
import os
import random
from pyglet.gl import GL_NEAREST
import math

# Constants.
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
SCREEN_TITLE = 'Game'
WORLD_BOTTOM = -200

# Constants used to scale our sprites from their original size.
PIXEL_SCALING = 4
UI_SCALING = 4
SPRITE_PIXEL_SIZE = 128
GRID_PIXEL_SIZE = (SPRITE_PIXEL_SIZE * PIXEL_SCALING)

# Movement speed of player, in pixels per frame.
PLAYER_MOVEMENT_SPEED = 7
GRAVITY = 1.5
PLAYER_JUMP_SPEED = 30
UPDATES_PER_FRAME = 9

# How many pixels to keep as a minimum margin between
# the character and the edge of the screen.
LEFT_VIEWPORT_MARGIN = 300
RIGHT_VIEWPORT_MARGIN = 300
BOTTOM_VIEWPORT_MARGIN = 150
TOP_VIEWPORT_MARGIN = 100

PLAYER_START_X = 250
PLAYER_START_Y = 2000

# Constants used to track if the player is facing left or right.
RIGHT_FACING = 0
LEFT_FACING = 1
IMAGE_ROTATION = 90


def load_texture_pair(filename):
    '''Loads a texture pair, with the second being a mirror image.'''
    return [
        arcade.load_texture(filename),
        arcade.load_texture(filename, flipped_horizontally=True)
    ]


class PlayerCharacter(arcade.Sprite):
    '''Player Sprite.'''

    def __init__(self):
        # Set up parent class.
        super().__init__()

        # Default to face-right.
        self.character_face_direction = RIGHT_FACING

        # Used for flipping between image sequences.
        self.cur_texture = 0
        self.scale = PIXEL_SCALING

        # Track our state.
        self.jumping = False
        self.climbing = False
        self.is_on_ladder = False
        self.idling = False

        # --- Load Textures --- #

        # Load textures for IDLE standing.
        self.idle_texture_pair = load_texture_pair(f'resources/images/characters/body/idle_to_walk_0.png')
        self.jump_texture_pair = load_texture_pair(f'resources/images/characters/body/idle_to_walk_0.png')
        self.fall_texture_pair = load_texture_pair(f'resources/images/characters/body/idle_to_walk_0.png')

        # Load textures for WALKING.
        self.walk_textures = []
        for i in range(9):
            texture = load_texture_pair(f'resources/images/characters/body/walk_{i}.png')
            self.walk_textures.append(texture)

        # Load textures for CLIMBING.
        self.climbing_textures = []
        texture = arcade.load_texture(f'resources/images/characters/body/idle_to_walk_0.png')
        self.climbing_textures.append(texture)
        texture = arcade.load_texture(f'resources/images/characters/body/idle_to_walk_0.png')
        self.climbing_textures.append(texture)

        # Set the initial texture.
        self.texture = self.idle_texture_pair[0]

        # Hit box will be set based on the first image used. If you want to specify
        # a different hit box, you can do it like the code below.
        self.set_hit_box([[-10, -31], [-7, 32], [7, 32], [10, -31]])
        # self.set_hit_box(self.texture.hit_box_points)

        self.mouse_pos_x = 0
        self.mouse_pos_y = 0

        # Set up the legs, the two arms sprites, and the head.
        self.legs = self.PlayerCharacterLegs()
        self.legs.idling = self.idling

        self.head = self.PlayerCharacterHead()

    def update_appendages(self):
        '''Positions the sprites and updates variables such as jumping and idling for the legs.'''

        # Legs.
        self.legs.center_x = self.center_x
        self.legs.center_y = self.center_y

        self.legs.jumping = self.jumping
        self.legs.climbing = self.climbing
        self.legs.is_on_ladder = self.is_on_ladder
        self.legs.idling = self.idling

        self.legs.cur_texture = self.cur_texture
        self.legs.character_face_direction = self.character_face_direction

        # Head.
        self.head.center_x = self.center_x
        self.head.center_y = self.center_y

        self.head.jumping = self.jumping
        self.head.climbing = self.climbing
        self.head.is_on_ladder = self.is_on_ladder
        self.head.idling = self.idling

        self.head.cur_texture = self.cur_texture
        self.head.character_face_direction = self.character_face_direction

        # TODO: Change system of head rotation to be based on a single 'head.png', with position determined by the frame index of an animation type. Do this with a function.
        # Rotate the player's head to look towards the mouse pointer.
        self.player_sprite.head.update_rotation(dest_x=self.mouse_pos_x,
                                                dest_y=self.mouse_pos_y, )

    def update_animation(self, delta_time: float = 1 / 60):
        # Figure out if we need to flip face left or right.
        if self.change_x < 0 and self.character_face_direction == RIGHT_FACING:
            self.character_face_direction = LEFT_FACING
        elif self.change_x > 0 and self.character_face_direction == LEFT_FACING:
            self.character_face_direction = RIGHT_FACING

        # CLIMBING animation.
        if self.is_on_ladder:
            self.climbing = True
        if not self.is_on_ladder and self.climbing:
            self.climbing = False
        if self.climbing and abs(self.change_y) > 1:
            self.cur_texture += 1
            if self.cur_texture > 7:
                self.cur_texture = 0
        if self.climbing:
            self.texture = self.climbing_textures[self.cur_texture // 4]
            return

        # JUMPING animation.
        if self.change_y > 0 and not self.is_on_ladder:
            self.jumping = True
            self.texture = self.jump_texture_pair[self.character_face_direction]
            return
        elif self.change_y < 0 and not self.is_on_ladder:
            self.jumping = True
            self.texture = self.fall_texture_pair[self.character_face_direction]
            return
        self.jumping = False

        # IDLE animation.
        if self.change_x == 0:
            self.idling = True
            self.texture = self.idle_texture_pair[self.character_face_direction]
            return

        # WALKING animation.
        self.idling = False
        self.cur_texture += 1
        if self.cur_texture > 8 * UPDATES_PER_FRAME:
            self.cur_texture = 0
        frame = self.cur_texture // UPDATES_PER_FRAME
        direction = self.character_face_direction
        self.texture = self.walk_textures[frame][direction]

    class PlayerCharacterLegs(arcade.Sprite):
        '''Player Sprite legs.'''

        def __init__(self):
            # Set up parent class.
            super().__init__()

            # Default to face-right.
            self.character_face_direction = RIGHT_FACING

            # Used for flipping between image sequences.
            self.cur_texture = 0
            self.scale = PIXEL_SCALING

            # Track our state.
            self.jumping = False
            self.climbing = False
            self.is_on_ladder = False
            self.idling = False

            # --- Load Textures --- #

            # Load textures for IDLE standing.
            self.idle_texture_pair = load_texture_pair(f'resources/images/characters/legs/idle_to_walk_0.png')
            self.jump_texture_pair = load_texture_pair(f'resources/images/characters/legs/idle_to_walk_0.png')
            self.fall_texture_pair = load_texture_pair(f'resources/images/characters/legs/idle_to_walk_0.png')

            # Load textures for WALKING.
            self.walk_textures = []
            for i in range(9):
                texture = load_texture_pair(f'resources/images/characters/legs/walk_{i}.png')
                self.walk_textures.append(texture)

            # Load textures for CLIMBING.
            self.climbing_textures = []
            texture = arcade.load_texture(f'resources/images/characters/legs/idle_to_walk_0.png')
            self.climbing_textures.append(texture)
            texture = arcade.load_texture(f'resources/images/characters/legs/idle_to_walk_0.png')
            self.climbing_textures.append(texture)

            # Set the initial texture.
            self.texture = self.idle_texture_pair[0]

            # Hit box will be set based on the first image used. If you want to specify
            # a different hit box, you can do it like the code below.
            # self.set_hit_box([[-6, -31], [-6, 32], [17, 32], [17, -31]])
            # self.set_hit_box(self.texture.hit_box_points)

        def update_animation(self, delta_time: float = 1 / 60):
            # CLIMBING animation.
            if self.climbing:
                self.texture = self.climbing_textures[self.cur_texture // 4]
                return

            # JUMPING animation.
            if self.jumping:
                self.texture = self.jump_texture_pair[self.character_face_direction]
                return

            # IDLE animation.
            if self.idling:
                self.texture = self.idle_texture_pair[self.character_face_direction]
                return

            # WALKING animation.
            frame = self.cur_texture // UPDATES_PER_FRAME
            direction = self.character_face_direction
            self.texture = self.walk_textures[frame][direction]

    class PlayerCharacterHead(arcade.Sprite):
        '''Player Sprite head.'''

        def __init__(self):
            # Set up parent class.
            super().__init__()

            # Default to face-right.
            self.character_face_direction = RIGHT_FACING

            self.scale = PIXEL_SCALING

            # Track our state.
            self.jumping = False
            self.climbing = False
            self.is_on_ladder = False
            self.idling = False

            # --- Load Textures --- #

            # Load textures for IDLE standing.
            self.idle_texture_pair = load_texture_pair(f'resources/images/characters/head/idle_to_walk_0.png')
            self.jump_texture_pair = load_texture_pair(f'resources/images/characters/head/idle_to_walk_0.png')
            self.fall_texture_pair = load_texture_pair(f'resources/images/characters/head/idle_to_walk_0.png')

            # Load textures for WALKING.
            self.walk_textures = []
            for i in range(9):
                texture = load_texture_pair(f'resources/images/characters/head/walk_{i}.png')
                self.walk_textures.append(texture)

            # Load textures for CLIMBING.
            self.climbing_textures = []
            texture = arcade.load_texture(f'resources/images/characters/head/idle_to_walk_0.png')
            self.climbing_textures.append(texture)
            texture = arcade.load_texture(f'resources/images/characters/head/idle_to_walk_0.png')
            self.climbing_textures.append(texture)

            # Set the initial texture.
            self.texture = self.idle_texture_pair[0]

            # Destination point is where we are going.
            self.dest_x = 0
            self.dest_y = 0

            # Max speed we can rotate.
            self.rot_speed = 5

            # TODO: Add separate hitbox for the head, to allow headshots.
            # Hit box will be set based on the first image used. If you want to specify
            # a different hit box, you can do it like the code below.
            # self.set_hit_box([[-6, -31], [-6, 32], [17, 32], [17, -31]])
            # self.set_hit_box(self.texture.hit_box_points)

        def update_animation(self, delta_time: float = 1 / 60):
            # CLIMBING animation.
            if self.climbing:
                self.texture = self.climbing_textures[self.cur_texture // 4]
                return

            # JUMPING animation.
            if self.jumping:
                self.texture = self.jump_texture_pair[self.character_face_direction]
                return

            # IDLE animation.
            if self.idling:
                self.texture = self.idle_texture_pair[self.character_face_direction]
                return

            # WALKING animation.
            frame = self.cur_texture // UPDATES_PER_FRAME
            direction = self.character_face_direction
            self.texture = self.walk_textures[frame][direction]

        def update_rotation(self, dest_x, dest_y):
            # Do math to calculate how to get the sprite to the destination.
            # Calculation the angle in radians between the start points
            # and end points. This is the angle the player will travel.
            x_diff = dest_x - self.center_x
            y_diff = dest_y - self.center_y
            target_angle_radians = math.atan2(y_diff, x_diff)
            if target_angle_radians < 0:
                target_angle_radians += 2 * math.pi

            # What angle are we at now in radians?
            actual_angle_radians = math.radians(self.angle - IMAGE_ROTATION)

            # How fast can we rotate?
            rot_speed_radians = math.radians(self.rot_speed)

            # What is the difference between what we want, and where we are?
            angle_diff_radians = target_angle_radians - actual_angle_radians

            # Figure out if we rotate clockwise or counter-clockwise
            if abs(angle_diff_radians) <= rot_speed_radians:
                # Close enough, let's set our angle to the target
                actual_angle_radians = target_angle_radians
                clockwise = None
            elif angle_diff_radians > 0 and abs(angle_diff_radians) < math.pi:
                clockwise = False
            elif angle_diff_radians > 0 and abs(angle_diff_radians) >= math.pi:
                clockwise = True
            elif angle_diff_radians < 0 and abs(angle_diff_radians) < math.pi:
                clockwise = True
            else:
                clockwise = False

            # Rotate the proper direction if needed
            if actual_angle_radians != target_angle_radians and clockwise:
                actual_angle_radians -= rot_speed_radians
            elif actual_angle_radians != target_angle_radians:
                actual_angle_radians += rot_speed_radians

            # Keep in a range of 0 to 2pi
            if actual_angle_radians > 2 * math.pi:
                actual_angle_radians -= 2 * math.pi
            elif actual_angle_radians < 0:
                actual_angle_radians += 2 * math.pi

            # Convert back to degrees
            self.angle = math.degrees(actual_angle_radians) + IMAGE_ROTATION


class MyGame(arcade.Window):
    '''Main application class.'''

    def __init__(self):
        '''Initialiser for the game.'''

        # Call the parent class and set up the window.
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

        # Set the path to start with this program.
        file_path = os.path.dirname(os.path.abspath(__file__))
        os.chdir(file_path)

        # Track the current state of what key is pressed.
        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        self.down_pressed = False
        self.jump_needs_reset = False

        # These are 'lists' that keep track of our sprites. Each sprite should
        # go into a list.
        self.coin_list = None
        self.wall_list = None
        self.background_list = None
        self.ladder_list = None
        self.player_list = None

        # Player sprite variables. Body, legs etc.
        self.player_sprite = None

        # Our 'physics' engine.
        self.physics_engine = None

        # Used to keep track of our scrolling.
        self.view_bottom = 0
        self.view_left = 0

        self.end_of_map = 0

        # Keep track of the score.
        self.score = 0

        # Mouse position.
        self.mouse_position_x = 0
        self.mouse_position_y = 0

        # Load sounds.
        self.collect_coin_sound = arcade.load_sound(':resources:sounds/coin1.wav')
        self.jump_sound = arcade.load_sound(':resources:sounds/jump1.wav')
        self.game_over = arcade.load_sound(':resources:sounds/gameover1.wav')

        # Set background colour.
        arcade.set_background_color(arcade.color.CORNFLOWER_BLUE)

    def setup(self):
        '''Set up the game here. Call this function to restart the game.'''

        # Used to keep track of our scrolling.
        self.view_bottom = 0
        self.view_left = 0

        # Keep track of the score.
        self.score = 0

        # Create the Sprite lists.
        self.player_list = arcade.SpriteList()
        self.background_list = arcade.SpriteList()
        self.wall_list = arcade.SpriteList()
        self.coin_list = arcade.SpriteList()

        # Set up the player, specifically placing it at these coordinates.
        self.player_sprite = PlayerCharacter()
        self.player_sprite.center_x = PLAYER_START_X
        self.player_sprite.center_y = PLAYER_START_Y

        self.player_list.append(self.player_sprite.legs)
        self.player_list.append(self.player_sprite)
        self.player_list.append(self.player_sprite.head)

        # --- Load in a map from the tiled editor --- #

        # Name of the layer in the file that has our platforms/walls.
        walls_layer_name = 'Walls'
        moving_platforms_layer_name = 'Moving Platforms'

        # Name of the layer that has items for pick-up.
        coins_layer_name = 'Coins'

        # Map name.
        map_name = f'resources/maps/test.tmx'

        # Read in the tiled map.
        my_map = arcade.tilemap.read_tmx(map_name)

        # Calculate the right edge of the my_map in pixels.
        self.end_of_map = my_map.map_size.width * GRID_PIXEL_SIZE

        # Platforms.
        self.wall_list = arcade.tilemap.process_layer(my_map,
                                                      walls_layer_name,
                                                      PIXEL_SCALING,
                                                      use_spatial_hash=True)
        '''
        # Moving Platforms.
        moving_platforms_list = arcade.tilemap.process_layer(my_map, moving_platforms_layer_name, PIXEL_SCALING)
        for sprite in moving_platforms_list:
            self.wall_list.append(sprite)

        # Background objects.
        self.background_list = arcade.tilemap.process_layer(my_map, 'Background', PIXEL_SCALING)

        # Ladders.
        self.ladder_list = arcade.tilemap.process_layer(my_map, 'Ladders',
                                                        PIXEL_SCALING,
                                                        use_spatial_hash=True)

        # Coins.
        self.coin_list = arcade.tilemap.process_layer(my_map, coins_layer_name,
                                                      PIXEL_SCALING,
                                                      use_spatial_hash=True)
        '''
        # Other stuff.
        # Set the background color
        if my_map.background_color:
            arcade.set_background_color(my_map.background_color)

        # Create the 'physics engine'.
        self.physics_engine = arcade.PhysicsEnginePlatformer(self.player_sprite,
                                                             self.wall_list,
                                                             gravity_constant=GRAVITY,
                                                             ladders=self.ladder_list)

    def on_draw(self):
        '''Render the screen.'''

        # Clear the screen to the background colour.
        arcade.start_render()

        # Draw our sprites.
        self.wall_list.draw(filter=GL_NEAREST)
        '''
        self.background_list.draw(filter=GL_NEAREST)
        self.ladder_list.draw(filter=GL_NEAREST)
        self.coin_list.draw(filter=GL_NEAREST)
        '''
        self.player_list.draw(filter=GL_NEAREST)

        # Draw our score on the screen, scrolling it with the viewport.
        score_text = f'Score: {self.score}'
        arcade.draw_text(score_text, 10 + self.view_left, 10 + self.view_bottom,
                         arcade.csscolor.WHITE, 32, font_name='resources/Unexplored.ttf')

        # Draw hit boxes.
        # for wall in self.wall_list:
        # wall.draw_hit_box(arcade.color.BLACK, 3)

        self.player_sprite.draw_hit_box(arcade.color.RED, 2)

    def process_keychange(self):
        '''Called when we change a key up/down or we move on/off a ladder.'''

        # Process up/down.
        if self.up_pressed and not self.down_pressed:
            if self.physics_engine.is_on_ladder():
                self.player_sprite.change_y = PLAYER_MOVEMENT_SPEED
            elif self.physics_engine.can_jump(y_distance=10) and not self.jump_needs_reset:
                self.player_sprite.change_y = PLAYER_JUMP_SPEED
                self.jump_needs_reset = True
                arcade.play_sound(self.jump_sound)
        elif self.down_pressed and not self.up_pressed:
            if self.physics_engine.is_on_ladder():
                self.player_sprite.change_y = -PLAYER_MOVEMENT_SPEED

        # Process up/down when on a ladder and no movement.
        if self.physics_engine.is_on_ladder():
            if not self.up_pressed and not self.down_pressed:
                self.player_sprite.change_y = 0
            elif self.up_pressed and self.down_pressed:
                self.player_sprite.change_y = 0

        # Process left/right.
        if self.right_pressed and not self.left_pressed:
            self.player_sprite.change_x = PLAYER_MOVEMENT_SPEED
        elif self.left_pressed and not self.right_pressed:
            self.player_sprite.change_x = -PLAYER_MOVEMENT_SPEED
        else:
            self.player_sprite.change_x = 0

    def on_key_press(self, key, modifiers):
        '''Called whenever a key is pressed.'''

        if key == arcade.key.W:
            self.up_pressed = True
        elif key == arcade.key.S:
            self.down_pressed = True
        elif key == arcade.key.A:
            self.left_pressed = True
        elif key == arcade.key.D:
            self.right_pressed = True

        self.process_keychange()

    def on_key_release(self, key, modifiers):
        '''Called when the user releases a key.'''

        if key == arcade.key.W:
            self.up_pressed = False
            self.jump_needs_reset = False
        elif key == arcade.key.S:
            self.down_pressed = False
        elif key == arcade.key.A:
            self.left_pressed = False
        elif key == arcade.key.D:
            self.right_pressed = False

        self.process_keychange()

    def on_update(self, delta_time):
        '''Movement and game logic.'''

        if self.player_sprite.center_y < WORLD_BOTTOM:
            self.setup()

        # Move the player with the physics engine.
        self.physics_engine.update()

        # Update animations.
        if self.physics_engine.can_jump():
            self.player_sprite.can_jump = False
        else:
            self.player_sprite.can_jump = True

        if self.physics_engine.is_on_ladder() and not self.physics_engine.can_jump():
            self.player_sprite.is_on_ladder = True
            self.process_keychange()
        else:
            self.player_sprite.is_on_ladder = False
            self.process_keychange()

        # Move body parts to player's position and update checking variables.
        self.player_sprite.update_appendages()

        self.coin_list.update_animation(delta_time)
        self.background_list.update_animation(delta_time)
        self.player_list.update_animation(delta_time)

        # Update walls, used with moving platforms.
        self.wall_list.update()

        # See if the moving wall hit a boundary and needs to reverse direction.
        for wall in self.wall_list:

            if wall.boundary_right and wall.right > wall.boundary_right and wall.change_x > 0:
                wall.change_x *= -1
            if wall.boundary_left and wall.left < wall.boundary_left and wall.change_x < 0:
                wall.change_x *= -1
            if wall.boundary_top and wall.top > wall.boundary_top and wall.change_y > 0:
                wall.change_y *= -1
            if wall.boundary_bottom and wall.bottom < wall.boundary_bottom and wall.change_y < 0:
                wall.change_y *= -1

        # See if we hit any coins.
        coin_hit_list = arcade.check_for_collision_with_list(self.player_sprite,
                                                             self.coin_list)

        # Loop through each coin we hit (if any) and remove it.
        for coin in coin_hit_list:

            # Figure out how many points this coin is worth.
            if 'Points' not in coin.properties:
                print('Warning, collected a coin without a Points property.')
            else:
                points = int(coin.properties['Points'])
                self.score += points

            # Remove the coin.
            coin.remove_from_sprite_lists()
            arcade.play_sound(self.collect_coin_sound)

        # Track if we need to change the viewport.
        changed_viewport = False

        # --- Manage Scrolling --- #

        # Scroll left.
        left_boundary = self.view_left + LEFT_VIEWPORT_MARGIN
        if self.player_sprite.left < left_boundary:
            self.view_left -= left_boundary - self.player_sprite.left
            changed_viewport = True

        # Scroll right.
        right_boundary = self.view_left + SCREEN_WIDTH - RIGHT_VIEWPORT_MARGIN
        if self.player_sprite.right > right_boundary:
            self.view_left += self.player_sprite.right - right_boundary
            changed_viewport = True

        # Scroll up.
        top_boundary = self.view_bottom + SCREEN_HEIGHT - TOP_VIEWPORT_MARGIN
        if self.player_sprite.top > top_boundary:
            self.view_bottom += self.player_sprite.top - top_boundary
            changed_viewport = True

        # Scroll down.
        bottom_boundary = self.view_bottom + BOTTOM_VIEWPORT_MARGIN
        if self.player_sprite.bottom < bottom_boundary:
            self.view_bottom -= bottom_boundary - self.player_sprite.bottom
            changed_viewport = True

        if changed_viewport:
            # Only scroll to integers. Otherwise we end up with pixels that
            # don't line up on the screen.
            self.view_bottom = int(self.view_bottom)
            self.view_left = int(self.view_left)

            # Do the scrolling.
            arcade.set_viewport(self.view_left,
                                SCREEN_WIDTH + self.view_left,
                                self.view_bottom,
                                SCREEN_HEIGHT + self.view_bottom)

    def on_mouse_motion(self, x, y, dx, dy):
        '''Handle Mouse Motion'''

        # Update the position of the mouse.
        self.mouse_position_x = x
        self.mouse_position_y = y


def main():
    '''Main method.'''
    window = MyGame()
    window.setup()
    arcade.run()


if __name__ == '__main__':
    main()
