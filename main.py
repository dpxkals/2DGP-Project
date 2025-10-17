from pico2d import *

from shadow_man import ShadowMan
#from short_sword import short_sword


# Game object class here
# 1. 객체의 도출 - 추상화
# 2. 속성을 도출 - 추상화
# 3. 행위를 도출
# 4. 클래스를 제작

class background:
    def __init__(self):
        self.image = load_image('backGround.png')

    def update(self):
        pass

    def draw(self):
        self.image.draw(960,540,1920,1080)

def handle_events():
    global running

    events = get_events()
    for event in events:
        if event.type == SDL_QUIT:
            running = False
        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            running = False
        else:
            shadow_man.handle_event(event)

open_canvas(1920, 1080)

def reset_world():

    global running
    global shadow_man
    running = True

    global world # 모든 게임 객체를 담는 리스트
    world = [] # 빈 월드

    # 객체들을 생성
    bg = background()
    world.append(bg)

    shadow_man = ShadowMan()
    world.append(shadow_man)

    # sword = short_sword()
    # world.append(sword)



reset_world()


def update_world():
    for game_object in world:
        game_object.update()


def render_world():
    clear_canvas()
    for game_object in world:
        game_object.draw()
    update_canvas()

while running:
    handle_events()
    update_world() # 객체들의 상호작용을 시뮬레이션, 계산
    render_world() # 객체들의 모습을 그린다
    delay(0.1)

close_canvas()