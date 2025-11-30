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

# 라운드 및 게임 상태 관리 변수
round_num = 1  # 현재 라운드
p1_score = 0  # 1P 승리 횟수
p2_score = 0  # 2P 승리 횟수

# 게임 페이즈: 'FIGHT'(전투), 'ROUND_OVER'(라운드끝), 'GAME_OVER'(최종종료)
game_phase = 'FIGHT'
phase_start_time = 0  # 페이즈 전환 시간 기록용
result_font = None  # 결과 출력용 폰트


def init():
    global p1, p2, ui, ai
    global round_num, p1_score, p2_score, game_phase, result_font

    # 게임 변수 초기화
    round_num = 1
    p1_score = 0
    p2_score = 0
    game_phase = 'FIGHT'

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


def finish():
    global result_font
    game_world.clear()
    del result_font


def update():
    global game_phase, phase_start_time, p1_score, p2_score, round_num

    # -------------------------------------------------------
    # 1. 전투 진행 중 (FIGHT)
    # -------------------------------------------------------
    if game_phase == 'FIGHT':
        game_world.update()
        game_world.handle_collisions()

        if ai: ai.update()

        check_attack(p1, p2)
        check_attack(p2, p1)

        # 승패 체크 (HP가 0 이하가 되면 라운드 종료)
        if p1.hp <= 0:
            finish_round(winner='2P')
        elif p2.hp <= 0:
            finish_round(winner='1P')

    # -------------------------------------------------------
    # 2. 라운드 종료 대기 (ROUND_OVER)
    # -------------------------------------------------------
    elif game_phase == 'ROUND_OVER':
        game_world.update()
        # 3초 동안 결과 보여주고 다음으로 넘어감
        if get_time() - phase_start_time > 3.0:
            # 누군가 2승을 먼저 했는지 확인
            if p1_score >= 2 or p2_score >= 2:
                game_phase = 'GAME_OVER'
                phase_start_time = get_time()
            else:
                next_round()  # 다음 라운드 시작

    # -------------------------------------------------------
    # 3. 게임 완전 종료 (GAME_OVER)
    # -------------------------------------------------------
    elif game_phase == 'GAME_OVER':
        # 4초 뒤 타이틀 화면으로 이동
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
    """다음 라운드 세팅 (위치, HP 초기화)"""
    global round_num, game_phase
    round_num += 1
    game_phase = 'FIGHT'

    # 캐릭터 상태 리셋
    reset_character(p1, 400, 300, 1)  # 1P 위치, 오른쪽 보기
    reset_character(p2, 1500, 300, -1)  # 2P 위치, 왼쪽 보기

    # AI 상태 리셋 (누르고 있던 키 해제)
    if ai:
        ai.pressed_keys.clear()
        ai.attack_cooldown = 0


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
    ui.draw(p1, p2)

    # --- UI 추가 표시 (라운드 및 스코어) ---
    # 중앙 상단에 라운드와 점수 표시
    ui.font.draw(880, 1000, f"ROUND {round_num}", (255, 255, 0))
    ui.font.draw(850, 950, f"{p1_score}  :  {p2_score}", (255, 255, 255))

    # --- 상태별 텍스트 표시 ---
    if game_phase == 'ROUND_OVER':
        # 라운드 승자 표시
        if p1.hp > 0:
            result_font.draw(800, 600, "1P WIN!", (255, 0, 0))
        else:
            result_font.draw(800, 600, "2P WIN!", (0, 0, 255))

    elif game_phase == 'GAME_OVER':
        # 최종 우승자 표시
        result_font.draw(750, 700, "GAME SET", (255, 255, 255))
        if p1_score > p2_score:
            result_font.draw(600, 500, "FINAL WINNER: 1P", (255, 0, 0))
        else:
            result_font.draw(600, 500, "FINAL WINNER: 2P", (0, 0, 255))

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