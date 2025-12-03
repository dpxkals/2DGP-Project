from pico2d import *
import game_framework
import select_mode  # 캐릭터 선택 모드로 이동하기 위해 임포트
import game_data  # 선택한 모드를 저장하기 위해 임포트

image = None
font = None
bgm = None
button_sound = None
select_mode_sound = None

menu_selection = 0  # 0: 1 vs 1,  1: AI Mode


def init():
    global image, font
    image = load_image('title.png')  # 배경 이미지 (원하는걸로 교체 가능)
    font = load_font('ENCR10B.TTF', 40)

    # bgm
    global bgm
    bgm = load_wav('Sound/play_mode.wav')
    bgm.set_volume(100)
    bgm.play()


def finish():
    global image, font
    del image
    del font


def update():
    pass


def draw():
    clear_canvas()
    image.draw(960, 540, 1920, 1080)

    # 메뉴 텍스트 그리기
    # 선택된 항목은 빨간색, 아닌건 검은색(혹은 흰색)
    if menu_selection == 0:
        font.draw(800, 400, '> 1 vs 1 (PVP) <', (255, 0, 0))
        font.draw(850, 300, '  AI Mode  ', (255, 255, 255))
    else:
        font.draw(800, 400, '  1 vs 1 (PVP)  ', (255, 255, 255))
        font.draw(850, 300, '> AI Mode <', (255, 0, 0))

    update_canvas()


def handle_events():
    global menu_selection
    global button_sound
    global select_mode_sound
    events = get_events()
    for event in events:
        if event.type == SDL_QUIT:
            game_framework.quit()
        elif event.type == SDL_KEYDOWN:
            if event.key == SDLK_ESCAPE:
                game_framework.quit()

            # 메뉴 이동 (위/아래)
            elif event.key == SDLK_UP:
                menu_selection = 0
                button_sound = load_wav('Sound/button.wav')
                button_sound.set_volume(50)
                button_sound.play()
            elif event.key == SDLK_DOWN:
                menu_selection = 1
                button_sound = load_wav('Sound/button.wav')
                button_sound.set_volume(50)
                button_sound.play()

            # 선택 확정 (스페이스바)
            elif event.key == SDLK_SPACE:
                if menu_selection == 0:
                    game_data.game_mode = 'PVP'
                    select_mode_sound = load_wav('Sound/selectmode.wav')
                    select_mode_sound.set_volume(50)
                    select_mode_sound.play()
                else:
                    game_data.game_mode = 'AI'
                    select_mode_sound = load_wav('Sound/selectmode.wav')
                    select_mode_sound.set_volume(50)
                    select_mode_sound.play()

                # 캐릭터 선택 모드로 이동!
                game_framework.change_mode(select_mode)