'''
UNEXPLORED by Kael.
'''

import arcade
import arcade.gui
from arcade.gui import UIManager
import os
import random
from pyglet.gl import GL_NEAREST
import math
import timeit
import game_constants as c
import game_player as p
import game_functions as f
import game_audio as a
import game_backgrounds as b
import game_entities as e
import game_gui as g


class GameView(arcade.View):
    '''Main application class.'''

    def __init__(self):
        '''Initialiser for the game.'''

        # Call the parent class and set up the window.
        super().__init__()

        # Set the path to start with this program.
        file_path = os.path.dirname(os.path.abspath(__file__))
        os.chdir(file_path)

        # Checks if the treasure has been found and the game won.
        self.game_won = False

        # Manages the GUI.
        self.ui_manager = UIManager()

        # For if we are in fullscreen mode.
        self.is_fullscreen = False

        # Track the current state of what key is pressed.
        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        self.down_pressed = False
        self.jump_needs_reset = False
        self.shift_pressed = False

        # These are 'lists' that keep track of our sprites. Each sprite should
        # go into a list.
        self.coin_list = None
        self.backgrounds_list = None
        self.foreground_decorations_list = None
        self.explosions_list = None
        self.barrel_list = None
        self.background_decorations_list = None
        self.background_walls_list = None
        self.treasure_list = None
        self.wall_list = None
        self.ladder_list = None
        self.player_list = None
        self.bullet_list = None
        self.fade_list = None
        self.user_interface_list = None

        # Player sprite variables. Body, legs etc.
        self.player_sprite = None

        # Our background sprites.
        self.background_0 = None

        # The hit effects textures.
        self.explosion_texture_list = []

        # The frames for the barrel itself exploding, not the actual fiery explosion animation.
        self.barrel_texture_list = []

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

        # Set mouse to invisible.
        self.window.set_mouse_visible(False)

        # Reticle used instead of the mouse cursor.
        self.reticle = None

        # -- Variables for our statistics -- #

        # Time for on_update.
        self.processing_time = 0

        # Time for on_draw.
        self.draw_time = 0

        # Variables used to calculate frames per second.
        self.frame_count = 0
        self.fps_start_timer = None
        self.fps = None
        # Set background colour.
        arcade.set_background_color(arcade.color.CORNFLOWER_BLUE)

        # Load all of the audio into a dictionary.
        a.add_audio_to_list()
        a.load_audio()

        # Load all of the positions for the head from the different animation frames.
        f.add_frames_to_list()
        f.load_frames_and_positions()

        # Do the same for the arms.
        f.arms_add_frames_to_list()
        f.arms_load_frames_and_positions()

    def setup(self):
        '''Set up the game here. Call this function to restart the game.'''

        self.ui_manager.purge_ui_elements()

        # Used to keep track of our scrolling.
        self.view_bottom = 0
        self.view_left = 0

        # Keep track of the score.
        self.score = 0

        # Create the Sprite lists.
        self.player_list = arcade.SpriteList()
        self.backgrounds_list = arcade.SpriteList()
        self.background_decorations_list = arcade.SpriteList()
        self.explosions_list = arcade.SpriteList()
        self.foreground_decorations_list = arcade.SpriteList()
        self.treasure_list = arcade.SpriteList()
        self.wall_list = arcade.SpriteList()
        self.coin_list = arcade.SpriteList()
        self.bullet_list = arcade.SpriteList()
        self.fade_list = arcade.SpriteList()
        self.user_interface_list = arcade.SpriteList()

        # Set up the player, specifically placing it at these coordinates.
        self.player_sprite = p.PlayerCharacter()
        self.player_sprite.center_x = c.PLAYER_START_X
        self.player_sprite.center_y = c.PLAYER_START_Y

        self.player_list.append(self.player_sprite.legs)
        self.player_list.append(self.player_sprite.back_arm)
        self.player_list.append(self.player_sprite)
        self.player_list.append(self.player_sprite.head)
        self.player_list.append(self.player_sprite.front_arm)

        # Reticle used instead of the mouse cursor.
        self.reticle = g.Reticle()
        self.reticle.follow_x = self.mouse_position_x
        self.reticle.follow_y = self.mouse_position_y
        self.user_interface_list.append(self.reticle)

        # --- Load in a map from the tiled editor --- #

        # Name of the layer in the file that has our platforms/walls.
        walls_layer_name = 'Walls'
        moving_platforms_layer_name = 'Moving Platforms'

        # Name of the layer that has items for pick-up.
        coins_layer_name = 'Coins'

        # Names of the decorations layers, these only show sprites.
        foreground_decorations_layer_name = 'Foreground Decorations'
        background_decorations_layer_name = 'Background Decorations'

        # Darkened background walls.
        background_walls_layer_name = 'Background Walls'

        # Explosive barrels that explode when shot.
        barrels_layer_name = 'Barrels'

        # The treasure at the end of the game.
        treasure_layer_name = 'Treasure'

        # Map name.
        map_name = f'resources/maps/1.tmx'

        # Read in the tiled map.
        my_map = arcade.tilemap.read_tmx(map_name)

        # Calculate the right edge of the my_map in pixels.
        self.end_of_map = my_map.map_size.width * c.GRID_PIXEL_SIZE

        # Add and reset fading layer.
        f.screen_fade.alpha = 0
        self.fade_list.append(f.screen_fade)

        # Parallax environment backgrounds.
        self.background_0 = b.Background()

        self.background_0.follow_x = self.player_sprite.center_x
        self.background_0.follow_y = self.player_sprite.center_y
        self.backgrounds_list.append(self.background_0)

        # Platforms.
        self.wall_list = arcade.tilemap.process_layer(my_map,
                                                      walls_layer_name,
                                                      c.PIXEL_SCALING,
                                                      use_spatial_hash=True)
        # Foreground decorations.
        self.foreground_decorations_list = arcade.tilemap.process_layer(my_map, foreground_decorations_layer_name,
                                                                        c.PIXEL_SCALING,
                                                                        use_spatial_hash=True)

        # Explosive barrels.
        self.barrel_list = arcade.tilemap.process_layer(my_map, barrels_layer_name,
                                                                c.PIXEL_SCALING,
                                                                use_spatial_hash=True)
        # Background decorations.
        self.background_decorations_list = arcade.tilemap.process_layer(my_map, background_decorations_layer_name,
                                                                        c.PIXEL_SCALING,
                                                                        use_spatial_hash=True)
        # Background walls.
        # self.background_walls_list = arcade.tilemap.process_layer(my_map, background_walls_layer_name,
        #                                                          c.PIXEL_SCALING,
        #                                                          use_spatial_hash=True)
        '''
        # Moving Platforms.
        moving_platforms_list = arcade.tilemap.process_layer(my_map, moving_platforms_layer_name, PIXEL_SCALING)
        for sprite in moving_platforms_list:
            self.wall_list.append(sprite)

        # Ladders.
        self.ladder_list = arcade.tilemap.process_layer(my_map, 'Ladders',
                                                        PIXEL_SCALING,
                                                        use_spatial_hash=True)
        '''
        # Treasure (end goal).
        self.treasure_list = arcade.tilemap.process_layer(my_map, treasure_layer_name,
                                                          c.PIXEL_SCALING,
                                                          use_spatial_hash=True)

        # Pre-load the animation frames for hit effects. We don't do this in the __init__
        # of the explosion sprite because it
        # takes too long and would cause the game to pause.
        self.explosion_texture_list = []

        # Load the explosions.
        for i in range(8):
            texture = arcade.load_texture(f'resources/images/effects/dirt_{i}.png')
            self.explosion_texture_list.append(texture)

        # The frames for the barrel itself exploding, not the actual fiery explosion animation.
        for i in range(5):
            texture = arcade.load_texture(f'resources/images/effects/barrel_{i}.png')
            self.barrel_texture_list.append(texture)

        # Other stuff.
        # Set the background color
        if my_map.background_color:
            arcade.set_background_color(my_map.background_color)

        # Create the 'physics engine'.
        self.physics_engine = arcade.PhysicsEnginePlatformer(self.player_sprite,
                                                             self.wall_list,
                                                             gravity_constant=c.GRAVITY,
                                                             ladders=self.ladder_list)

    def on_draw(self):
        '''Render the screen.'''

        # Start timing how long this takes
        start_time = timeit.default_timer()

        # --- Calculate FPS

        fps_calculation_freq = 60
        # Once every 60 frames, calculate our FPS.
        if self.frame_count % fps_calculation_freq == 0:
            # Do we have a start time?
            if self.fps_start_timer is not None:
                # Calculate FPS.
                total_time = timeit.default_timer() - self.fps_start_timer
                self.fps = fps_calculation_freq / total_time
            # Reset the timer.
            self.fps_start_timer = timeit.default_timer()
        # Add one to our frame count.
        self.frame_count += 1

        # Clear the screen to the background colour.
        arcade.start_render()

        # Draw our sprites.
        self.backgrounds_list.draw(filter=GL_NEAREST)
        # self.background_walls_list.draw(filter=GL_NEAREST)
        self.background_decorations_list.draw(filter=GL_NEAREST)
        self.treasure_list.draw(filter=GL_NEAREST)
        self.player_list.draw(filter=GL_NEAREST)
        self.bullet_list.draw(filter=GL_NEAREST)
        self.barrel_list.draw(filter=GL_NEAREST)
        self.explosions_list.draw(filter=GL_NEAREST)
        self.wall_list.draw(filter=GL_NEAREST)
        '''
        self.ladder_list.draw(filter=GL_NEAREST)
        self.coin_list.draw(filter=GL_NEAREST)
        '''
        self.foreground_decorations_list.draw(filter=GL_NEAREST)
        self.user_interface_list.draw(filter=GL_NEAREST)

        self.fade_list.draw(filter=GL_NEAREST)

        # Draw our score on the screen, scrolling it with the viewport.
        # score_text = f'Score: {self.score}'
        # arcade.draw_text(score_text, 10 + self.view_left, 10 + self.view_bottom,
        #                 arcade.csscolor.WHITE, 32, font_name='resources/Unexplored.ttf')

        # Draw hit boxes.
        # for wall in self.wall_list:
        # wall.draw_hit_box(arcade.color.BLACK, 3)

        # self.player_sprite.draw_hit_box(arcade.color.RED, 2)

        # Display timings.
        '''
        output = f"Processing time: {self.processing_time:.3f}"
        arcade.draw_text(output,  + self.view_left, c.SCREEN_HEIGHT - 25 + self.view_bottom,
                         arcade.color.WHITE, 18, font_name='resources/Unexplored.ttf')

        output = f"Drawing time: {self.draw_time:.3f}"
        arcade.draw_text(output, 20 + self.view_left, c.SCREEN_HEIGHT - 50 + self.view_bottom,
                         arcade.color.WHITE, 18, font_name='resources/Unexplored.ttf')
        '''
        if self.fps is not None:
            output = f'{self.fps:.0f} FPS'
            arcade.draw_text(output, 20 + self.view_left, c.SCREEN_HEIGHT - 40 + self.view_bottom,
                             arcade.color.WHITE, 18, font_name='resources/Unexplored.ttf')

        # Stop the draw timer, and calculate total on_draw time.
        self.draw_time = timeit.default_timer() - start_time

    def process_keychange(self):
        '''Called when we change a key up/down or we move on/off a ladder.'''

        # Process up/down.
        if self.up_pressed and not self.down_pressed:
            if self.physics_engine.is_on_ladder():
                self.player_sprite.change_y = c.PLAYER_WALK_SPEED
            elif self.physics_engine.can_jump(y_distance=10) and not self.jump_needs_reset:
                self.player_sprite.change_y = c.PLAYER_JUMP_SPEED
                self.jump_needs_reset = True
                arcade.play_sound(a.sound[f'jump_{random.randint(1, 2)}'])
        elif self.down_pressed and not self.up_pressed:
            if self.physics_engine.is_on_ladder():
                self.player_sprite.change_y = -c.PLAYER_WALK_SPEED

        # Process up/down when on a ladder and no movement.
        if self.physics_engine.is_on_ladder():
            if not self.up_pressed and not self.down_pressed:
                self.player_sprite.change_y = 0
            elif self.up_pressed and self.down_pressed:
                self.player_sprite.change_y = 0

        # Process left/right and sprinting.
        if self.shift_pressed:
            if self.right_pressed and not self.left_pressed:
                self.player_sprite.change_x = c.PLAYER_RUN_SPEED
                self.player_sprite.sprinting = True
            elif self.left_pressed and not self.right_pressed:
                self.player_sprite.change_x = -c.PLAYER_RUN_SPEED
                self.player_sprite.sprinting = True
            else:
                self.player_sprite.change_x = 0
                self.player_sprite.sprinting = False
        else:
            if self.right_pressed and not self.left_pressed:
                self.player_sprite.change_x = c.PLAYER_WALK_SPEED
                self.player_sprite.sprinting = False
            elif self.left_pressed and not self.right_pressed:
                self.player_sprite.change_x = -c.PLAYER_WALK_SPEED
                self.player_sprite.sprinting = False
            else:
                self.player_sprite.change_x = 0
                self.player_sprite.sprinting = False

    def on_key_press(self, key, modifiers):
        '''Called whenever a key is pressed.'''

        if key == arcade.key.LSHIFT:
            self.shift_pressed = True
        elif key == arcade.key.W:
            self.up_pressed = True
        elif key == arcade.key.S:
            self.down_pressed = True
        elif key == arcade.key.A:
            self.left_pressed = True
        elif key == arcade.key.D:
            self.right_pressed = True
        elif key == arcade.key.KEY_2:
            if self.player_sprite.equipped_one_handed:
                self.player_sprite.equipped_one_handed = False
            elif not self.player_sprite.equipped_one_handed:
                self.player_sprite.equipped_one_handed = True

            if self.player_sprite.equipped_one_handed:
                self.player_sprite.equipped_any = True
            else:
                self.player_sprite.equipped_any = False

        self.process_keychange()

    def on_key_release(self, key, modifiers):
        '''Called when the user releases a key.'''

        if key == arcade.key.LSHIFT:
            self.shift_pressed = False
        elif key == arcade.key.W:
            self.up_pressed = False
            self.jump_needs_reset = False
        elif key == arcade.key.S:
            self.down_pressed = False
        elif key == arcade.key.A:
            self.left_pressed = False
        elif key == arcade.key.D:
            self.right_pressed = False

        self.process_keychange()

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        '''Called whenever the user uses the scroll on the mouse.
            Used mostly for weapon selection for the player.'''
        pass

    def on_mouse_press(self, x, y, button, modifiers):
        '''Called whenever the mouse button is clicked.'''

        # Create a bullet.
        if self.player_sprite.equipped_one_handed and button == arcade.MOUSE_BUTTON_LEFT:
            self.player_sprite.front_arm.firing = True
            bullet = arcade.Sprite('resources/images/effects/bullet_projectile.png', c.PIXEL_SCALING)
            bullet.set_hit_box([[-2, -2], [-2, 2], [2, 2], [2, -2]])

            # Position the bullet at the player's front arm.
            start_x = self.player_sprite.front_arm.center_x
            start_y = self.player_sprite.front_arm.center_y  # TODO: Change this to gun position.
            bullet.center_x = start_x
            bullet.center_y = start_y

            # Get from the mouse the destination location for the bullet
            # IMPORTANT! If you have a scrolling screen, you will also need
            # to add in self.view_bottom and self.view_left.
            dest_x = x + self.view_left
            dest_y = y + self.view_bottom

            # Do maths to calculate how to get the bullet to the destination.
            # Calculation the angle in radians between the start points
            # and end points. This is the angle the bullet will travel.
            x_diff = dest_x - start_x
            y_diff = dest_y - start_y
            angle = math.atan2(y_diff, x_diff)

            # Angle the bullet sprite so it doesn't look like it is flying
            # sideways.
            bullet.angle = math.degrees(angle)

            # Taking into account the angle, calculate our change_x
            # and change_y. Velocity is how fast the bullet travels.
            bullet.change_x = (math.cos(angle) * c.BULLET_SPEED)
            bullet.change_y = (math.sin(angle) * c.BULLET_SPEED)

            # Reposition bullet
            bullet.center_x += math.cos(angle) * (36 * c.PIXEL_SCALING)
            bullet.center_y += math.sin(angle) * (36 * c.PIXEL_SCALING)

            # Add the bullet to the appropriate lists
            self.bullet_list.append(bullet)
            arcade.play_sound(a.sound['glock_17_fire'])

    def on_update(self, delta_time):
        '''Movement and game logic.'''

        # Start timing how long this takes.
        start_time = timeit.default_timer()

        if self.player_sprite.center_y < c.WORLD_BOTTOM:
            self.setup()

        # Get mouse position.
        # view_left and view_bottom added so that the position works when the scrolling screen moves.
        self.player_sprite.acquire_mouse_position(self.mouse_position_x + self.view_left,
                                                  self.mouse_position_y + self.view_bottom)


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
        self.player_list.update_animation(delta_time)

        self.coin_list.update_animation(delta_time)

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

        # Bullets and hit effects.
        self.bullet_list.update()
        self.explosions_list.update()

        # Loop through each bullet
        for bullet in self.bullet_list:

            # See if we hit any barrels.
            barrel_hit_list = arcade.check_for_collision_with_list(bullet,
                                                                   self.barrel_list)
            # Loop through each barrel we hit (if any) and remove it.
            for barrel in barrel_hit_list:
                # TODO: the barrel getting destroyed animation.

                # Remove the barrel.
                barrel.remove_from_sprite_lists()

            # If it did, get rid of the bullet
            if len(barrel_hit_list) > 0:
                bullet.remove_from_sprite_lists()

            # Check this bullet to see if it hit a wall.
            hit_list = arcade.check_for_collision_with_list(bullet, self.wall_list)

            # If it did, get rid of the bullet
            if len(hit_list) > 0:
                # Make an explosion.
                explosion = e.Explosion(texture_list=self.explosion_texture_list)

                # Move it to the location of the coin.
                explosion.center_x = bullet.center_x
                explosion.center_y = bullet.center_y
                explosion.scale = c.PIXEL_SCALING

                # Call update() because it sets which image we start on.
                explosion.update()

                # Add to a list of sprites that are explosions.
                self.explosions_list.append(explosion)
                bullet.remove_from_sprite_lists()

            # If the bullet flies out of the map, remove it.
            if bullet.bottom > c.CULL_DISTANCE_Y + self.player_sprite.center_y or bullet.top < c.CULL_DISTANCE_Y * -1 + self.player_sprite.center_y or bullet.right < c.CULL_DISTANCE_X * -1 + self.player_sprite.center_x or bullet.left > c.CULL_DISTANCE_X + self.player_sprite.center_x:
                bullet.remove_from_sprite_lists()


        # See if we hit the treasure.
        if not self.game_won:
            treasure_hit_list = arcade.check_for_collision_with_list(self.player_sprite.legs,
                                                                     self.treasure_list)
            # Loop through each treasure we hit.
            if treasure_hit_list:
                # Change the game to 'won'. Accessed by the if statement below.
                self.game_won = True
                # End the game.

        if self.game_won:
            # If sufficiently dark, move to end view.
            f.screen_fade.center_x = self.view_left + c.SCREEN_WIDTH // 2
            f.screen_fade.center_y = self.view_bottom + c.SCREEN_HEIGHT // 2
            f.screen_fade.change_fade(target=255, change=4)
            if f.screen_fade.alpha >= 250:
                end_view = EndView()
                self.window.show_view(end_view)

        # Update the environment backgrounds.
        self.background_0.follow_x = self.player_sprite.center_x
        self.background_0.follow_y = self.player_sprite.center_y
        self.backgrounds_list.update()

        # Track if we need to change the viewport.
        changed_viewport = False

        # --- Manage Scrolling --- #

        # Scroll left.
        left_boundary = self.view_left + c.LEFT_VIEWPORT_MARGIN
        if self.player_sprite.left < left_boundary:
            self.view_left -= left_boundary - self.player_sprite.left
            changed_viewport = True

        # Scroll right.
        right_boundary = self.view_left + c.SCREEN_WIDTH - c.RIGHT_VIEWPORT_MARGIN
        if self.player_sprite.right > right_boundary:
            self.view_left += self.player_sprite.right - right_boundary
            changed_viewport = True

        # Scroll up.
        top_boundary = self.view_bottom + c.SCREEN_HEIGHT - c.TOP_VIEWPORT_MARGIN
        if self.player_sprite.top > top_boundary:
            self.view_bottom += self.player_sprite.top - top_boundary
            changed_viewport = True

        # Scroll down.
        bottom_boundary = self.view_bottom + c.BOTTOM_VIEWPORT_MARGIN
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
                                c.SCREEN_WIDTH + self.view_left,
                                self.view_bottom,
                                c.SCREEN_HEIGHT + self.view_bottom)

            # Stop the draw timer, and calculate total on_draw time.
            self.processing_time = timeit.default_timer() - start_time

        # Position the reticle. This is after the viewport code so that the view_left and view_bottom are updated.
        self.reticle.visible = True
        self.reticle.follow_x = self.mouse_position_x + self.view_left
        self.reticle.follow_y = self.mouse_position_y + self.view_bottom
        self.user_interface_list.update()

    def on_mouse_motion(self, x, y, dx, dy):
        '''Handle Mouse Motion.'''

        # Update the position of the mouse.
        self.mouse_position_x = x
        self.mouse_position_y = y

    def on_hide_view(self):
        # For when the view is switched.
        self.ui_manager.unregister_handlers()


