from pico2d import *
import game_framework
import play_mode
import game_data

# 이미지 리소스
monk_image = None
peasant_image = None
font = None
button_sound = None

# 선택 상태 변수
step = 0  # 0: 1P 선택중, 1: 2P 선택중
cursor = 0  # 0: Monk, 1: Peasant


def init():
    global monk_image, peasant_image, font, step, cursor,image
    image = load_image('backGround.png')  # 배경 이미지 (원하는걸로 교체 가능)
    # 캐릭터 초상화 로드 (없으면 임시로 기존 스프라이트 사용)
    monk_image = load_image('Monk_idle.png')
    peasant_image = load_image('Peasant_idle.png')
    font = load_font('ENCR10B.TTF', 50)

    step = 0  # 1P부터 선택 시작
    cursor = 0  # Monk에 커서


def finish():
    global monk_image, peasant_image, font
    del monk_image
    del peasant_image
    del font


def update():
    pass


def draw():
    clear_canvas()
    image.draw(960, 540, 1920, 1080)

    # 안내 문구
    if step == 0:
        font.draw(600, 800, f"[ 1P SELECT CHARACTER ]", (255, 0, 0))
    else:
        mode_str = "AI" if game_data.game_mode == 'AI' else "2P"
        font.draw(600, 800, f"[ {mode_str} SELECT CHARACTER ]", (0, 0, 255))

    # 캐릭터 이미지 그리기 (왼쪽: Monk, 오른쪽: Peasant)
    # 선택된 캐릭터 강조 표시

    # Monk (왼쪽)
    if cursor == 0:
        draw_rectangle(480, 380, 720, 620)  # 선택 테두리
    monk_image.clip_draw(0, 0, 96, 96, 600, 500, 200, 200)
    font.draw(530, 350, "MONK", (255, 255, 255))

    # Peasant (오른쪽)
    if cursor == 1:
        draw_rectangle(1080, 380, 1320, 620)  # 선택 테두리
    peasant_image.clip_draw(0, 0, 96, 96, 1200, 500, 200, 200)
    font.draw(1100, 350, "PEASANT", (255, 255, 255))

    update_canvas()


def handle_events():
    global cursor, step
    global button_sound
    events = get_events()
    for event in events:
        if event.type == SDL_QUIT:
            game_framework.quit()
        elif event.type == SDL_KEYDOWN:
            if event.key == SDLK_ESCAPE:
                import title_mode
                game_framework.change_mode(title_mode)

            # 좌우 이동
            elif event.key == SDLK_LEFT:
                cursor = 0
                button_sound = load_wav('Sound/button.wav')
                button_sound.set_volume(50)
                button_sound.play()
            elif event.key == SDLK_RIGHT:
                cursor = 1
                button_sound = load_wav('Sound/button.wav')
                button_sound.set_volume(50)
                button_sound.play()

            # 선택 (스페이스바)
            elif event.key == SDLK_SPACE:
                selected_char = 'Monk' if cursor == 0 else 'Peasant'

                if step == 0:  # 1P 선택 완료
                    game_data.p1_char = selected_char
                    step = 1  # 2P 선택 단계로 넘어감
                    cursor = 0  # 커서 초기화
                else:  # 2P 선택 완료
                    game_data.p2_char = selected_char
                    # 모든 선택 완료 -> 게임 시작!
                    game_framework.change_mode(play_mode)