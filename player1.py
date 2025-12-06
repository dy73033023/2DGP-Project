from pico2d import load_image, clamp, load_font
from sdl2 import SDL_KEYDOWN, SDL_KEYUP, SDLK_SPACE, SDLK_g, SDLK_d, SDLK_a

import game_world
import game_framework
from state_machine import StateMachine
from stageBlock import StageBlock

# 공통 상수: 단위/속도 계산을 파일 단위로 통일하여 중복 제거
PIXEL_PER_METER = 10.0 / 0.3
RUN_SPEED_KMPH = 20.0
RUN_SPEED_PPS = (RUN_SPEED_KMPH * 1000.0 / 3600.0) * PIXEL_PER_METER

time_out = lambda e: e[0] == 'TIMEOUT'
run_off = lambda e: e[0] == 'RUN_OFF'
fall_start = lambda e: e[0] == 'FALL_START'

def right_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_d


def right_up(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYUP and e[1].key == SDLK_d


def left_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_a


def left_up(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYUP and e[1].key == SDLK_a

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

    def get_bb(self):
        pass



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
        self.player1.obstacle_hit = False

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

    def get_bb(self):
        if self.player1.face_dir == 1:
            return self.player1.x - 5, self.player1.y - 15, self.player1.x + 20, self.player1.y + 15
        else:
            return self.player1.x - 20, self.player1.y - 15, self.player1.x + 5, self.player1.y + 15

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

        # 모듈 상수를 재사용
        self.RUN_SPEED_PPS = RUN_SPEED_PPS

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
        self.player1.obstacle_hit = False

    def exit(self, e):
        pass

    def do(self):
        self.frame += self.FRAMES_PER_ACTION * self.ACTION_PER_TIME * game_framework.frame_time
        self.player1.x += self.player1.dir * self.RUN_SPEED_PPS * game_framework.frame_time

        # dir이 0이 아니면 마지막 이동 방향 저장 및 idle_delay 리셋
        if self.player1.dir != 0:
            self.player1.last_dir = self.player1.dir
            self.idle_delay = 0
        else:
            # dir == 0이면 일정 시간 후에 TIMEOUT 전이 (중복 호출 제거)
            self.idle_delay += game_framework.frame_time
            if self.idle_delay > 0.1:
                self.player1.state_machine.handle_state_event(('TIMEOUT', None))

        self.player1.x = clamp(10, self.player1.x, 800 - 10)

    def draw(self):
        frame_idx = int(self.frame) % 5
        img = Run.images['run'][frame_idx]

        if self.player1.face_dir == 1:
            img.draw(self.player1.x, self.player1.y)
        else:
            img.composite_draw(0, 'h', self.player1.x, self.player1.y)

    def get_bb(self):
        if self.player1.face_dir == 1:
            return self.player1.x - 5, self.player1.y - 15, self.player1.x + 20, self.player1.y + 15
        else:
            return self.player1.x - 20, self.player1.y - 15, self.player1.x + 5, self.player1.y + 15

class Attack:
    images = None

    def load_images(self):
        if Attack.images is None:
            Attack.images = {}
            Attack.images['attack'] = [load_image(f"./player_1/attack ({i}).png") for i in range(1, 9)]

    def __init__(self, player1):
        self.frame = 0.0
        self.player1 = player1
        self.load_images()
        self.animation_finished = False

        # 중복된 속도 계산 제거 (사용되지 않음)
        self.TIME_PER_ACTION = 0.5
        self.ACTION_PER_TIME = 1.0 / self.TIME_PER_ACTION
        self.FRAMES_PER_ACTION = 8

    def enter(self, e):
        self.frame = 0.0  # ★ 프레임 초기화!
        self.animation_finished = False
        self.player1.attack_hit = False
        self.player1.obstacle_hit = False
        if hasattr(self.player1, 'attack_target'):
            game_world.update_collision_pair('sword:player2', self.player1, self.player1.attack_target)

    def exit(self, e):
        game_world.update_collision_pair('sword:player2', None, None)

    def do(self):
        if self.animation_finished:
            return

        # self.frame만 증가! (player1.frame는 건드리지 말기)
        self.frame += self.FRAMES_PER_ACTION * self.ACTION_PER_TIME * game_framework.frame_time

        # 마지막 프레임 넘어가면 바로 Idle로 전이
        if self.frame >= 7:  # 0~7까지 8프레임
            self.animation_finished = True
            self.player1.state_machine.handle_state_event(('TIMEOUT', None))

        self.player1.x = clamp(10, self.player1.x, 800 - 10)


    def draw(self):
        frame_idx = int(self.frame) % 8
        img = Attack.images['attack'][frame_idx]
        # 원본 이미지 크기 자르기 (캐릭터 크기 고정!)
        if self.player1.face_dir == 1:
            img.draw(self.player1.x, self.player1.y)
        else:
            img.composite_draw(0, 'h', self.player1.x, self.player1.y)  # ★ 뒤집기만!!

    def get_bb(self):
        if self.player1.face_dir == 1:
            return self.player1.x - 25, self.player1.y - 15, self.player1.x + 5, self.player1.y + 15
        else:
            return self.player1.x - 5, self.player1.y - 15, self.player1.x + 25, self.player1.y + 15

    # 칼 범위 바운딩 박스
    def get_attack_bb(self):
        # 항상 칼 히트박스 활성 (이전 버전 복구)
        if self.player1.face_dir == 1:
            return self.player1.x + 5, self.player1.y - 15, self.player1.x + 28, self.player1.y + 15
        else:
            return self.player1.x - 28, self.player1.y - 15, self.player1.x - 5, self.player1.y + 15


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
        self.ground_y = 32
        self.on_ground = False

        # 점프 관련 상수는 파일 상수 사용
        self.PIXEL_PER_METER = PIXEL_PER_METER
        self.JUMP_POWER = 18.0
        self.HORIZONTAL_BOOST = 6.0
        self.GRAVITY = 45.0

        self.TIME_PER_ACTION = 1.0
        self.ACTION_PER_TIME = 1.0 / self.TIME_PER_ACTION
        self.FRAMES_PER_ACTION = 7

        self.xv = 0.0  # m/s
        self.yv = 0.0  # m/s
        self.ground_y = 50  # 착지 y 좌표

    def enter(self, e):
        self.frame = 0.0
        self.animation_finished = False
        self.player1.obstacle_hit = False
        if e[0] == 'RUN_OFF':
            self.yv = 0
            self.xv = 0
        else:
            self.player1.y = self.player1.ground_y
            self.yv = self.JUMP_POWER * self.PIXEL_PER_METER

            # 달리기 속도는 파일 상수 사용
            pps = RUN_SPEED_PPS
            if self.player1.dir != 0:
                self.xv = pps * self.player1.dir
            else:
                self.xv = self.HORIZONTAL_BOOST * self.PIXEL_PER_METER * self.player1.face_dir

    def exit(self, e):
        pass

    def do(self):
        self.frame += self.FRAMES_PER_ACTION * self.ACTION_PER_TIME * game_framework.frame_time
        self.player1.x += self.xv * game_framework.frame_time
        self.player1.y += self.yv * game_framework.frame_time
        self.yv -= self.GRAVITY * self.PIXEL_PER_METER * game_framework.frame_time

        # 상승 종료(하강 시작) 즉시 Fall로 전이
        if self.yv <= 0:
            # 수평/수직 속도 전달
            self.player1.air_xv = self.xv
            self.player1.air_yv = self.yv
            self.player1.state_machine.handle_state_event(('FALL_START', None))
            return

        if self.frame >= 6.5:
            self.player1.state_machine.handle_state_event(('TIMEOUT', None))

        self.player1.x = clamp(10, self.player1.x, 800 - 10)

    def draw(self):
        frame_idx = int(self.frame) % 7
        img = Jump.images['jump'][frame_idx]
        # ★ 원본 이미지 크기 자르기 (캐릭터 크기 고정!)
        if self.player1.face_dir == 1:
            img.draw(self.player1.x, self.player1.y)
        else:
            img.composite_draw(0, 'h', self.player1.x, self.player1.y)  # ★ 뒤집기만!!

    def get_bb(self):
        if self.player1.face_dir == 1:
            return self.player1.x - 10, self.player1.y - 17, self.player1.x + 15, self.player1.y + 17
        else:
            return self.player1.x - 15, self.player1.y - 17, self.player1.x + 10, self.player1.y + 17

class Fall:
    images = None

    def load_images(self):
        if Fall.images is None:
            Fall.images = {}
            Fall.images['fall'] = [load_image(f"./player_1/fall ({i}).png") for i in range(1, 5)]

    def __init__(self, player1):
        self.frame = 0.0
        self.player1 = player1
        self.load_images()
        self.animation_finished = False
        self.PIXEL_PER_METER = PIXEL_PER_METER
        self.GRAVITY = 45.0
        self.TIME_PER_ACTION = 1.0
        self.ACTION_PER_TIME = 1.0 / self.TIME_PER_ACTION
        self.FRAMES_PER_ACTION = 4

        self.xv = 0.0
        self.yv = 0.0

    def enter(self, e):
        self.frame = 0.0
        self.animation_finished = False
        if e[0] == 'FALL_START':
            self.xv = getattr(self.player1, 'air_xv', 0.0)
            self.yv = getattr(self.player1, 'air_yv', 0.0)
        elif e[0] == 'RUN_OFF':
            # 달리다가 떨어지는 경우 - 수평 속도 유지
            direction = self.player1.dir if self.player1.dir != 0 else self.player1.last_dir
            self.xv = RUN_SPEED_PPS * direction
            self.yv = 0.0
        else:
            self.xv = 0.0
            self.yv = 0.0

    def exit(self, e):
        pass

    def do(self):
        self.frame += self.FRAMES_PER_ACTION * self.ACTION_PER_TIME * game_framework.frame_time
        self.player1.x += self.xv * game_framework.frame_time
        self.player1.y += self.yv * game_framework.frame_time
        self.yv -= self.GRAVITY * self.PIXEL_PER_METER * game_framework.frame_time

        # 애니메이션 끝나도 낙하는 유지 -> 착지로만 종료, 프레임 루프만 유지
        if self.frame >= self.FRAMES_PER_ACTION - 0.5:
            self.frame = 0.0

        self.player1.x = clamp(10, self.player1.x, 800 - 10)

    def draw(self):
        frame_idx = int(self.frame) % self.FRAMES_PER_ACTION
        img = Fall.images['fall'][frame_idx]

        if self.player1.face_dir == 1:
            img.draw(self.player1.x, self.player1.y)
        else:
            img.composite_draw(0, 'h', self.player1.x, self.player1.y)

    def get_bb(self):
        if self.player1.face_dir == 1:
            return self.player1.x - 10, self.player1.y - 17, self.player1.x + 15, self.player1.y + 17
        else:
            return self.player1.x - 15, self.player1.y - 17, self.player1.x + 10, self.player1.y + 17


class Player1:
    BASE_GROUND_Y = 32
    font = None

    def __init__(self):
        self.x, self.y = 100, 49
        self.face_dir = 1
        self.dir = 0
        self.last_dir = 0
        self.hp = 5
        self.attack_hit = False
        self.obstacle_hit = False
        self.ground_y = 32

        self.APPEARANCE = Appearance(self)
        self.IDLE = Idle(self)
        self.RUN = Run(self)
        self.ATTACK = Attack(self)
        self.JUMP = Jump(self)
        self.FALL = Fall(self)

        self.state_machine = StateMachine(
            self.APPEARANCE,
            {
                self.APPEARANCE: {time_out: self.IDLE},
                self.IDLE: { space_down: self.JUMP,
                             right_down: self.RUN, left_down: self.RUN,
                             g_down: self.ATTACK,
                             run_off: self.FALL},
                self.RUN: { space_down: self.JUMP,
                            right_up: self.IDLE, left_up: self.IDLE, right_down: self.RUN, left_down: self.RUN,
                            g_down: self.ATTACK,
                            run_off: self.FALL},
                self.ATTACK: {time_out: self.IDLE, run_off: self.FALL},
                self.JUMP: {fall_start: self.FALL, time_out: self.IDLE},
                self.FALL: {time_out: self.IDLE}
            }
        )

        if Player1.font is None:
            Player1.font = load_font('megaman.ttf', 10)

    def update(self):
        self.state_machine.update()

        cur = getattr(self.state_machine, 'cur_state', None)
        if isinstance(cur, (Jump, Fall)):
            support = None
            if hasattr(cur, 'yv') and cur.yv <= 0:
                support = self._find_support_block()
            if support:
                top = support.get_bb()[3]
                foot_y = self.get_bb()[1]
                if foot_y <= top + 10 and foot_y >= top - 3:
                    self.ground_y = top
                    self.y = top + 17
                    if hasattr(cur, 'yv'):
                        cur.yv = 0
                    self.state_machine.handle_state_event(('TIMEOUT', None))
            return

        support = self._find_support_block()
        if support:
            top = support.get_bb()[3]
            self.ground_y = top
            if self.y < top + 17:
                self.y = top + 17
        else:
            if self.ground_y > self.BASE_GROUND_Y:
                self.ground_y = self.BASE_GROUND_Y
                self.state_machine.handle_state_event(('RUN_OFF', None))
            if self.y < self.BASE_GROUND_Y + 17:
                self.y = self.BASE_GROUND_Y + 17
                self.ground_y = self.BASE_GROUND_Y

    def _find_support_block(self):
        left, bottom, right, top = self.get_bb()
        foot_y = bottom
        foot_width = (right - left)
        margin = foot_width * 0.35
        check_left = left + margin
        check_right = right - margin

        nearest = None
        nearest_top = -9999

        for layer in game_world.world:
            for o in layer:
                if isinstance(o, StageBlock):
                    l, b, r, t = o.get_bb()
                    horizontal_overlap = not (check_right < l or check_left > r)
                    vertical_near = foot_y <= t + 10 and foot_y >= t - 5
                    if horizontal_overlap and vertical_near and t > nearest_top:
                        nearest = o
                        nearest_top = t
        return nearest

    def handle_event(self, event):
        self.state_machine.handle_state_event(('INPUT', event))

    def draw(self):
        self.state_machine.draw()
        if Player1.font:
            Player1.font.draw(self.x - 10, self.y + 50, 'P1', (255, 255, 255))

    def get_bb(self):
        cur = getattr(self.state_machine, 'cur_state', None)
        if cur and hasattr(cur, 'get_bb'):
            bb = cur.get_bb()
            if bb:
                return bb
        return self.x - 15, self.y - 15, self.x + 15, self.y + 15

    def get_attack_bb(self):
        cur = getattr(self.state_machine, 'cur_state', None)
        if cur and hasattr(cur, 'get_attack_bb'):
            return cur.get_attack_bb()
        return None

    def handle_collision(self, group, other):
        def _overlap(a, b):
            ax1, ay1, ax2, ay2 = a
            bx1, by1, bx2, by2 = b
            return not (ax2 < bx1 or bx2 < ax1 or ay2 < by1 or by2 < ay1)

        def _get_attack_bb(src):
            return getattr(src, 'get_attack_bb', lambda: None)()

        if group.startswith('sword:'):
            atk_bb = _get_attack_bb(other)
            if not atk_bb or getattr(other, 'attack_hit', False):
                return
            if not _overlap(atk_bb, self.get_bb()):
                return
            self.hp = max(0, self.hp - 1)
            other.attack_hit = True
            print("Player1 hit! HP:", self.hp)
            return

        if group.startswith('obstacle:'):
            bb = getattr(other, 'get_bb', lambda: None)()
            if not bb or getattr(other, 'obstacle_hit', False):
                return
            if not _overlap(bb, self.get_bb()):
                return
            self.hp = max(0, self.hp - 1)
            other.obstacle_hit = True
            print("Player1 hit by obstacle! HP:", self.hp)
            game_world.remove_object(other)
            return

        if group.endswith(':stageBlock'):
            block_bb = other.get_bb()
            player_bb = self.get_bb()
            block_top = block_bb[3]
            foot_y = player_bb[1]
            cur_state = self.state_machine.cur_state
            descending = hasattr(cur_state, 'yv') and cur_state.yv <= 0
            if foot_y >= block_top - 8 and self.y >= block_top and descending:
                self.ground_y = block_top
                self.y = block_top + (player_bb[3] - player_bb[1]) / 2
                if hasattr(cur_state, 'yv'):
                    cur_state.yv = 0
                return
            return
