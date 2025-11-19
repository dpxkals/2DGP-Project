from pico2d import load_image, get_time, load_font, draw_rectangle
from sdl2 import SDL_KEYDOWN, SDL_KEYUP, SDLK_a, SDLK_d, SDLK_j, SDLK_LCTRL, SDLK_e, SDLK_q

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

# events
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

def hurt_start(e):
    return e[0] == 'HURT_START'

def hurt_done(e):
    return e[0] == 'HURT_DONE'

def dead(e):
    return e[0] == 'DEAD'

# 상태 클래스들
class Dead:
    def __init__(self, monk):
        self.monk = monk

    def enter(self, e):
        self.monk.current_image = self.monk.dead_image
        self.monk.current_sprite_size = self.monk.sprite_size
        self.monk.frame = self.monk.frame_dead
        self.monk.current_frame = 0

    def exit(self, e):
        pass

    def do(self):
        self.monk.current_frame += FRAMES_PER_SECOND * game_framework.frame_time
        if self.monk.current_frame >= (self.monk.frame - 1):
            self.monk.current_frame = self.monk.frame - 1

    def draw(self):
        w, h = self.monk.current_sprite_size
        self.monk.current_image.clip_draw(int(self.monk.current_frame) * w, 0, w, h, self.monk.x, self.monk.y, 300, 300)

class Hurt:
    def __init__(self, monk):
        self.monk = monk

    def enter(self, e):
        self.monk.current_image = self.monk.hurt_image
        self.monk.current_sprite_size = self.monk.sprite_size
        self.monk.frame = self.monk.frame_hurt
        self.monk.current_frame = 0

    def exit(self, e):
        self.monk.is_hurt = False

    def do(self):
        self.monk.current_frame += FRAMES_PER_SECOND * game_framework.frame_time
        if self.monk.current_frame >= (self.monk.frame - 1):
            self.monk.state_machine.handle_state_event(('HURT_DONE', None))

    def draw(self):
        w, h = self.monk.current_sprite_size
        self.monk.current_image.clip_draw(int(self.monk.current_frame) * w, 0, w, h, self.monk.x, self.monk.y, 300, 300)

class Attack1:
    def __init__(self, monk):
        self.monk = monk

    def enter(self, e):
        self.monk.current_image = self.monk.attack1_image
        self.monk.current_sprite_size = self.monk.sprite_size
        self.monk.frame = self.monk.frame_attack1
        self.monk.current_frame = 0
        self.monk.attack_power = self.monk.attack_power1

    def exit(self, e):
        pass

    def do(self):
        self.monk.current_frame += FRAMES_PER_SECOND * game_framework.frame_time
        if self.monk.current_frame >= (self.monk.frame - 1):
            self.monk.state_machine.handle_state_event(('ATTACK1_DONE', None))

    def draw(self):
        w, h = self.monk.current_sprite_size
        self.monk.current_image.clip_draw(int(self.monk.current_frame) * w, 0, w, h, self.monk.x, self.monk.y, 300, 300)

class Attack2:
    def __init__(self, monk):
        self.monk = monk

    def enter(self, e):
        self.monk.current_image = self.monk.attack2_image
        self.monk.current_sprite_size = self.monk.sprite_size
        self.monk.frame = self.monk.frame_attack2
        self.monk.current_frame = 0
        self.monk.attack_power = self.monk.attack_power2

    def exit(self, e):
        pass

    def do(self):
        self.monk.current_frame += FRAMES_PER_SECOND * game_framework.frame_time
        if self.monk.current_frame >= (self.monk.frame - 1):
            self.monk.state_machine.handle_state_event(('ATTACK2_DONE', None))

    def draw(self):
        w, h = self.monk.current_sprite_size
        self.monk.current_image.clip_draw(int(self.monk.current_frame) * w, 0, w, h, self.monk.x, self.monk.y, 300, 300)

