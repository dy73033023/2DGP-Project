from pico2d import *
import game_framework
import game_world
import random


TIME_PER_ACTION = 1.0
ACTION_PER_TIME = 1.0 / TIME_PER_ACTION
FRAMES_PER_ACTION = 4 # 이미지 개수에 맞게 수정

class Obstacle:
    images = None

    def load_images(self):
        if Obstacle.images == None:
            Obstacle.images = {}
            Obstacle.images['obstacle'] = [load_image(f"./obstacle/obstacle ({i}).png") for i in range(1, 5)]

    def __init__(self, x, y):
        # 전달받은 x를 사용하도록 변경
        self.x = x
        self.y = y
        self.load_images()
        # 이미지 인덱스는 1~10 까지이므로 randint 범위를 수정
        self.frame = 0.0
        self.width, self.length = 32, 32
        self.bb_x, self.bb_y = 32, 32
        self.obstacle_hit = False

    def update(self):
        self.frame = (self.frame + FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time) % FRAMES_PER_ACTION
        self.y -= 80 * game_framework.frame_time # 장애물이 아래로 떨어지는 속도 조절
        if self.y < -40:
            self.x = random.randint(0, 800)
            self.y = random.randint(600, 1200)

    def draw(self):
        Obstacle.images['obstacle'][int(self.frame)].draw(self.x, self.y, self.width, self.length)
        draw_rectangle(*self.get_bb())

    def handle_event(self, event):
        pass

    def get_bb(self):
        return (self.x - self.bb_x/2, self.y - self.bb_y/2,
                self.x + self.bb_x/2, self.y + self.bb_y/2)

    def handle_collision(self, group, other):
        pass