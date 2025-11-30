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
        # 피격 중이면 AI 리셋 (멍때림 방지)
        my_state = self.me.state_machine.current_state.__class__.__name__
        if my_state == 'Hurt':
            self.release_all_keys()
            self.pressed_keys.clear()
            return

        if self.attack_cooldown > 0:
            self.attack_cooldown -= game_framework.frame_time

        # 키 상태 관리: 대쉬가 끝났는데 키를 누르고 있으면 떼줌 (재사용 위해)
        if my_state != 'Dash' and self.me.key_map['dash'] in self.pressed_keys:
            self.release_key(self.me.key_map['dash'])

        self.bt.run()

    def build_behavior_tree(self):
        # 1. 방어 (최우선)
        c_threat = Condition('위협 감지', self.is_threatened, 150)
        a_defend = Action('방어하기', self.do_defend)
        seq_defense = Sequence('위협 시 방어', c_threat, a_defend)

        # 2. 대쉬 후퇴 (Hit & Run)
        # 조건: 공격 후 쿨타임 중이고, 적과 너무 가까우면 -> 뒤로 대쉬
        c_retreat_need = Condition('후퇴 필요한가?', self.need_to_retreat, 120)
        a_dash_back = Action('뒤로 대쉬', self.do_dash_retreat)
        seq_retreat = Sequence('치고 빠지기', c_retreat_need, a_dash_back)

        # 3. 대쉬 추격 (Gap Closing)
        # 조건: 적과 거리가 아주 멀면 -> 앞으로 대쉬
        c_very_far = Condition('너무 먼가?', self.is_very_far, 300)
        a_dash_fwd = Action('앞으로 대쉬', self.do_dash_chase)
        seq_dash_chase = Sequence('급습', c_very_far, a_dash_fwd)

        # 4. 일반 추격
        c_far = Condition('거리가 먼가?', self.is_far, 100)
        a_chase = Action('걸어서 추격', self.do_chase)
        seq_chase = Sequence('추적', c_far, a_chase)

        # 5. 공격 및 대기
        a_attack = Action('공격', self.do_attack)
        a_idle = Action('대기', self.do_idle)

        # 우선순위: 방어 > 후퇴 > 급습 > 추적 > 공격 > 대기
        root = Selector('AI 판단', seq_defense, seq_retreat, seq_dash_chase, seq_chase, a_attack, a_idle)
        self.bt = BehaviorTree(root)

    # --- 조건 함수 (Conditions) ---

    def is_threatened(self, dist):
        d = abs(self.target.x - self.me.x)
        t_state = self.target.state_machine.current_state.__class__.__name__
        if t_state in ['Attack1', 'Attack2'] and d < dist:
            return BehaviorTree.SUCCESS
        return BehaviorTree.FAIL

    def need_to_retreat(self, dist):
        """공격 쿨타임 중(무방비)인데 적이 가까이 있으면 후퇴"""
        d = abs(self.target.x - self.me.x)
        # 쿨타임이 남아있고 && 거리가 가까우면
        if self.attack_cooldown > 0.1 and d < dist:
            return BehaviorTree.SUCCESS
        return BehaviorTree.FAIL

    def is_very_far(self, dist):
        """거리가 300픽셀 이상 벌어지면"""
        d = abs(self.target.x - self.me.x)
        if d > dist:
            return BehaviorTree.SUCCESS
        return BehaviorTree.FAIL

    def is_far(self, dist):
        d = abs(self.target.x - self.me.x)
        if d > dist:
            return BehaviorTree.SUCCESS
        return BehaviorTree.FAIL

    # --- 행동 함수 (Actions) ---

    def do_defend(self):
        self.release_move_keys()
        self.release_key(self.me.key_map['dash'])  # 대쉬 중이면 캔슬 시도
        self.press_key(self.me.key_map['defense'])
        return BehaviorTree.SUCCESS

    def do_dash_retreat(self):
        """적 반대 방향으로 대쉬"""
        self.release_key(self.me.key_map['defense'])

        # 적 반대 방향 키 누르기
        if self.target.x > self.me.x:  # 적이 오른쪽에 있으면
            self.press_key(self.me.key_map['left'])  # 왼쪽으로
            self.release_key(self.me.key_map['right'])
        else:
            self.press_key(self.me.key_map['right'])  # 오른쪽으로
            self.release_key(self.me.key_map['left'])

        # 대쉬 키 입력 (톡 누름)
        self.tap_key(self.me.key_map['dash'])
        return BehaviorTree.SUCCESS

    def do_dash_chase(self):
        """적 방향으로 대쉬"""
        self.release_key(self.me.key_map['defense'])

        # 적 방향 키 누르기
        if self.target.x > self.me.x:
            self.press_key(self.me.key_map['right'])
            self.release_key(self.me.key_map['left'])
        else:
            self.press_key(self.me.key_map['left'])
            self.release_key(self.me.key_map['right'])

        # 대쉬 키 입력
        self.tap_key(self.me.key_map['dash'])
        return BehaviorTree.SUCCESS

    def do_chase(self):
        """걸어서 추격"""
        self.release_key(self.me.key_map['defense'])
        self.release_key(self.me.key_map['dash'])  # 혹시 대쉬 키 눌려있으면 뗌

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

        self.release_all_keys()  # 이동 멈춤

        # 30% 강공격, 70% 약공격
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

    # --- Helper ---
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
        # 대쉬 같은 경우 트리거를 위해 바로 떼는 신호를 보내는게 나을 수 있음
        # 다만 press 상태가 한 프레임 유지되어야 한다면 update에서 처리해야 하나,
        # 여기서는 즉시 뗌 (Pico2d 이벤트 큐 순서상 DOWN -> UP 순차 처리됨)
        self.release_key(key)


class SDL_Event:
    def __init__(self, type, key):
        self.type = type
        self.key = key