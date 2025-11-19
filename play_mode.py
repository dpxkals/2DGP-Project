from pico2d import *

from back_ground import background
import game_world
import game_framework

# 플레이어 생성/관리 모듈
import player1 as p1_mod
import player2 as p2_mod

# 전역 플레이어 인스턴스
p1 = None
p2 = None

def handle_events():
    events = get_events()
    for event in events:
        if event.type == SDL_QUIT:
            game_framework.quit()
        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            game_framework.quit()
        # 키 이벤트만 플레이어에게 전달해서 처리되지 않은 INPUT 로그를 줄임
        elif event.type == SDL_KEYDOWN or event.type == SDL_KEYUP:
            if p1:
                p1.handle_event(event)
            if p2:
                p2.handle_event(event)


def init():
    global p1, p2

    # 배경 추가
    bg = background()
    game_world.add_object(bg, 0)

    # 플레이어 생성 (여기서 캐릭터 선택과 키맵을 지정)
    # 예: p1은 그림자검객, p2도 그림자검객 선택 가능
    # p1은 기본 키맵 (A/D/J/LCTRL)
    p1 = p1_mod.create_player1(char='monk', start_pos=(500,300), key_map=None, layer=1)
    # p2는 화살표/우측 컨트롤 등 다른 키맵 사용 (같은 캐릭터 선택 가능)
    # Peasant 클래스는 attack1/attack2도 지원하므로 여기에 포함시킵니다
    # attack1을 '/' (슬래시), attack2를 오른쪽 Shift로 설정
    p2_keymap = {
        'left': SDLK_LEFT,
        'right': SDLK_RIGHT,
        'defense': SDLK_PERIOD,
        'dash': SDLK_RCTRL,
        'attack1': SDLK_SLASH,
        'attack2': SDLK_RSHIFT,
    }
    p2 = p2_mod.create_player2(char='peasant', start_pos=(1400,300), key_map=p2_keymap, layer=1)

    # 충돌 등록
    p1_mod.register_collision_with(p2)

def finish():
    game_world.clear()

def update():
    game_world.update()
    game_world.handle_collisions()

def draw():
    clear_canvas()
    game_world.render()
    update_canvas()

def pause(): pass
def resume(): pass