from pico2d import load_image
from sdl2 import SDL_KEYDOWN, SDLK_SPACE, SDLK_RIGHT, SDL_KEYUP, SDLK_LEFT, SDLK_a, SDLK_d, SDLK_j, SDLK_LCTRL

import game_framework
from state_machine import StateMachine


# Run speed
PIXEL_PER_METER = (10.0 / 0.5)  # 10 pixel 5 cm
RUN_SPEED_KMPH = 20.0 # Km / Hour 보행 속도
RUN_SPEED_MPM = (RUN_SPEED_KMPH * 1000.0 / 60.0)
RUN_SPEED_MPS = (RUN_SPEED_MPM / 60.0)
RUN_SPEED_PPS = (RUN_SPEED_MPS * PIXEL_PER_METER)

TIME_PER_ACTION = 0.4
ACTION_PER_TIME = 1.0 / TIME_PER_ACTION
FRAMES_PER_ACTION = 5
FRAMES_PER_SECOND = FRAMES_PER_ACTION * ACTION_PER_TIME

# dash speed
DASH_SPEED_KMPH = 50.0 # Km / Hour
DASH_SPEED_MPM = (DASH_SPEED_KMPH * 1000.0 / 60.0)
DASH_SPEED_MPS = (DASH_SPEED_MPM / 60.0)
DASH_SPEED_PPS = (DASH_SPEED_MPS * PIXEL_PER_METER)

DASH_TIME_PER_ACTION = 0.1
DASH_ACTION_PER_TIME = 1.0 / TIME_PER_ACTION
DASH_FRAMES_PER_ACTION = 3
DASH_FRAMES_PER_SECOND = DASH_FRAMES_PER_ACTION * DASH_ACTION_PER_TIME

