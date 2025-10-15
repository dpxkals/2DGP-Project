from pico2d import load_image

class IDLE:
    def __init__(self, shadowman):
        pass

    def enter(self):
        pass

    def exit(self):
        pass

    def do(self):
        pass

    def draw(self):
        pass


class ShadowMan:
    def __init__(self):
        self.x, self.y = 200, 200
        self.is_walking = False
        self.idle_image = load_image('그림자검객_idlePNG.png')
        self.walk_image = load_image('그림자검객_walk.png')
        self.idle_sprite_size = (340, 360)
        self.walk_sprite_size = (227, 260)
        self.frame_idle = 3
        self.frame_walk = 5
        self.current_image = self.idle_image
        self.current_sprite_size = self.idle_sprite_size
        self.frame = self.frame_idle
        self.current_frame = 0

    def set_walking(self, walking):
        self.is_walking = walking
        if walking:
            self.current_image = self.walk_image
            self.current_sprite_size = self.walk_sprite_size
            self.frame = self.frame_walk
        else:
            self.current_image = self.idle_image
            self.current_sprite_size = self.idle_sprite_size
            self.frame = self.frame_idle

    def update(self):
        self.current_frame = (self.current_frame + 1) % self.frame
        if self.is_walking:
            self.x += 10

    def draw(self):
        sprite_w, sprite_h = self.current_sprite_size
        self.current_image.clip_draw(
            self.current_frame * sprite_w, 0, sprite_w, sprite_h,
            self.x, self.y, 400, 400
        )
