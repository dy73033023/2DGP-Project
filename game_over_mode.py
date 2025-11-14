from pico2d import *
import time
import game_framework
import title_mode
import game_world

image = None
font = None
font_small = None

def init():
    global image, font, font_small
    image = load_image('game_over_background.png')
    # 폰트 파일명은 프로젝트에 있는 것을 사용
    font = load_font('megaman.ttf', 60)
    font_small = load_font('megaman.ttf', 20)

def finish():
    global font, font_small
    del font
    del font_small

def handle_events():
    event_list = get_events()
    for event in event_list:
        if event.type == SDL_QUIT:
            game_framework.quit()
        elif event.type == SDL_KEYDOWN:
            if event.key == SDLK_ESCAPE:
                game_framework.quit()
            elif event.key == SDLK_SPACE:
                # 타이틀로 돌아감
                game_framework.change_mode(title_mode)

def draw():
    clear_canvas()
    image.draw(400, 300)
    # 결과 가져오기
    result = getattr(game_world, 'game_result', None)
    if result == 'PLAYER1':
        message = 'Player 1 Wins!'
    elif result == 'PLAYER2':
        message = 'Player 2 Wins!'
    else:
        message = '게임 종료'

    # 중앙 정렬 시도 (font.get_width 가 없을 경우 대략 계산)
    try:
        w = font.get_width(message)
    except Exception:
        w = len(message) * 18
    font.draw(180 - w / 2, 320, message, (255, 255, 255))

    # 안내 문구 깜박이기
    if int(time.time() * 2) % 2 == 0:
        small = 'Press SPACE to return to Title'
        try:
            sw = font_small.get_width(small)
        except Exception:
            sw = len(small) * 10
        font_small.draw(275 - sw / 2, 260, small, (255, 255, 255))

    update_canvas()

def update():
    pass