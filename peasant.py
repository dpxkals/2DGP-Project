from pico2d import load_image, get_time, load_font, draw_rectangle
from sdl2 import SDL_KEYDOWN, SDLK_SPACE, SDLK_RIGHT, SDL_KEYUP, SDLK_LEFT, SDLK_a, SDLK_d

import game_framework
from state_machine import StateMachine

# Run speed
PIXEL_PER_METER = (10.0 / 2)  # 10 pixel 5 cm
RUN_SPEED_KMPH = 20.0 # Km / Hour 보행 속도
RUN_SPEED_MPM = (RUN_SPEED_KMPH * 1000.0 / 60.0)
RUN_SPEED_MPS = (RUN_SPEED_MPM / 60.0)
RUN_SPEED_PPS = (RUN_SPEED_MPS * PIXEL_PER_METER)

TIME_PER_ACTION = 0.4
ACTION_PER_TIME = 1.0 / TIME_PER_ACTION
FRAMES_PER_ACTION = 6
FRAMES_PER_SECOND = FRAMES_PER_ACTION * ACTION_PER_TIME

# 이벤트 체크 함수
def a_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_a
def d_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_d
def a_up(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYUP and e[1].key == SDLK_a
def d_up(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYUP and e[1].key == SDLK_d

class Idle:
    def __init__(self, Peasant):
        self.peasant = Peasant

    def enter(self, e):
        self.peasant.current_image = self.peasant.idle_image
        self.peasant.current_sprite_size = self.peasant.idle_sprite_size
        self.peasant.frame = self.peasant.frame_idle
    def exit(self, e):
        pass

    def do(self):
        self.peasant.current_frame = (self.peasant.current_frame + FRAMES_PER_SECOND * game_framework.frame_time) % self.peasant.frame
        pass

    def draw(self):
        sprite_w, sprite_h = self.peasant.current_sprite_size
        self.peasant.current_image.clip_draw(
            int(self.peasant.current_frame) * sprite_w, 0, sprite_w, sprite_h,
            self.peasant.x, self.peasant.y, 250, 300
        )

class Peasant:
    def __init__(self):
        self.idle_image = load_image('Peasant_idle.png')
        self.x, self.y = 700, 300
        self.idle_sprite_size = (96, 96)
        self.frame_idle = 6
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
        self.state_machine = StateMachine(
            self.IDLE,
            {
                self.IDLE: {
                    a_down: self.IDLE,
                    d_down: self.IDLE,
                    a_up: self.IDLE,
                    d_up: self.IDLE,
                }
            }
        )  # 상태머신 생성 및 초기 시작 상태 설정

    def update(self):
        self.state_machine.update()

    def draw(self):
        self.state_machine.draw()
        draw_rectangle(*self.get_bb())

    def handle_event(self, event):
        self.state_machine.handle_state_event(('INPUT', event))


    def get_bb(self):
        return self.x-20, self.y-40, self.x+20, self.y+40

    def handle_collision(self, group, other):
        if group == '1p:2p':
           pass