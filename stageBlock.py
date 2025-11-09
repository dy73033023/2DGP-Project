from pico2d import *
import game_framework
import random


TIME_PER_ACTION = 1.0
ACTION_PER_TIME = 1.0 / TIME_PER_ACTION
FRAMES_PER_ACTION = 10 # 이미지 개수에 맞게 수정

class StageBlock:
    images = None

    def load_images(self):
        if StageBlock.images == None:
            StageBlock.images = {}
            StageBlock.images['stageBlock'] = [load_image(f"./stageBlock/stageBlock ({i}).png") for i in range(1, 11)]

    def __init__(self, x, y):
        # 전달받은 x를 사용하도록 변경
        self.x = x
        self.y = y
        self.load_images()
        # 이미지 인덱스는 1~10 까지이므로 randint 범위를 수정
        self.frame = 0.0
        self.width, self.length = 32, 32
        self.bb_x, self.bb_y = 32, 32

    def update(self):
        self.frame = (self.frame + FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time) % FRAMES_PER_ACTION

    def draw(self):
        StageBlock.images['stageBlock'][int(self.frame)].draw(self.x, self.y, self.width, self.length)
        draw_rectangle(*self.get_bb())

    def handle_event(self, event):
        pass

    def get_bb(self):
        return (self.x - self.bb_x/2, self.y - self.bb_y/2,
                self.x + self.bb_x/2, self.y + self.bb_y/2)

    def handle_collision(self, group, other):
        if group.startswith('player:stageBlock'):
            block_bb = self.get_bb()
            player_bb = other.get_bb()

            # 플레이어가 블록 위에 있는지 확인
            if player_bb[1] >= block_bb[3] - 5:
                other.y = block_bb[3] + (player_bb[3] - player_bb[1]) / 2
                if hasattr(other.state_machine.cur_state, 'yv'):
                    other.state_machine.cur_state.yv = 0
                    other.state_machine.cur_state.ground_y = block_bb[3]
