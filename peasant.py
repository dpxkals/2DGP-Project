from pico2d import load_image, SDL_KEYDOWN, SDL_KEYUP, SDLK_a, SDLK_d, SDLK_j, SDLK_LCTRL, SDLK_e, SDLK_q, SDLK_LEFT, \
    SDLK_RIGHT, SDLK_SLASH, SDLK_RSHIFT, SDLK_PERIOD, SDLK_RCTRL, get_time
from character import Character, State, Idle, Walk, Hurt, Dead, FRAMES_PER_SECOND
import game_framework
from state_machine import StateMachine


# --- Peasant 전용 상태 클래스 정의 ---

class Attack1(State):
    def enter(self, e):
        self.entity.current_image = self.entity.attack1_image
        self.entity.frame = self.entity.frame_attack1
        self.entity.current_frame = 0
        self.entity.attack_power = 10  # 공격력 설정

    def do(self):
        self.entity.current_frame += FRAMES_PER_SECOND * game_framework.frame_time
        if self.entity.current_frame >= self.entity.frame - 1:
            self.entity.state_machine.handle_state_event(('ATTACK1_DONE', None))


class Attack2(State):
    def enter(self, e):
        self.entity.current_image = self.entity.attack2_image
        self.entity.frame = self.entity.frame_attack2
        self.entity.current_frame = 0
        self.entity.attack_power = 20  # 강공격

    def do(self):
        self.entity.current_frame += FRAMES_PER_SECOND * game_framework.frame_time
        if self.entity.current_frame >= self.entity.frame - 1:
            self.entity.state_machine.handle_state_event(('ATTACK2_DONE', None))


class Defense(State):
    def __init__(self, entity):
        super().__init__(entity)
        self.hold_frame_index = 5  # 방어 자세 유지할 프레임

    def enter(self, e):
        self.entity.current_image = self.entity.defense_image
        self.entity.frame = self.entity.frame_defense
        self.entity.current_frame = 0
        self.entity.defense_factor = 0.5  # 데미지 50% 감소

        self.entity.defense_start_time = get_time()

    def exit(self, e):
        self.entity.defense_factor = 1.0  # 방어 해제
        self.entity.defense_start_time = 0  # 초기화

    def do(self):
        # 방어 자세를 취하다가 hold_frame에서 멈춤
        next_frame = self.entity.current_frame + FRAMES_PER_SECOND * game_framework.frame_time
        max_hold = min(self.hold_frame_index, self.entity.frame - 1)

        if next_frame < max_hold:
            self.entity.current_frame = next_frame
        else:
            self.entity.current_frame = max_hold


class DefenseRelease(State):
    def enter(self, e):
        self.entity.current_image = self.entity.defense_image
        self.entity.frame = self.entity.frame_defense
        # current_frame은 Defense 상태에서 이어서 진행

    def do(self):
        self.entity.current_frame += FRAMES_PER_SECOND * game_framework.frame_time
        if self.entity.current_frame >= self.entity.frame - 1:
            self.entity.state_machine.handle_state_event(('DEFENSE_DONE', None))


class Dash(State):
    def __init__(self, entity):
        super().__init__(entity)
        self.dash_timer = 0
        self.dash_duration = 0.3
        self.dash_speed = 500.0  # 픽셀/초

    def enter(self, e):
        self.entity.current_image = self.entity.dash_image
        self.entity.frame = self.entity.frame_dash
        self.dash_timer = self.dash_duration

        # 대시 방향 결정 (키 입력 or 보는 방향)
        if self.entity.d_down(e) or self.entity.a_up(e):
            self.entity.dir = 1
        elif self.entity.a_down(e) or self.entity.d_up(e):
            self.entity.dir = -1
        # 키 입력 없으면 보는 방향으로 대시
        if self.entity.dir == 0: self.entity.dir = self.entity.face_dir

        self.entity.face_dir = self.entity.dir

    def do(self):
        self.entity.current_frame = (
                                                self.entity.current_frame + FRAMES_PER_SECOND * game_framework.frame_time) % self.entity.frame
        self.entity.x += self.entity.dir * self.dash_speed * game_framework.frame_time
        self.entity.clamp_position()

        self.dash_timer -= game_framework.frame_time
        if self.dash_timer <= 0:
            self.entity.state_machine.handle_state_event(('DASH_END', None))


# --- 이벤트 함수들 ---
def dash_end(e): return e[0] == 'DASH_END'


def defense_done(e): return e[0] == 'DEFENSE_DONE'


def attack1_done(e): return e[0] == 'ATTACK1_DONE'


def attack2_done(e): return e[0] == 'ATTACK2_DONE'


def hurt_start(e): return e[0] == 'HURT_START'


def hurt_done(e): return e[0] == 'HURT_DONE'


def dead(e): return e[0] == 'DEAD'


