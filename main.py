import pygame as pg

from game.map.map_settings import MAP_SIZE
from setings import *
from game.game import Game
import sys

pg.init()
pg.mixer.init()
pg.mixer.music.set_volume(1)
pg.display.set_caption("Игрулька")
screen = pg.display.set_mode(SCREEN_SIZE, pg.DOUBLEBUF, vsync=1)
clock = pg.time.Clock()
game = Game(screen)
while True:
    dt = clock.tick(60)/1000
    events = pg.event.get()
    for event in events:
        if event.type == pg.QUIT:
            pg.quit()
            sys.exit()
        if event.type == pg.MOUSEBUTTONDOWN:
            game.side_panel.handle_event(event)
            game.mouse_down(pg.mouse.get_pos())
        if event.type == pg.MOUSEBUTTONUP:
            game.side_panel.handle_event(event)
            game.mouse_up(pg.mouse.get_pos())
        if event.type == pg.KEYDOWN:
            game.key_down = pg.key.get_pressed()
            game.key_up = False
        if event.type == pg.KEYUP:
            game.key_down = False
            game.key_up = True

    game.create_frame(dt, events)
    game.draw_frame(list(pg.mouse.get_pos()))
    clock.tick(60)
    pg.display.update()

