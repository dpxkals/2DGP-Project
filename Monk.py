from pico2d import load_image, SDL_KEYDOWN, SDL_KEYUP, SDLK_a, SDLK_d, SDLK_j, SDLK_LCTRL, SDLK_e, SDLK_q, get_time
from character import Character, State, FRAMES_PER_SECOND
import game_framework
from state_machine import StateMachine


# --- 이벤트 체크 함수들 ---
def attack1_done(e): return e[0] == 'ATTACK1_DONE'


def attack2_done(e): return e[0] == 'ATTACK2_DONE'


def defense_done(e): return e[0] == 'DEFENSE_DONE'


def defense_attack_done(e): return e[0] == 'DEFENSE_ATTACK_DONE'


def dash_end(e): return e[0] == 'DASH_END'


def hurt_start(e): return e[0] == 'HURT_START'


def hurt_done(e): return e[0] == 'HURT_DONE'


def dead(e): return e[0] == 'DEAD'


# --- 상태 클래스 정의 ---

class Attack1(State):
    def enter(self, e):
        self.entity.current_image = self.entity.attack1_image
        self.entity.frame = self.entity.frame_attack1
        self.entity.current_frame = 0
        self.entity.attack_power = 10

    def do(self):
        self.entity.current_frame += FRAMES_PER_SECOND * game_framework.frame_time
        if self.entity.current_frame >= self.entity.frame - 1:
            self.entity.state_machine.handle_state_event(('ATTACK1_DONE', None))


class Attack2(State):
    def enter(self, e):
        self.entity.current_image = self.entity.attack2_image
        self.entity.frame = self.entity.frame_attack2
        self.entity.current_frame = 0
        self.entity.attack_power = 20

    def do(self):
        self.entity.current_frame += FRAMES_PER_SECOND * game_framework.frame_time
        if self.entity.current_frame >= self.entity.frame - 1:
            self.entity.state_machine.handle_state_event(('ATTACK2_DONE', None))


class Defense(State):
    def enter(self, e):
        self.entity.current_image = self.entity.defense_image
        self.entity.frame = self.entity.frame_defense
        self.entity.current_frame = 0
        self.entity.defense_factor = 0.5  # 데미지 반감
        self.hold_frame = 2  # 방어 자세 고정 프레임

        # 패링 적용을 위한
        self.entity.defense_start_time = get_time()

    def exit(self, e):
        self.entity.defense_factor = 1.0
        self.entity.defense_start_time = 0  # 초기화

    def do(self):
        next_frame = self.entity.current_frame + FRAMES_PER_SECOND * game_framework.frame_time
        # 특정 프레임에서 멈춤 (키를 누르고 있는 동안)
        if next_frame < self.hold_frame:
            self.entity.current_frame = next_frame
        else:
            self.entity.current_frame = self.hold_frame


class DefenseRelease(State):
    def enter(self, e):
        self.entity.current_image = self.entity.defense_image
        self.entity.frame = self.entity.frame_defense
        # current_frame 유지

    def do(self):
        self.entity.current_frame += FRAMES_PER_SECOND * game_framework.frame_time
        if self.entity.current_frame >= self.entity.frame - 1:
            self.entity.state_machine.handle_state_event(('DEFENSE_DONE', None))


class Dash(State):
    def enter(self, e):
        self.entity.current_image = self.entity.dash_image
        self.entity.frame = self.entity.frame_dash
        self.timer = 0.3  # 대시 시간

        # 대시 방향 설정
        if self.entity.d_down(e) or self.entity.a_up(e):
            self.entity.dir = 1
        elif self.entity.a_down(e) or self.entity.d_up(e):
            self.entity.dir = -1
        if self.entity.dir == 0: self.entity.dir = self.entity.face_dir

        self.entity.face_dir = self.entity.dir

    def do(self):
        self.entity.current_frame = (
                                                self.entity.current_frame + FRAMES_PER_SECOND * game_framework.frame_time) % self.entity.frame
        self.entity.x += self.entity.dir * 500 * game_framework.frame_time  # 빠른 속도
        self.entity.clamp_position()

        self.timer -= game_framework.frame_time
        if self.timer <= 0:
            self.entity.state_machine.handle_state_event(('DASH_END', None))


class Monk(Character):
    def __init__(self, key_map=None):
        super().__init__()
        self.load_images()
        self.setup_keys(key_map)
        self.build_state_machine()
        self.defense_factor = 1.0

    def load_images(self):
        self.idle_image = load_image('Monk_idle.png')
        self.walk_image = load_image('Monk_walk.png')
        self.dash_image = load_image('Monk_run.png')  # 파일명 주의: run 이미지 사용
        self.defense_image = load_image('Monk_defense.png')
        self.attack1_image = load_image('Monk_attack1.png')
        self.attack2_image = load_image('Monk_attack2.png')
        # self.defense_attack_image = load_image('Monk_defense_attack.png') # 필요 시 추가
        self.hurt_image = load_image('Monk_hurt.png')
        self.dead_image = load_image('Monk_dead.png')

        self.frame_idle = 7
        self.frame_walk = 7
        self.frame_dash = 8
        self.frame_defense = 5
        self.frame_attack1 = 4
        self.frame_attack2 = 4
        self.frame_hurt = 4
        self.frame_dead = 5

        self.current_image = self.idle_image

    def get_attack_bb(self):
        current_state = self.state_machine.current_state

        # Attack 1 판정 (프레임 1~3)
        if isinstance(current_state, Attack1):
            if 1 <= int(self.current_frame) <= 3:
                if self.face_dir == 1:
                    return self.x, self.y - 30, self.x + 120, self.y + 30
                else:
                    return self.x - 120, self.y - 30, self.x, self.y + 30

        # Attack 2 판정 (프레임 2~3)
        elif isinstance(current_state, Attack2):
            if 2 <= int(self.current_frame) <= 3:
                if self.face_dir == 1:
                    return self.x, self.y - 40, self.x + 140, self.y + 40
                else:
                    return self.x - 140, self.y - 40, self.x, self.y + 40

        return 0, 0, 0, 0

    def take_damage(self, amount):
        final_damage = amount * self.defense_factor
        super().take_damage(final_damage)

    def setup_keys(self, key_map):
        default_keys = {
            'left': SDLK_a, 'right': SDLK_d,
            'defense': SDLK_j, 'dash': SDLK_LCTRL,
            'attack1': SDLK_e, 'attack2': SDLK_q
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

        self.e_down = make_check(self.key_map['attack1'], True)
        self.q_down = make_check(self.key_map['attack2'], True)

        self.j_down = make_check(self.key_map['defense'], True)
        self.j_up = make_check(self.key_map['defense'], False)

        self.ctrl_down = make_check(self.key_map['dash'], True)

    def build_state_machine(self):
        # Character에서 공통 상태(Idle, Walk, Hurt, Dead)를 가져옴
        from character import Idle, Walk, Hurt, Dead

        # Monk 전용 상태 인스턴스 생성
        self.IDLE = Idle(self)
        self.WALK = Walk(self)
        self.ATTACK1 = Attack1(self)
        self.ATTACK2 = Attack2(self)
        self.DEFENSE = Defense(self)
        self.DEFENSE_RELEASE = DefenseRelease(self)
        self.DASH = Dash(self)
        self.HURT = Hurt(self)
        self.DEAD = Dead(self)

        # 상태 머신 구성
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
                dash_end: self.IDLE,
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