import pygame as pg
from setings import SND

pg.mixer.init()                       # инициализация

# отдельный канал для эффектов
SFX_CH = pg.mixer.Channel(3)

def play_music(key: str, loop: bool = True):
    """Фоновая музыка — через pg.mixer.music."""
    pg.mixer.music.stop()
    pg.mixer.music.load(SND[key])
    pg.mixer.music.play(-1 if loop else 0)

def play_sfx(key: str, volume: float = 1.0):
    """Разовый эффект — через выделенный канал."""
    sound = pg.mixer.Sound(SND[key])
    sound.set_volume(volume)
    SFX_CH.play(sound)