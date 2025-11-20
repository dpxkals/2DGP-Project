import random
from pico2d import *
import game_framework


class AIController:
    def __init__(self, me, target):
        self.me = me  # AI 캐릭터 (2P)
        self.target = target  # 플레이어 캐릭터 (1P)

        self.think_time = 0  # 다음 행동까지 남은 시간
        self.state = "IDLE"  # AI의 현재 상태 (IDLE, CHASE, ATTACK, DEFEND, RUNAWAY)

        # 사거리 설정 (픽셀 단위)
        self.attack_range = 100

        # 현재 누르고 있는 키를 기억 (떼기 위해서)
        self.pressed_keys = set()

    def update(self):
        # 1. 사고 주기 조절 (너무 빠르면 사람이 이길 수 없음)
        if get_time() < self.think_time:
            return

        # 2. 상황 인지 (거리 및 방향 계산)
        distance = self.target.x - self.me.x
        abs_dist = abs(distance)
        direction = 1 if distance > 0 else -1  # 1이면 오른쪽, -1이면 왼쪽

        # 3. 상대방의 상태 확인 (공격 중인가?)
        # 상대방의 현재 상태 클래스 이름을 문자열로 가져옴
        target_state_name = self.target.state_machine.current_state.__class__.__name__
        is_target_attacking = target_state_name in ['Attack1', 'Attack2']

        # [우선순위 1] 상대가 공격 중이고, 거리가 가까우면 -> 방어
        if is_target_attacking and abs_dist < 150:
            self.change_action('DEFEND')
            self.think_time = get_time() + 0.5  # 0.5초 동안 방어 유지

        # [우선순위 2] 거리가 멀면 -> 추적
        elif abs_dist > self.attack_range:
            self.change_action('CHASE', direction)
            self.think_time = get_time() + 0.1

        # [우선순위 3] 거리가 가까우면 -> 공격
        else:
            # 30% 확률로 강공격, 70% 약공격, 가끔 대시로 뒤잡기
            choice = random.random()
            if choice < 0.7:
                self.change_action('ATTACK1')
            elif choice < 0.9:
                self.change_action('ATTACK2')
            else:
                self.change_action('WAIT')  # 가끔 멍때림 (인간미)

            self.think_time = get_time() + random.uniform(0.3, 0.7)  # 다음 행동 딜레이

    def change_action(self, action, direction=0):
        # 이전에 누르던 키 모두 떼기 (Reset)
        self.release_all_keys()

        # 행동에 따른 키 입력 시뮬레이션
        if action == 'CHASE':
            key = self.me.key_map['right'] if direction == 1 else self.me.key_map['left']
            self.press_key(key)

        elif action == 'DEFEND':
            # 상대가 공격하면 쫄아서 방어 키 꾹 누름
            self.press_key(self.me.key_map['defense'])

        elif action == 'ATTACK1':
            # 공격은 꾹 누르는 게 아니라 '톡' 누르는 것 (Tap)
            self.tap_key(self.me.key_map['attack1'])

        elif action == 'ATTACK2':
            self.tap_key(self.me.key_map['attack2'])

        elif action == 'WAIT':
            pass  # 아무것도 안 누르고 대기

    # --- 키보드 시뮬레이션 도구들 ---

    def press_key(self, key):
        """키를 누른 상태로 유지 (이동, 방어용)"""
        if key in self.pressed_keys: return  # 이미 누르고 있으면 무시

        event = SDL_Event(SDL_KEYDOWN, key)
        self.me.handle_event(event)
        self.pressed_keys.add(key)

    def release_key(self, key):
        """키를 뗌"""
        if key not in self.pressed_keys: return

        event = SDL_Event(SDL_KEYUP, key)
        self.me.handle_event(event)
        self.pressed_keys.remove(key)

    def release_all_keys(self):
        """누르고 있던 모든 키를 뗌"""
        # 집합(set) 복사본을 만들어서 순회 (반복 중 제거 오류 방지)
        for key in list(self.pressed_keys):
            self.release_key(key)

    def tap_key(self, key):
        """키를 눌렀다 바로 뗌 (공격용)"""
        self.press_key(key)
        self.release_key(key)


# Pico2d 이벤트 구조체 흉내내기
class SDL_Event:
    def __init__(self, type, key):
        self.type = type
        self.key = key