from pico2d import *
import game_world
import game_framework
import game_data
from back_ground import background
from Monk import Monk
from peasant import Peasant
from ui import UI
from AI import AIController

p1 = None
p2 = None
ui = None
ai = None


def init():
    global p1, p2, ui, ai

    # 배경
    bg = background()
    game_world.add_object(bg, 0)

    # ---------------------------------------------------------
    # [1P 키 설정] 캐릭터가 누구든 무조건 이 키를 사용
    # A(좌), D(우), J(방어), E(약공), Q(강공), LCtrl(대시)
    # ---------------------------------------------------------
    key_map_1p = {
        'left': SDLK_a,
        'right': SDLK_d,
        'defense': SDLK_j,
        'dash': SDLK_LCTRL,
        'attack1': SDLK_e,
        'attack2': SDLK_q
    }

    # 1P 생성 (Peasant로 하되 키맵은 key_map_1p 적용)
    if game_data.p1_char == 'Monk':
        p1 = Monk(key_map=key_map_1p)
    else:
        p1 = Peasant(key_map=key_map_1p)
    p1.x, p1.y = 400, 300
    p1.player_id = "1P"
    game_world.add_object(p1, 1)

    # ---------------------------------------------------------
    # [2P 키 설정] 캐릭터가 누구든 무조건 이 키를 사용
    # 화살표(이동), .(방어), /(약공), RShift(강공), RCtrl(대시)
    # ---------------------------------------------------------
    key_map_2p = {
        'left': SDLK_LEFT,
        'right': SDLK_RIGHT,
        'defense': SDLK_PERIOD,  # . 키
        'dash': SDLK_RCTRL,  # 오른쪽 컨트롤 (대시)
        'attack1': SDLK_SLASH,  # / 키
        'attack2': SDLK_RSHIFT  # 오른쪽 쉬프트
    }

    # 2P 생성 (Monk로 하되 키맵은 key_map_2p 적용)
    if game_data.p2_char == 'Monk':
        p2 = Monk(key_map=key_map_2p)
    else:
        p2 = Peasant(key_map=key_map_2p)
    p2.x, p2.y = 1500, 300
    p2.player_id = "2P"
    p2.face_dir = -1
    game_world.add_object(p2, 1)

    # 충돌 파트너 등록 (밀어내기 물리용)
    game_world.add_collision_pairs('1p:2p', p1, p2)

    # UI 및 AI 생성
    ui = UI()

    ai = None  # 초기화
    if game_data.game_mode == 'AI':
        ai = AIController(p2, p1)  # 2P를 AI가 조종


def update():
    game_world.update()
    game_world.handle_collisions()  # 밀어내기 처리

    # AI 업데이트
    if ai:  # AI 모드일 때만 업데이트
        ai.update()

    # P1 공격 -> P2 피격 확인
    check_attack(p1, p2)
    # P2 공격 -> P1 피격 확인
    check_attack(p2, p1)


def check_attack(attacker, victim):
    # 공격자가 공격 박스를 가지고 있는지(공격중인지) 확인
    attack_box = attacker.get_attack_bb()
    if attack_box == (0, 0, 0, 0): return

    # 피해자 몸통 박스
    victim_box = victim.get_bb()

    if collide(attack_box, victim_box):
        # 데미지 적용
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
    ui.draw(p1, p2)  # UI 그리기
    update_canvas()


def handle_events():
    events = get_events()
    for event in events:
        if event.type == SDL_QUIT:
            game_framework.quit()
        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            game_framework.quit()
        else:
            if p1: p1.handle_event(event)
            # pvp 모드
            if not ai and p2:
                p2.handle_event(event)


def finish():
    game_world.clear()