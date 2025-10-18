from pico2d import load_image
from sdl2 import SDL_KEYDOWN, SDLK_SPACE, SDLK_RIGHT, SDL_KEYUP, SDLK_LEFT, SDLK_a, SDLK_d

from state_machine import StateMachine

# 이벤트 체크 함수
def a_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_a
def d_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_d
def a_up(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYUP and e[1].key == SDLK_a
def d_up(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYUP and e[1].key == SDLK_d

class Walk:

    def __init__(self, shadowMan):
        self.shadowMan = shadowMan

    def enter(self, e):
        self.shadowMan.current_image = self.shadowMan.walk_image
        self.shadowMan.current_sprite_size = self.shadowMan.walk_sprite_size
        self.shadowMan.frame = self.shadowMan.frame_walk
        if d_down(e) or a_up(e):
            self.shadowMan.dir = self.shadowMan.face_dir =1
        elif a_down(e) or d_up(e):
            self.shadowMan.dir = self.shadowMan.face_dir = -1

    def exit(self, e):
        pass

    def do(self):
        self.shadowMan.current_frame = (self.shadowMan.current_frame + 1) % self.shadowMan.frame
        self.shadowMan.x += self.shadowMan.dir * 20

    def draw(self):
        sprite_w, sprite_h = self.shadowMan.current_sprite_size
        if self.shadowMan.face_dir == 1:  # 오른쪽을 바라볼 때
            self.shadowMan.current_image.clip_draw(
                self.shadowMan.current_frame * sprite_w, 0, sprite_w, sprite_h,
                self.shadowMan.x, self.shadowMan.y, 300, 300
            )
        else:  # 왼쪽을 바라볼 때 (face_dir == -1)
            self.shadowMan.current_image.clip_composite_draw(
                self.shadowMan.current_frame * sprite_w, 0, sprite_w, sprite_h,
                0, 'h',  # 'h'는 수평 반전
                self.shadowMan.x, self.shadowMan.y, 300, 300
            )

class Idle:
    def __init__(self, shadowMan):
        self.shadowMan = shadowMan
        pass

    def enter(self, e):
        self.shadowMan.current_image = self.shadowMan.idle_image
        self.shadowMan.current_sprite_size = self.shadowMan.idle_sprite_size
        self.shadowMan.frame = self.shadowMan.frame_idle
        pass

    def exit(self, e):
        pass

    def do(self):
        self.shadowMan.current_frame = (self.shadowMan.current_frame + 1) % self.shadowMan.frame
        pass

    def draw(self):
        sprite_w, sprite_h = self.shadowMan.current_sprite_size
        if self.shadowMan.face_dir == 1:  # 오른쪽을 바라볼 때
            self.shadowMan.current_image.clip_draw(
                self.shadowMan.current_frame * sprite_w, 0, sprite_w, sprite_h,
                self.shadowMan.x, self.shadowMan.y, 300, 300
            )
        else:  # 왼쪽을 바라볼 때 (face_dir == -1)
            self.shadowMan.current_image.clip_composite_draw(
                self.shadowMan.current_frame * sprite_w, 0, sprite_w, sprite_h,
                0, 'h',  # 'h'는 수평 반전
                self.shadowMan.x, self.shadowMan.y, 300, 300
            )


class ShadowMan:
    def __init__(self):
        self.x, self.y = 200, 300
        self.idle_image = load_image('그림자검객_idle.png')
        self.walk_image = load_image('그림자검객_walk.png')
        self.idle_sprite_size = (340, 360)
        self.walk_sprite_size = (227, 260)
        self.frame_idle = 3
        self.frame_walk = 5
        # 이동 방향 변수
        self.dir = 0
        # 바라보는 방향 변수
        self.face_dir = 1
        # 현재 스프라이트 이미지 정보 선택 변수
        self.current_image = self.idle_image
        self.current_sprite_size = self.idle_sprite_size
        self.frame = self.frame_idle
        self.current_frame = 0

        # 상태 변화 테이블
        self.IDLE = Idle(self)
        self.WALK = Walk(self)
        self.state_machine = StateMachine(
            self.IDLE,
            {
                self.IDLE:{a_down : self.WALK, d_down : self.WALK},
                self.WALK:{a_up : self.IDLE, d_up : self.IDLE}
            }
        )  # 상태머신 생성 및 초기 시작 상태 설정

    def update(self):
        self.state_machine.update()

    def draw(self):
        self.state_machine.draw()

    def handle_event(self, event):
        self.state_machine.handle_state_event(('INPUT', event))
        pass
