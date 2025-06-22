import random
import pygame as pg
from game.map.map_settings import MAP, CELL_SIZE, MAP_SIZE
from setings import *
from game.map.Levels import *
from game.door import Door
from game.map.Levels import DOOR_COORDS   # уже импортируются lvl, просто добавь новую константу
from game.chest import Chest


class Dungeon:
    def __init__(self, lvl_id):
        self.lvl = lvl_id
        self.matrix = lvl[self.lvl]
        self.active = False
        self.pause = False
        self.cells = []
        self.cells_by_coord = {}
        self.surface = pg.Surface(MAP_SIZE, pg.SRCALPHA)
        self.floor_cells = pg.sprite.Group()
        self.create_map()
        self.map = self.surface.copy()
        self.doors = pg.sprite.Group()
        self.chests = pg.sprite.Group()
        self._create_doors()
        self.game_ref = None
        self._create_chests()
        self.draw_map()
        self.cam_x = 0
        self.cam_y = 0

    def create_map(self):
        for y in range(len(lvl[self.lvl][0])):
            for x in range(len(lvl[self.lvl][0])):
                cell = Cell((x, y), lvl[self.lvl][y][x]-1)
                self.cells.append(cell)
                self.cells_by_coord[(x, y)] = cell
                if lvl[self.lvl][y][x]-1 == 11:
                    self.floor_cells.add(cell)

    def draw_map(self):
        for cell in self.cells:
            cell.draw(self.map)

    def draw_dungeon(self, screen, monsters):
        self.surface.blit(self.map, (0 ,0))
        for door in self.doors:
            door.draw(self.surface)
        for ch in self.chests:
            ch.draw(self.surface)
        screen.blit(self.surface, (self.cam_x, self.cam_y))
        for monster in monsters:
            monster.draw(self.surface)

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

    def _create_doors(self):
        for tag, (x, y) in DOOR_COORDS[self.lvl].items():
            is_exit = (tag == 'OUT')
            door = Door((x, y), is_exit=is_exit, locked=is_exit)  # выход → закрыт
            self.doors.add(door)

    def get_doors(self):
        return self.doors

    from game.chest import Chest
      # значение клетки «проходимо» (если другое — замените)

    def _create_chests(self):
        """Ставим сундуки только на клетках пола, максимум 10."""
        # 1) координаты всех проходимых клеток
        free = [cell.cords for cell in self.floor_cells]

        # 2) убираем клетки с дверями
        door_coords = {d.cords for d in self.doors}
        free = [c for c in free if c not in door_coords]

        if not free:
            return

        # 3) выбираем случайно ≤ 10 клеток
        for coords in random.sample(free, min(10, len(free))):
            self.chests.add(Chest(coords, self.game_ref))

        # 4) если Game уже передан — обновляем счётчик
        if self.game_ref:
            self.game_ref.total_chests = len(self.chests)

    def get_chests(self):
        return self.chests

    def set_game(self, game):
        """
        Устанавливает у этого подземелья ссылку на Game
        и раздаёт её всем существующим сундукам.
        """
        self.game_ref = game
        for chest in getattr(self, 'chests', []):
            chest.game = game

    def get_random_floor_cell(self):
        """Вернуть случайную клетку, которая гарантированно является полом."""
        return random.choice(self.floor_cells.sprites())


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

