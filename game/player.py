import random

import pygame as pg
from game.Entity import Entity
from game.map.map_settings import CELL_SIZE
from setings import *
from game.armor import Armor
from game.weapon import Weapon


class Player(Entity):
    def __init__(self,cell, speed, get_cell, get_cell_by_cord):
        super().__init__(cell, speed, get_cell, get_cell_by_cord)
        self.offset_pos = list(SCREEN_CENTER)
        self.ox = self.offset_pos[0]
        self.oy = self.offset_pos[1]
        self.walk_right_images = [pg.image.load(f"assets/images/Player/Walking/right/X-12L4 RW {i}.png") for i in range(0, 4)]
        self.walk_left_images = [pg.image.load(f"assets/images/Player/Walking/left/X-12L4 LW {i}.png") for i in range(0, 4)]
        self.walk_down_images = [pg.image.load(f"assets/images/Player/Walking/down/X-12L4 DW {i}.png") for i in range(0, 4)]
        self.walk_up_images = [pg.image.load(f"assets/images/Player/Walking/up/X-12L4 UW {i}.png") for i in range(0, 4)]
        self.fight_prefix = "assets/images/Player/Fighting/X_12L4 Fighting"
        self.image = pg.transform.smoothscale(self.walk_right_images[0], (self.rect.size[0]*0.75, self.rect.size[1]*1.5))
        self.current_frame = 0
        self.frame_interval = 200
        self.last_update = pg.time.get_ticks()
        self.moving_up = False
        self.moving_down = False
        self.moving_right = False
        self.moving_left = False
        self.max_hp = 100
        self.hp = self.max_hp
        self.gauge = 0
        self.gauge_max = 100
        self.gauge_speed = 100
        self.armor = None
        self.weapon = None
        self.has_key = False


    def obtain_key(self):
        self.has_key = True

    def equip_weapon(self, weapon: Weapon):
        self.weapon = weapon

    def equip_armor(self, armor: Armor):
        self.armor = armor

    def take_damage(self, dmg: int) -> int:
        """Возвращает фактический урон, снятый с HP."""
        if self.armor and self.armor.durability > 0:
            dmg = self.armor.absorb_damage(dmg)
        self.hp = max(0, self.hp - dmg)
        return dmg

    def reset_battle_stats(self):
        self.gauge = 0

    def attack(self, target):
        base = 20
        hit_chance = 0.7
        damage = base
        if self.weapon:
            damage += self.weapon.damage
            hit_chance = self.weapon.accuracy
        if random.random() <= hit_chance:
            if hasattr(target, "take_damage"):
                return target.take_damage(damage)
            target.hp -= damage
            return damage
        return 0

    def move(self):
        if self.moving:
            if self.in_center_cell():
                self.rect.center = self.cell.rect.center
                cell = self.get_cell_by_cord((self.cell.cords[0]+self.future_moving[0], self.cell.cords[1]+self.future_moving[1]))
                if cell is None or not cell.type in cell.floor:
                    self.move_to = [0, 0]
                else:
                    self.move_to = self.future_moving
                self.future_moving = [0, 0]
            self.rect.x += self.move_to[0]*self.speed
            self.rect.y += self.move_to[1]*self.speed
            self.cell = self.get_cell(self.rect.center)
            now = pg.time.get_ticks()
            if now - self.last_update >= self.frame_interval:
                self.last_update = now
                self.current_frame = (self.current_frame+1) % len(self.walk_right_images)

    def draw(self, surface):
        if self.moving:
            if self.moving_right:
                image = pg.transform.smoothscale(self.walk_right_images[self.current_frame], (self.rect.size[0]*0.75, self.rect.size[1]*1.5))
                self.image = pg.transform.smoothscale(self.walk_right_images[0], (self.rect.size[0]*0.75, self.rect.size[1]*1.5))
                surface.blit(image, (GAME_CENTER_X-CELL_SIZE//2+CELL_SIZE*0.09375, SCREEN_CENTER_Y-CELL_SIZE//2-CELL_SIZE*0.7))
            if self.moving_left:
                image = pg.transform.smoothscale(self.walk_left_images[self.current_frame], (self.rect.size[0]*0.75, self.rect.size[1]*1.5))
                self.image = pg.transform.smoothscale(self.walk_left_images[0], (self.rect.size[0]*0.75, self.rect.size[1]*1.5))
                surface.blit(image, (GAME_CENTER_X-CELL_SIZE//2+CELL_SIZE*0.09375, SCREEN_CENTER_Y-CELL_SIZE//2-CELL_SIZE*0.7))
            if self.moving_down:
                image = pg.transform.smoothscale(self.walk_down_images[self.current_frame], (self.rect.size[0]*0.75, self.rect.size[1]*1.5))
                self.image = pg.transform.smoothscale(self.walk_down_images[0], (self.rect.size[0]*0.75, self.rect.size[1]*1.5))
                surface.blit(image, (GAME_CENTER_X-CELL_SIZE//2+CELL_SIZE*0.09375, SCREEN_CENTER_Y-CELL_SIZE//2-CELL_SIZE*0.7))
            if self.moving_up:
                image = pg.transform.smoothscale(self.walk_up_images[self.current_frame], (self.rect.size[0]*0.75, self.rect.size[1]*1.5))
                self.image = pg.transform.smoothscale(self.walk_up_images[0], (self.rect.size[0]*0.75, self.rect.size[1]*1.5))
                surface.blit(image, (GAME_CENTER_X-CELL_SIZE//2+CELL_SIZE*0.09375, SCREEN_CENTER_Y-CELL_SIZE//2-CELL_SIZE*0.7))
        else:
            surface.blit(self.image, (GAME_CENTER_X-CELL_SIZE//2+CELL_SIZE*0.09375, SCREEN_CENTER_Y-CELL_SIZE//2-CELL_SIZE*0.7))