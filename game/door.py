import pygame as pg
from game.map.map_settings import CELL_SIZE

class Door(pg.sprite.Sprite):
    """
    Верхняя дверь (вход) изначально открыта.
    Нижняя дверь (выход) по умолчанию закрыта; когда откроется – меняет текстуру.
    """
    def __init__(self, cords, is_exit: bool, locked: bool = False):
        super().__init__()
        self.cords  = cords          # клеточные координаты (x, y)
        self.is_exit = is_exit       # True → нижняя дверь
        self.locked  = locked

        # прямоугольник в пикселях
        self.rect = pg.Rect(cords[0]*CELL_SIZE, cords[1]*CELL_SIZE,
                            CELL_SIZE, CELL_SIZE)

        # загружаем все нужные текстуры один раз
        if self.is_exit:   # нижняя дверь
            self._img_closed = pg.image.load(
                "assets/images/Door/DooR Down Closed.png").convert_alpha()
            self._img_open   = pg.image.load(
                "assets/images/Door/DooR Down Opened.png").convert_alpha()
        else:              # верхняя дверь
            self._img_closed = pg.image.load(
                "assets/images/Door/DooR UP Closed.png").convert_alpha()
            self._img_open   = pg.image.load(
                "assets/images/Door/DooR UP Opened.png").convert_alpha()

        # подгоняем к размеру тайла
        self._img_closed = pg.transform.smoothscale(self._img_closed,
                                                    (CELL_SIZE, CELL_SIZE))
        self._img_open   = pg.transform.smoothscale(self._img_open,
                                                    (CELL_SIZE, CELL_SIZE))

        # выставляем стартовую картинку
        self._update_image()

    # ──────────────────────────────────────────────────────────
    def unlock(self) -> None:
        """Снимаем замок и меняем спрайт."""
        if self.locked:
            self.locked = False
            self._update_image()

    def _update_image(self):
        self.image = self._img_open if not self.locked else self._img_closed

    def draw(self, surface: pg.Surface) -> None:
        surface.blit(self.image, self.rect.topleft)

    def is_locked(self):
        return self.locked

    def is_exit_door(self):
        return self.is_exit