class MainMenuView(arcade.View):
    '''The main menu that shows when you start the game.'''

    def __init__(self):
        '''This is run once when we switch to this view.'''
        super().__init__()

        # For managing the GUI.
        self.ui_manager = UIManager()

        # Reset the viewport, necessary if we have a scrolling game and we need
        # to reset the viewport back to the start so we can see what we draw.
        arcade.set_viewport(0, c.SCREEN_WIDTH - 1, 0, c.SCREEN_HEIGHT - 1)

        self.main_menu_list = arcade.SpriteList()
        self.menu_texture = arcade.load_texture('resources/images/ui/main_menu.png')
        self.main_menu_image = None

        self.fade_list = arcade.SpriteList()

    def on_show(self):
        '''This is run once when we switch to this view.'''

        # Get rid of any existing ui elements.
        self.ui_manager.purge_ui_elements()

        # Set mouse to visible.
        self.window.set_mouse_visible(True)

        y_slot = self.window.height // 4
        left_column_x = self.window.width // 4
        right_column_x = 3 * self.window.width // 4

        # TODO: Comments here.
        button_normal = arcade.load_texture('resources/images/ui/new_game_regular.png')
        hovered_texture = arcade.load_texture('resources/images/ui/new_game_hover.png')
        pressed_texture = arcade.load_texture('resources/images/ui/new_game_hover.png')
        button = g.StartButton(
            center_x=left_column_x - 50 * c.PIXEL_SCALING,
            center_y=y_slot * 3,
            normal_texture=button_normal,
            hover_texture=hovered_texture,
            press_texture=pressed_texture,
        )

        self.ui_manager.add_ui_element(button)
        self.main_menu_image = arcade.Sprite()
        self.main_menu_image.texture = self.menu_texture
        self.main_menu_image.scale = c.PIXEL_SCALING
        self.main_menu_image.center_x = c.SCREEN_WIDTH / 2
        self.main_menu_image.center_y = c.SCREEN_HEIGHT / 2
        self.main_menu_list.append(self.main_menu_image)
        # Reset the viewport, necessary if we have a scrolling game and we need
        # to reset the viewport back to the start so we can see what we draw.
        arcade.set_viewport(0, c.SCREEN_WIDTH - 1, 0, c.SCREEN_HEIGHT - 1)

        self.fade_list.append(f.screen_fade)

    def on_draw(self):
        '''Draw this view.'''
        arcade.start_render()
        self.main_menu_list.draw(filter=GL_NEAREST)
        self.fade_list.draw(filter=GL_NEAREST)

    def on_update(self, delta_time: float):
        '''For updating the scenes and animations.'''
        if f.screen_fade.fade:
            self.ui_manager.purge_ui_elements()
            f.screen_fade.change_fade(target=255, change=4)

        # If sufficiently dark, move to intro view.
        if f.screen_fade.alpha >= 250:
            intro_view = IntroView()
            self.window.show_view(intro_view)

    def on_mouse_press(self, x, y, button, modifiers):
        '''If the user presses the mouse button, start the intro.'''


