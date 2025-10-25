from pico2d import *
import game_framework
import play_mode

image = None
font = None
font_small = None

def init():
    global image, font, font_small
    image = load_image('title.png')
    font = load_font('megaman.ttf', 60)
    font_small = load_font('megaman.ttf', 30)

def finish():
    global image, font, font_small
    del image
    del font, font_small

def handle_events():
    event_list = get_events()
    for event in event_list:
        if event.type == SDL_QUIT:
            game_framework.quit()
        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            game_framework.quit()
        elif event.type == SDL_KEYDOWN and event.key == SDLK_SPACE:
            game_framework.change_mode(play_mode)

def draw():
    clear_canvas()
    image.draw(400,300)
    # 선택한 폰트로 텍스트 출력
    font.draw(125, 350, 'DROP  FIGHT', (255, 255, 255))
    font_small.draw(100, 100, 'Press Space to Start', (255, 255, 255))
    update_canvas()

def update():
    # 렌더링은 draw()에서 처리하므로 update는 비워둡니다
    pass

def pause():
    pass

def resume():
    pass
