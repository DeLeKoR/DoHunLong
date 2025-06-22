import pygame as pg, random
from game.floating_text import FloatingText
from game.map.map_settings import CELL_SIZE
from game.weapon import Weapon
from game.armor  import Armor
from game.key_item import KeyItem          # см. ниже
from game.door import Door                 # чтобы сразу сменить текстуру выхода
CELL = CELL_SIZE  # оставляем как было

class Chest(pg.sprite.Sprite):
    _img_closed = _img_open = None

    def __init__(self, coords, game):
        """
        coords – tuple (x_cell, y_cell)
        """
        super().__init__()
        self.coords = coords
        self.game   = game
        self.opened = False

        # лениво загружаем текстуры
        if Chest._img_closed is None:
            closed = pg.image.load("assets/images/Chest/Chest Closed.png").convert_alpha()
            opened = pg.image.load("assets/images/Chest/Chest Opened.png").convert_alpha()
            Chest._img_closed = pg.transform.smoothscale(closed, (CELL, CELL))
            Chest._img_open   = pg.transform.smoothscale(opened,  (CELL, CELL))

        self.image = Chest._img_closed
        px, py = coords[0] * CELL, coords[1] * CELL
        self.rect = self.image.get_rect(topleft=(px, py))

    # ——— новое: метод отрисовки на поверхность
    def draw(self, surface: pg.Surface):
        surface.blit(self.image, self.rect.topleft)

    # остальной код (_drop_loot и т.д.) без изменений
    # ───── лут & открытие ────────────────────────────────────────
    def open(self):
        if self.opened: return
        self.opened=True; self.image=Chest._img_open
        self.game.opened_chests+=1
        self._drop_loot()

    def _drop_loot(self):
        """
        Если шанс на ключ сработал → даём только ключ и выходим,
        иначе — падает один предмет из пула.
        """
        # 1) рассчитываем, нужно ли выдать ключ
        total = self.game.total_chests
        opened = self.game.opened_chests
        if not self.game.player.has_key and total > 0 and opened / total >= 0.6:
            # линейно: при opened/total == 0.6 → chance=0; при ==1.0 → chance=1.0
            chance = min(1.0, (opened / total - 0.6) / 0.4)
            if random.random() < chance:
                # выдаём ключ
                self.game.player.obtain_key()
                self.game.add_ftext(FloatingText("Ключ!", self.rect.center))
                # разблокируем выходную дверь
                for d in self.game.doors:
                    if d.is_exit:
                        d.unlock()
                return  # *** ВАЖНО: прекращаем дальнейший дропаут лута ***

        # 2) иначе падает один предмет из пула
        pool = [Weapon("Топор", random.randint(24, 30), 0.85),
                Weapon("Копьё", random.randint(18, 22), 0.85),
                Weapon("Арматура", random.randint(12, 15), 0.85),
                Armor("Бинты", 5, 50),
                Armor("Плащ", 8, 50),
                Armor("Химзащита", 12, 50)]
        item = random.choice(pool)
        self.game.pickup_item(item)
        self.game.add_ftext(FloatingText(f"+ {item.id}", self.rect.center))