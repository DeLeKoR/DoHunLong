import os
import pygame as pg
import random
from setings import GAME_WIDTH, SCREEN_HEIGHT
from game.sound_manager import play_sfx

_BG_PATH = "assets/images/Fight screen/Fight screen Bottom part.png"
_FG_PATH = "assets/images/Fight screen/Fight screen Upper part.png"


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
    _bg_layer = None
    _fg_layer = None

    @classmethod
    def _ensure_layers(cls):
        """Лениво загружает фоновые слои."""
        if cls._bg_layer is not None and cls._fg_layer is not None:
            return

        def _safe_load(path, fallback_color):
            if not pg.display.get_init():
                raise RuntimeError("Display not initialised before loading images")
            try:
                surf = pg.image.load(path).convert_alpha()
                surf = pg.transform.scale(surf, (GAME_WIDTH, SCREEN_HEIGHT))
                return surf
            except FileNotFoundError:
                tmp = pg.Surface((GAME_WIDTH, SCREEN_HEIGHT), pg.SRCALPHA)
                tmp.fill(fallback_color)
                return tmp

        cls._bg_layer = _safe_load(_BG_PATH, (0, 0, 0))
        cls._fg_layer = _safe_load(_FG_PATH, (0, 0, 0, 0))

    def __init__(self, player, monster):
        width, height = GAME_WIDTH, SCREEN_HEIGHT
        self.surface = pg.Surface((width, height), pg.SRCALPHA).convert_alpha()
        self.player = player
        self.monster = monster

        # ── Загружаем анимацию боя и настраиваем таймеры ──
        for fighter in (self.player, self.monster):
            scale = 1.0
            fighter._fight_frames = self._load_anim_strip(fighter.fight_prefix, scale)
            fighter._fight_idx = 0
            fighter._fight_delay_ms = 150
            fighter._fight_timer = pg.time.get_ticks()
            if not fighter._fight_frames:
                fighter._fight_frames = [fighter.image]
            # настройка «атака-анимация»
            fighter.attack_anim_len = len(fighter._fight_frames) * fighter._fight_delay_ms
            fighter.attack_anim_ms = 0

        # Сброс боевых параметров
        self.player.reset_battle_stats()
        self.monster.reset_battle_stats()

        # Поп-апы урона
        self.damage_texts = []

    def _load_anim_strip(self, prefix, scale=1.0):
        """Загружает кадры '<prefix> N.png' последовательно."""
        frames = []
        i = 0
        while True:
            path = f"{prefix} {i}.png"
            if not os.path.exists(path):
                break
            img = pg.image.load(path).convert_alpha()
            if scale != 1.0:
                w, h = img.get_size()
                img = pg.transform.smoothscale(img, (int(w * scale), int(h * scale)))
            frames.append(img)
            i += 1
        return frames

    def _trigger_attack_anim(self, fighter):
        """Запустить анимацию ударного цикла."""
        fighter.attack_anim_ms = fighter.attack_anim_len
        fighter._fight_idx = 0
        fighter._fight_timer = pg.time.get_ticks()

    def _current_frame(self, fighter):
        """Выбрать кадр: если идёт анимация удара — циклически, иначе статичный первый."""
        if fighter.attack_anim_ms > 0:
            now = pg.time.get_ticks()
            if now - fighter._fight_timer >= fighter._fight_delay_ms:
                fighter._fight_timer = now
                fighter._fight_idx = (fighter._fight_idx + 1) % len(fighter._fight_frames)
            return fighter._fight_frames[fighter._fight_idx]
        return fighter._fight_frames[0] if fighter._fight_frames else fighter.image

    def draw(self, screen):
        # Фон
        Battle._ensure_layers()
        self.surface.blit(Battle._bg_layer, (0, 0))

        # Получаем текущие кадры бойцов
        p_surface = self._current_frame(self.player)
        m_surface = self._current_frame(self.monster)

        sw, sh = self.surface.get_size()
        img_h = int(sh * 0.45)

        pr = p_surface.get_width() / p_surface.get_height()
        mr = m_surface.get_width() / m_surface.get_height()
        pw = int(img_h * pr)
        mw = int(img_h * mr)

        p_img = pg.transform.scale(p_surface, (pw, img_h))
        m_img = pg.transform.scale(m_surface, (mw, img_h))

        # Позиции
        hero_pos = (int(sw * 0.3 - pw / 2), sh // 2 - img_h // 2)
        mon_pos = (int(sw * 0.7 - mw / 2), sh // 2 - img_h // 2)

        self.surface.blit(p_img, hero_pos)
        self.surface.blit(m_img, mon_pos)

        # Тексты урона
        for dmg in self.damage_texts:
            self.surface.blit(dmg.image, dmg.rect)

        # Фронтальная «плёнка»
        self.surface.blit(Battle._fg_layer, (0, 0))

        # Рисуем на экран
        screen.blit(self.surface, (0, 0))

    def update(self, dt):
        # 1) корректируем оставшееся время анимации удара (dt в секундах → мс)
        dt_ms = dt * 1000
        for f in (self.player, self.monster):
            if f.attack_anim_ms > 0:
                f.attack_anim_ms = max(0, f.attack_anim_ms - dt_ms)

        # 2) заполняем шкалы
        self.player.gauge = min(self.player.gauge + self.player.gauge_speed * dt,
                                self.player.gauge_max)
        self.monster.gauge = min(self.monster.gauge + self.monster.gauge_speed * dt,
                                 self.monster.gauge_max)

        # 3) ход игрока
        if self.player.gauge >= self.player.gauge_max:
            damage = self.player.attack(self.monster)
            self.player.gauge = 0
            self._trigger_attack_anim(self.player)

            sw, sh = self.surface.get_size()
            img_h = int(sh * 0.3)
            mr = self.monster.image.get_width() / self.monster.image.get_height()
            mw = int(img_h * mr)
            mon_x = int(sw * 0.7 - mw / 2)
            mon_y = sh // 2 - img_h // 2
            x = mon_x + mw // 2 + random.randint(-10, 10)
            y = mon_y + random.randint(0, 10)
            txt = DamageText(damage if damage > 0 else "промах",
                             (x, y),
                             color=(255, 200, 0) if damage > 0 else (255, 255, 255))
            play_sfx("hit")
            self.damage_texts.append(txt)

        # 4) ход монстра
        if self.monster.hp > 0 and self.monster.gauge >= self.monster.gauge_max:
            damage = self.monster.attack(self.player)
            self.monster.gauge = 0
            self._trigger_attack_anim(self.monster)

            sw, sh = self.surface.get_size()
            img_h = int(sh * 0.3)
            pr = self.player.image.get_width() / self.player.image.get_height()
            pw = int(img_h * pr)
            hero_x = int(sw * 0.3 - pw / 2)
            hero_y = sh // 2 - img_h // 2
            x = hero_x + pw // 2 + random.randint(-10, 10)
            y = hero_y + random.randint(0, 10)
            txt = DamageText(damage if damage > 0 else "промах",
                             (x, y),
                             color=(255, 200, 0) if damage > 0 else (255, 255, 255))
            play_sfx("hit")
            self.damage_texts.append(txt)

        # 5) обновляем и убираем «мертвые» тексты
        for dmg in self.damage_texts[:]:
            dmg.update(dt)
            if dmg.is_dead():
                self.damage_texts.remove(dmg)

        # 6) возвращаем False, если бой окончен
        return not (self.player.hp <= 0 or self.monster.hp <= 0)