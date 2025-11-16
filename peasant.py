from pico2d import load_image, get_time, load_font, draw_rectangle
from sdl2 import SDL_KEYDOWN, SDLK_SPACE, SDLK_RIGHT, SDL_KEYUP, SDLK_LEFT, SDLK_a, SDLK_d, SDLK_j, SDLK_LCTRL,SDLK_e,SDLK_q

import game_framework
from state_machine import StateMachine

# Run speed
PIXEL_PER_METER = (10.0 / 0.2)  # 10 pixel 5 cm
RUN_SPEED_KMPH = 10.0 # Km / Hour 보행 속도
RUN_SPEED_MPM = (RUN_SPEED_KMPH * 1000.0 / 60.0)
RUN_SPEED_MPS = (RUN_SPEED_MPM / 60.0)
RUN_SPEED_PPS = (RUN_SPEED_MPS * PIXEL_PER_METER)

TIME_PER_ACTION = 0.4
ACTION_PER_TIME = 1.0 / TIME_PER_ACTION
FRAMES_PER_ACTION = 8
FRAMES_PER_SECOND = FRAMES_PER_ACTION * ACTION_PER_TIME

# dash speed
DASH_SPEED_KMPH = 50.0 # Km / Hour 보행 속도
DASH_SPEED_MPM = (DASH_SPEED_KMPH * 1000.0 / 60.0)
DASH_SPEED_MPS = (DASH_SPEED_MPM / 60.0)
DASH_SPEED_PPS = (DASH_SPEED_MPS * PIXEL_PER_METER)

DASH_TIME_PER_ACTION = 0.4
DASH_ACTION_PER_TIME = 1.0 / DASH_TIME_PER_ACTION
DASH_FRAMES_PER_ACTION = 6
DASH_FRAMES_PER_SECOND = DASH_FRAMES_PER_ACTION * DASH_ACTION_PER_TIME

# 이벤트 체크 함수
def a_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_a
def d_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_d
def j_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_j
def e_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_e
def q_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_q
def l_ctrl_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_LCTRL
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
def defense_done(e):
    return e[0] == 'DEFENSE_DONE'
def attack1_done(e):
    return e[0] == 'ATTACK1_DONE'
def attack2_done(e):
    return e[0] == 'ATTACK2_DONE'
def defense_attack_done(e):
    return e[0] == 'DEFENSE_ATTACK_DONE'

class Attack1:
    def __init__(self, Peasant):
        self.peasant = Peasant

    def enter(self, e):
        self.peasant.current_image = self.peasant.attack1_image
        self.peasant.current_sprite_size = self.peasant.sprite_size
        self.peasant.frame = self.peasant.frame_attack1
        self.peasant.current_frame = 0

    def exit(self, e):
        pass

    def do(self):
        self.peasant.current_frame += FRAMES_PER_SECOND * game_framework.frame_time
        # 애니메이션이 끝나면 IDLE로 전환
        if self.peasant.current_frame >= (self.peasant.frame - 1):
            self.peasant.state_machine.handle_state_event(('ATTACK1_DONE', None))

    def draw(self):
        sprite_w, sprite_h = self.peasant.current_sprite_size
        self.peasant.current_image.clip_draw(
            int(self.peasant.current_frame) * sprite_w, 0, sprite_w, sprite_h,
            self.peasant.x, self.peasant.y, 300, 300
        )
class Attack2:
    def __init__(self, Peasant):
        self.peasant = Peasant

    def enter(self, e):
        self.peasant.current_image = self.peasant.attack2_image
        self.peasant.current_sprite_size = self.peasant.sprite_size
        self.peasant.frame = self.peasant.frame_attack2
        self.peasant.current_frame = 0

    def exit(self, e):
        pass

    def do(self):
        self.peasant.current_frame += FRAMES_PER_SECOND * game_framework.frame_time
        # 애니메이션이 끝나면 IDLE로 전환
        if self.peasant.current_frame >= (self.peasant.frame - 1):
            self.peasant.state_machine.handle_state_event(('ATTACK2_DONE', None))

    def draw(self):
        sprite_w, sprite_h = self.peasant.current_sprite_size
        self.peasant.current_image.clip_draw(
            int(self.peasant.current_frame) * sprite_w, 0, sprite_w, sprite_h,
            self.peasant.x, self.peasant.y, 300, 300
        )

class DefenseAttack:
    def __init__(self, Peasant):
        self.peasant = Peasant

    def enter(self, e):
        self.peasant.current_image = self.peasant.defense_attack_image
        self.peasant.current_sprite_size = self.peasant.sprite_size
        self.peasant.frame = self.peasant.frame_defense_attack
        self.peasant.current_frame = 0

    def exit(self, e):
        pass

    def do(self):
        self.peasant.current_frame += FRAMES_PER_SECOND * game_framework.frame_time
        # 애니메이션이 끝나면 IDLE로 전환
        if self.peasant.current_frame >= (self.peasant.frame - 1):
            self.peasant.state_machine.handle_state_event(('DEFENSE_ATTACK_DONE', None))

    def draw(self):
        sprite_w, sprite_h = self.peasant.current_sprite_size
        self.peasant.current_image.clip_draw(
            int(self.peasant.current_frame) * sprite_w, 0, sprite_w, sprite_h,
            self.peasant.x, self.peasant.y, 300, 300
        )

