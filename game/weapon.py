
import pygame as pg

class Weapon:
    _cache = {}

    def __init__(self, weapon_id: str, damage: int, accuracy: float = 0.9):
        self.id = weapon_id
        self.damage = damage
        self.accuracy = accuracy

        if weapon_id not in Weapon._cache:
            img = pg.image.load(f"assets/images/Weapon/{weapon_id}.png").convert_alpha()
            Weapon._cache[weapon_id] = pg.transform.smoothscale(img, (40, 40))
        self.icon = Weapon._cache[weapon_id]