'''
Player character classes and functions.
Import these as p for consistency.

Organisation:

PlayerCharacter
    PlayerCharacterLegs
    PlayerCharacterHead
    PlayerCharacterFrontArm
    PlayerCharacterBackArm
'''

import arcade
import os
import random
from pyglet.gl import GL_NEAREST
import math
import game_constants as c
import game_functions as f


class PlayerCharacter(arcade.Sprite):
    '''Player Sprite.'''

    def __init__(self):
        # Set up parent class.
        super().__init__()

        # Default to face-right.
        self.character_face_direction = c.RIGHT_FACING

        # Used for flipping between image sequences.
        self.cur_texture = 0
        self.scale = c.PIXEL_SCALING

        # Track our state.
        self.jumping = False
        self.climbing = False
        self.is_on_ladder = False
        self.idling = False
        self.can_jump = False
        self.sprinting = False
        self.firing = False

        # Whether the player is armed in any sort of way.
        self.equipped_any = False

        # Whether the player has a gun or not.
        self.equipped_one_handed = False

        # --- Load Textures --- #

        # Load textures for IDLE standing.
        self.idle_texture_pair = f.load_texture_pair(f'resources/images/characters/test/body/idle_to_walk_0.png')
        self.jump_texture_pair = f.load_texture_pair(f'resources/images/characters/test/body/idle_to_walk_0.png')
        self.fall_texture_pair = f.load_texture_pair(f'resources/images/characters/test/body/idle_to_walk_0.png')

        # Load textures for WALKING.
        self.walk_textures = []
        for i in range(9):
            texture = f.load_texture_pair(f'resources/images/characters/test/body/walk_{i}.png')
            self.walk_textures.append(texture)

        # Load textures for RUNNING.
        self.run_textures = []
        for i in range(5):
            texture = f.load_texture_pair(f'resources/images/characters/test/body/run_{i}.png')
            self.run_textures.append(texture)

        # Load textures for CLIMBING.
        self.climbing_textures = []
        texture = arcade.load_texture(f'resources/images/characters/test/body/idle_to_walk_0.png')
        self.climbing_textures.append(texture)
        texture = arcade.load_texture(f'resources/images/characters/test/body/idle_to_walk_0.png')
        self.climbing_textures.append(texture)

        # Load textures for going from IDLE to JUMPING.
        self.idle_to_jump_textures = []
        for i in range(16):
            texture = f.load_texture_pair(f'resources/images/characters/test/body/idle_to_jump_{i}.png')
            self.idle_to_jump_textures.append(texture)

        # Set the initial texture.
        self.texture = self.idle_texture_pair[0]

        # Hit box will be set based on the first image used. If you want to specify
        # a different hit box, you can do it like the code below.
        self.set_hit_box([[-10, -31], [-7, 32], [7, 32], [10, -31]])
        # self.set_hit_box(self.texture.hit_box_points)

        # Mouse position.
        self.mouse_pos_x = 0
        self.mouse_pos_y = 0

        # Set up the legs, the two arms sprites, and the head.
        self.legs = self.PlayerCharacterLegs()
        self.legs.idling = self.idling

        self.head = self.PlayerCharacterHead()
        self.front_arm = self.PlayerCharacterFrontArm()
        self.back_arm = self.PlayerCharacterBackArm()

    def get_head_offset(self):
        '''Gets a number in pixels of how much higher or lower the head should be positioned
            on each frame of animation, so it doesn't stay still.'''

    def acquire_mouse_position(self, x, y):
        '''Get the mouse x and y from the Game class.'''
        self.mouse_pos_x = x
        self.mouse_pos_y = y

    def update_appendages(self, delta_time: float = 1 / 60):
        '''Positions the sprites and updates variables such as jumping and idling for the legs.'''

        # Set type of gun equipped.
        self.front_arm.equipped_one_handed = self.equipped_one_handed
        self.back_arm.equipped_one_handed = self.equipped_one_handed

        # Legs.
        self.legs.center_x = self.center_x
        self.legs.center_y = self.center_y

        self.legs.jumping = self.jumping
        self.legs.climbing = self.climbing
        self.legs.is_on_ladder = self.is_on_ladder
        self.legs.idling = self.idling
        self.legs.sprinting = self.sprinting

        self.legs.cur_texture = self.cur_texture
        self.legs.character_face_direction = self.character_face_direction

        # Head.
        self.head.center_x = self.center_x
        self.head.center_y = self.center_y + (25 * c.PIXEL_SCALING)

        self.head.jumping = self.jumping
        self.head.climbing = self.climbing
        self.head.is_on_ladder = self.is_on_ladder
        self.head.idling = self.idling

        # Rotate the player's head to look towards the mouse pointer.
        self.head.update_rotation(dest_x=self.mouse_pos_x,
                                  dest_y=self.mouse_pos_y)

        # Front arm.
        self.front_arm.jumping = self.jumping
        self.front_arm.climbing = self.climbing
        self.front_arm.is_on_ladder = self.is_on_ladder
        self.front_arm.idling = self.idling
        self.front_arm.sprinting = self.sprinting
        self.front_arm.firing = True

        self.front_arm.character_face_direction = self.character_face_direction

        if self.equipped_one_handed:
            self.front_arm.center_y = self.center_y + (15 * c.PIXEL_SCALING)
            self.front_arm.update_rotation(dest_x=self.mouse_pos_x,
                                           dest_y=self.mouse_pos_y)
            if self.character_face_direction == c.RIGHT_FACING:
                self.front_arm.center_x = self.center_x - (4 * c.PIXEL_SCALING)
            elif self.character_face_direction == c.LEFT_FACING:
                self.front_arm.center_x = self.center_x + (4 * c.PIXEL_SCALING)
        else:
            self.front_arm.center_x = self.center_x
            self.front_arm.center_y = self.center_y
            self.front_arm.angle = 0
            self.front_arm.cur_texture = self.cur_texture

        # Back arm.
        self.back_arm.jumping = self.jumping
        self.back_arm.climbing = self.climbing
        self.back_arm.is_on_ladder = self.is_on_ladder
        self.back_arm.idling = self.idling
        self.back_arm.sprinting = self.sprinting

        self.back_arm.character_face_direction = self.character_face_direction

        self.back_arm.center_x = self.center_x
        self.back_arm.center_y = self.center_y
        self.back_arm.angle = 0
        self.back_arm.cur_texture = self.cur_texture

    def update_animation(self, delta_time: float = 1 / 60):
        self.update_appendages()
        # Figure out if we need to flip face left or right.
        if self.change_x < 0 and self.character_face_direction == c.RIGHT_FACING:
            self.character_face_direction = c.LEFT_FACING
        elif self.change_x > 0 and self.character_face_direction == c.LEFT_FACING:
            self.character_face_direction = c.RIGHT_FACING

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
            self.cur_texture += 1
            if self.cur_texture > 15 * c.UPDATES_PER_FRAME:
                self.cur_texture = 0
            frame = self.cur_texture // c.UPDATES_PER_FRAME
            direction = self.character_face_direction
            self.texture = self.idle_to_jump_textures[frame][direction]
            return
        elif self.change_y < 0 and not self.is_on_ladder:
            self.jumping = True
            self.cur_texture += 1
            if self.cur_texture > 15 * c.UPDATES_PER_FRAME:
                self.cur_texture = 0
            frame = self.cur_texture // c.UPDATES_PER_FRAME
            direction = self.character_face_direction
            self.texture = self.idle_to_jump_textures[frame][direction]
            return
        self.jumping = False

        # IDLE animation.
        if self.change_x == 0 and self.change_y == 0:
            self.idling = True
            self.texture = self.idle_texture_pair[self.character_face_direction]
            return

        self.idling = False
        if self.sprinting:
            # RUNNING animation.
            self.cur_texture += 1
            if self.cur_texture > 4 * c.UPDATES_PER_FRAME:
                self.cur_texture = 0
            frame = self.cur_texture // c.UPDATES_PER_FRAME
            direction = self.character_face_direction
            self.texture = self.run_textures[frame][direction]
            return

        else:
            # WALKING animation.
            self.cur_texture += 1
            if self.cur_texture > 8 * c.UPDATES_PER_FRAME:
                self.cur_texture = 0
            frame = self.cur_texture // c.UPDATES_PER_FRAME
            direction = self.character_face_direction
            self.texture = self.walk_textures[frame][direction]
            return

    class PlayerCharacterLegs(arcade.Sprite):
        '''Player Sprite legs.'''

        def __init__(self):
            # Set up parent class.
            super().__init__()

            # Default to face-right.
            self.character_face_direction = c.RIGHT_FACING

            # Used for flipping between image sequences.
            self.cur_texture = 0
            self.scale = c.PIXEL_SCALING

            # Track our state.
            self.jumping = False
            self.climbing = False
            self.is_on_ladder = False
            self.idling = False
            self.sprinting = False

            # --- Load Textures --- #

            # Load textures for IDLE standing.
            self.idle_texture_pair = f.load_texture_pair(f'resources/images/characters/test/legs/idle_to_walk_0.png')
            self.jump_texture_pair = f.load_texture_pair(f'resources/images/characters/test/legs/idle_to_walk_0.png')
            self.fall_texture_pair = f.load_texture_pair(f'resources/images/characters/test/legs/idle_to_walk_0.png')

            # Load textures for WALKING.
            self.walk_textures = []
            for i in range(9):
                texture = f.load_texture_pair(f'resources/images/characters/test/legs/walk_{i}.png')
                self.walk_textures.append(texture)

            # Load textures for RUNNING.
            self.run_textures = []
            for i in range(5):
                texture = f.load_texture_pair(f'resources/images/characters/test/legs/run_{i}.png')
                self.run_textures.append(texture)

            # Load textures for going from IDLE to JUMPING.
            self.idle_to_jump_textures = []
            for i in range(16):
                texture = f.load_texture_pair(f'resources/images/characters/test/legs/idle_to_jump_{i}.png')
                self.idle_to_jump_textures.append(texture)

            # Load textures for CLIMBING.
            self.climbing_textures = []
            texture = arcade.load_texture(f'resources/images/characters/test/legs/idle_to_walk_0.png')
            self.climbing_textures.append(texture)
            texture = arcade.load_texture(f'resources/images/characters/test/legs/idle_to_walk_0.png')
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

            # IDLE to JUMPING animation.
            if self.jumping:
                frame = self.cur_texture // c.UPDATES_PER_FRAME
                direction = self.character_face_direction
                self.texture = self.idle_to_jump_textures[frame][direction]
                return

            # IDLE animation.
            if self.idling:
                self.texture = self.idle_texture_pair[self.character_face_direction]
                return

            if self.sprinting:
                # RUNNING animation.
                frame = self.cur_texture // c.UPDATES_PER_FRAME
                direction = self.character_face_direction
                self.texture = self.run_textures[frame][direction]
                return

            else:
                # WALKING animation.
                frame = self.cur_texture // c.UPDATES_PER_FRAME
                direction = self.character_face_direction
                self.texture = self.walk_textures[frame][direction]
                return

    class PlayerCharacterHead(arcade.Sprite):
        '''Player Sprite head.'''

        def __init__(self):
            # Set up parent class.
            super().__init__()

            # Default to face-right.
            self.character_face_direction = c.RIGHT_FACING

            self.scale = c.PIXEL_SCALING

            # Track our state.
            self.jumping = False
            self.climbing = False
            self.is_on_ladder = False
            self.idling = False
            self.sprinting = False

            # --- Load Textures --- #

            # Load textures for IDLE standing.
            self.texture_pair = f.load_texture_pair_vertical_flip(f'resources/images/characters/test/head/head.png')

            # Set the initial texture.
            self.texture = self.texture_pair[0]

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

        def update_rotation(self, dest_x, dest_y):
            # Calculate the angle in radians between the start points
            # and end points. This is the angle the head will face.
            x_diff = dest_x - self.center_x
            y_diff = dest_y - self.center_y

            # Determine if the head should be flipped.
            if dest_x > self.center_x:
                self.character_face_direction = c.RIGHT_FACING
            elif dest_x < self.center_x:
                self.character_face_direction = c.LEFT_FACING
            else:
                # Stay the same direction.
                pass
            self.texture = self.texture_pair[self.character_face_direction]

            angle = math.atan2(y_diff, x_diff)

            # Set the head to face the mouse position.
            self.angle = math.degrees(angle)

    class PlayerCharacterFrontArm(arcade.Sprite):
        '''Player Sprite front arm.'''

        def __init__(self):
            # Set up parent class.
            super().__init__()

            # Default to face-right.
            self.character_face_direction = c.RIGHT_FACING

            self.scale = c.PIXEL_SCALING
            self.cur_texture = 0
            self.equipped_one_handed = False

            # Track our state.
            self.jumping = False
            self.climbing = False
            self.is_on_ladder = False
            self.idling = False
            self.sprinting = False
            self.firing = False

            # --- Load Textures --- #

            # Load textures for idle standing.
            self.idle_texture_pair = f.load_texture_pair(f'resources/images/characters/test/front_arms/idle_to_walk_0.png')

            # Load textures for climbing.
            self.climbing_textures = f.load_texture_pair(f'resources/images/characters/test/front_arms/idle_to_walk_0.png')

            # Load textures for One-Handed weapons.
            self.one_handed_texture_pair = f.load_texture_pair_vertical_flip(f'resources/images/characters/test/front_arms'
                                                                  f'/one_handed_arm_front_glock_17.png')

            # Load textures for going from IDLE to JUMPING.
            self.idle_to_jump_textures = []
            for i in range(16):
                texture = f.load_texture_pair(f'resources/images/characters/test/front_arms/idle_to_jump_{i}.png')
                self.idle_to_jump_textures.append(texture)

            # Load textures for walking.
            self.walk_textures = []
            for i in range(9):
                texture = f.load_texture_pair(f'resources/images/characters/test/front_arms/walk_{i}.png')
                self.walk_textures.append(texture)

            # Load textures for RUNNING.
            self.run_textures = []
            for i in range(5):
                texture = f.load_texture_pair(f'resources/images/characters/test/front_arms/run_{i}.png')
                self.run_textures.append(texture)

            # Load textures for ONE-HANDED FIRING.
            self.one_handed_firing_textures = []
            for i in range(5):
                texture = f.load_texture_pair(f'resources/images/characters/test/front_arms/one_handed_firing_{i}.png')
                self.one_handed_firing_textures.append(texture)

            # Set the initial texture.
            self.texture = self.idle_texture_pair[self.character_face_direction]

            # Destination point is where we are going.
            self.dest_x = 0
            self.dest_y = 0

            # Max speed we can rotate.
            self.rot_speed = 5

        def update_animation(self, delta_time: float = 1 / 60):
            # Equip gun
            if self.equipped_one_handed and not self.firing:
                self.texture = self.one_handed_texture_pair[self.character_face_direction]
                return

            # Fire one-handed weapon.
            if self.firing:

                self.cur_texture += 1
                if self.cur_texture > 4 * c.UPDATES_PER_FRAME:
                    self.cur_texture = 0
                frame = self.cur_texture // c.UPDATES_PER_FRAME
                direction = self.character_face_direction
                self.texture = self.one_handed_firing_textures[frame][direction]
                return

            # CLIMBING animation.
            if self.climbing:
                self.texture = self.climbing_textures[self.cur_texture // 4]
                return

            # IDLE to JUMPING animation.
            if self.jumping:
                frame = self.cur_texture // c.UPDATES_PER_FRAME
                direction = self.character_face_direction
                self.texture = self.idle_to_jump_textures[frame][direction]
                return

            # IDLE animation.
            if self.idling:
                self.texture = self.idle_texture_pair[self.character_face_direction]
                return

            if self.sprinting:
                # RUNNING animation.
                frame = self.cur_texture // c.UPDATES_PER_FRAME
                direction = self.character_face_direction
                self.texture = self.run_textures[frame][direction]
                return

            else:
                # WALKING animation.
                frame = self.cur_texture // c.UPDATES_PER_FRAME
                direction = self.character_face_direction
                self.texture = self.walk_textures[frame][direction]
                return

        def update_rotation(self, dest_x, dest_y):
            # Calculate the angle in radians between the start points
            # and end points. This is the angle the head will face.
            x_diff = dest_x - self.center_x
            y_diff = dest_y - self.center_y

            # Determine if the arm should be flipped.
            if dest_x > self.center_x:
                self.character_face_direction = c.RIGHT_FACING
            elif dest_x < self.center_x:
                self.character_face_direction = c.LEFT_FACING
            else:
                # Stay the same direction.
                pass

            angle = math.atan2(y_diff, x_diff)

            # Set the arm to face the mouse position.
            self.angle = math.degrees(angle)

    class PlayerCharacterBackArm(arcade.Sprite):
        '''Player Sprite back arm.'''

        def __init__(self):
            # Set up parent class.
            super().__init__()

            # Default to face-right.
            self.character_face_direction = c.RIGHT_FACING

            self.scale = c.PIXEL_SCALING
            self.cur_texture = 0
            self.equipped_one_handed = False

            # Track our state.
            self.jumping = False
            self.climbing = False
            self.is_on_ladder = False
            self.idling = False
            self.sprinting = False

            # --- Load Textures --- #

            # Load textures for idle standing.
            self.idle_texture_pair = f.load_texture_pair(
                f'resources/images/characters/test/back_arms/idle_to_walk_0.png')

            # Load textures for climbing.
            self.climbing_textures = f.load_texture_pair(
                f'resources/images/characters/test/back_arms/idle_to_walk_0.png')

            # Load textures for going from IDLE to JUMPING.
            self.idle_to_jump_textures = []
            for i in range(16):
                texture = f.load_texture_pair(f'resources/images/characters/test/back_arms/idle_to_jump_{i}.png')
                self.idle_to_jump_textures.append(texture)

            # Load textures for walking.
            self.walk_textures = []
            for i in range(9):
                texture = f.load_texture_pair(f'resources/images/characters/test/back_arms/walk_{i}.png')
                self.walk_textures.append(texture)

            # Load textures for RUNNING.
            self.run_textures = []
            for i in range(5):
                texture = f.load_texture_pair(f'resources/images/characters/test/back_arms/run_{i}.png')
                self.run_textures.append(texture)

            # Set the initial texture.
            self.texture = self.idle_texture_pair[self.character_face_direction]

            # Destination point is where we are going.
            self.dest_x = 0
            self.dest_y = 0

            # Max speed we can rotate.
            self.rot_speed = 5

        def update_animation(self, delta_time: float = 1 / 60):
            # CLIMBING animation.
            if self.climbing:
                self.texture = self.climbing_textures[self.cur_texture // 4]
                return

            # IDLE to JUMPING animation.
            if self.jumping:
                frame = self.cur_texture // c.UPDATES_PER_FRAME
                direction = self.character_face_direction
                self.texture = self.idle_to_jump_textures[frame][direction]
                return

            # IDLE animation.
            if self.idling:
                self.texture = self.idle_texture_pair[self.character_face_direction]
                return

            if self.sprinting:
                # RUNNING animation.
                frame = self.cur_texture // c.UPDATES_PER_FRAME
                direction = self.character_face_direction
                self.texture = self.run_textures[frame][direction]
                return

            else:
                # WALKING animation.
                frame = self.cur_texture // c.UPDATES_PER_FRAME
                direction = self.character_face_direction
                self.texture = self.walk_textures[frame][direction]
                return

        def update_rotation(self, dest_x, dest_y):
            # Calculate the angle in radians between the start points
            # and end points. This is the angle the head will face.
            x_diff = dest_x - self.center_x
            y_diff = dest_y - self.center_y

            # Determine if the arm should be flipped.
            if dest_x > self.center_x:
                self.character_face_direction = c.RIGHT_FACING
            elif dest_x < self.center_x:
                self.character_face_direction = c.LEFT_FACING
            else:
                # Stay the same direction.
                pass

            angle = math.atan2(y_diff, x_diff)

            # Set the arm to face the mouse position.
            self.angle = math.degrees(angle)
