import pygame as pg
from game.map.map_settings import MAP, CELL_SIZE, MAP_SIZE
from setings import SCREEN_SIZE, SCREEN_CENTER_X, SCREEN_CENTER_Y
from game.map.Levels import *


class Dungeon:
    def __init__(self, lvl):
        self.lvl = lvl
        self.active = False
        self.pause = False
        self.cells = []
        self.cells_by_coord = {}
        self.surface = pg.Surface(MAP_SIZE, pg.SRCALPHA)
        self.create_map()
        self.map = self.surface.copy()
        self.draw_map()
        self.cam_x = 0
        self.cam_y = 0

    def create_map(self):
        for y in range(len(lvl[self.lvl])):
            for x in range(len(lvl[self.lvl])):
                cell = Cell((x, y), lvl[self.lvl][y][x]-1)
                self.cells.append(cell)
                self.cells_by_coord[(x, y)] = cell

    def draw_map(self):
        for cell in self.cells:
            cell.draw(self.map)

    def draw_dungeon(self, screen, monsters):
        self.surface.blit(self.map, (0 ,0))
        for monster in monsters:
            monster.draw(self.surface)
        screen.blit(self.surface, (self.cam_x, self.cam_y))

    def active_dungeon(self):
        self.active = True

    def movement(self):
        pass

    def get_cell(self, cords):
        for cell in self.cells:
            if cell.rect.collidepoint(cords):
                return cell

    def  get_cell_by_cords(self, cords):
        return self.cells_by_coord.get(tuple(cords))


class Cell(pg.sprite.Sprite):
    def __init__(self, cords, type):
        super().__init__()
        self.floor = [11]
        self.wall = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 13, 14, 15]
        self.cords = cords
        self.size = CELL_SIZE
        self.real_cords = [self.cords[0]*self.size, self.cords[1]*self.size]
        self.type = type
        self.rect = pg.rect.Rect(*self.real_cords, self.size, self.size)
        picture = pg.image.load(f"assets/images/Floor_tiles/Floor tiles - {self.type}.png")
        self.image = pg.transform.smoothscale(picture, (self.size, self.size)).convert_alpha()

    def draw(self, surface):
        surface.blit(self.image, self.real_cords)

