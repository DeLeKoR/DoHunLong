import pygame as pg

from setings import *
from game.map.map_settings import CELL_SIZE


class Entity(pg.sprite.Sprite):
    def __init__(self, cell, speed, get_cell, get_cell_by_cord):
        super().__init__()
        self.get_cell_by_cord = get_cell_by_cord
        self.get_cell = get_cell
        self.speed = speed
        self.move_to = [0, 0]
        self.future_moving = [0, 0]
        self.moving = False
        self.move_score = 0
        self.cell = cell
        self.rect = pg.rect.Rect(self.cell.rect.x*CELL_SIZE, self.cell.rect.y*CELL_SIZE, CELL_SIZE, CELL_SIZE)
        self.rect.center = self.cell.rect.center
        self.collision_rect = pg.rect.Rect(0, 0, CELL_SIZE/2, CELL_SIZE/2)
        self.collision_rect.center = self.rect.center
        self.health = 100
        self.weapon = None

    def draw(self):
        pass

    def in_center_cell(self):
        return (self.cell.rect.center[0]-self.speed/2 <= self.rect.center[0] <= self.cell.rect.center[0]+self.speed/2 and
                self.cell.rect.center[1]-self.speed/2 <= self.rect.center[1] <= self.cell.rect.center[1]+self.speed/2)

    def move(self):
        if self.moving:
            if self.in_center_cell():
                self.rect.center = self.cell.rect.center
                if (self.get_cell_by_cord((self.cell.cords[0]+self.future_moving[0], self.cell.cords[1]+self.future_moving[1])) is None or
                    not(self.get_cell_by_cord((self.cell.cords[0]+self.future_moving[0], self.cell.cords[1]+self.future_moving[1])).type)):
                    self.move_to = [0, 0]
                else:
                    self.move_to = self.future_moving
                self.future_moving = [0, 0]
            self.rect.x += self.move_to[0]*self.speed
            self.rect.y += self.move_to[1]*self.speed
            self.cell = self.get_cell(self.rect.center)
