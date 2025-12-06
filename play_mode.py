from pico2d import *
import game_world
import game_framework
import game_data
from back_ground import background
from Monk import Monk
from peasant import Peasant
from ui import UI
from AI import AIController

# --- 전역 변수 ---
p1 = None
p2 = None
ui = None
ai = None

round_start = None

# 라운드 및 게임 상태 관리 변수
round_num = 1  # 현재 라운드
p1_score = 0  # 1P 승리 횟수
p2_score = 0  # 2P 승리 횟수

# 게임 페이즈: 'FIGHT'(전투), 'ROUND_OVER'(라운드끝), 'GAME_OVER'(최종종료)
game_phase = 'FIGHT'
phase_start_time = 0  # 페이즈 전환 시간 기록용
result_font = None  # 결과 출력용 폰트

fight_start_time = 0 # 전투 시작 시간 (타이머용)
ROUND_TIME_LIMIT = 99.0 # 라운드 제한 시간 (초)


def init():
    global p1, p2, ui, ai
    global round_num, p1_score, p2_score, game_phase, result_font
    global round_start, phase_start_time

    # 게임 변수 초기화
    round_num = 1
    p1_score = 0
    p2_score = 0
    game_phase = 'ROUND_START'
    phase_start_time = get_time()

    # 폰트 로드 (결과창용 큰 폰트)
    result_font = load_font('ENCR10B.TTF', 60)

    # 배경
    bg = background()
    game_world.add_object(bg, 0)

    # ---------------------------------------------------------
    # [1P 키 설정]
    # ---------------------------------------------------------
    key_map_1p = {
        'left': SDLK_a, 'right': SDLK_d, 'defense': SDLK_j,
        'dash': SDLK_LCTRL, 'attack1': SDLK_e, 'attack2': SDLK_q
    }

    if game_data.p1_char == 'Monk':
        p1 = Monk(key_map=key_map_1p)
    else:
        p1 = Peasant(key_map=key_map_1p)
    p1.x, p1.y = 400, 300
    p1.player_id = "1P"
    game_world.add_object(p1, 1)

    # ---------------------------------------------------------
    # [2P 키 설정]
    # ---------------------------------------------------------
    key_map_2p = {
        'left': SDLK_LEFT, 'right': SDLK_RIGHT, 'defense': SDLK_PERIOD,
        'dash': SDLK_RCTRL, 'attack1': SDLK_SLASH, 'attack2': SDLK_RSHIFT
    }

    if game_data.p2_char == 'Monk':
        p2 = Monk(key_map=key_map_2p)
    else:
        p2 = Peasant(key_map=key_map_2p)
    p2.x, p2.y = 1500, 300
    p2.player_id = "2P"
    p2.face_dir = -1
    game_world.add_object(p2, 1)

    # 충돌 파트너 등록
    game_world.add_collision_pairs('1p:2p', p1, p2)

    # UI 및 AI 생성
    ui = UI()
    ai = None
    if game_data.game_mode == 'AI':
        ai = AIController(p2, p1)

    try:
        round_start = load_wav('Sound/round_start.wav')
        round_start.set_volume(64)
        round_start.play()
    except Exception:
        round_start = None
    phase_start_time = get_time()


def finish():
    global result_font
    game_world.clear()
    del result_font


def update():
    global game_phase, phase_start_time, p1_score, p2_score, round_num, round_start, fight_start_time

    game_world.update()

    # --- 1. FIGHT (전투 중) ---
    if game_phase == 'FIGHT':
        game_world.handle_collisions()
        if ai: ai.update()
        check_attack(p1, p2)
        check_attack(p2, p1)

        # [타이머 체크] 시간이 다 되면 체력 많은 쪽 승리
        if get_time() - fight_start_time > ROUND_TIME_LIMIT:
            if p1.hp > p2.hp: finish_round('1P')
            elif p2.hp > p1.hp: finish_round('2P')
            else: finish_round('DRAW') # 무승부면 일단 2P 승 등으로 처리

        # [HP 체크]
        if p1.hp <= 0: finish_round('2P')
        elif p2.hp <= 0: finish_round('1P')

    # --- 2. ROUND_START (대기) ---
    elif game_phase == 'ROUND_START':
        wait_time = 2.0
        if get_time() - phase_start_time > wait_time:
            game_phase = 'FIGHT'
            fight_start_time = get_time() # ★ 전투 시작 시간 기록! (타이머 시작)

    # --- 나머지 상태 (ROUND_OVER, GAME_OVER)는 기존 코드 유지 ---
    elif game_phase == 'ROUND_OVER':
        if get_time() - phase_start_time > 3.0:
            if p1_score >= 2 or p2_score >= 2:
                game_phase = 'GAME_OVER'
                phase_start_time = get_time()
            else:
                next_round()

    elif game_phase == 'GAME_OVER':
        if get_time() - phase_start_time > 4.0:
            import title_mode
            game_framework.change_mode(title_mode)