class IntroView(arcade.View):
    '''The cinematic intro that plays once the player selects 'New game'.'''

    def __init__(self):
        '''This is run once when we switch to this view.'''
        super().__init__()

        # For managing the GUI.
        self.ui_manager = UIManager()

        # Reset the viewport, necessary if we have a scrolling game and we need
        # to reset the viewport back to the start so we can see what we draw.
        arcade.set_viewport(0, c.SCREEN_WIDTH - 1, 0, c.SCREEN_HEIGHT - 1)

        self.scene_list = arcade.SpriteList()

        # Black fading effect.
        self.fade_list = arcade.SpriteList()

        # Initial scene.
        self.scene = 1
        self.cur_texture = 0

        # The image that is displayed
        self.image = arcade.Sprite()

        # Load textures for scene 1.
        self.scene_1_textures = []
        for i in range(12):
            texture = arcade.load_texture(f'resources/images/cutscene/auckland_{i}.png')
            self.scene_1_textures.append(texture)

        # Load initial texture.
        self.image.texture = self.scene_1_textures[0]

        self.scene_list.append(self.image)
        self.fade_list.append(f.screen_fade)

        # TODO: TEMPORARY INSTRUCTIONS IN INTRO
        self.instructions_image = arcade.Sprite()
        self.instructions_image.texture = arcade.load_texture('resources/images/ui/instructions_text.png')
        self.instructions_image.scale = c.INTRO_SCALING
        self.instructions_image.center_x = c.SCREEN_WIDTH / 2
        self.instructions_image.center_y = c.SCREEN_HEIGHT / 2

        self.scene_list.append(self.instructions_image)

    def on_show(self):
        '''This is run once when we switch to this view.'''

        # Remove all previous UI.
        self.ui_manager.purge_ui_elements()

        # Set mouse to visible.
        self.window.set_mouse_visible(True)

        # Reset the viewport, necessary if we have a scrolling game and we need
        # to reset the viewport back to the start so we can see what we draw.
        arcade.set_viewport(0, c.SCREEN_WIDTH - 1, 0, c.SCREEN_HEIGHT - 1)

        # Start the screen fading.
        f.screen_fade.fade = True

    def on_update(self, delta_time: float):
        '''For updating the scenes and animations.'''

        # Check which scene we are on.
        if self.scene == 1:
            # Update the animation.
            self.cur_texture += 1
            if self.cur_texture > (len(self.scene_1_textures) - 1) * c.INTRO_UPDATES_PER_FRAME:
                # Back to first frame if loop is complete.
                self.cur_texture = 0
            frame = self.cur_texture // c.INTRO_UPDATES_PER_FRAME
            self.image.texture = self.scene_1_textures[frame]
        self.image.scale = c.INTRO_SCALING
        self.image.center_x = c.SCREEN_WIDTH / 2
        self.image.center_y = c.SCREEN_HEIGHT / 2
        if f.screen_fade.fade:
            f.screen_fade.change_fade(target=0, change=4)

    def on_draw(self):
        '''Draw this view.'''
        arcade.start_render()
        self.scene_list.draw(filter=GL_NEAREST)
        self.fade_list.draw(filter=GL_NEAREST)

    def on_mouse_press(self, x, y, button, modifiers):
        '''If the user presses the mouse button, start the game.'''
        game_view = GameView()
        game_view.setup()
        self.window.show_view(game_view)


