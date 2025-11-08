from pico2d import *
import game_framework
import random
from player1 import Player1
from player2 import Player2

TIME_PER_ACTION = 1.0
ACTION_PER_TIME = 1.0 / TIME_PER_ACTION
FRAMES_PER_ACTION = 1 # 이미지 개수에 맞게 수정

class Hp:
    images = None

    def load_images(self):
        if Hp.images == None:
            Hp.images = {}
            Hp.images['hp'] = [load_image(f"./hp/hp ({i}).png") for i in range(1, 2)]

    def __init__(self, x, y):
        # 전달받은 x를 사용하도록 변경
        self.x = x
        self.y = y
        self.load_images()
        # 이미지 인덱스는 1~10 까지이므로 randint 범위를 수정
        self.frame = 0.0
        self.width, self.length = 15, 15

    def update(self):
        self.frame = (self.frame + FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time) % FRAMES_PER_ACTION

    def draw(self):
        Hp.images['hp'][int(self.frame)].draw(self.x, self.y, self.width, self.length)

    def handle_event(self, event):
        pass

    def get_bb(self):
        pass

    def handle_collision(self, group, other):
        pass