SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 750
SCREEN_CENTER = (SCREEN_WIDTH//2, SCREEN_HEIGHT//2)
SCREEN_CENTER_X = SCREEN_WIDTH//2
SCREEN_CENTER_Y = SCREEN_HEIGHT//2
SCREEN_SIZE = (SCREEN_WIDTH, SCREEN_HEIGHT)
PANEL_WIDTH = 260
GAME_WIDTH = SCREEN_WIDTH - PANEL_WIDTH
GAME_CENTER_X = GAME_WIDTH // 2
GAME_CENTER_Y = SCREEN_HEIGHT//2
FLOOR_IDS = {11}
FREE = 12
# ─── звуки ──────────────────────────────────────────────
SND_DIR = "assets/sounds/"
SND = {
    "menu"      : SND_DIR + "menu.mp3",
    "main_game" : SND_DIR + "main_game.mp3",
    "fight"     : SND_DIR + "fight!.mp3",
    "hit"       : SND_DIR + "hit_ph.mp3",
    "low_hp"    : SND_DIR + "low_hp.mp3",
    "game_over" : SND_DIR + "game_over.mp3",
}