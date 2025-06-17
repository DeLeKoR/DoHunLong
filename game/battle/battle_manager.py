import pygame as pg
import random
from setings import GAME_WIDTH, SCREEN_HEIGHT

class DamageText:
    def __init__(self, text, pos, color=(255, 200, 0), font_size=36):
        self.text = str(text)
        self.pos = [pos[0], pos[1]]
        self.color = color
        self.alpha = 255
        self.velocity = -50  # pixels per second upward
        self.font = pg.font.Font(None, font_size)
        self.image = self.font.render(self.text, True, self.color)
        self.image.set_alpha(self.alpha)
        self.rect = self.image.get_rect(center=self.pos)

    def update(self, dt):
        # Move up
        self.pos[1] += self.velocity * dt
        # Fade out
        fade_rate = 200  # alpha units per second
        self.alpha = max(0, self.alpha - fade_rate * dt)
        self.image = self.font.render(self.text, True, self.color)
        self.image.set_alpha(int(self.alpha))
        self.rect = self.image.get_rect(center=(int(self.pos[0]), int(self.pos[1])))

    def is_dead(self):
        return self.alpha <= 0

class Battle:
    def __init__(self, player, monster):
        width = GAME_WIDTH - 100
        height = SCREEN_HEIGHT - 100
        self.surface = pg.Surface((width, height), pg.SRCALPHA).convert_alpha()
        self.player = player
        self.monster = monster
        # Reset combat stats
        self.player.reset_battle_stats()
        self.monster.reset_battle_stats()
        # Active damage pop-ups
        self.damage_texts = []

    def draw(self, screen):
        # Clear battle surface
        self.surface.fill((0, 0, 0))

        # Draw fighters
        sw, sh = self.surface.get_size()
        img_h = int(sh * 0.3)
        # Hero image
        pr = self.player.image.get_width() / self.player.image.get_height()
        pw = int(img_h * pr)
        p_img = pg.transform.scale(self.player.image, (pw, img_h))
        # Monster image
        mr = self.monster.image.get_width() / self.monster.image.get_height()
        mw = int(img_h * mr)
        m_img = pg.transform.scale(self.monster.image, (mw, img_h))

        # Positions
        hero_pos = (int(sw * 0.3 - pw / 2), sh // 2 - img_h // 2)
        mon_pos  = (int(sw * 0.7 - mw / 2), sh // 2 - img_h // 2)

        self.surface.blit(p_img, hero_pos)
        self.surface.blit(m_img, mon_pos)

        # Draw damage texts only
        for dmg in self.damage_texts:
            self.surface.blit(dmg.image, dmg.rect)

        # Blit to screen
        screen.blit(self.surface, (50, 50))

    def update(self, dt):
        # Update gauges
        self.player.gauge = min(self.player.gauge + self.player.gauge_speed * dt, self.player.gauge_max)
        self.monster.gauge = min(self.monster.gauge + self.monster.gauge_speed * dt, self.monster.gauge_max)
        # Player attack
        if self.player.gauge >= self.player.gauge_max:
            damage = self.player.attack(self.monster)
            self.player.gauge = 0
            # Calculate monster position
            sw, sh = self.surface.get_size()
            img_h = int(sh * 0.3)
            mr = self.monster.image.get_width() / self.monster.image.get_height()
            mw = int(img_h * mr)
            mon_x = int(sw * 0.7 - mw / 2)
            mon_y = sh // 2 - img_h // 2
            x = mon_x + mw // 2 + random.randint(-10, 10)
            y = mon_y + random.randint(0, 10)
            # Show damage or miss
            if damage > 0:
                self.damage_texts.append(DamageText(damage, (x, y)))
            else:
                self.damage_texts.append(DamageText("промах", (x, y), color=(255,255,255)))
        # Monster attack
        if self.monster.hp > 0 and self.monster.gauge >= self.monster.gauge_max:
            damage = self.monster.attack(self.player)
            self.monster.gauge = 0
            # Calculate hero position
            sw, sh = self.surface.get_size()
            img_h = int(sh * 0.3)
            pr = self.player.image.get_width() / self.player.image.get_height()
            pw = int(img_h * pr)
            hero_x = int(sw * 0.3 - pw / 2)
            hero_y = sh // 2 - img_h // 2
            x = hero_x + pw // 2 + random.randint(-10, 10)
            y = hero_y + random.randint(0, 10)
            if damage > 0:
                self.damage_texts.append(DamageText(damage, (x, y)))
            else:
                self.damage_texts.append(DamageText("промах", (x, y), color=(255,255,255)))
        # Update damage texts
        for dmg in self.damage_texts[:]:
            dmg.update(dt)
            if dmg.is_dead():
                self.damage_texts.remove(dmg)
        # Continue battle?
        return not (self.player.hp <= 0 or self.monster.hp <= 0)
