from pico2d import *

from back_ground import background
from shadow_man import ShadowMan
from short_sword import short_sword

import game_world

import game_framework

# Game object class here
# 1. 객체의 도출 - 추상화
# 2. 속성을 도출 - 추상화
# 3. 행위를 도출
# 4. 클래스를 제작

def handle_events():
    global running

    events = get_events()
    for event in events:
        if event.type == SDL_QUIT:
            game_framework.quit()
        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            game_framework.quit()
        else:
            shadow_man.handle_event(event)

def init():
    global shadow_man

    # 객체들을 생성
    bg = background()
    game_world.add_object(bg, 0)

    shadow_man = ShadowMan()
    game_world.add_object(shadow_man, 1)

    sword = short_sword()
    game_world.add_object(sword, 1)

    # 충돌 대상 설정 - 근데 아직 완벽한것은 아님 바꿀 건데 일단 적용만
    game_world.add_collision_pairs('1p:2p', shadow_man, sword)


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