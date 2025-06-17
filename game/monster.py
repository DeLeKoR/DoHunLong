from game.Entity import Entity
import random
import pygame as pg
import math
from setings import *
from game.map.map_settings import *
from collections import deque

class Monster(Entity):
    def __init__(self, cell, speed, get_cell, get_cell_by_cord):
        super().__init__(cell, speed, get_cell, get_cell_by_cord)
        picture = pg.image.load("assets/images/кайданович.png")
        self.image = pg.transform.smoothscale(picture, self.rect.size)
        self.free_cells = pg.sprite.Group()
        self.target_cell = None
        self.path = []
        self.next_step_index = 0
        self.max_hp = 80
        self.hp = self.max_hp
        self.gauge = 0
        self.gauge_max = 100
        self.gauge_speed = 100

        # инициируем первую цель и путь
        self.get_target_cell()

    def reset_battle_stats(self):
        self.hp = self.max_hp
        self.gauge = 0

    def attack(self, target) -> bool:
        hit_chance = 0.6
        damage = 15
        if random.random() <= hit_chance:
            if hasattr(target, "take_damage"):
                return target.take_damage(damage)
            target.hp -= damage
            return damage
        return 0

    def draw(self, surface):
        surface.blit(self.image, self.rect.topleft)

    def get_free_cells(self):
        self.free_cells.empty()
        for x in range(self.cell.cords[0] - 4, self.cell.cords[0] + 5):
            for y in range(self.cell.cords[1] - 4, self.cell.cords[1] + 5):
                c = self.get_cell_by_cord((x, y))
                if c and c.type in c.floor and c.type not in c.wall and c != self.cell:
                    self.free_cells.add(c)

    def get_target_cell(self):
        self.get_free_cells()
        if self.free_cells:
            self.target_cell = random.choice(list(self.free_cells))
        else:
            self.target_cell = self.cell
        self.find_path()

    def find_path(self):
        start = tuple(self.cell.cords)
        goal = tuple(self.target_cell.cords)

        queue = deque([start])
        came_from = {start: None}

        while queue:
            current = queue.popleft()
            if current == goal:
                break
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nbr = (current[0] + dr, current[1] + dc)
                if nbr not in came_from:
                    c = self.get_cell_by_cord(nbr)
                    if c and c.type in c.floor and c.type not in c.wall:
                        came_from[nbr] = current
                        queue.append(nbr)

        # собираем путь
        path = []
        node = goal
        while node is not None and node in came_from:
            path.append(node)
            node = came_from[node]
        path.reverse()

        # если удачный путь
        if path and path[0] == start:
            self.path = path
            self.next_step_index = 1
        else:
            self.path = []
            self.next_step_index = 0

    def move(self, player_cell):
        # проверяем наличие пути к цели
        if not self.path or self.next_step_index >= len(self.path):
            self.get_target_cell()

        # получаем следующую клетку в пути
        next_coords = self.path[self.next_step_index]
        next_cell = self.get_cell_by_cord(next_coords)
        target_center = next_cell.rect.center

        # вектор к цели
        dx = target_center[0] - self.rect.centerx
        dy = target_center[1] - self.rect.centery
        dist = math.hypot(dx, dy)

        # если можем дойти за один шаг — прыжок
        if dist <= self.speed:
            self.rect.center = target_center
            self.cell = next_cell
            self.next_step_index += 1
        else:
            # нормализуем скорость
            vx = dx / dist * self.speed
            vy = dy / dist * self.speed
            self.rect.x += vx
            self.rect.y += vy

        # реагируем на игрока
        self.go_to_player(player_cell)

    def go_to_player(self, player_cell):
        # если игрок в зоне — переназначаем цель
        if abs(self.cell.cords[0] - player_cell.cords[0]) <= 4 and \
           abs(self.cell.cords[1] - player_cell.cords[1]) <= 4:
            self.target_cell = player_cell
            self.find_path()
