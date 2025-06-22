import random

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
from game.enemy_types import AiryMonster, IronChanMonster
from game.sound_manager import play_music
from game.sound_manager import play_sfx


class Game:
    def __init__(self, screen):
        self.death_timer = 0
        self.large_font = pg.font.Font(None, 72)
        self.base_vign = pg.image.load("assets/images/Base Screen Vignatte.png").convert_alpha()
        self.base_vign = pg.transform.scale(self.base_vign, (GAME_WIDTH, SCREEN_HEIGHT))
        self.screen = screen
        self.opened_chests = 0
        self.total_chests = 0
        self.float_texts = []
        self.dungeon = Dungeon(0)
        self.chests = self.dungeon.get_chests()
        self.doors = self.dungeon.get_doors()
        self.monsters = pg.sprite.Group()
        self.dungeon.set_game(self)
        self.current_level = 0
        self.fade_alpha = 0
        self.fade_state = "none"  # none | fading_out | loading | fading_in
        self.fade_speed = 250  # α-единиц в секунду
        self.fade_surface = pg.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.fade_surface.fill((0, 0, 0))
        self.speed = 5
        self.player = Player(self.dungeon.get_cell_by_cords((1, 1)), self.speed, self.dungeon.get_cell, self.dungeon.get_cell_by_cords)
        self.menu = Menu(self.screen, self.start_game)
        self.menu.create_menu()
        self.room = None
        self.key_down = False
        self.key_up = True
        self.battle_active = False
        self.monster = None
        self.create_monsters()
        self.side_panel = SidePanel(self.player, self.dungeon)
        self.dungeon.game_ref = self  # чтобы сундук мог дернуть game.pickup_item
        self.total_chests = len(self.chests)

    def start_game(self):
        """Запуск/перезапуск игры из меню."""
        play_music("main_game")
        self.current_level = 0
        in_xy = DOOR_COORDS[self.current_level]['IN']  # координаты верхней двери
        spawn = self.dungeon.get_cell_by_cords(in_xy)

        self.player.hp = self.player.max_hp
        self.player.gauge = 0
        self.player.cell = spawn
        self.player.rect.center = spawn.rect.center

        self.monsters.empty()
        self.create_monsters()

        self.dungeon.active = True
        self.battle_active = False
        self.fade_state = 'fading_in'
        self.fade_alpha = 255

    def _update_fade(self, dt: float):
        if self.fade_state == "fading_out":
            # наращиваем альфу
            self.fade_alpha = min(255, self.fade_alpha + self.fade_speed * dt)
            if self.fade_alpha >= 255:
                self.fade_state = "loading"  # ← переключаемся
        elif self.fade_state == "loading":
            # загружаем следующую карту ОДИН раз
            self._load_next_level()
            self.fade_state = "fading_in"
        elif self.fade_state == "fading_in":
            # уменьшаем альфу
            self.fade_alpha = max(0, self.fade_alpha - self.fade_speed * dt)
            if self.fade_alpha <= 0:
                self.fade_state = "none"

        elif self.fade_state == 'death_fade_out':
            self.fade_alpha = min(255, self.fade_alpha + self.fade_speed * dt)
            if self.fade_alpha >= 255:
                self.fade_state = 'death_message'
                self.death_timer = 0

        elif self.fade_state == 'death_message':
            self.death_timer += dt
            if self.death_timer > 1.5:  # задержка показа надписи
                self.fade_state = 'death_to_menu'

        elif self.fade_state == 'death_to_menu':
            self.menu.active = True
            self.dungeon.active = False
            self.fade_state = 'fading_in'  # плавный выход из чёрного

        # обновляем прозрачность чёрной плёнки
        self.fade_surface.set_alpha(int(self.fade_alpha))

    def _load_next_level(self):
        """
        Переходит к следующему уровню: очищает старые данные, создаёт новый Dungeon,
        сбрасывает счётчики и ставит игрока на входную клетку нового уровня.
        """
        # 1) вычисляем ID следующего уровня (кольцевой цикл)
        self.current_level = (self.current_level + 1) % len(lvl)

        # 2) очищаем старые группы спрайтов
        self.doors.empty()
        self.chests.empty()
        self.monsters.empty()

        # 3) создаём новый Dungeon и привязываем к нему Game
        self.dungeon = Dungeon(self.current_level)
        self.dungeon.set_game(self)
        self.dungeon.active_dungeon()

        # 4) обновляем ссылки на двери, сундуки и монстров
        self.doors = self.dungeon.get_doors()
        self.chests = self.dungeon.get_chests()
        self.monsters = pg.sprite.Group()
        self.create_monsters()

        # 5) обновляем методы получения клеток у игрока
        self.player.get_cell = self.dungeon.get_cell
        self.player.get_cell_by_cord = self.dungeon.get_cell_by_cords

        # 6) сбрасываем игровые счётчики и состояния
        self.opened_chests = 0
        self.total_chests = len(self.chests)
        self.float_texts.clear()
        self.player.has_key = False

        # 7) переносим игрока на входную клетку нового уровня
        in_xy = DOOR_COORDS[self.current_level]["IN"]
        in_cell = self.dungeon.get_cell_by_cords(in_xy)
        self.player.cell = in_cell
        self.player.rect.center = in_cell.rect.center

        # 8) синхронизируем камеру
        self.dungeon.cam_x = -(self.player.rect.centerx - GAME_CENTER_X)
        self.dungeon.cam_y = -(self.player.rect.centery - GAME_CENTER_Y)

    def _update_floating_texts(self, dt):
        for ft in self.float_texts[:]:
            ft.update(dt)
            if ft.dead():
                self.float_texts.remove(ft)

    def add_ftext(self, ft):
        self.float_texts.append(ft)

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

    def create_monsters(self, count: int = 5):
        """Спавним монстров ТОЛЬКО на клетках-полах, вне дверей/сундуков/игрока."""
        self.monsters.empty()
        kinds = [AiryMonster, IronChanMonster]
        tries = 0
        doors = tuple(self.dungeon.doors)
        chests = tuple(self.chests)

        while len(self.monsters) < count and tries < 300:
            tries += 1
            cell = self.dungeon.get_random_floor_cell()

            # 1) не ставим на игрока
            if cell is self.player.cell:
                continue
            # 2) не ставим в ту же клетку, где уже стоит монстр
            if any(m.cell is cell for m in self.monsters):
                continue
            # 3) не перекрываем двери и сундуки
            if any(cell.rect.colliderect(obj.rect) for obj in (*doors, *chests)):
                continue

            Kind = random.choice(kinds)
            self.monsters.add(Kind(cell,
                                   self.speed,
                                   self.dungeon.get_cell,
                                   self.dungeon.get_cell_by_cords))
    def _go_to_next_level(self):
        # TODO: fade-out + создание нового Dungeon
        print("Level complete → загружаем следующую карту")


    def create_frame(self, dt, events):
        if self.fade_state == 'none' and self.dungeon.active and self.player.hp <= 0:
            self.fade_state = 'death_fade_out'
            self.fade_alpha = 0
            self.death_timer = 0
            self.battle_active = False
        self._update_fade(dt)
        if self.dungeon.active:
            if not self.dungeon.pause:
                self.Key_down()
                self.player.move()
                for chest in pg.sprite.spritecollide(self.player, self.chests, False):
                    chest.open()
                for ft in self.float_texts[:]:
                    ft.update(dt)
                    if ft.dead(): self.float_texts.remove(ft)
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
                    play_sfx("fight")
                # столкновения с дверями
                for door in pg.sprite.spritecollide(self.player, self.doors, False):
                    if door.is_exit_door():
                        if door.is_exit_door() and not door.is_locked() and self.fade_state == "none":
                            self.fade_state = "fading_out"
                    else:
                        pass  # входная дверь, ничего не делаем
            if self.battle_active:
                alive = self.battle.update(dt)
                if not alive:
                    self.battle_active = False
                    self.dungeon.pause = False
                    if self.battle.monster.hp <= 0:
                        self.player.hp = (self.player.hp + 30) if self.player.hp + 30 < self.player.max_hp else 100
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
            self.screen.blit(self.base_vign, (0, 0))
            if self.battle_active:
                self.battle.draw(self.screen)
                self.screen.blit(self.base_vign, (0, 0))
            else:
                for ft in self.float_texts:
                    ft.draw(self.screen, self.dungeon.cam_x, self.dungeon.cam_y)
            self.side_panel.draw(self.screen)
        if self.fade_alpha:
            self.screen.blit(self.fade_surface, (0, 0))

        if self.fade_state in ('death_message', 'death_to_menu'):
            play_music("game_over", loop=False)
            txt = self.large_font.render('ПОРАЖЕНИЕ', True, (220, 0, 0))
            rect = txt.get_rect(center=(SCREEN_CENTER_X, SCREEN_CENTER_Y))
            self.screen.blit(txt, rect)


