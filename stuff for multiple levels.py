self.level = 1
self.next_level_list = arcade.SpriteList()

# self.change_level_list, and use custom properties as to whether
# it decreases the self.level variable or increases it.


# Check if the player got to the end of the current map
# and made it to the next level. If so, go to the next level.
if arcade.check_for_collision_with_list(self.player_sprite,
                                        self.next_level_list):
    self.level += 1
    
    self.setup(self.level)

on_draw():
    self.next_level_list.draw(filter=GL_NEAREST)
