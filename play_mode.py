import random
from pico2d import *

import game_framework
import game_world
import title_mode

from background import Background
from stageBlock import StageBlock
from player1 import Player1

player1 = None

def handle_events():
    event_list = get_events()
    for event in event_list:
        if event.type == SDL_QUIT:
            game_framework.quit()
        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            game_framework.change_mode(title_mode)
        else:
            player1.handle_event(event)

def init():
    # 스테이지 배경
    # background = Background()
    # game_world.add_object(background, 0)

    # 스테이지 블록들
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

    # 플레이어 1 - 왼쪽에서 시작
    global player1

    player1 = Player1()
    game_world.add_object(player1, 1)  # Player1이 아니라 player1 인스턴스를 추가


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
