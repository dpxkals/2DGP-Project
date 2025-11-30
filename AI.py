import random
from pico2d import *
import game_framework
from behavior_tree import BehaviorTree, Action, Sequence, Condition, Selector


class AIController:
    def __init__(self, me, target):
        self.me = me  # AI 캐릭터 (2P)
        self.target = target  # 플레이어 캐릭터 (1P)

        self.pressed_keys = set()  # 현재 누르고 있는 키 관리
        self.attack_cooldown = 0  # 공격 속도 조절용

        self.build_behavior_tree()  # 트리 생성

    def update(self):
        # 쿨타임 감소
        if self.attack_cooldown > 0:
            self.attack_cooldown -= game_framework.frame_time

        # 행동 트리 실행 (매 프레임 판단)
        self.bt.run()

    def build_behavior_tree(self):
        # -----------------------------------------------------------
        # 1. 방어 전략 (Defense Strategy)
        # -----------------------------------------------------------
        # 조건: 상대가 공격 중이고 거리가 가까우면
        c_is_threatened = Condition('위협을 느끼는가?', self.is_threatened, 150)
        # 행동: 방어 키를 누른다
        a_defend = Action('방어하기', self.do_defend)

        # [방어 시퀀스]: 위협 조건이 맞으면 -> 방어 행동 실행
        seq_defense = Sequence('위협 감지 시 방어', c_is_threatened, a_defend)

        # -----------------------------------------------------------
        # 2. 추적 전략 (Chase Strategy)
        # -----------------------------------------------------------
        # 조건: 거리가 멀면 (공격 사거리 밖이면)
        c_is_far = Condition('거리가 먼가?', self.is_far, 100)
        # 행동: 상대방 방향으로 이동
        a_chase = Action('추적하기', self.do_chase)

        # [추적 시퀀스]: 멀리 있으면 -> 추적
        seq_chase = Sequence('거리 좁히기', c_is_far, a_chase)

        # -----------------------------------------------------------
        # 3. 공격 전략 (Attack Strategy)
        # -----------------------------------------------------------
        # 행동: 공격 (쿨타임 체크 포함)
        a_attack = Action('공격하기', self.do_attack)

        # -----------------------------------------------------------
        # 4. 루트 노드 (Root Selector)
        # -----------------------------------------------------------
        # 우선순위: 방어 > 추적 > 공격 > 대기(Idle)
        # Selector는 자식 중 하나라도 성공하면 즉시 종료하므로 우선순위가 높은 것을 앞에 둡니다.

        # 마지막 fallback으로 아무것도 안하는 Idle 액션 추가
        a_idle = Action('대기', self.do_idle)

        root = Selector('AI 행동 결정', seq_defense, seq_chase, a_attack, a_idle)

        self.bt = BehaviorTree(root)

    # --- [조건 함수들 (Conditions)] ---
    # 성공(SUCCESS) 또는 실패(FAIL)를 반환해야 함

    def is_threatened(self, danger_range):
        """상대가 공격 상태이고 거리가 가까운지 확인"""
        # 1. 거리 계산
        distance = abs(self.target.x - self.me.x)

        # 2. 상대방 상태 확인 (Attack1, Attack2 클래스인지 확인)
        target_state = self.target.state_machine.current_state.__class__.__name__
        is_attacking = target_state in ['Attack1', 'Attack2']

        if is_attacking and distance < danger_range:
            return BehaviorTree.SUCCESS
        else:
            return BehaviorTree.FAIL

    def is_far(self, range_threshold):
        """거리가 특정 범위보다 먼지 확인"""
        distance = abs(self.target.x - self.me.x)
        if distance > range_threshold:
            return BehaviorTree.SUCCESS
        else:
            return BehaviorTree.FAIL

    # --- [행동 함수들 (Actions)] ---
    # 성공(SUCCESS), 실행중(RUNNING), 실패(FAIL) 반환

    def do_defend(self):
        """이동을 멈추고 방어 키 입력"""
        self.release_move_keys()  # 이동 키 떼기
        self.press_key(self.me.key_map['defense'])  # 방어 키 누르기
        return BehaviorTree.SUCCESS

    def do_chase(self):
        """상대방 방향으로 이동"""
        self.release_key(self.me.key_map['defense'])  # 방어 풀기

        # 방향 결정
        if self.target.x > self.me.x:
            self.press_key(self.me.key_map['right'])
            self.release_key(self.me.key_map['left'])
        else:
            self.press_key(self.me.key_map['left'])
            self.release_key(self.me.key_map['right'])

        return BehaviorTree.SUCCESS

    def do_attack(self):
        """공격 실행 (확률적 선택 + 쿨타임)"""
        # 사거리 안인데 공격 쿨타임이면 대기(SUCCESS 처리해서 다른 행동 못하게)
        if self.attack_cooldown > 0:
            self.do_idle()
            return BehaviorTree.SUCCESS

        self.release_all_keys()  # 이동/방어 멈춤

        # 30% 확률로 강공격, 70% 약공격
        if random.random() < 0.3:
            self.tap_key(self.me.key_map['attack2'])
            self.attack_cooldown = 1.0  # 강공격 후 딜레이
        else:
            self.tap_key(self.me.key_map['attack1'])
            self.attack_cooldown = 0.5  # 약공격 후 딜레이

        return BehaviorTree.SUCCESS

    def do_idle(self):
        """아무것도 안 함 (키 떼기)"""
        self.release_all_keys()
        return BehaviorTree.SUCCESS

    # --- [키보드 입력 시뮬레이션 헬퍼 함수] ---

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


# SDL 이벤트 모의 클래스
class SDL_Event:
    def __init__(self, type, key):
        self.type = type
        self.key = key