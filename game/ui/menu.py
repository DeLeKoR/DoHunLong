import pygame as pg
from setings import SCREEN_SIZE, SCREEN_CENTER_X, SCREEN_CENTER_Y
from game.ui.button import Button
from game.sound_manager import play_music


class Menu:
    def __init__(self, screen, dungeon_activ):
        play_music("menu")
        self.screen          = screen
        self.__start_game_cb = dungeon_activ
        self.active          = True
        self.screen = screen
        self.surface = pg.Surface(SCREEN_SIZE)
        self.surface.fill((100, 100, 100))
        self.buttons = []
        self.create_buttons()

    def __start_game(self):
        self.active = False
        self.__start_game_cb()

    def mouse_down(self, pos):
        for button in self.buttons:
            if button.hovered:
                button.call()

    def mouse_up(self, pos):
        pass

    def draw_menu(self, mouth_pos):
        self.surface.fill((0, 0, 0))
        for button in self.buttons:
            button.draw(self.surface, mouth_pos)
        self.screen.blit(self.surface,(0, 0))


    def update_menu(self, mouth_pos):
        pass

    def create_menu(self):
        pass

    def create_buttons(self):
        self.buttons.append(Button((SCREEN_CENTER_X, SCREEN_CENTER_Y),
                              'Начать игру',
                              True,
                              (255, 255, 255),
                              (150, 150, 150),
                              self.__start_game))
