from pico2d import load_image, get_time, load_font, draw_rectangle, clamp
from sdl2 import SDL_KEYDOWN, SDL_KEYUP, SDLK_SPACE, SDLK_RIGHT, SDLK_LEFT, SDLK_g


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

def g_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_g

# 점프 키다운

def space_down(e): # e is space down ?
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_SPACE

class Appearance:
    images = None
    def load_images(self):
        if Appearance.images is None:
            Appearance.images = {}
            Appearance.images['appearance'] = [load_image(f"./player_1/appearance ({i}).png") for i in range(1, 15)]

    def __init__(self, player1):
        self.frame = 0.0
        self.player1 = player1
        self.load_images()
        self.animation_finished = False

        # player Action Speed
        self.TIME_PER_ACTION = 1.0
        self.ACTION_PER_TIME = 1.0 / self.TIME_PER_ACTION
        self.FRAMES_PER_ACTION = 8

    def enter(self, e):
        self.frame = 0.0
        self.animation_finished = False
        self.player1.dir = 0

    def exit(self, e):
        pass

    def do(self):
        if self.animation_finished:
            return

        self.frame += self.FRAMES_PER_ACTION * self.ACTION_PER_TIME * game_framework.frame_time

        if self.frame >= 14:
            self.animation_finished = True
            self.player1.state_machine.handle_state_event(('TIMEOUT', None))

    def draw(self):
        frame_idx = int(self.frame) % 14
        img = Appearance.images['appearance'][frame_idx]
        img.draw(self.player1.x, self.player1.y)  # 뒤집기 없어도 됨
        draw_rectangle(*self.get_bb())

    def get_bb(self):
        return self.player1.x - 20, self.player1.y - 40, self.player1.x + 20, self.player1.y + 40



class Idle:
    images = None

    def load_images(self):
        if Idle.images is None:
            Idle.images = {}
            Idle.images['idle'] = [load_image(f"./player_1/idle ({i}).png") for i in range(1, 3)]

    def __init__(self, player1):
        self.frame = 0.0
        self.player1 = player1
        self.load_images()

        self.TIME_PER_ACTION = 1.0
        self.ACTION_PER_TIME = 1.0 / self.TIME_PER_ACTION
        self.FRAMES_PER_ACTION = 2

    def enter(self, e):
        self.frame = 0.0
        self.player1.dir = 0

    def exit(self, e):
        pass

    def do(self):
        self.frame += self.FRAMES_PER_ACTION * self.ACTION_PER_TIME * game_framework.frame_time

    def draw(self):
        frame_idx = int(self.frame) % 2
        img = Idle.images['idle'][frame_idx]

        if self.player1.face_dir == 1:
            img.draw(self.player1.x, self.player1.y)
        else:
            img.composite_draw(0, 'h', self.player1.x, self.player1.y)
        draw_rectangle(*self.get_bb())

    def get_bb(self):
        return self.player1.x - 20, self.player1.y - 40, self.player1.x + 20, self.player1.y + 40



class Run:
    images = None
    def load_images(self):
        if Run.images is None:
            Run.images = {}
            Run.images['run'] = [load_image(f"./player_1/run ({i}).png") for i in range(1, 6)]

    def __init__(self, player1):
        self.frame = 0.0
        self.player1 = player1
        self.load_images()

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
        self.frame = 0.0
        if right_down(e):
            self.player1.dir = 1
            self.player1.face_dir = 1
        elif left_down(e):
            self.player1.dir = -1
            self.player1.face_dir = -1
        elif right_up(e) or left_up(e):
            self.player1.dir = 0

        self.idle_delay = 0

    def exit(self, e):
        pass

    def do(self):
        self.frame += self.FRAMES_PER_ACTION * self.ACTION_PER_TIME * game_framework.frame_time
        self.player1.x += self.player1.dir * self.RUN_SPEED_PPS * game_framework.frame_time

        # ★ dir = 0이면 강제 IDLE (버그 방지)
        if self.player1.dir == 0:
            self.player1.state_machine.handle_state_event(('TIMEOUT', None))
            if self.idle_delay > 0.1:  # 0.1초 대기
                self.player1.state_machine.handle_state_event(('TIMEOUT', None))
        else:
            self.idle_delay = 0

        self.player1.x = clamp(10, self.player1.x, 800 - 10)

    def draw(self):
        frame_idx = int(self.frame) % 5
        img = Run.images['run'][frame_idx]

        if self.player1.face_dir == 1:
            img.draw(self.player1.x, self.player1.y)
        else:
            img.composite_draw(0, 'h', self.player1.x, self.player1.y)
        draw_rectangle(*self.get_bb())

    def get_bb(self):
        return self.player1.x - 20, self.player1.y - 40, self.player1.x + 20, self.player1.y + 40

