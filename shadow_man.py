from pico2d import load_image
from state_machine import StateMachine

class Idle:
    def __init__(self, shadowman):
        self.shadowman = shadowman
        pass

    def enter(self):
        pass

    def exit(self):
        pass

    def do(self):
        if self.shadowman.is_walking:
            self.shadowman.current_image = self.shadowman.walk_image
            self.shadowman.current_sprite_size = self.shadowman.walk_sprite_size
            self.shadowman.frame = self.shadowman.frame_walk
        else:
            self.shadowman.current_image = self.shadowman.idle_image
            self.shadowman.current_sprite_size = self.shadowman.idle_sprite_size
            self.shadowman.frame = self.shadowman.frame_idle

        self.shadowman.current_frame = (self.shadowman.current_frame + 1) % self.shadowman.frame
        if self.shadowman.is_walking:
            self.shadowman.x += 10
        pass

    def draw(self):
        sprite_w, sprite_h = self.shadowman.current_sprite_size
        self.shadowman.current_image.clip_draw(
            self.shadowman.current_frame * sprite_w, 0, sprite_w, sprite_h,
            self.shadowman.x, self.shadowman.y, 400, 400
        )
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

        self.IDLE = Idle(self)
        self.state_machine = StateMachine(self.IDLE)  # 상태머신 생성 및 초기 시작 상태 설정

    def update(self):
        self.state_machine.update()

    def draw(self):
        self.state_machine.draw()
