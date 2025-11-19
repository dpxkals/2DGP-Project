import game_framework
from pico2d import *
from state_machine import StateMachine

# 공통 상수
PIXEL_PER_METER = (10.0 / 0.2)
RUN_SPEED_PPS = (10.0 * 1000.0 / 60.0 / 60.0 * PIXEL_PER_METER)
FRAMES_PER_SECOND = 20

class Character:
    def __init__(self):
        self.x, self.y = 0, 0
        self.hp = 200
        self.max_hp = 200
        self.dir = 0
        self.face_dir = 1 # 1: Right, -1: Left
        self.frame = 0
        self.current_frame = 0
        self.state_machine = None
        self.sprite_size = (96, 96)
        self.is_hurt = False
        self.font = load_font('ENCR10B.TTF', 16)

    def update(self):
        self.state_machine.update()
        self.clamp_position()

    def draw(self):
        self.state_machine.draw()
        # 디버그용: 공격박스와 피격박스 그리기
        # draw_rectangle(*self.get_bb())
        # draw_rectangle(*self.get_attack_bb())

    def get_bb(self):
        """피격 박스 (몸통)"""
        return self.x - 40, self.y - 50, self.x + 40, self.y + 50

    def get_attack_bb(self):
        """공격 박스 (무기) - 자식 클래스나 상태에서 오버라이딩 필요"""
        return 0, 0, 0, 0

    def handle_collision(self, group, other):
        # 물리적 충돌 (밀어내기)
        if group == '1p:2p':
            if self.x < other.x: self.x -= 2
            else: self.x += 2

    def take_damage(self, amount):
        if self.is_hurt: return
        self.hp = max(0, self.hp - amount)
        if self.hp == 0:
            self.state_machine.handle_state_event(('DEAD', 0))
        else:
            self.state_machine.handle_state_event(('HURT_START', 0))

        knockback_power = 30  # 밀려날 거리
        self.x -= knockback_power * self.face_dir
        self.clamp_position()  # 화면 밖으로 나가는 것 방지

    def clamp_position(self):
        self.x = max(50, min(1920 - 50, self.x))
        self.y = max(50, min(1080 - 50, self.y))

    def handle_event(self, event):
        if event.type in (SDL_KEYDOWN, SDL_KEYUP):
            valid = {k for k in self.key_map.values() if k is not None}
            if event.key in valid:
                self.state_machine.handle_state_event(('INPUT', event))

# --- 공통 상태 클래스 ---
class State:
    def __init__(self, entity):
        self.entity = entity
    def enter(self, e): pass
    def exit(self, e): pass
    def do(self): pass
    def draw(self):
        w, h = self.entity.sprite_size
        # face_dir에 따라 이미지 반전 처리 (op='h' 사용)
        if self.entity.face_dir == -1:
             self.entity.current_image.clip_composite_draw(
                int(self.entity.current_frame) * w, 0, w, h,
                0, 'h', self.entity.x, self.entity.y, 300, 300)
        else:
            self.entity.current_image.clip_draw(
                int(self.entity.current_frame) * w, 0, w, h,
                self.entity.x, self.entity.y, 300, 300)

class Idle(State):
    def enter(self, e):
        self.entity.current_image = self.entity.idle_image
        self.entity.frame = self.entity.frame_idle
    def do(self):
        self.entity.current_frame = (self.entity.current_frame + FRAMES_PER_SECOND * game_framework.frame_time) % self.entity.frame

class Walk(State):
    def enter(self, e):
        self.entity.current_image = self.entity.walk_image
        self.entity.frame = self.entity.frame_walk
        # 키 입력에 따른 방향 설정
        if self.entity.d_down(e) or self.entity.a_up(e): self.entity.dir = 1
        elif self.entity.a_down(e) or self.entity.d_up(e): self.entity.dir = -1
        if self.entity.dir != 0: self.entity.face_dir = self.entity.dir # 바라보는 방향 갱신
    def do(self):
        self.entity.current_frame = (self.entity.current_frame + FRAMES_PER_SECOND * game_framework.frame_time) % self.entity.frame
        self.entity.x += self.entity.dir * RUN_SPEED_PPS * game_framework.frame_time

class Hurt(State):
    def enter(self, e):
        self.entity.current_image = self.entity.hurt_image
        self.entity.frame = self.entity.frame_hurt
        self.entity.current_frame = 0
        self.entity.is_hurt = True
    def exit(self, e):
        self.entity.is_hurt = False
    def do(self):
        self.entity.current_frame += FRAMES_PER_SECOND * game_framework.frame_time
        if self.entity.current_frame >= self.entity.frame - 1:
            self.entity.state_machine.handle_state_event(('HURT_DONE', None))

class Dead(State):
    def enter(self, e):
        self.entity.current_image = self.entity.dead_image
        self.entity.frame = self.entity.frame_dead
        self.entity.current_frame = 0
    def do(self):
        self.entity.current_frame = min(self.entity.current_frame + FRAMES_PER_SECOND * game_framework.frame_time, self.entity.frame - 1)