class Defense:
    def __init__(self, Peasant):
        self.peasant = Peasant
        # 멈출 프레임 인덱스 (조정 가능, 0-based)
        self.hold_frame_index = 5

    def enter(self, e):
        self.peasant.current_image = self.peasant.defense_image
        self.peasant.current_sprite_size = self.peasant.sprite_size
        self.peasant.frame = self.peasant.frame_defense
        # 애니 시작은 0부터
        self.peasant.current_frame = 0

    def exit(self, e):
        pass

    def do(self):
        # 자연스럽게 증가시키되 hold_frame_index를 넘지 않게 고정
        next_frame = self.peasant.current_frame + FRAMES_PER_SECOND * game_framework.frame_time
        max_hold = min(self.hold_frame_index, self.peasant.frame - 1)
        if next_frame < max_hold:
            self.peasant.current_frame = next_frame
        else:
            self.peasant.current_frame = max_hold

    def draw(self):
        sprite_w, sprite_h = self.peasant.current_sprite_size
        self.peasant.current_image.clip_draw(
            int(self.peasant.current_frame) * sprite_w, 0, sprite_w, sprite_h,
            self.peasant.x, self.peasant.y, 300, 300
        )
class DefenseRelease:
    def __init__(self, Peasant):
        self.peasant = Peasant

    def enter(self, e):
        # 그대로 현재 프레임을 이어서 재생
        self.peasant.current_image = self.peasant.defense_image
        self.peasant.current_sprite_size = self.peasant.sprite_size
        self.peasant.frame = self.peasant.frame_defense
        # (current_frame는 이전 상태에서 유지)

    def exit(self, e):
        pass

    def do(self):
        # 남은 프레임을 자연스럽게 재생
        self.peasant.current_frame = (self.peasant.current_frame +
                                      FRAMES_PER_SECOND * game_framework.frame_time)
        # 애니 끝까지 도달하면 Peasant에 이벤트 전송
        if self.peasant.current_frame >= (self.peasant.frame - 1):
            # 방어 애니메이션 완료 이벤트
            self.peasant.state_machine.handle_state_event(('DEFENSE_DONE', None))

    def draw(self):
        sprite_w, sprite_h = self.peasant.current_sprite_size
        self.peasant.current_image.clip_draw(
            int(self.peasant.current_frame) * sprite_w, 0, sprite_w, sprite_h,
            self.peasant.x, self.peasant.y, 300, 300
        )

class Dash:
    def __init__(self, Peasant):
        self.peasant = Peasant
        self.dash_duration = 0.3  # 대시 지속 프레임
        self.dash_timer = 0

    def enter(self, e):
        self.peasant.current_image = self.peasant.dash_image
        self.peasant.current_sprite_size = self.peasant.sprite_size
        self.peasant.frame = self.peasant.frame_dash

        if d_down(e) or a_up(e):
            self.peasant.dir = 1
        elif a_down(e) or d_up(e):
            self.peasant.dir = -1

        self.dash_timer = self.dash_duration
    def exit(self, e):
        pass

    def do(self):
        self.peasant.current_frame = (self.peasant.current_frame + DASH_FRAMES_PER_SECOND *
                                      game_framework.frame_time) % self.peasant.frame
        self.peasant.x += self.peasant.dir * DASH_SPEED_PPS * game_framework.frame_time

        self.peasant.clamp_position()

        self.dash_timer -= game_framework.frame_time
        # 대시 시간이 끝나면 IDLE로 전환
        if self.dash_timer <= 0:
            self.peasant.state_machine.handle_state_event(('DASH_END', None))

    def draw(self):
        sprite_w, sprite_h = self.peasant.current_sprite_size
        self.peasant.current_image.clip_draw(
            int(self.peasant.current_frame) * sprite_w, 0, sprite_w, sprite_h,
            self.peasant.x, self.peasant.y, 300, 300)

class Walk:
    def __init__(self, Peasant):
        self.peasant = Peasant

    def enter(self, e):
        self.peasant.current_image = self.peasant.walk_image
        self.peasant.current_sprite_size = self.peasant.sprite_size
        self.peasant.frame = self.peasant.frame_walk

        if d_down(e) or a_up(e):
            self.peasant.dir = 1
        elif a_down(e) or d_up(e):
            self.peasant.dir = -1
    def exit(self, e):
        pass

    def do(self):
        self.peasant.current_frame = ( self.peasant.current_frame + FRAMES_PER_SECOND *
                                         game_framework.frame_time) % self.peasant.frame
        self.peasant.x += self.peasant.dir * RUN_SPEED_PPS * game_framework.frame_time

        self.peasant.clamp_position()

    def draw(self):
        sprite_w, sprite_h = self.peasant.current_sprite_size
        self.peasant.current_image.clip_draw(
            int(self.peasant.current_frame) * sprite_w, 0, sprite_w, sprite_h,
            self.peasant.x, self.peasant.y, 300, 300)
        pass

