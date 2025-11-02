from pico2d import *
import game_framework
import title_mode

image = None
logo_start_time = 0

def init():
    global image, logo_start_time
    image = load_image('tuk_credit.png')
    logo_start_time = get_time()

def finish():
    global image
    del image

def update():
    if get_time() - logo_start_time > 2.0:
        game_framework.change_mode(title_mode)


def draw():
    clear_canvas()
    image.draw(960, 540, 1920, 1080)
    image.draw(960, 540,)
    update_canvas()

def handle_events():
    event_list = get_events()
    # do nothing

def pause(): pass
def resume(): pass
