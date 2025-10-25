import random
from pico2d import *

import game_framework
import game_world
import title_mode

from background import Background
from stageBlock import StageBlock
from boy import Boy
from ball import Ball


boy = None

def handle_events():
    event_list = get_events()
    for event in event_list:
        if event.type == SDL_QUIT:
            game_framework.quit()
        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            game_framework.change_mode(title_mode)
        else:
            boy.handle_event(event)

def init():
    # 스테이지 배경
    background = Background()
    game_world.add_object(background, 0)

    # 가로로 10개 배치, 시작 x는 화면 좌측(예: 100), 간격은 32
    start_x, start_y, gap = 16, 16, 32
    stageBlocks = [StageBlock(start_x + i * gap, start_y) for i in range(25)]
    stageBlocks2 = [StageBlock(start_x + 64 + i * gap, start_y + 160) for i in range(5)]
    stageBlocks3 = [StageBlock(start_x + 800 - 64 - i * gap, start_y + 160) for i in range(5)]
    stageBlocks4 = [StageBlock(start_x + 400 - 80 + i * gap, start_y + 320) for i in range(5)]
    game_world.add_objects(stageBlocks, 1)
    game_world.add_objects(stageBlocks2, 1)
    game_world.add_objects(stageBlocks3, 1)
    game_world.add_objects(stageBlocks4, 1)

    global boy

    boy = Boy()
    game_world.add_object(boy, 1)


    global balls
    balls = [Ball(random.randint(100, 1500), 60, 0) for _ in range(30)]
    game_world.add_objects(balls, 1)

    # 소년과 볼 사이에 대한 충돌 검사가 필요하다는 정보를 추가
    game_world.add_collision_pair('boy : ball', boy, None)


    for ball in balls:
        game_world.add_collision_pair('boy : ball', None, ball)



def update():
    game_world.update()
    game_world.handle_collision()


def draw():
    clear_canvas()
    game_world.render()
    update_canvas()


def finish():
    game_world.clear()

def pause(): pass
def resume(): pass
