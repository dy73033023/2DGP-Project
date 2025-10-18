import random
from pico2d import *

import game_framework
import game_world

from boy import Boy
from grass import Grass
from ball import Ball
from zombie import Zombie

boy = None

def handle_events():
    event_list = get_events()
    for event in event_list:
        if event.type == SDL_QUIT:
            game_framework.quit()
        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            game_framework.quit()
        else:
            boy.handle_event(event)

def init():
    global boy

    grass = Grass()
    game_world.add_object(grass, 0)
    game_world.add_collision_pair('grass : ball', grass, None)  # 볼과 잔디 사이의 충돌 검사를 위해 빈 쌍 추가

    boy = Boy()
    game_world.add_object(boy, 1)


    zombies = [Zombie() for _ in range(4)]
    game_world.add_objects(zombies, 1)

    global balls
    balls = [Ball(random.randint(100, 1500), 60, 0) for _ in range(30)]
    game_world.add_objects(balls, 1)

    # 소년과 볼 사이에 대한 충돌 검사가 필요하다는 정보를 추가
    game_world.add_collision_pair('boy : ball', boy, None)

    # 소년과 좀비 사이에 대한 충돌 검사가 필요하다는 정보를 추가
    game_world.add_collision_pair('boy : zombie', boy, None)

    for zombie in zombies:
        # 소년과 좀비 사이에 대한 충돌 검사가 필요하다는 정보를 추가
        game_world.add_collision_pair('boy : zombie', None, zombie)
        # 좀비와 볼 사이에 대한 충돌 검사가 필요하다는 정보를 추가
        game_world.add_collision_pair('zombie : ball', zombie, None)

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