# 이벤트 체크 함수
# down 이벤트
def a_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_a
def d_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_d
def j_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_j
def l_ctrl_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_LCTRL
# up 이벤트
def a_up(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYUP and e[1].key == SDLK_a
def d_up(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYUP and e[1].key == SDLK_d
def j_up(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYUP and e[1].key == SDLK_j
def l_ctrl_up(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYUP and e[1].key == SDLK_LCTRL
# 타이머 이벤트
def dash_end(e):
    return e[0] == 'DASH_END'

class Defence:
    def __init__(self, shadowMan):
        self.shadowMan = shadowMan
        pass

    def enter(self, e):
        self.shadowMan.current_image = self.shadowMan.defense_image
        self.shadowMan.current_sprite_size = self.shadowMan.defense_sprite_size
        self.shadowMan.frame = self.shadowMan.frame_defense
        pass

    def exit(self, e):
        pass

    def do(self):
        self.shadowMan.current_frame = (self.shadowMan.current_frame + FRAMES_PER_SECOND * game_framework.frame_time) % self.shadowMan.frame
        pass

    def draw(self):
        sprite_w, sprite_h = self.shadowMan.current_sprite_size
        self.shadowMan.current_image.clip_draw(
            int(self.shadowMan.current_frame) * sprite_w, 0, sprite_w, sprite_h,
            self.shadowMan.x, self.shadowMan.y, 300, 300
        )

class Dash:
    def __init__(self, shadowMan):
        self.shadowMan = shadowMan
        self.dash_duration = 2.5  # 대시 지속 프레임
        self.dash_timer = 0

    def enter(self, e):
        # 대시 이미지가 있다면 변경 (없다면 walk 이미지 사용)
        self.shadowMan.current_image = self.shadowMan.back_dash_image
        self.shadowMan.current_sprite_size = self.shadowMan.back_dash_sprite_size
        self.shadowMan.frame = self.shadowMan.frame_back_dash



        self.dash_timer = self.dash_duration
        # 현재 바라보는 방향으로 대시

    def exit(self, e):
        pass

    def do(self):
        self.shadowMan.current_frame = (self.shadowMan.current_frame + DASH_FRAMES_PER_SECOND * game_framework.frame_time) % self.shadowMan.frame
        # 대시 이동
        self.shadowMan.x += self.shadowMan.dir * DASH_SPEED_PPS * game_framework.frame_time
        # 경계 체크
        self.shadowMan.clamp_position()

        self.dash_timer -= game_framework.frame_time
        # 대시 시간이 끝나면 IDLE로 전환
        if self.dash_timer <= 0:
            self.shadowMan.state_machine.handle_state_event(('DASH_END', None))

    def draw(self):
        sprite_w, sprite_h = self.shadowMan.current_sprite_size
        self.shadowMan.current_image.clip_draw(
            int(self.shadowMan.current_frame) * sprite_w, 0, sprite_w, sprite_h,
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
            self.shadowMan.dir = 1
        elif a_down(e) or d_up(e):
            self.shadowMan.dir = -1

    def exit(self, e):
        pass

    def do(self):
        self.shadowMan.current_frame = (self.shadowMan.current_frame + FRAMES_PER_SECOND * game_framework.frame_time) % self.shadowMan.frame
        self.shadowMan.x += self.shadowMan.dir * RUN_SPEED_PPS * game_framework.frame_time
        # 경계 체크
        self.shadowMan.clamp_position()

    def draw(self):
        sprite_w, sprite_h = self.shadowMan.current_sprite_size
        if self.shadowMan.face_dir == 1:  # 오른쪽을 바라볼 때
            self.shadowMan.current_image.clip_draw(
                int(self.shadowMan.current_frame) * sprite_w, 0, sprite_w, sprite_h,
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
                int(self.shadowMan.current_frame) * sprite_w, 0, sprite_w, sprite_h,
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

        # 화면 경계 설정 (화면 크기에 맞게 조정)
        self.screen_width = 1920  # 화면 너비
        self.screen_height = 1080  # 화면 높이
        self.half_width = 150  # 캐릭터 반폭 (300/2)
        self.half_height = 150  # 캐릭터 반높이 (300/2)

        # 스프라이트 이미지 로드 및 속성 설정
        self.idle_image = load_image('그림자검객_idle.png')
        self.walk_image = load_image('그림자검객_walk.png')
        self.dash_image = load_image('그림자검객_dash.png')
        self.back_dash_image = load_image('그림자검객_back_dash.png')
        self.defense_image = load_image('그림자검객_defense.png')

        self.idle_sprite_size = (340, 360)
        self.walk_sprite_size = (227, 260)
        self.dash_sprite_size = (400, 285)
        self.back_dash_sprite_size = (340, 360)
        self.defense_sprite_size = (340,290)

        self.frame_idle = 3
        self.frame_walk = 5
        self.frame_dash = 2
        self.frame_back_dash = 3
        self.frame_defense = 1

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
        self.DEFENCE = Defence(self)
        self.state_machine = StateMachine(
            self.IDLE,
            {
                self.IDLE: {a_down: self.WALK, d_down: self.WALK, a_up: self.WALK, d_up: self.WALK,
                            j_down: self.DEFENCE},
                self.WALK: {a_down: self.IDLE, d_down: self.IDLE, a_up: self.IDLE, d_up: self.IDLE,
                            l_ctrl_down: self.DASH,
                            j_down: self.DEFENCE},
                self.DASH: {dash_end: self.WALK, l_ctrl_up: self.WALK},
                self.DEFENCE: {j_up: self.IDLE},
            }
        )  # 상태머신 생성 및 초기 시작 상태 설정

    def clamp_position(self):
        self.x = max(self.half_width, min(self.screen_width - self.half_width, self.x))
        self.y = max(self.half_height, min(self.screen_height - self.half_height, self.y))

    def update(self):
        self.state_machine.update()

    def draw(self):
        self.state_machine.draw()

    def handle_event(self, event):
        self.state_machine.handle_state_event(('INPUT', event))
        pass