class DefenseAttack:
    def __init__(self, monk):
        self.monk = monk

    def enter(self, e):
        self.monk.current_image = self.monk.defense_attack_image
        self.monk.current_sprite_size = self.monk.sprite_size
        self.monk.frame = self.monk.frame_defense_attack
        self.monk.current_frame = 0
        self.monk.attack_power = self.monk.attack_power3

    def exit(self, e):
        pass

    def do(self):
        self.monk.current_frame += FRAMES_PER_SECOND * game_framework.frame_time
        if self.monk.current_frame >= (self.monk.frame - 1):
            self.monk.state_machine.handle_state_event(('DEFENSE_ATTACK_DONE', None))

    def draw(self):
        w, h = self.monk.current_sprite_size
        self.monk.current_image.clip_draw(int(self.monk.current_frame) * w, 0, w, h, self.monk.x, self.monk.y, 300, 300)

class Defense:
    def __init__(self, monk):
        self.monk = monk
        self.hold_frame_index = 5

    def enter(self, e):
        self.monk.current_image = self.monk.defense_image
        self.monk.current_sprite_size = self.monk.sprite_size
        self.monk.frame = self.monk.frame_defense
        self.monk.current_frame = 0

    def exit(self, e):
        pass

    def do(self):
        next_frame = self.monk.current_frame + FRAMES_PER_SECOND * game_framework.frame_time
        max_hold = min(self.hold_frame_index, self.monk.frame - 1)
        if next_frame < max_hold:
            self.monk.current_frame = next_frame
        else:
            self.monk.current_frame = max_hold

    def draw(self):
        w, h = self.monk.current_sprite_size
        self.monk.current_image.clip_draw(int(self.monk.current_frame) * w, 0, w, h, self.monk.x, self.monk.y, 300, 300)

class DefenseRelease:
    def __init__(self, monk):
        self.monk = monk

    def enter(self, e):
        self.monk.current_image = self.monk.defense_image
        self.monk.current_sprite_size = self.monk.sprite_size
        self.monk.frame = self.monk.frame_defense

    def exit(self, e):
        pass

    def do(self):
        self.monk.current_frame = (self.monk.current_frame + FRAMES_PER_SECOND * game_framework.frame_time)
        if self.monk.current_frame >= (self.monk.frame - 1):
            self.monk.state_machine.handle_state_event(('DEFENSE_DONE', None))

    def draw(self):
        w, h = self.monk.current_sprite_size
        self.monk.current_image.clip_draw(int(self.monk.current_frame) * w, 0, w, h, self.monk.x, self.monk.y, 300, 300)

class Dash:
    def __init__(self, monk):
        self.monk = monk
        self.dash_duration = 0.3
        self.dash_timer = 0

    def enter(self, e):
        self.monk.current_image = self.monk.dash_image
        self.monk.current_sprite_size = self.monk.sprite_size
        self.monk.frame = self.monk.frame_dash
        # 방향은 인스턴스 키체크로 결정
        if self.monk.d_down(e) or self.monk.a_up(e):
            self.monk.dir = 1
        elif self.monk.a_down(e) or self.monk.d_up(e):
            self.monk.dir = -1
        self.dash_timer = self.dash_duration

    def exit(self, e):
        pass

    def do(self):
        self.monk.current_frame = (self.monk.current_frame + DASH_FRAMES_PER_SECOND * game_framework.frame_time) % self.monk.frame
        self.monk.x += self.monk.dir * DASH_SPEED_PPS * game_framework.frame_time
        self.monk.clamp_position()
        self.dash_timer -= game_framework.frame_time
        if self.dash_timer <= 0:
            self.monk.state_machine.handle_state_event(('DASH_END', None))

    def draw(self):
        w, h = self.monk.current_sprite_size
        self.monk.current_image.clip_draw(int(self.monk.current_frame) * w, 0, w, h, self.monk.x, self.monk.y, 300, 300)

class Walk:
    def __init__(self, monk):
        self.monk = monk

    def enter(self, e):
        self.monk.current_image = self.monk.walk_image
        self.monk.current_sprite_size = self.monk.sprite_size
        self.monk.frame = self.monk.frame_walk
        if self.monk.d_down(e) or self.monk.a_up(e):
            self.monk.dir = 1
        elif self.monk.a_down(e) or self.monk.d_up(e):
            self.monk.dir = -1

    def exit(self, e):
        pass

    def do(self):
        self.monk.current_frame = (self.monk.current_frame + FRAMES_PER_SECOND * game_framework.frame_time) % self.monk.frame
        self.monk.x += self.monk.dir * RUN_SPEED_PPS * game_framework.frame_time
        self.monk.clamp_position()

    def draw(self):
        w, h = self.monk.current_sprite_size
        self.monk.current_image.clip_draw(int(self.monk.current_frame) * w, 0, w, h, self.monk.x, self.monk.y, 300, 300)

