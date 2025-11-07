from pico2d import load_image, get_time, load_font, draw_rectangle, clamp
from sdl2 import SDL_KEYDOWN, SDL_KEYUP, SDLK_3, SDLK_RIGHT, SDLK_LEFT, SDLK_0

import game_world
import game_framework
from state_machine import StateMachine



time_out = lambda e: e[0] == 'TIMEOUT'

def right_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_RIGHT


def right_up(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYUP and e[1].key == SDLK_RIGHT


def left_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_LEFT


def left_up(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYUP and e[1].key == SDLK_LEFT

# 공격 키다운
def zero_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_0

# 점프 키다운

def three_down(e): # e is space down ?
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_3


class Appearance:
    images = None
    def load_images(self):
        if Appearance.images is None:
            Appearance.images = {}
            Appearance.images['appearance'] = [load_image(f"./player_2/appearance ({i}).png") for i in range(1, 15)]

    def __init__(self, player2):
        self.frame = 0.0
        self.player2 = player2
        self.load_images()
        self.animation_finished = False

        # player Action Speed
        self.TIME_PER_ACTION = 1.0
        self.ACTION_PER_TIME = 1.0 / self.TIME_PER_ACTION
        self.FRAMES_PER_ACTION = 8

    def enter(self, e):
        self.frame = 0.0
        self.animation_finished = False
        self.player2.dir = 0

    def exit(self, e):
        pass

    def do(self):
        if self.animation_finished:
            return

        self.frame += self.FRAMES_PER_ACTION * self.ACTION_PER_TIME * game_framework.frame_time

        if self.frame >= 14:
            self.animation_finished = True
            self.player2.state_machine.handle_state_event(('TIMEOUT', None))

    def draw(self):
        frame_idx = int(self.frame) % 14
        img = Appearance.images['appearance'][frame_idx]
        img.composite_draw(0, 'h', self.player2.x, self.player2.y)  # 뒤집기 없어도 됨
        draw_rectangle(*self.get_bb())

    def get_bb(self):
        return self.player2.x - 20, self.player2.y - 40, self.player2.x + 20, self.player2.y + 40


class Idle:
    images = None

    def load_images(self):
        if Idle.images is None:
            Idle.images = {}
            Idle.images['idle'] = [load_image(f"./player_2/idle ({i}).png") for i in range(1, 3)]

    def __init__(self, player2):
        self.frame = 0.0
        self.player2 = player2
        self.load_images()

        self.TIME_PER_ACTION = 1.0
        self.ACTION_PER_TIME = 1.0 / self.TIME_PER_ACTION
        self.FRAMES_PER_ACTION = 2

    def enter(self, e):
        self.frame = 0.0
        self.player2.dir = 0

    def exit(self, e):
        pass

    def do(self):
        self.frame += self.FRAMES_PER_ACTION * self.ACTION_PER_TIME * game_framework.frame_time

    def draw(self):
        frame_idx = int(self.frame) % 2
        img = Idle.images['idle'][frame_idx]

        if self.player2.face_dir == 1:
            img.draw(self.player2.x, self.player2.y)
        else:
            img.composite_draw(0, 'h', self.player2.x, self.player2.y)
        draw_rectangle(*self.get_bb())

    def get_bb(self):
        return self.player2.x - 20, self.player2.y - 40, self.player2.x + 20, self.player2.y + 40


class Attack:
    images = None

    def load_images(self):
        if Attack.images is None:
            Attack.images = {}
            Attack.images['attack'] = [load_image(f"./player_2/attack ({i}).png") for i in range(1, 9)]

    def __init__(self, player2):
        self.frame = 0.0
        self.player2 = player2
        self.load_images()
        self.animation_finished = False

        # player의 Run Speed 계산
        self.PIXEL_PER_METER = (10.0 / 0.3)  # 10 pixel 30 cm
        self.RUN_SPEED_KMPH = 20.0  # Km / Hour
        self.RUN_SPEED_MPM = (self.RUN_SPEED_KMPH * 1000.0 / 60.0)
        self.RUN_SPEED_MPS = (self.RUN_SPEED_MPM / 60.0)
        self.RUN_SPEED_PPS = (self.RUN_SPEED_MPS * self.PIXEL_PER_METER)

        self.TIME_PER_ACTION = 0.5
        self.ACTION_PER_TIME = 1.0 / self.TIME_PER_ACTION
        self.FRAMES_PER_ACTION = 8

    def enter(self, e):
        self.frame = 0.0  # ★ 프레임 초기화!
        self.animation_finished = False

    def exit(self, e):
        pass

    def do(self):
        if self.animation_finished:
            return

        # ★ self.frame만 증가! (player1.frame는 건드리지 말기)
        self.frame += self.FRAMES_PER_ACTION * self.ACTION_PER_TIME * game_framework.frame_time

        # 마지막 프레임 넘어가면 바로 Idle로 전이
        if self.frame >= 7:  # 0~7까지 8프레임
            self.animation_finished = True
            self.player2.state_machine.handle_state_event(('TIMEOUT', None))

        self.player2.x = clamp(10, self.player2.x, 800 - 10)

    def draw(self):
        frame_idx = int(self.frame) % 8
        img = Attack.images['attack'][frame_idx]
        # ★ 원본 이미지 크기 자르기 (캐릭터 크기 고정!)
        if self.player2.face_dir == 1:
            img.draw(self.player2.x, self.player2.y)
        else:
            img.composite_draw(0, 'h', self.player2.x, self.player2.y)
        draw_rectangle(*self.get_bb())

    def get_bb(self):
        return self.player2.x - 20, self.player2.y - 40, self.player2.x + 20, self.player2.y + 40



class Player2:
    def __init__(self):
        self.x, self.y = 700, 50
        self.face_dir = -1
        self.dir = 0

        # 플레이어 상태 관리 (먼저 생성해서 이미지 로드)
        self.Appearance = Appearance(self)
        self.IDLE = Idle(self)
        # self.RUN = Run(self)
        self.ATTACK = Attack(self)
        # self.JUMP = Jump(self)

        self.state_machine = StateMachine(
            self.Appearance,
            {
                self.Appearance : {time_out: self.IDLE},
                self.IDLE : { zero_down: self.ATTACK},#space_down: self.JUMP,right_down: self.RUN, left_down: self.RUN,g_down: self.ATTACK
                # self.RUN : {space_down: self.JUMP,
                #             right_up: self.IDLE, left_up: self.IDLE, right_down: self.RUN, left_down: self.RUN,
                #             g_down: self.ATTACK},
                self.ATTACK : {time_out: self.IDLE}
                # self.JUMP : {time_out: self.IDLE}
            }
        )

    def update(self):
        self.state_machine.update()

    def handle_event(self, event):
        self.state_machine.handle_state_event(('INPUT', event))

    def draw(self):
        self.state_machine.draw()
        draw_rectangle(*self.get_bb())

    def get_bb(self):
        return self.x - 20, self.y - 40, self.x + 20, self.y + 40

    def handle_collision(self, group, other):
        pass