def finish_round(winner):
    """라운드 종료 처리"""
    global game_phase, phase_start_time, p1_score, p2_score

    game_phase = 'ROUND_OVER'
    phase_start_time = get_time()

    if winner == '1P':
        p1_score += 1
    else:
        p2_score += 1


def next_round():
    global round_num, game_phase, phase_start_time, round_start

    round_num += 1

    # 1. [핵심] 소리 재생 전에 캐릭터 위치와 상태를 먼저 리셋합니다.
    # 그래야 "Round 2" 소리가 나올 때 캐릭터들이 양쪽에 서 있게 됩니다.
    reset_character(p1, 400, 300, 1)   # 1P 위치 초기화
    reset_character(p2, 1500, 300, -1) # 2P 위치 초기화

    # AI 상태도 리셋
    if ai:
        ai.pressed_keys.clear()
        ai.attack_cooldown = 0

    # 2. 라운드 시작 사운드 재생
    try:
        # 매번 로드하는 것보다 init에서 로드해두는 게 좋지만, 여기선 기존 방식 유지
        round_start = load_wav('Sound/round_start.wav')
        round_start.set_volume(64)
        round_start.play()
    except Exception:
        pass

    # 3. 페이즈 전환 (대기 상태로)
    game_phase = 'ROUND_START'
    phase_start_time = get_time()


def reset_character(player, x, y, face):
    """캐릭터를 초기 상태로 되돌리는 헬퍼 함수"""
    player.x, player.y = x, y
    player.face_dir = face
    player.hp = player.max_hp
    player.is_hurt = False

    # 상태머신 강제 초기화 (Idle 상태로 전환)
    player.state_machine.current_state = player.IDLE
    player.IDLE.enter(None)


def check_attack(attacker, victim):
    # 공격 판정 로직 (기존과 동일)
    attack_box = attacker.get_attack_bb()
    if attack_box == (0, 0, 0, 0): return

    victim_box = victim.get_bb()

    if collide(attack_box, victim_box):
        victim.take_damage(attacker.attack_power)


def collide(a, b):
    left_a, bottom_a, right_a, top_a = a
    left_b, bottom_b, right_b, top_b = b
    if left_a > right_b: return False
    if right_a < left_b: return False
    if top_a < bottom_b: return False
    if bottom_a > top_b: return False
    return True


def draw():
    clear_canvas()
    game_world.render()

    # [타이머 시간 계산]
    if game_phase == 'FIGHT':
        # 남은 시간 = 제한시간 - 경과시간
        current_fight_time = max(0, ROUND_TIME_LIMIT - (get_time() - fight_start_time))
    elif game_phase == 'ROUND_START':
        current_fight_time = ROUND_TIME_LIMIT  # 시작 전엔 99초로 표시
    else:
        current_fight_time = 0  # 끝났으면 0

    # UI 그리기 (모든 정보 전달)
    # 순서: p1, p2, 1P점수, 2P점수, 라운드수, 현재상태, 상태시작시간, 남은전투시간
    ui.draw(p1, p2, p1_score, p2_score, round_num, game_phase, phase_start_time, current_fight_time)

    update_canvas()


def handle_events():
    events = get_events()
    for event in events:
        if event.type == SDL_QUIT:
            game_framework.quit()
        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            import title_mode
            game_framework.change_mode(title_mode)
        else:
            # ★ 중요: 전투 중일 때만 캐릭터 조작 가능
            if game_phase == 'FIGHT':
                if p1: p1.handle_event(event)
                if not ai and p2:
                    p2.handle_event(event)