class Peasant(Character):
    def __init__(self, key_map=None):
        super().__init__()
        self.load_images()
        self.setup_keys(key_map)
        self.build_state_machine()
        self.defense_factor = 1.0  # 기본은 데미지 100% 받음

    def load_images(self):
        self.idle_image = load_image('Peasant_idle.png')
        self.walk_image = load_image('Peasant_walk.png')
        self.dash_image = load_image('Peasant_dash.png')
        self.defense_image = load_image('Peasant_defense.png')
        self.attack1_image = load_image('Peasant_attack1.png')
        self.attack2_image = load_image('Peasant_attack2.png')
        self.hurt_image = load_image('Peasant_hurt.png')
        self.dead_image = load_image('Peasant_dead.png')

        # 프레임 수 설정
        self.frame_idle = 6
        self.frame_walk = 8
        self.frame_dash = 6
        self.frame_defense = 9
        self.frame_attack1 = 6
        self.frame_attack2 = 4
        self.frame_hurt = 2
        self.frame_dead = 4

        self.current_image = self.idle_image

    def get_attack_bb(self):
        """Peasant 전용 공격 판정 박스"""
        current_state = self.state_machine.current_state

        # Attack1: 2~4 프레임 사이 공격 판정
        if isinstance(current_state, Attack1):
            if 2 <= int(self.current_frame) <= 4:
                if self.face_dir == 1:
                    return self.x, self.y - 30, self.x + 100, self.y + 30
                else:
                    return self.x - 100, self.y - 30, self.x, self.y + 30

        # Attack2: 1~2 프레임 사이 공격 판정 (더 좁고 셈)
        elif isinstance(current_state, Attack2):
            if 1 <= int(self.current_frame) <= 2:
                if self.face_dir == 1:
                    return self.x, self.y - 30, self.x + 120, self.y + 30
                else:
                    return self.x - 120, self.y - 30, self.x, self.y + 30

        return 0, 0, 0, 0

    def take_damage(self, amount):
        # 1. 방어 상태인지 확인
        if isinstance(self.state_machine.current_state, Defense):
            # 2. 타이밍 계산
            current_time = get_time()
            timing = current_time - getattr(self, 'defense_start_time', 0)

            # 3. 0.2초 이내면 패링 성공 (데미지 0)
            if timing < 0.2:
                print("★ PEASANT PARRY SUCCESS! ★")
                return

            # 4. 늦었으면 일반 방어
            print("Peasant Guard")
            amount = amount * self.defense_factor

        # 원래 데미지 처리 로직 실행
        super().take_damage(amount)

    def setup_keys(self, key_map):
        # 기본 키맵 (플레이어 2가 Peasant일 경우를 대비해 화살표 키 등을 기본값으로 둘 수도 있음)
        default_keys = {
            'left': SDLK_LEFT, 'right': SDLK_RIGHT,
            'defense': SDLK_PERIOD, 'dash': SDLK_RCTRL,
            'attack1': SDLK_SLASH, 'attack2': SDLK_RSHIFT
        }
        if key_map: default_keys.update(key_map)
        self.key_map = default_keys

        def make_check(key, down=True):
            def check(e):
                return e[0] == 'INPUT' and ((e[1].type == SDL_KEYDOWN and e[1].key == key) if down else (
                            e[1].type == SDL_KEYUP and e[1].key == key))

            return check

        self.a_down = make_check(self.key_map['left'], True)
        self.d_down = make_check(self.key_map['right'], True)
        self.a_up = make_check(self.key_map['left'], False)
        self.d_up = make_check(self.key_map['right'], False)
        self.j_down = make_check(self.key_map['defense'], True)
        self.j_up = make_check(self.key_map['defense'], False)
        self.ctrl_down = make_check(self.key_map['dash'], True)
        self.e_down = make_check(self.key_map['attack1'], True)
        self.q_down = make_check(self.key_map['attack2'], True)

    def build_state_machine(self):
        self.IDLE = Idle(self)
        self.WALK = Walk(self)
        self.DASH = Dash(self)
        self.DEFENSE = Defense(self)
        self.DEFENSE_RELEASE = DefenseRelease(self)
        self.ATTACK1 = Attack1(self)
        self.ATTACK2 = Attack2(self)
        self.HURT = Hurt(self)
        self.DEAD = Dead(self)

        self.state_machine = StateMachine(self.IDLE, {
            self.IDLE: {
                self.a_down: self.WALK, self.d_down: self.WALK,
                self.e_down: self.ATTACK1, self.q_down: self.ATTACK2,
                self.j_down: self.DEFENSE, self.ctrl_down: self.DASH,
                hurt_start: self.HURT, dead: self.DEAD
            },
            self.WALK: {
                self.a_up: self.IDLE, self.d_up: self.IDLE,
                self.e_down: self.ATTACK1, self.q_down: self.ATTACK2,
                self.j_down: self.DEFENSE, self.ctrl_down: self.DASH,
                hurt_start: self.HURT, dead: self.DEAD
            },
            self.DASH: {
                dash_end: self.WALK, self.e_down: self.ATTACK1,
                hurt_start: self.HURT, dead: self.DEAD
            },
            self.DEFENSE: {
                self.j_up: self.DEFENSE_RELEASE,
                hurt_start: self.HURT, dead: self.DEAD
            },
            self.DEFENSE_RELEASE: {
                defense_done: self.IDLE,
                hurt_start: self.HURT, dead: self.DEAD
            },
            self.ATTACK1: {
                attack1_done: self.IDLE,
                hurt_start: self.HURT, dead: self.DEAD
            },
            self.ATTACK2: {
                attack2_done: self.IDLE,
                hurt_start: self.HURT, dead: self.DEAD
            },
            self.HURT: {
                hurt_done: self.IDLE, dead: self.DEAD
            },
            self.DEAD: {}
        })