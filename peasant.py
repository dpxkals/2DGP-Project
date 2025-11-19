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
def hurt_start(e):
    return e[0] == 'HURT_START'
def hurt_done(e):
    return e[0] == 'HURT_DONE'
def dead(e):
    return e[0] == 'DEAD'

class Dead:
    def __init__(self, Peasant):
        self.peasant = Peasant

    def enter(self, e):
        self.peasant.current_image = self.peasant.dead_image
        self.peasant.current_sprite_size = self.peasant.sprite_size
        self.peasant.frame = self.peasant.frame_dead
        self.peasant.current_frame = 0

    def exit(self, e):
        pass

    def do(self):
        self.peasant.current_frame += FRAMES_PER_SECOND * game_framework.frame_time
        if self.peasant.current_frame >= (self.peasant.frame - 1):
            self.peasant.current_frame = self.peasant.frame - 1  # 멈춤

    def draw(self):
        sprite_w, sprite_h = self.peasant.current_sprite_size
        self.peasant.current_image.clip_draw(
            int(self.peasant.current_frame) * sprite_w, 0, sprite_w, sprite_h,
            self.peasant.x, self.peasant.y, 300, 300
        )

class Hurt:
    def __init__(self, Peasant):
        self.peasant = Peasant

    def enter(self, e):
        self.peasant.current_image = self.peasant.hurt_image
        self.peasant.current_sprite_size = self.peasant.sprite_size
        self.peasant.frame = self.peasant.frame_hurt
        self.peasant.current_frame = 0

    def exit(self, e):
        # Hurt 끝나면 다시 피격 가능하도록 플래그 해제
        self.peasant.is_hurt = False

    def do(self):
        self.peasant.current_frame += FRAMES_PER_SECOND * game_framework.frame_time
        if self.peasant.current_frame >= (self.peasant.frame - 1):
            self.peasant.state_machine.handle_state_event(('HURT_DONE', None))

    def draw(self):
        sprite_w, sprite_h = self.peasant.current_sprite_size
        self.peasant.current_image.clip_draw(
            int(self.peasant.current_frame) * sprite_w, 0, sprite_w, sprite_h,
            self.peasant.x, self.peasant.y, 300, 300
        )