class Attack:
    images = None

    def load_images(self):
        if Attack.images is None:
            Attack.images = {}
            Attack.images['attack'] = [load_image(f"./player_1/attack ({i}).png") for i in range(1, 10)]

    def __init__(self, player1):
        self.frame = 0.0
        self.player1 = player1
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
        self.FRAMES_PER_ACTION = 9

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
        if self.frame >= 8:  # 0~8까지 9프레임
            self.animation_finished = True
            self.player1.state_machine.handle_state_event(('TIMEOUT', None))

        self.player1.x = clamp(10, self.player1.x, 800 - 10)

    def draw(self):
        frame_idx = int(self.frame) % 9
        img = Attack.images['attack'][frame_idx]
        # ★ 원본 이미지 크기 자르기 (캐릭터 크기 고정!)
        if self.player1.face_dir == 1:
            img.draw(self.player1.x, self.player1.y + 5)
        else:
            img.composite_draw(0, 'h', self.player1.x, self.player1.y + 5)  # ★ 뒤집기만!!
        draw_rectangle(*self.get_bb())

    def get_bb(self):
        return self.player1.x - 20, self.player1.y - 40, self.player1.x + 20, self.player1.y + 40


class Jump:
    images = None

    def load_images(self):
        if Jump.images is None:
            Jump.images = {}
            Jump.images['jump'] = [load_image(f"./player_1/jump ({i}).png") for i in range(1, 8)]

    def __init__(self, player1):
        self.frame = 0.0
        self.player1 = player1
        self.load_images()
        self.animation_finished = False

        #점프 파워 설정
        self.PIXEL_PER_METER = 10.0 / 0.3  # 33.33 pixel = 1m
        self.JUMP_POWER = 16.0  # 수직 초속 (m/s)
        self.HORIZONTAL_BOOST = 6.0  # 수평 초속 (m/s)
        self.GRAVITY = 45.0  # 중력 (조금 세게 → 빠른 착지)

        # player의 Run Speed 계산
        self.PIXEL_PER_METER = (10.0 / 0.3)  # 10 pixel 30 cm

        self.TIME_PER_ACTION = 1.0
        self.ACTION_PER_TIME = 1.0 / self.TIME_PER_ACTION
        self.FRAMES_PER_ACTION = 7

        self.xv = 0.0  # m/s
        self.yv = 0.0  # m/s
        self.ground_y = 50  # 착지 y 좌표

    def enter(self, e):
        self.frame = 0.0  # ★ 프레임 초기화!
        self.animation_finished = False

        # 현재 위치가 땅 위인지 확인 (착지 후 재점프 방지)
        if self.player1.y <= self.ground_y + 5:  # 약간의 여유
            self.player1.y = self.ground_y

            # 수직 속도
            self.yv = self.JUMP_POWER * self.PIXEL_PER_METER

            # 수평 속도 (현재 방향 유지)
            run_speed = 20.0  # Run 클래스와 동일하게
            pps = (run_speed * 1000 / 60 / 60) * self.PIXEL_PER_METER
            if self.player1.dir != 0:
                self.xv = pps * self.player1.dir  # 달리는 중이면 더 빠르게
            else:
                self.xv = self.HORIZONTAL_BOOST * self.PIXEL_PER_METER * self.player1.face_dir

    def exit(self, e):
        pass

    def do(self):
        self.frame += self.FRAMES_PER_ACTION * self.ACTION_PER_TIME * game_framework.frame_time

        # 위치 업데이트
        self.player1.x += self.xv * game_framework.frame_time
        self.player1.y += self.yv * game_framework.frame_time
        self.yv -= self.GRAVITY * self.PIXEL_PER_METER * game_framework.frame_time

        # 바닥 충돌 처리
        if self.player1.y <= self.ground_y:
            self.player1.y = self.ground_y
            self.yv = 0  # 속도 완전 초기화
            self.xv *= 0.7  # 착지 시 관성 감소 (미끄러짐 효과)

            # 착지 후 바로 Idle로 강제 전이
            self.player1.state_machine.handle_state_event(('TIMEOUT', None))

        # 애니메이션 끝나면 강제 종료
        if self.frame >= 6.5:
            self.player1.state_machine.handle_state_event(('TIMEOUT', None))

        # 화면 경계
        self.player1.x = clamp(10, self.player1.x, 800 - 10)

    def draw(self):
        frame_idx = int(self.frame) % 7
        img = Jump.images['jump'][frame_idx]
        # ★ 원본 이미지 크기 자르기 (캐릭터 크기 고정!)
        if self.player1.face_dir == 1:
            img.draw(self.player1.x, self.player1.y)
        else:
            img.composite_draw(0, 'h', self.player1.x, self.player1.y)  # ★ 뒤집기만!!
        draw_rectangle(*self.get_bb())

    def get_bb(self):
        return self.player1.x - 20, self.player1.y - 40, self.player1.x + 20, self.player1.y + 40

class Player1:
    def __init__(self):
        self.x, self.y = 400, 50
        self.face_dir = 1
        self.dir = 0

        # 플레이어 상태 관리 (먼저 생성해서 이미지 로드)
        self.Appearance = Appearance(self)
        self.IDLE = Idle(self)
        self.RUN = Run(self)
        self.ATTACK = Attack(self)
        self.JUMP = Jump(self)

        self.state_machine = StateMachine(
            self.Appearance,
            {
                self.Appearance : {time_out: self.IDLE},
                self.IDLE : {space_down: self.JUMP,
                             right_down: self.RUN, left_down: self.RUN,
                             g_down: self.ATTACK},
                self.RUN : {space_down: self.JUMP,
                            right_up: self.IDLE, left_up: self.IDLE, right_down: self.RUN, left_down: self.RUN,
                            g_down: self.ATTACK},
                self.ATTACK : {time_out: self.IDLE},
                self.JUMP : {time_out: self.IDLE}
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
