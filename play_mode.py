import random
from pico2d import *

import game_framework
import game_world
import title_mode

from background import Background
from stageBlock import StageBlock
from obstacle import Obstacle
from hp import Hp
from player1 import Player1
from player2 import Player2

player1 = player2 = None
stageBlocks = stageBlocks2 = stageBlocks3 = stageBlocks4 = None
obstacles = None
hp_player1 = hp_player2 = None  # 리스트 아님! game_world에 들어간 객체들 자체


def handle_events():
    event_list = get_events()
    for event in event_list:
        if event.type == SDL_QUIT:
            game_framework.quit()
        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            game_framework.change_mode(title_mode)
        else:
            player1.handle_event(event)
            player2.handle_event(event)

def init():
    # 스테이지 배경
    # background = Background()
    # game_world.add_object(background, 0)

    # 스테이지 블록들
    # 가로로 10개 배치, 시작 x는 화면 좌측(예: 100), 간격은 32
    global stageBlocks, stageBlocks2, stageBlocks3, stageBlocks4
    start_x, start_y, gap = 16, 16, 32
    blocks = [
        [StageBlock(start_x + i * gap, start_y) for i in range(25)],
        [StageBlock(start_x + 64 + i * gap, start_y + 160) for i in range(5)],
        [StageBlock(start_x + 800 - 64 - i * gap, start_y + 160) for i in range(5)],
        [StageBlock(start_x + 400 - 80 + i * gap, start_y + 320) for i in range(5)]
    ]
    for b in blocks:
        game_world.add_objects(b, 1)

    # 떨어지는 장애물들
    # 시작 위치 - x는 랜덤 y 600 이상
    global obstacles
    obstacles = [Obstacle(random.randint(0, 800),random.randint(600, 1200)) for _ in range(40)]
    game_world.add_objects(obstacles, 1)

   # ------------------ 플레이어 관련 ------------------

    # 플레이어 1 - 왼쪽에서 시작
    global player1
    player1 = Player1()
    game_world.add_object(player1, 1)

    # 플레이어 2 - 오른쪽에서 시작
    global player2
    player2 = Player2()
    game_world.add_object(player2, 1)

    # ---------- 체력 UI (플레이어를 따라다님) ----------
    global hp_player1, hp_player2

    # Player1: 왼쪽부터 (index 0~4)
    hp_player1 = [Hp(player1.x - 32 + i * 15, player1.y + 50) for i in range(5)]
    game_world.add_objects(hp_player1, 3)

    # Player2: 오른쪽부터 (index 0~4)
    hp_player2 = [Hp(player2.x + 32 - i * 15, player2.y + 50) for i in range(5)]
    game_world.add_objects(hp_player2, 3)


def update():
    game_world.update()
    game_world.handle_collision()

    # ★ HP 실시간 따라다니기
    for i, hp in enumerate(hp_player1):
        hp.x = player1.x - 32 + i * 15
        hp.y = player1.y + 30
    for i, hp in enumerate(hp_player2):
        hp.x = player2.x + 32 - i * 15
        hp.y = player2.y + 30


def draw():
    clear_canvas()
    game_world.render()
    update_canvas()


def finish():
    game_world.clear()


def pause(): pass
def resume(): pass
