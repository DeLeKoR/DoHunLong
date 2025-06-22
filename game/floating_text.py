import pygame as pg
import pathlib

# ────────── настройки ─────────────────────────────────────────
FONT_PATH = pathlib.Path("assets/Fonts/Arial Black.ttf")   # ваш шрифт
FONT_SIZE = 34                                             # крупный
COLOR     = (255, 255, 255)                                # белый
VELOCITY  = -50                                            # px/сек вверх
FADE_RATE = 200                                            # alpha/сек
# ──────────────────────────────────────────────────────────────

class FloatingText:
    def __init__(self, text: str, world_pos: tuple):
        """
        world_pos – координаты на карте (без учёта смещения камеры)
        """
        self.text = str(text)
        self.wx, self.wy = world_pos              # мировые координаты
        self.pos    = [float(self.wx), float(self.wy)]
        self.alpha  = 255

        # ленивый одноразовый загрузчик шрифта
        if not hasattr(FloatingText, "_font"):
            FloatingText._font = pg.font.Font(FONT_PATH.as_posix(), FONT_SIZE)

        self.image = FloatingText._font.render(self.text, True, COLOR)
        self.image.set_alpha(self.alpha)
        self.rect  = self.image.get_rect(center=self.pos)

    # ──────────────────────────────────────────────────────────
    def update(self, dt: float):
        """
        dt – дельта-время в секундах
        """
        # подъём
        self.pos[1] += VELOCITY * dt
        # затухание
        self.alpha = max(0, self.alpha - FADE_RATE * dt)
        self.image.set_alpha(int(self.alpha))
        self.rect.center = (int(self.pos[0]), int(self.pos[1]))

    def draw(self, surface: pg.Surface, cam_x: int, cam_y: int):
        """
        Рендер с учётом смещения камеры.
        """
        screen_pos = (self.rect.centerx + cam_x,
                      self.rect.centery + cam_y)
        surface.blit(self.image, self.image.get_rect(center=screen_pos))

    def dead(self) -> bool:
        return self.alpha <= 0