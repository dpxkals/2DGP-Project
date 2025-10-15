from pico2d import *
import random

# Game object class here
# 1. 객체의 도출 - 추상화
# 2. 속성을 도출 - 추상화
# 3. 행위를 도출
# 4. 클래스를 제작

class ShadowMan:
    def __init__(self):
        self.x, self.y = 200, 200
        self.is_walking = False
        self.idle_image = load_image('그림자검객_idlePNG.png')
        self.walk_image = load_image('그림자검객_walk.png')
        self.idle_sprite_size = (340, 360)
        self.walk_sprite_size = (227, 260)
        self.frame_idle = 3
        self.frame_walk = 5
        self.current_image = self.idle_image
        self.current_sprite_size = self.idle_sprite_size
        self.frame = self.frame_idle
        self.current_frame = 0

    def set_walking(self, walking):
        pass

    def update(self):
        pass

    def draw(self):
        sprite_w, sprite_h = self.current_sprite_size
        self.current_image.clip_draw(
            self.current_frame * sprite_w, 0, sprite_w, sprite_h,
            self.x, self.y, 400, 400
        )

def handle_events():
    global running
    events = get_events()
    for event in events:
        if event.type == SDL_QUIT:
            running = False
        elif event.type == SDL_KEYDOWN:
            if event.key == SDLK_ESCAPE:
                running = False

open_canvas(1920, 1080)

def reset_world():

    global running
    running = True

    global world # 모든 게임 객체를 담는 리스트
    world = [] # 빈 월드

    # 객체들을 생성
    shadow_man = ShadowMan()
    world.append(shadow_man)

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
    delay(0.05)

close_canvas()