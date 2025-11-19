import random
from pico2d import *


class AIController:
    def __init__(self, me, target):
        self.me = me
        self.target = target
        self.last_action_time = 0
        self.action_interval = 0.5  # AI가 행동을 결정하는 주기

    def update(self):
        current_time = get_time()
        if current_time - self.last_action_time < self.action_interval:
            return

        self.last_action_time = current_time

        dist = self.target.x - self.me.x

        # 간단한 상태 결정 로직
        if abs(dist) > 120:  # 거리가 멀면 접근
            if dist > 0:  # 타겟이 오른쪽에 있음
                self.press_key(self.me.key_map['right'])
                self.release_key(self.me.key_map['left'])
            else:  # 타겟이 왼쪽에 있음
                self.press_key(self.me.key_map['left'])
                self.release_key(self.me.key_map['right'])
        else:  # 사거리 안
            # 이동 멈춤
            self.release_key(self.me.key_map['right'])
            self.release_key(self.me.key_map['left'])

            # 확률적으로 공격
            if random.random() < 0.7:
                self.tap_key(self.me.key_map['attack1'])

    def press_key(self, key):
        event = SDL_Event()
        event.type = SDL_KEYDOWN
        event.key = key
        self.me.handle_event(event)

    def release_key(self, key):
        event = SDL_Event()
        event.type = SDL_KEYUP
        event.key = key
        self.me.handle_event(event)

    def tap_key(self, key):
        self.press_key(key)
        # 실제로는 딜레이가 필요하지만, 단순화를 위해 바로 뗌 (State 전환만 트리거)
        self.release_key(key)


# SDL_Event 모의 클래스 (Pico2d 이벤트 구조 맞추기용)
class SDL_Event:
    def __init__(self):
        self.type = None
        self.key = None