class Idle:
    def __init__(self, monk):
        self.monk = monk

    def enter(self, e):
        self.monk.current_image = self.monk.idle_image
        self.monk.current_sprite_size = self.monk.sprite_size
        self.monk.frame = self.monk.frame_idle

    def exit(self, e):
        pass

    def do(self):
        self.monk.current_frame = (self.monk.current_frame + FRAMES_PER_SECOND * game_framework.frame_time) % self.monk.frame

    def draw(self):
        w, h = self.monk.current_sprite_size
        self.monk.current_image.clip_draw(int(self.monk.current_frame) * w, 0, w, h, self.monk.x, self.monk.y, 300, 300)

class Monk:
    def __init__(self, key_map=None):
        # 위치
        self.x, self.y = 500, 300
        # 스탯
        self.hp = 200
        self.attack_power = 0
        self.attack_power1 = 10
        self.attack_power2 = 20
        self.attack_power3 = 30
        self.defense = 0.5
        self.parry = 0
        self.is_hurt = False

        # 화면/바운딩
        self.screen_width = 1920
        self.screen_height = 1080
        self.half_width = 150
        self.half_height = 150

        # 이미지 로드 (그림자검객 이미지로 교체)
        self.idle_image = load_image('Monk_idle.png')
        self.walk_image = load_image('Monk_walk.png')
        self.dash_image = load_image('Monk_run.png')
        self.defense_image = load_image('Monk_defense.png')
        self.attack1_image = load_image('Monk_attack1.png')
        self.attack2_image = load_image('Monk_attack2.png')
        self.defense_attack_image = load_image('Monk_defense_attack.png')
        self.hurt_image = load_image('Monk_hurt.png')
        self.dead_image = load_image('Monk_dead.png')

        # 스프라이트 및 프레임
        self.sprite_size = (96, 96)
        self.frame_idle = 7
        self.frame_walk = 7
        self.frame_dash = 8
        self.frame_defense = 5
        self.frame_attack1 = 4
        self.frame_attack2 = 4
        self.frame_defense_attack = 4
        self.frame_hurt = 4
        self.frame_dead = 5

        # 이동/방향
        self.dir = 0
        self.face_dir = -1
        self.current_image = self.idle_image
        self.current_sprite_size = self.sprite_size
        self.frame = self.frame_idle
        self.current_frame = 0

        # 폰트
        self.font = load_font('ENCR10B.TTF', 24)
        self.hit_count = 0

        # 키맵
        default_keys = {
            'left': SDLK_a,
            'right': SDLK_d,
            'defense': SDLK_j,
            'dash': SDLK_LCTRL,
            'attack1': SDLK_e,
            'attack2': SDLK_q,
        }
        if key_map:
            default_keys.update(key_map)
        self.key_map = default_keys

        def make_key_check(key, keydown=True):
            def check(e):
                if e[0] != 'INPUT':
                    return False
                ev = e[1]
                if keydown:
                    return ev.type == SDL_KEYDOWN and ev.key == key
                else:
                    return ev.type == SDL_KEYUP and ev.key == key
            return check

        self.a_down = make_key_check(self.key_map['left'], keydown=True)
        self.d_down = make_key_check(self.key_map['right'], keydown=True)
        self.j_down = make_key_check(self.key_map['defense'], keydown=True)
        self.e_down = make_key_check(self.key_map['attack1'], keydown=True)
        self.q_down = make_key_check(self.key_map['attack2'], keydown=True)
        self.l_ctrl_down = make_key_check(self.key_map['dash'], keydown=True)
        self.a_up = make_key_check(self.key_map['left'], keydown=False)
        self.d_up = make_key_check(self.key_map['right'], keydown=False)
        self.j_up = make_key_check(self.key_map['defense'], keydown=False)
        self.l_ctrl_up = make_key_check(self.key_map['dash'], keydown=False)

        # 상태 객체
        self.IDLE = Idle(self)
        self.WALK = Walk(self)
        self.DASH = Dash(self)
        self.DEFENSE = Defense(self)
        self.DEFENSE_RELEASE = DefenseRelease(self)
        self.ATTACK1 = Attack1(self)
        self.ATTACK2 = Attack2(self)
        self.DEFENSE_ATTACK = DefenseAttack(self)
        self.HURT = Hurt(self)
        self.DEAD = Dead(self)

        self.state_machine = StateMachine(
            self.IDLE,
            {
                self.IDLE: {self.a_down: self.WALK,
                            self.d_down: self.WALK,
                            self.a_up: self.WALK,
                            self.d_up: self.WALK,
                            self.j_down: self.DEFENSE,
                            self.l_ctrl_down: self.DASH,
                            self.e_down: self.ATTACK1,
                            self.q_down: self.ATTACK2,
                            hurt_start: self.HURT,
                            dead: self.DEAD},
                self.WALK: {self.a_down: self.IDLE,
                            self.d_down: self.IDLE,
                            self.a_up: self.IDLE,
                            self.d_up: self.IDLE,
                            self.l_ctrl_down: self.DASH,
                            self.j_down: self.DEFENSE,
                            self.e_down: self.ATTACK1,
                            self.q_down: self.ATTACK2,
                            hurt_start: self.HURT,
                            dead: self.DEAD},
                self.DASH: {dash_end: self.WALK,
                            self.e_down: self.ATTACK1,
                            self.q_down: self.ATTACK2,
                            hurt_start: self.HURT,
                            dead: self.DEAD},
                self.DEFENSE: {self.j_up: self.DEFENSE_RELEASE,
                               hurt_start: self.HURT,
                               dead: self.DEAD},
                self.DEFENSE_RELEASE: {defense_done: self.IDLE,
                                       hurt_start: self.HURT,
                                       dead: self.DEAD},
                self.ATTACK1: {attack1_done: self.WALK,
                               hurt_start: self.HURT,
                               dead: self.DEAD},
                self.ATTACK2: {attack2_done: self.WALK,
                               hurt_start: self.HURT,
                               dead: self.DEAD},
                self.DEFENSE_ATTACK: {defense_attack_done: self.IDLE,
                                       hurt_start: self.HURT,
                                       dead: self.DEAD},
                self.HURT: {hurt_done: self.IDLE,
                            dead: self.DEAD},
                self.DEAD: {}
            }
        )

    def clamp_position(self):
        self.x = max(self.half_width, min(self.screen_width - self.half_width, self.x))
        self.y = max(self.half_height, min(self.screen_height - self.half_height, self.y))

    def update(self):
        self.state_machine.update()

    def draw(self):
        self.state_machine.draw()
        # HP 표시 (체력바 텍스트)
        self.font.draw(self.x - 30, self.y + 80, f'HP: {self.hp}', (255, 0, 0))
        draw_rectangle(*self.get_bb())

    def handle_event(self, event):
        # 키 이벤트만 전달 (인스턴스 키맵에 없는 키는 무시)
        if event.type == SDL_KEYDOWN or event.type == SDL_KEYUP:
            valid = {k for k in self.key_map.values() if k is not None}
            if event.key in valid:
                self.state_machine.handle_state_event(('INPUT', event))

    def get_bb(self):
        return self.x-70, self.y-150, self.x+70, self.y+80

    def handle_collision(self, group, other):
        if group == '1p:2p':
            if self.is_hurt:
                return
            self.is_hurt = True
            knockback = 50
            self.x -= knockback * self.face_dir
            self.clamp_position()

            # 방어 중이면 데미지 경감 적용
            damage = other.attack_power
            if isinstance(self.state_machine.current_state, (Defense, DefenseRelease)):
                damage = int(damage * self.defense)  # defense는 0.5이므로 50% 경감

            new_hp = self.hp - damage
            if new_hp <= 0:
                self.hp = 0
                self.state_machine.handle_state_event(('DEAD', other))
            else:
                self.hp = new_hp
                self.state_machine.handle_state_event(('HURT_START', other))
