import pygame as pg
from typing import List, Optional, Tuple
from setings import SCREEN_HEIGHT, PANEL_WIDTH
from game.weapon import Weapon
from game.armor import Armor

PADDING       = 10
SLOT_SIZE     = 40
GRID_COLS     = 5
GRID_ROWS     = 3
BAR_H         = 14

class SidePanel:
    """Постоянная правая панель: weapon-slot, armor-slot, сетка 5×3, HP/Gauge и drag-n-drop"""

    def __init__(self, player, dungeon):
        self.player = player
        self.dungeon = dungeon
        # Поверхность и глобальный rect панели
        self.surface = pg.Surface((PANEL_WIDTH, SCREEN_HEIGHT), pg.SRCALPHA)
        self.rect = pg.Rect(0, 0, PANEL_WIDTH, SCREEN_HEIGHT)
        self.font = pg.font.Font(None, 24)

        # ── геометрия слотов ──────────────────────────────
        self.slot_weapon = pg.Rect(PADDING, PADDING, SLOT_SIZE, SLOT_SIZE)
        self.slot_armor  = pg.Rect(PADDING + SLOT_SIZE + PADDING, PADDING, SLOT_SIZE, SLOT_SIZE)

        grid_top = self.slot_weapon.bottom + PADDING * 2
        self.grid_slots: List[pg.Rect] = []
        for r in range(GRID_ROWS):
            for c in range(GRID_COLS):
                x = PADDING + c * (SLOT_SIZE + PADDING)
                y = grid_top + r * (SLOT_SIZE + PADDING)
                self.grid_slots.append(pg.Rect(x, y, SLOT_SIZE, SLOT_SIZE))

        self.items: List[Optional[object]] = [None] * (GRID_COLS * GRID_ROWS)
        self.drag: Tuple[pg.Surface, object] | None = None

    def add_item(self, obj: object):
        """Добавить предмет в начало списка (и обрезать, если места нет)."""
        self.items.insert(0, obj)
        if len(self.items) > GRID_COLS * GRID_ROWS:
            self.items.pop()

    def draw(self, screen: pg.Surface):
        # Обновляем позицию rect панели
        self.rect.topright = (screen.get_width(), 0)

        # Рендерим фон и слоты
        self.surface.fill((20, 20, 20, 220))
        self._draw_slot(self.slot_weapon, self.player.weapon, "W")
        self._draw_slot(self.slot_armor,  self.player.armor,  "A")

        # Сетка 5×3
        for idx, rect in enumerate(self.grid_slots):
            pg.draw.rect(self.surface, (120, 120, 120), rect, 1)
            item = self.items[idx]
            if item and (self.drag is None or self.drag[1] is not item):
                self.surface.blit(item.icon, rect.inflate(-2, -2))

        # HP и Gauge
        bar_w = PANEL_WIDTH - 2 * PADDING
        bar_h = 12
        bars_top = self.grid_slots[-1].bottom + PADDING * 3
        hp_rect    = pg.Rect(PADDING, bars_top,         bar_w, bar_h)
        gauge_rect = pg.Rect(PADDING, bars_top + bar_h + 40, bar_w, bar_h)

        # Фон баров
        pg.draw.rect(self.surface, (80, 80, 80), hp_rect)
        pg.draw.rect(self.surface, (80, 80, 80), gauge_rect)
        # Заполнение
        hp_ratio = self.player.hp / self.player.max_hp if self.player.max_hp else 0
        g_ratio  = self.player.gauge / self.player.gauge_max if self.player.gauge_max else 0
        hp_fill = hp_rect.copy();    hp_fill.width    = int(bar_w * hp_ratio)
        gauge_fill = gauge_rect.copy(); gauge_fill.width = int(bar_w * g_ratio)
        pg.draw.rect(self.surface, (200, 50, 50),  hp_fill)
        pg.draw.rect(self.surface, (210, 180, 70), gauge_fill)

        # Тексты
        self.surface.blit(
            self.font.render(f"HP {self.player.hp}/{self.player.max_hp}", True, (220, 220, 220)),
            hp_rect.move(4, -18)
        )
        self.surface.blit(
            self.font.render("Gauge", True, (220, 220, 220)),
            gauge_rect.move(4, -18)
        )

        # Вывод панели
        screen.blit(self.surface, self.rect)

        # Если тащим предмет — рисуем поверх всего
        if self.drag:
            icon, _ = self.drag
            mx, my  = pg.mouse.get_pos()
            screen.blit(icon, (mx - SLOT_SIZE//2, my - SLOT_SIZE//2))

    def handle_event(self, ev: pg.event.Event):
        if ev.type == pg.MOUSEBUTTONDOWN and ev.button == 1 and self.drag is None:
            self._start_drag(ev.pos)
        elif ev.type == pg.MOUSEBUTTONUP and ev.button == 1 and self.drag:
            self._finish_drag(ev.pos)

    def _draw_slot(self, rect: pg.Rect, item: object | None, placeholder: str):
        pg.draw.rect(self.surface, (180, 180, 180), rect, 2)
        if item and (self.drag is None or self.drag[1] is not item):
            self.surface.blit(item.icon, rect.inflate(-2, -2))
        else:
            txt = self.font.render(placeholder, True, (180, 180, 180))
            self.surface.blit(txt, rect.move((SLOT_SIZE - txt.get_width())//2,
                                            (SLOT_SIZE - txt.get_height())//2))

    def _to_local(self, pos: Tuple[int, int]) -> Tuple[int, int]:
        """Перевод глобальных координат → локальные внутри панели"""
        return pos[0] - self.rect.left, pos[1] - self.rect.top

    def _start_drag(self, pos: Tuple[int, int]):
        local_x, local_y = self._to_local(pos)
        # Сетка
        for idx, rect in enumerate(self.grid_slots):
            if rect.collidepoint(local_x, local_y) and self.items[idx]:
                self.drag = (self.items[idx].icon, self.items[idx])
                self.items[idx] = None
                return
        # Weapon / Armor слоты
        if self.slot_weapon.collidepoint(local_x, local_y) and self.player.weapon:
            self.drag = (self.player.weapon.icon, self.player.weapon)
            self.player.weapon = None
            return
        if self.slot_armor.collidepoint(local_x, local_y) and self.player.armor:
            self.drag = (self.player.armor.icon, self.player.armor)
            self.player.armor = None

    def _finish_drag(self, pos: Tuple[int, int]):
        icon, obj = self.drag
        self.drag = None
        local_x, local_y = self._to_local(pos)
        # Weapon / Armor
        if isinstance(obj, Weapon) and self.slot_weapon.collidepoint(local_x, local_y):
            self.player.equip_weapon(obj)
            return
        if isinstance(obj, Armor) and self.slot_armor.collidepoint(local_x, local_y):
            self.player.equip_armor(obj)
            return
        # Сетка
        for idx, rect in enumerate(self.grid_slots):
            if rect.collidepoint(local_x, local_y):
                if self.items[idx] is None:
                    self.items[idx] = obj
                else:
                    self.add_item(obj)
                return
        # Если не попали — возвращаем в инвентарь
        self.add_item(obj)