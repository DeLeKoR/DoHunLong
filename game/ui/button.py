import pygame as pg
from pygame.display import update


class Button:
    def __init__(self, cords, text, font, idle_color, hover_color, callback):
        self.cords = cords
        self.text = text
        self.font = pg.font.Font('assets/Fonts/Arial Black.ttf', 48)
        self.idle_color = idle_color
        self.hover_color = hover_color
        self.color = (255, 255, 255)
        self.callback = callback
        self.hovered = False
        self.render_text()

    def render_text(self):
        self.text_surf = self.font.render(self.text, True, (self.color))
        self.text_rect = self.text_surf.get_rect()
        self.text_rect.center = self.cords

    def update(self, mouse_pos):
        if self.text_rect.collidepoint(mouse_pos):
            self.hovered = True
            self.text_surf = self.font.render(self.text, True, (200, 200, 200))
        else:
            self.text_surf = self.font.render(self.text, True, (255, 255, 255))
            self.hovered = False

    def call(self):
        self.callback()


    def draw(self, surface, mouth_pos):
        self.update(mouth_pos)
        surface.blit(self.text_surf, self.text_rect)
