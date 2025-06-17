# game/items/armor.py
import pygame as pg

class Armor:
    """Простейший объект брони."""
    _cache = {}           # чтобы не грузить один и тот же PNG много раз

    def __init__(self, armor_id: str, defense: int, durability: int = 999):
        """
        armor_id   – строка, совпадающая с именем PNG в assets/armor/
        defense    – сколько очков урона съедает до HP
        durability – сколько урона ещё выдержит (∞ = 999)
        """
        self.id = armor_id
        self.defense = defense
        self.durability = durability
        # — загружаем иконку один раз —
        if armor_id not in Armor._cache:
            img = pg.image.load(f"assets/images/armor/{armor_id}.png").convert_alpha()
            Armor._cache[armor_id] = pg.transform.smoothscale(img, (40, 40))
        self.icon = Armor._cache[armor_id]

    # ── логика износа ──────────────────────────────────────────────
    def absorb_damage(self, raw: int) -> int:
        """Возвращает, сколько урона пройдёт сквозь броню."""
        blocked = min(self.defense, raw)
        actual  = raw - blocked
        self.durability = max(0, self.durability - blocked)
        return actual