import random
import game_framework

from pico2d import *

# zombie Action Speed
TIME_PER_ACTION = 1.0
ACTION_PER_TIME = 1.0 / TIME_PER_ACTION
FRAMES_PER_ACTION = 10.0

animation_names = ['stageBlock']

class StageBlock:
    images = None

    def load_images(self):
        if StageBlock.images == None:
            StageBlock.images = {}
            for name in animation_names:
                StageBlock.images[name] = [load_image("./stageBlock/" + name + " (%d)" % i + ".png") for i in range(1, 11)]

    def __init__(self, x, y):
        # 전달받은 x를 사용하도록 변경
        self.x = x
        self.y = y
        self.load_images()
        # 이미지 인덱스는 1~10 까지이므로 randint 범위를 수정
        self.frame = random.randint(1, 10)
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
        pass