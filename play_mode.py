from pico2d import *
import game_world
import game_framework
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

    # P1 생성 (키보드 조작)
    p1 = Peasant()  # 기본 키맵 사용
    p1.x, p1.y = 400, 300
    p1.player_id = "1P"
    game_world.add_object(p1, 1)

    # P2 생성 (AI 조작용 - 키맵은 AI가 시뮬레이션함)
    p2_keymap = {'left': SDLK_LEFT, 'right': SDLK_RIGHT, 'attack1': SDLK_SLASH}
    p2 = Monk(key_map=p2_keymap)  # 테스트를 위해 둘 다 Monk 사용, 원하면 Peasant로 변경
    p2.x, p2.y = 1500, 300
    p2.player_id = "2P"
    p2.face_dir = -1  # 시작할 때 왼쪽 보기
    game_world.add_object(p2, 1)

    # 충돌 파트너 등록 (밀어내기 물리용)
    game_world.add_collision_pairs('1p:2p', p1, p2)

    # UI 및 AI 생성
    ui = UI()
    ai = AIController(p2, p1)  # p2가 AI, p1이 타겟


def update():
    game_world.update()
    game_world.handle_collisions()  # 밀어내기 처리

    # AI 업데이트
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
            # p2는 AI가 조종하므로 이벤트 전달 X (수동 조작 필요하면 주석 해제)
            #if p2: p2.handle_event(event)


def finish():
    game_world.clear()