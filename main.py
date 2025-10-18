from pico2d import open_canvas, delay, close_canvas
import game_framework

import title_mode as start_mode

open_canvas(800, 600)
game_framework.run(start_mode)
close_canvas()

# 커밋용 주석처리