from pico2d import load_image, draw_rectangle, clamp
from sdl2 import SDL_KEYDOWN, SDL_KEYUP, SDLK_KP_0, SDLK_KP_ENTER, SDLK_RIGHT, SDLK_LEFT

import game_world
import game_framework
from state_machine import StateMachine
from stageBlock import StageBlock


time_out = lambda e: e[0] == 'TIMEOUT'
run_off = lambda e: e[0] == 'RUN_OFF'
fall_start = lambda e: e[0] == 'FALL_START'

def right_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_RIGHT


def right_up(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYUP and e[1].key == SDLK_RIGHT


def left_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_LEFT


def left_up(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYUP and e[1].key == SDLK_LEFT

# 공격 키다운
def enter_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_KP_ENTER

# 점프 키다운

def zero_down(e): # e is space down ?
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_KP_0


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

    def get_bb(self):
        pass


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
        self.player2.obstacle_hit = False

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
        if self.player2.face_dir == 1:
            return self.player2.x - 5, self.player2.y - 15, self.player2.x + 20, self.player2.y + 15
        else:
            return self.player2.x - 20, self.player2.y - 15, self.player2.x + 5, self.player2.y + 15



class Run:
    images = None
    def load_images(self):
        if Run.images is None:
            Run.images = {}
            Run.images['run'] = [load_image(f"./player_2/run ({i}).png") for i in range(1, 6)]

    def __init__(self, player2):
        self.frame = 0.0
        self.player2 = player2
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
            self.player2.dir = 1
            self.player2.face_dir = 1
        elif left_down(e):
            self.player2.dir = -1
            self.player2.face_dir = -1
        elif right_up(e) or left_up(e):
            self.player2.dir = 0

        self.idle_delay = 0
        self.player2.obstacle_hit = False

    def exit(self, e):
        pass

    def do(self):
        self.frame += self.FRAMES_PER_ACTION * self.ACTION_PER_TIME * game_framework.frame_time
        self.player2.x += self.player2.dir * self.RUN_SPEED_PPS * game_framework.frame_time

        # dir이 0이 아니면 마지막 이동 방향 저장
        if self.player2.dir != 0:
            self.player2.last_dir = self.player2.dir

        # ★ dir = 0이면 강제 IDLE (버그 방지)
        if self.player2.dir == 0:
            self.player2.state_machine.handle_state_event(('TIMEOUT', None))
            if self.idle_delay > 0.1:  # 0.1초 대기
                self.player2.state_machine.handle_state_event(('TIMEOUT', None))
        else:
            self.idle_delay = 0

        self.player2.x = clamp(10, self.player2.x, 800 - 10)

    def draw(self):
        frame_idx = int(self.frame) % 5
        img = Run.images['run'][frame_idx]

        if self.player2.face_dir == 1:
            img.draw(self.player2.x, self.player2.y)
        else:
            img.composite_draw(0, 'h', self.player2.x, self.player2.y)
        draw_rectangle(*self.get_bb())

    def get_bb(self):
        if self.player2.face_dir == 1:
            return self.player2.x - 5, self.player2.y - 15, self.player2.x + 20, self.player2.y + 15
        else:
            return self.player2.x - 20, self.player2.y - 15, self.player2.x + 5, self.player2.y + 15



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
        self.player2.attack_hit = False
        self.player2.obstacle_hit = False
        if hasattr(self.player2, 'attack_target'):
            game_world.update_collision_pair('sword:player1', self.player2, self.player2.attack_target)

    def exit(self, e):
        game_world.update_collision_pair('sword:player1', None, None)

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
        if self.player2.face_dir == 1:
            img.draw(self.player2.x, self.player2.y)
        else:
            img.composite_draw(0, 'h', self.player2.x, self.player2.y)
        draw_rectangle(*self.get_bb())
        atk_bb = self.get_attack_bb()
        if atk_bb:
            draw_rectangle(*atk_bb)

    def get_bb(self):
        if self.player2.face_dir == 1:
            return self.player2.x - 25, self.player2.y - 15, self.player2.x + 5, self.player2.y + 15
        else:
            return self.player2.x - 5, self.player2.y - 15, self.player2.x + 25, self.player2.y + 15

    # 칼 범위 바운딩 박스 (player1과 동일 폭 28로 통일)
    def get_attack_bb(self):
        if self.player2.face_dir == 1:
            return self.player2.x + 5, self.player2.y - 15, self.player2.x + 28, self.player2.y + 15
        else:
            return self.player2.x - 28, self.player2.y - 15, self.player2.x - 5, self.player2.y + 15

    def _find_support_block(self):
        # 플레이어 발 위치 - 중앙 부분만 체크 (가장자리에서 떨어지기 쉽게)
        left, bottom, right, top = self.get_bb()
        foot_y = bottom

        # 발의 중앙 30%만 체크 (양 끝 35%씩 제외) - 더 좁게 체크하여 떨어지기 쉽게
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

class Jump:
    images = None

    def load_images(self):
        if Jump.images is None:
            Jump.images = {}
            Jump.images['jump'] = [load_image(f"./player_2/jump ({i}).png") for i in range(1, 8)]

    def __init__(self, player2):
        self.frame = 0.0
        self.player2 = player2
        self.load_images()
        self.animation_finished = False
        self.ground_y = 32  # 기본 바닥
        self.on_ground = False

        #점프 파워 설정
        self.PIXEL_PER_METER = 10.0 / 0.3  # 33.33 pixel = 1m
        self.JUMP_POWER = 18.0  # 수직 초속 (m/s) - 16에서 22로 증가
        self.HORIZONTAL_BOOST = 6.0  # 수평 초속 (m/s)
        self.GRAVITY = 45.0  # 중력 (조금 세게 → 빠른 착지)

        self.TIME_PER_ACTION = 1.0
        self.ACTION_PER_TIME = 1.0 / self.TIME_PER_ACTION
        self.FRAMES_PER_ACTION = 7

        self.xv = 0.0  # m/s
        self.yv = 0.0  # m/s
        self.ground_y = 50  # 착지 y 좌표

    def enter(self, e):
        self.frame = 0.0
        self.animation_finished = False
        self.player2.obstacle_hit = False
        if e[0] == 'RUN_OFF':
            # 낙하: 상승 속도 없이 시작, 기존 수평 속도 유지하지 않음
            self.yv = 0
            self.xv = 0
        else:
            # 점프 시작 - ground_y에 위치 고정하고 수직 속도 부여
            self.player2.y = self.player2.ground_y
            # 수직 속도
            self.yv = self.JUMP_POWER * self.PIXEL_PER_METER

            # 수평 속도 (현재 방향 유지)
            run_speed = 20.0  # Run 클래스와 동일하게
            pps = (run_speed * 1000 / 60 / 60) * self.PIXEL_PER_METER
            if self.player2.dir != 0:
                self.xv = pps * self.player2.dir  # 달리는 중이면 더 빠르게
            else:
                self.xv = self.HORIZONTAL_BOOST * self.PIXEL_PER_METER * self.player2.face_dir

    def exit(self, e):
        pass

    def do(self):
        self.frame += self.FRAMES_PER_ACTION * self.ACTION_PER_TIME * game_framework.frame_time
        self.player2.x += self.xv * game_framework.frame_time
        self.player2.y += self.yv * game_framework.frame_time
        self.yv -= self.GRAVITY * self.PIXEL_PER_METER * game_framework.frame_time

        if self.yv <= 0:
            self.player2.air_xv = self.xv
            self.player2.air_yv = self.yv
            self.player2.state_machine.handle_state_event(('FALL_START', None))
            return

        if self.frame >= 6.5:
            self.player2.state_machine.handle_state_event(('TIMEOUT', None))

        self.player2.x = clamp(10, self.player2.x, 800 - 10)

    def draw(self):
        frame_idx = int(self.frame) % 7
        img = Jump.images['jump'][frame_idx]
        # ★ 원본 이미지 크기 자르기 (캐릭터 크기 고정!)
        if self.player2.face_dir == 1:
            img.draw(self.player2.x, self.player2.y)
        else:
            img.composite_draw(0, 'h', self.player2.x, self.player2.y)  # ★ 뒤집기만!!
        draw_rectangle(*self.get_bb())

    def get_bb(self):
        if self.player2.face_dir == 1:
            return self.player2.x - 10, self.player2.y - 17, self.player2.x + 15, self.player2.y + 17
        else:
            return self.player2.x - 15, self.player2.y - 17, self.player2.x + 10, self.player2.y + 17



class Fall:
    images = None
    def load_images(self):
        if Fall.images is None:
            Fall.images = {}
            Fall.images['fall'] = [load_image(f"./player_2/fall ({i}).png") for i in range(1, 5)]

    def __init__(self, player2):
        self.frame = 0.0
        self.player2 = player2
        self.load_images()
        self.animation_finished = False
        self.PIXEL_PER_METER = 10.0 / 0.3
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
            self.xv = getattr(self.player2, 'air_xv', 0.0)
            self.yv = getattr(self.player2, 'air_yv', 0.0)
        elif e[0] == 'RUN_OFF':
            # 달리다가 떨어지는 경우 - 수평 속도 유지
            run_speed = 20.0
            pps = (run_speed * 1000 / 60 / 60) * self.PIXEL_PER_METER
            # dir이 0이면 last_dir 사용 (키를 뗀 직후 떨어지는 경우)
            direction = self.player2.dir if self.player2.dir != 0 else self.player2.last_dir
            self.xv = pps * direction
            self.yv = 0.0  # 초기 낙하 속도는 0
        else:
            self.xv = 0.0
            self.yv = 0.0

    def exit(self, e):
        pass

    def do(self):
        self.frame += self.FRAMES_PER_ACTION * self.ACTION_PER_TIME * game_framework.frame_time
        self.player2.x += self.xv * game_framework.frame_time
        self.player2.y += self.yv * game_framework.frame_time
        self.yv -= self.GRAVITY * self.PIXEL_PER_METER * game_framework.frame_time

        if self.frame >= self.FRAMES_PER_ACTION - 0.5:
            self.frame = 0.0

        self.player2.x = clamp(10, self.player2.x, 800 - 10)

    def draw(self):
        frame_idx = int(self.frame) % self.FRAMES_PER_ACTION
        img = Fall.images['fall'][frame_idx]
        if self.player2.face_dir == 1:
            img.draw(self.player2.x, self.player2.y)
        else:
            img.composite_draw(0, 'h', self.player2.x, self.player2.y)
        draw_rectangle(*self.get_bb())

    def get_bb(self):
        if self.player2.face_dir == 1:
            return self.player2.x - 10, self.player2.y - 17, self.player2.x + 15, self.player2.y + 17
        else:
            return self.player2.x - 15, self.player2.y - 17, self.player2.x + 10, self.player2.y + 17



class Player2:
    BASE_GROUND_Y = 32

    def __init__(self):
        self.x, self.y = 700, 49  # 바닥(32) + 발 오프셋(17) = 49
        self.face_dir = -1
        self.dir = 0
        self.last_dir = 0  # 마지막 이동 방향 저장
        # 플레이어 체력
        self.hp = 5
        self.attack_hit = False
        self.obstacle_hit = False
        self.ground_y = 32  # 기본 바닥 높이를 BASE_GROUND_Y와 동일하게

        # 플레이어 상태 관리 (먼저 생성해서 이미지 로드)
        self.APPEARANCE = Appearance(self)
        self.IDLE = Idle(self)
        self.RUN = Run(self)
        self.ATTACK = Attack(self)
        self.JUMP = Jump(self)
        self.FALL = Fall(self)

        self.state_machine = StateMachine(
            self.APPEARANCE,
            {
                self.APPEARANCE : {time_out: self.IDLE},
                self.IDLE : { zero_down: self.JUMP,
                              right_down: self.RUN, left_down: self.RUN,
                              enter_down: self.ATTACK,
                              run_off: self.FALL},
                self.RUN : { zero_down: self.JUMP,
                             right_up: self.IDLE, left_up: self.IDLE, right_down: self.RUN, left_down: self.RUN,
                             enter_down: self.ATTACK,
                             run_off: self.FALL},
                self.ATTACK : {time_out: self.IDLE, run_off: self.FALL},
                self.JUMP : {fall_start: self.FALL, time_out: self.IDLE},
                self.FALL : {time_out: self.IDLE}
            }
        )

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
        # 플레이어 발 위치 - 중앙 부분만 체크 (가장자리에서 떨어지기 쉽게)
        left, bottom, right, top = self.get_bb()
        foot_y = bottom

        # 발의 중앙 30%만 체크 (양 끝 35%씩 제외) - 더 좁게 체크하여 떨어지기 쉽게
        foot_width = (right - left)
        margin = foot_width * 0.35
        check_left = left + margin
        check_right = right - margin

        nearest = None
        nearest_top = -9999

        # world 레이어 순회
        for layer in game_world.world:
            for o in layer:
                if isinstance(o, StageBlock):
                    l, b, r, t = o.get_bb()

                    # 발의 중앙 부분이 블록 범위와 겹치는지 확인
                    horizontal_overlap = not (check_right < l or check_left > r)

                    # 발이 블록 윗면 근처에 있는지 확인
                    vertical_near = foot_y <= t + 10 and foot_y >= t - 5

                    if horizontal_overlap and vertical_near:
                        # 가장 높은 것 선택 (겹칠 경우)
                        if t > nearest_top:
                            nearest = o
                            nearest_top = t
        return nearest

    def handle_event(self, event):
        self.state_machine.handle_state_event(('INPUT', event))

    def draw(self):
        self.state_machine.draw()

    def get_bb(self):
        # 현재 상태의 바운딩 박스를 안전하게 반환 (없으면 임시 박스)
        cur = getattr(self.state_machine, 'cur_state', None)
        if cur and hasattr(cur, 'get_bb'):
            bb = cur.get_bb()
            if bb:
                return bb
        # fallback (등장 등에서 None 방지)
        return self.x - 15, self.y - 15, self.x + 15, self.y + 15

    def get_attack_bb(self):
        # 현재 상태가 공격 히트박스를 제공하면 그걸 사용, 아니면 None
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
            print("Player2 hit! HP:", self.hp)
            return

        if group.startswith('obstacle:'):
            bb = getattr(other, 'get_bb', lambda: None)()
            if not bb or getattr(other, 'obstacle_hit', False):
                return
            if not _overlap(bb, self.get_bb()):
                return
            self.hp = max(0, self.hp - 1)
            other.obstacle_hit = True
            print("Player2 hit by obstacle! HP:", self.hp)
            game_world.remove_object(other)
            return

        # 스테이지 블록 충돌 처리
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