class EndView(arcade.View):
    '''The end view that shows when the player finds the treasure and ends the game.'''

    def __init__(self):
        '''This is run once when we switch to this view.'''
        super().__init__()

        # For managing the GUI.
        self.ui_manager = UIManager()

        # Reset the viewport, necessary if we have a scrolling game and we need
        # to reset the viewport back to the start so we can see what we draw.
        arcade.set_viewport(0, c.SCREEN_WIDTH - 1, 0, c.SCREEN_HEIGHT - 1)

        self.end_image_list = arcade.SpriteList()
        self.image_texture = arcade.load_texture('resources/images/ui/end_screen.png')
        self.end_image = arcade.Sprite()

        self.fade_list = arcade.SpriteList()

    def on_show(self):
        '''Set stuff for the end screen image.'''

        # Remove all previous UI.
        self.ui_manager.purge_ui_elements()

        # Set mouse to visible.
        self.window.set_mouse_visible(True)

        # Reset the viewport, necessary if we have a scrolling game and we need
        # to reset the viewport back to the start so we can see what we draw.
        arcade.set_viewport(0, c.SCREEN_WIDTH - 1, 0, c.SCREEN_HEIGHT - 1)

        self.end_image.texture = self.image_texture
        self.end_image.scale = c.PIXEL_SCALING
        self.end_image.center_x = c.SCREEN_WIDTH / 2
        self.end_image.center_y = c.SCREEN_HEIGHT / 2
        self.end_image_list.append(self.end_image)

        self.fade_list.append(f.screen_fade)

    def on_draw(self):
        '''Draw this view.'''
        arcade.start_render()
        self.end_image_list.draw(filter=GL_NEAREST)
        self.fade_list.draw(filter=GL_NEAREST)

    def on_update(self, delta_time: float):
        '''For updating the scenes and animations.'''
        f.screen_fade.change_fade(target=0, change=4)
        arcade.set_viewport(0, c.SCREEN_WIDTH - 1, 0, c.SCREEN_HEIGHT - 1)


def main():
    '''Main method.'''
    window = arcade.Window(c.SCREEN_WIDTH, c.SCREEN_HEIGHT, c.SCREEN_TITLE, resizable=False, fullscreen=True)
    start_view = MainMenuView()
    window.show_view(start_view)
    arcade.run()


if __name__ == '__main__':
    main()
