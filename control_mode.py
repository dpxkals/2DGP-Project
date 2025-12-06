from pico2d import *
import game_framework
import title_mode

image = None
image_p1 = None
image_p2 = None

def init():
    global image, image_p1, image_p2

    image = load_image('backGround.png')
    image_p1 = load_image('p1.png')
    image_p2 = load_image('p2.png')

def finish():
    global image, image_p1, image_p2
    del image, image_p1, image_p2

def update():
    pass

def draw():
    clear_canvas()
    image.draw(960, 540, 1920, 1080)

    image_p1.draw(500, 500)
    image_p2.draw(1320, 500)
    update_canvas()

def handle_events():
    events = get_events()
    for event in events:
        if event.type == SDL_QUIT:
            game_framework.quit()
        elif event.type == SDL_KEYDOWN:
            if event.key == SDLK_ESCAPE:
                import title_mode
                game_framework.change_mode(title_mode)

def pause(): pass
def resume(): pass
