from pico2d import *

class Background:
    def __init__(self):
        self.image = load_image('background.png')

    def update(self):
        pass

    def draw(self):
        self.image.draw(400, 300)

    def get_bb(self):
       pass

    def handle_collision(self, group, other):
        pass