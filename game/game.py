import pygame as pg

from game.map.Levels import *
from game.ui.menu import Menu
from game.map.dungeon import Dungeon, Cell
from game.weapon import Weapon
from setings import *
from game.map.map_settings import *
from game.player import Player
from game.monster import Monster
from random import randint
from game.battle.battle_manager import Battle
from game.ui.side_panel import SidePanel
from game.armor import Armor
from game.weapon import Weapon
from game.armor  import Armor

class Game:
    def __init__(self, screen):
        self.screen = screen
        self.dungeon = Dungeon(1)
        self.speed = 5
        self.player = Player(self.dungeon.get_cell_by_cords((1, 1)), self.speed, self.dungeon.get_cell, self.dungeon.get_cell_by_cords)
        self.menu = Menu(self.screen, self.dungeon.active_dungeon)
        self.menu.create_menu()
        self.room = None
        self.key_down = False
        self.key_up = True
        self.battle_active = False
        self.monsters = pg.sprite.Group()
        self.monster = None
        self.create_monsters()
        self.side_panel = SidePanel(self.player)
        self.player.equip_armor(Armor("leather", defense=4, durability=50))
        self.player.equip_weapon(Weapon("sword", damage=10, accuracy=0.85))
        self.pickup_item(Weapon('sword', 12, 0.8))

    def pickup_item(self, obj):
        """Вызывайте из логики игры, чтобы добавить найденный предмет."""
        self.side_panel.add_item(obj)

    def mouse_down(self, pos):
        if self.menu is not None and self.menu.active:
            self.menu.mouse_down(pos)

    def mouse_up(self, pos):
        pass

    def Key_down(self):
        if self.key_down:
            self.player.moving = True
            if self.key_down[pg.K_w]:
                self.player.future_moving = [0, -1]
                self.player.moving_up, self.player.moving_left, self.player.moving_down, self.player.moving_right = True, False, False, False
            if self.key_down[pg.K_s]:
                self.player.future_moving = [0, 1]
                self.player.moving_up, self.player.moving_left, self.player.moving_down, self.player.moving_right = False, False, True, False
            if self.key_down[pg.K_a]:
                self.player.future_moving = [-1, 0]
                self.player.moving_up, self.player.moving_left, self.player.moving_down, self.player.moving_right = False, True, False, False
            if self.key_down[pg.K_d]:
                self.player.future_moving = [1, 0]
                self.player.moving_up, self.player.moving_left, self.player.moving_down, self.player.moving_right = False, False, False, True
        if self.key_up and self.player.in_center_cell():
            self.player.future_moving = [0, 0]
            self.player.moving = False

    def create_monsters(self):
        for i in range(40):
            self.monsters.add(Monster(self.dungeon.get_cell_by_cords((10, 10)), self.speed, self.dungeon.get_cell, self.dungeon.get_cell_by_cords))


    def create_frame(self, dt, events):
        if self.dungeon.active:
            if not self.dungeon.pause:
                self.Key_down()
                self.player.move()
                for monster in self.monsters:
                    monster.move(self.player.cell)
                self.dungeon.cam_x = -(self.player.rect.centerx-GAME_CENTER_X)
                self.dungeon.cam_y = -(self.player.rect.centery-SCREEN_CENTER_Y)
                hits = pg.sprite.spritecollide(self.player, self.monsters, False)
                if hits:
                    self.monster = hits[0]
                    self.battle = Battle(self.player, self.monster)
                    self.battle_active = True
                    self.dungeon.pause = True
            if self.battle_active:
                alive = self.battle.update(dt)
                if not alive:
                    self.battle_active = False
                    self.dungeon.pause = False
                    # pg.mixer.music.fadeout(1000)
                    if self.battle.monster.hp <= 0:
                        self.monsters.remove(self.battle.monster)
                    self.battle = None
                return

    def draw_frame(self, mouth_pos):
        self.screen.fill((0, 0, 0))
        if self.menu.active:
            self.menu.draw_menu(mouth_pos)
        if self.dungeon.active:
            self.dungeon.draw_dungeon(self.screen, self.monsters)
            self.player.draw(self.screen)
            if self.battle_active:
                self.battle.draw(self.screen)
            self.side_panel.draw(self.screen)