class Idle:
    def __init__(self, Peasant):
        self.peasant = Peasant

    def enter(self, e):
        self.peasant.current_image = self.peasant.idle_image
        self.peasant.current_sprite_size = self.peasant.sprite_size
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
            self.peasant.x, self.peasant.y, 300, 300
        )

class Peasant:
    def __init__(self):
        # 기본위치(삭제 혹은 변경 예정)
        self.x, self.y = 700, 300

        # 화면 경계 설정 (화면 크기에 맞게 조정)
        self.screen_width = 1920  # 화면 너비
        self.screen_height = 1080  # 화면 높이
        self.half_width = 50  # 캐릭터 반폭 (300/2)
        self.half_height = 50  # 캐릭터 반높이 (300/2)

        # 스프라이트 이미지 로드
        self.idle_image = load_image('Peasant_idle.png')
        self.walk_image = load_image('Peasant_walk.png')
        self.dash_image = load_image('Peasant_dash.png')
        self.defense_image = load_image('Peasant_defense.png')
        self.attack1_image = load_image('Peasant_attack1.png')
        self.attack2_image = load_image('Peasant_attack2.png')
        self.defense_attack_image = load_image('Peasant_defense_attack.png')
        self.hurt_image = load_image('Peasant_hurt.png')
        self.dead_image = load_image('Peasant_dead.png')
        # 스프라이트 크기
        self.sprite_size = (96, 96)
        # 프레임 수
        self.frame_idle = 6
        self.frame_walk = 8
        self.frame_dash = 6
        self.frame_defense = 9
        self.frame_attack1 = 6
        self.frame_attack2 = 4
        self.frame_defense_attack = 6

        # 이동 방향 변수
        self.dir = 0
        # 바라보는 방향 변수
        self.face_dir = 1
        # 현재 스프라이트 이미지 정보 선택 변수
        self.current_image = self.idle_image
        self.current_sprite_size = self.sprite_size
        self.frame = self.frame_idle
        self.current_frame = 0

        # 상태 변화 테이블
        self.IDLE = Idle(self)
        self.WALK = Walk(self)
        self.DASH = Dash(self)
        self.DEFENSE = Defense(self)
        self.DEFENSE_RELEASE = DefenseRelease(self)
        self.ATTACK1 = Attack1(self)
        self.ATTACK2 = Attack2(self)
        self.DEFENSE_ATTACK = DefenseAttack(self)
        self.state_machine = StateMachine(
            self.IDLE,
            {
                self.IDLE: {
                    a_down: self.WALK,
                    d_down: self.WALK,
                    a_up: self.WALK,
                    d_up: self.WALK,
                    j_down: self.DEFENSE,
                    l_ctrl_down: self.DASH,
                    e_down: self.ATTACK1,
                    q_down: self.ATTACK2,
                },
                self.WALK: {
                    a_down: self.IDLE,
                    d_down: self.IDLE,
                    a_up: self.IDLE,
                    d_up: self.IDLE,
                    l_ctrl_down: self.DASH,
                    j_down: self.DEFENSE,
                    e_down: self.ATTACK1,
                    q_down: self.ATTACK2,
                },
                self.DASH: {
                    dash_end: self.WALK,
                    e_down: self.ATTACK1,
                    q_down: self.ATTACK2,
                },
                self.DEFENSE: {
                    j_up: self.DEFENSE_RELEASE,
                },
                self.DEFENSE_RELEASE: {
                    defense_done: self.IDLE,
                },
                self.ATTACK1: {
                    attack1_done: self.WALK,
                },
                self.ATTACK2: {
                    attack2_done: self.WALK,
                },
                self.DEFENSE_ATTACK: {
                    defense_attack_done: self.IDLE,
                }
            }
        )  # 상태머신 생성 및 초기 시작 상태 설정

    def clamp_position(self):
        self.x = max(self.half_width, min(self.screen_width - self.half_width, self.x))
        self.y = max(self.half_height, min(self.screen_height - self.half_height, self.y))

    def update(self):
        self.state_machine.update()

    def draw(self):
        self.state_machine.draw()
        draw_rectangle(*self.get_bb())

    def handle_event(self, event):
        self.state_machine.handle_state_event(('INPUT', event))


    def get_bb(self):
        return self.x-75, self.y-150, self.x+55, self.y+55

    def handle_collision(self, group, other):
        if group == '1p:2p':
           pass
