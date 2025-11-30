import random
from pico2d import *
import game_framework
from behavior_tree import BehaviorTree, Action, Sequence, Condition, Selector

class AIController:
    def __init__(self, me, target):
        self.me = me
        self.target = target
        self.pressed_keys = set()
        self.attack_cooldown = 0
        self.build_behavior_tree()

    def update(self):
        if self.attack_cooldown > 0:
            self.attack_cooldown -= game_framework.frame_time
        self.bt.run()

    def build_behavior_tree(self):
        c_is_threatened = Condition('위협을 느끼는가?', self.is_threatened, 150)
        a_defend = Action('방어하기', self.do_defend)
        seq_defense = Sequence('위협 감지 시 방어', c_is_threatened, a_defend)

        c_is_far = Condition('거리가 먼가?', self.is_far, 100)
        a_chase = Action('추적하기', self.do_chase)
        seq_chase = Sequence('거리 좁히기', c_is_far, a_chase)

        a_attack = Action('공격하기', self.do_attack)
        a_idle = Action('대기', self.do_idle)

        root = Selector('AI 행동 결정', seq_defense, seq_chase, a_attack, a_idle)
        self.bt = BehaviorTree(root)

    def is_threatened(self, danger_range):
        distance = abs(self.target.x - self.me.x)
        target_state = self.target.state_machine.current_state.__class__.__name__
        is_attacking = target_state in ['Attack1', 'Attack2']

        if is_attacking and distance < danger_range:
            return BehaviorTree.SUCCESS
        else:
            return BehaviorTree.FAIL

    def is_far(self, range_threshold):
        distance = abs(self.target.x - self.me.x)
        if distance > range_threshold:
            return BehaviorTree.SUCCESS
        else:
            return BehaviorTree.FAIL

    def do_defend(self):
        self.release_move_keys()
        self.press_key(self.me.key_map['defense'])
        return BehaviorTree.SUCCESS

    def do_chase(self):
        self.release_key(self.me.key_map['defense'])
        if self.target.x > self.me.x:
            self.press_key(self.me.key_map['right'])
            self.release_key(self.me.key_map['left'])
        else:
            self.press_key(self.me.key_map['left'])
            self.release_key(self.me.key_map['right'])
        return BehaviorTree.SUCCESS

    def do_attack(self):
        if self.attack_cooldown > 0:
            self.do_idle()
            return BehaviorTree.SUCCESS

        self.release_all_keys()

        if random.random() < 0.3:
            self.tap_key(self.me.key_map['attack2'])
            self.attack_cooldown = 1.0
        else:
            self.tap_key(self.me.key_map['attack1'])
            self.attack_cooldown = 0.5
        return BehaviorTree.SUCCESS

    def do_idle(self):
        self.release_all_keys()
        return BehaviorTree.SUCCESS

    def press_key(self, key):
        if key in self.pressed_keys: return
        self.me.handle_event(SDL_Event(SDL_KEYDOWN, key))
        self.pressed_keys.add(key)

    def release_key(self, key):
        if key not in self.pressed_keys: return
        self.me.handle_event(SDL_Event(SDL_KEYUP, key))
        self.pressed_keys.remove(key)

    def release_move_keys(self):
        self.release_key(self.me.key_map['left'])
        self.release_key(self.me.key_map['right'])

    def release_all_keys(self):
        for key in list(self.pressed_keys):
            self.release_key(key)

    def tap_key(self, key):
        self.press_key(key)
        self.release_key(key)

class SDL_Event:
    def __init__(self, type, key):
        self.type = type
        self.key = key