from pico2d import load_image
from sdl2 import SDL_KEYDOWN, SDLK_SPACE, SDLK_RIGHT, SDL_KEYUP, SDLK_LEFT, SDLK_a, SDLK_d, SDLK_LCTRL

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
def lctrl_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_LCTRL
def lctrl_up(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYUP and e[1].key == SDLK_LCTRL
def dash_end(e):
    return e[0] == 'DASH_END'


class Dash:
    def __init__(self, shadowMan):
        self.shadowMan = shadowMan
        self.dash_speed = 100  # 대시 속도
        self.dash_duration = 3  # 대시 지속 프레임
        self.dash_timer = 0

    def enter(self, e):
        # 대시 이미지가 있다면 변경 (없다면 walk 이미지 사용)
        self.shadowMan.current_image = self.shadowMan.dash_image
        self.shadowMan.current_sprite_size = self.shadowMan.dash_sprite_size
        self.shadowMan.frame = self.shadowMan.frame_dash
        self.dash_timer = self.dash_duration
        # 현재 바라보는 방향으로 대시

    def exit(self, e):
        pass

    def do(self):
        self.shadowMan.current_frame = (self.shadowMan.current_frame + 1) % self.shadowMan.frame
        # 대시 이동
        self.shadowMan.x += self.shadowMan.face_dir * self.dash_speed
        self.dash_timer -= 1

        # 대시 시간이 끝나면 IDLE로 전환
        if self.dash_timer <= 0:
            self.shadowMan.state_machine.handle_state_event(('DASH_END', None))

    def draw(self):
        sprite_w, sprite_h = self.shadowMan.current_sprite_size
        if self.shadowMan.face_dir == 1:
            self.shadowMan.current_image.clip_draw(
                self.shadowMan.current_frame * sprite_w, 0, sprite_w, sprite_h,
                self.shadowMan.x, self.shadowMan.y, 300, 300
            )
        else:
            self.shadowMan.current_image.clip_composite_draw(
                self.shadowMan.current_frame * sprite_w, 0, sprite_w, sprite_h,
                0, 'h',
                self.shadowMan.x, self.shadowMan.y, 300, 300
            )

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
        self.dash_image = load_image('그림자검객_dash.png')
        self.idle_sprite_size = (340, 360)
        self.walk_sprite_size = (227, 260)
        self.dash_sprite_size = (400, 285)
        self.frame_idle = 3
        self.frame_walk = 5
        self.frame_dash = 2
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
        self.DASH = Dash(self)
        self.state_machine = StateMachine(
            self.IDLE,
            {
                self.IDLE: {a_down: self.WALK, d_down: self.WALK, lctrl_down: self.DASH},
                self.WALK: {a_up: self.IDLE, d_up: self.IDLE, lctrl_down: self.DASH},
                self.DASH: {dash_end: self.IDLE}
            }
        )  # 상태머신 생성 및 초기 시작 상태 설정

    def update(self):
        self.state_machine.update()

    def draw(self):
        self.state_machine.draw()

    def handle_event(self, event):
        self.state_machine.handle_state_event(('INPUT', event))
        pass
