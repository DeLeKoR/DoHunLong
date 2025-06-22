import pygame as pg
class KeyItem:
    def __init__(self):
        img=pg.image.load("assets/images/key.png").convert_alpha()
        self.icon=pg.transform.smoothscale(img,(40,40))
        self.id="key"