class Attack1:
    def __init__(self, Peasant):
        self.peasant = Peasant

    def enter(self, e):
        self.peasant.current_image = self.peasant.attack1_image
        self.peasant.current_sprite_size = self.peasant.sprite_size
        self.peasant.frame = self.peasant.frame_attack1
        self.peasant.current_frame = 0

        self.peasant.attack_power = self.peasant.attack_power1

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

        self.peasant.attack_power = self.peasant.attack_power2

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

        self.peasant.attack_power = self.peasant.attack_power3

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

        # 인스턴스별 키체크 사용
        if self.peasant.d_down(e) or self.peasant.a_up(e):
            self.peasant.dir = 1
        elif self.peasant.a_down(e) or self.peasant.d_up(e):
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

        # 인스턴스별 키체크 사용
        if self.peasant.d_down(e) or self.peasant.a_up(e):
            self.peasant.dir = 1
        elif self.peasant.a_down(e) or self.peasant.d_up(e):
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
    def __init__(self, key_map=None):
        # 기본위치(삭제 혹은 변경 예정)
        self.x, self.y = 100, 300

        # 기본 스펙
        self.hp = 200 # 체력
        self.attack_power = 0  # 공격 상태 3개 중 현재 공격력을 더해서 넘기는 방식으로 함
        self.attack_power1 = 10 # 공격 1
        self.attack_power2 = 20 # 공격 2
        self.attack_power3 = 30 # 방어 상태에서 공격(특수 공격)
        self.defense = 0.5 # 방어력 (피해량 감소 비율)
        self.parry = 0 # 패링을 판정하고 패링이면 피해를 0으로 만듬

        # 피격 플래그 초기화
        self.is_hurt = False

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
        self.frame_hurt = 2
        self.frame_dead = 4

        # 이동 방향 변수
        self.dir = 0
        # 바라보는 방향 변수
        self.face_dir = 1
        # 현재 스프라이트 이미지 정보 선택 변수
        self.current_image = self.idle_image
        self.current_sprite_size = self.sprite_size
        self.frame = self.frame_idle
        self.current_frame = 0

        # 폰트 로드 (체력바 텍스트용)
        self.font = load_font('ENCR10B.TTF', 24)

        # 키 매핑 (인스턴스마다 다르게 설정 가능)
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

        # 인스턴스용 이벤트 체크 함수 생성
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

        # 상태 변화 테이블
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
                self.IDLE: {
                    self.a_down: self.WALK,
                    self.d_down: self.WALK,
                    self.a_up: self.WALK,
                    self.d_up: self.WALK,
                    self.j_down: self.DEFENSE,
                    self.l_ctrl_down: self.DASH,
                    self.e_down: self.ATTACK1,
                    self.q_down: self.ATTACK2,
                    hurt_start: self.HURT,
                    dead: self.DEAD,
                },
                self.WALK: {
                    self.a_down: self.IDLE,
                    self.d_down: self.IDLE,
                    self.a_up: self.IDLE,
                    self.d_up: self.IDLE,
                    self.l_ctrl_down: self.DASH,
                    self.j_down: self.DEFENSE,
                    self.e_down: self.ATTACK1,
                    self.q_down: self.ATTACK2,
                    hurt_start: self.HURT,
                    dead: self.DEAD,
                },
                self.DASH: {
                    dash_end: self.WALK,
                    self.e_down: self.ATTACK1,
                    self.q_down: self.ATTACK2,
                    hurt_start: self.HURT,
                    dead: self.DEAD,
                },
                self.DEFENSE: {
                    self.j_up: self.DEFENSE_RELEASE,
                    hurt_start: self.HURT,
                    dead: self.DEAD,
                },
                self.DEFENSE_RELEASE: {
                    defense_done: self.IDLE,
                    hurt_start: self.HURT,
                    dead: self.DEAD,
                },
                self.ATTACK1: {
                    attack1_done: self.WALK,
                    hurt_start: self.HURT,
                    dead: self.DEAD,
                },
                self.ATTACK2: {
                    attack2_done: self.WALK,
                    hurt_start: self.HURT,
                    dead: self.DEAD,
                },
                self.DEFENSE_ATTACK: {
                    defense_attack_done: self.IDLE,
                    hurt_start: self.HURT,
                    dead: self.DEAD,
                },
                self.HURT: {
                    hurt_done: self.IDLE,
                    dead: self.DEAD,
                },
                self.DEAD: {}
            }
        )  # 상태머신 생성 및 초기 시작 상태 설정

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
        self.state_machine.handle_state_event(('INPUT', event))


    def get_bb(self):
        return self.x-75, self.y-150, self.x+55, self.y+55

    def handle_collision(self, group, other):
        if group == '1p:2p':
            # 이미 피격 중이면 중복 피격 방지
            if self.is_hurt:
                return

            # 피격 플래그 설정
            self.is_hurt = True

            # 간단한 넉백 처리 (방향에 따라 뒤로 밀기)
            knockback = 50
            self.x -= knockback * self.face_dir
            self.clamp_position()

            # 방어 중이면 데미지 경감 적용
            damage = other.attack_power
            if isinstance(self.state_machine.current_state, (Defense, DefenseRelease)):
                damage = int(damage * self.defense)  # defense는 0.5이므로 50% 경감

            new_hp = self.hp - damage

            # 사망 체크 (감소 후 HP로 판단)
            if new_hp <= 0:
                self.hp = 0  # HP를 0으로 설정
                self.state_machine.handle_state_event(('DEAD', other))
            else:
                self.hp = new_hp  # HP 감소 적용
                self.state_machine.handle_state_event(('HURT_START', other))