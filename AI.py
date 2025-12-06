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
        # 피격(Hurt) 중이면 AI 리셋 (방향 꼬임 방지)
        my_state = self.me.state_machine.current_state.__class__.__name__
        if my_state == 'Hurt':
            self.release_all_keys()
            self.pressed_keys.clear()
            return

        if self.attack_cooldown > 0:
            self.attack_cooldown -= game_framework.frame_time

        # 대쉬 상태가 끝났는데 키가 눌려있으면 떼기
        if my_state != 'Dash' and self.me.key_map['dash'] in self.pressed_keys:
            self.release_key(self.me.key_map['dash'])

        self.bt.run()

    def build_behavior_tree(self):
        # 1. 방어 (최우선)
        c_threat = Condition('위협 감지', self.is_threatened, 100)
        a_defend = Action('방어하기', self.do_defend)
        seq_defense = Sequence('위협 시 방어', c_threat, a_defend)

        # # 2. 후퇴 (Hit & Run)
        # # 조건: 공격 쿨타임 중이고(무방비), 적이 가까우면 -> 적 반대로 대쉬
        # c_retreat = Condition('후퇴 필요한가?', self.need_to_retreat, 100)
        # a_retreat = Action('방향잡고 후퇴', self.do_dash_retreat)
        # seq_retreat = Sequence('치고 빠지기', c_retreat, a_retreat)

        # 3. 대쉬 추격 (Gap Closing)
        c_very_far = Condition('너무 먼가?', self.is_very_far, 300)
        a_dash_fwd = Action('방향잡고 돌격', self.do_dash_chase)
        seq_dash_chase = Sequence('급습', c_very_far, a_dash_fwd)

        # 4. 일반 추격
        c_far = Condition('거리가 먼가?', self.is_far, 100)
        a_chase = Action('방향잡고 추격', self.do_chase)
        seq_chase = Sequence('추적', c_far, a_chase)

        # 5. 공격 및 대기
        a_attack = Action('공격', self.do_attack)
        a_idle = Action('대기', self.do_idle)

        # 우선순위: 방어 > 후퇴(New) > 급습 > 추적 > 공격 > 대기
        root = Selector('AI 판단', seq_defense, seq_dash_chase, seq_chase, a_attack, a_idle)
        self.bt = BehaviorTree(root)

    # --- 조건 함수 ---
    def is_threatened(self, dist):
        d = abs(self.target.x - self.me.x)
        t_state = self.target.state_machine.current_state.__class__.__name__
        if t_state in ['Attack1', 'Attack2'] and d < dist:
            return BehaviorTree.SUCCESS
        return BehaviorTree.FAIL

    def need_to_retreat(self, dist):
        """공격 쿨타임 중(무방비)인데 적이 가까이 있으면 후퇴"""
        d = abs(self.target.x - self.me.x)
        # 쿨타임이 남아있고(공격 직후) && 거리가 가까우면
        if self.attack_cooldown > 0.2 and d < dist:
            return BehaviorTree.SUCCESS
        return BehaviorTree.FAIL

    def is_very_far(self, dist):
        d = abs(self.target.x - self.me.x)
        return BehaviorTree.SUCCESS if d > dist else BehaviorTree.FAIL

    def is_far(self, dist):
        d = abs(self.target.x - self.me.x)
        return BehaviorTree.SUCCESS if d > dist else BehaviorTree.FAIL

    # --- 행동 함수 ---

    def do_dash_retreat(self):
        """적 반대 방향으로 방향키를 누르고 -> 대쉬"""
        self.release_key(self.me.key_map['defense'])

        # ★ 좌표 기준으로 적의 반대 방향키 입력
        if self.target.x > self.me.x:  # 적이 오른쪽에 있다
            # 반대인 왼쪽으로 가야 함
            self.release_key(self.me.key_map['right'])  # 오른쪽 떼고
            self.press_key(self.me.key_map['left'])  # 왼쪽 누름
        else:  # 적이 왼쪽에 있다
            # 반대인 오른쪽으로 가야 함
            self.release_key(self.me.key_map['left'])
            self.press_key(self.me.key_map['right'])

        # 방향이 잡힌 상태에서 대쉬 키 입력
        self.tap_key(self.me.key_map['dash'])
        return BehaviorTree.SUCCESS

    def do_dash_chase(self):
        """적 방향으로 방향키를 누르고 -> 대쉬"""
        self.release_key(self.me.key_map['defense'])

        if self.target.x > self.me.x:  # 적이 오른쪽
            self.release_key(self.me.key_map['left'])
            self.press_key(self.me.key_map['right'])
        else:  # 적이 왼쪽
            self.release_key(self.me.key_map['right'])
            self.press_key(self.me.key_map['left'])

        self.tap_key(self.me.key_map['dash'])
        return BehaviorTree.SUCCESS

    def do_chase(self):
        """걸어서 추격"""
        self.release_key(self.me.key_map['defense'])
        self.release_key(self.me.key_map['dash'])

        if self.target.x > self.me.x:
            self.release_key(self.me.key_map['left'])
            self.press_key(self.me.key_map['right'])
        else:
            self.release_key(self.me.key_map['right'])
            self.press_key(self.me.key_map['left'])
        return BehaviorTree.SUCCESS

    def do_defend(self):
        self.release_move_keys()
        self.release_key(self.me.key_map['dash'])
        self.press_key(self.me.key_map['defense'])
        return BehaviorTree.SUCCESS

    def do_attack(self):
        if self.attack_cooldown > 0:
            self.do_idle()
            return BehaviorTree.SUCCESS

        self.release_all_keys()

        # 30% 확률 강공격
        if random.random() < 0.3:
            self.tap_key(self.me.key_map['attack2'])
            self.attack_cooldown = 0.8
        else:
            self.tap_key(self.me.key_map['attack1'])
            self.attack_cooldown = 0.4
        return BehaviorTree.SUCCESS

    def do_idle(self):
        self.release_all_keys()
        return BehaviorTree.SUCCESS

    # --- Helper Functions ---
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