class state:
    def __init__(self):
        self.menu = True
        self.lobby = False
        self.game = False

    def start_lobby(self):
        self.menu = False
        self.lobby = True
        self.game = False

    def start_game(self):
        self.menu = False
        self.lobby = False
        self.game = True

    def start_menu(self):
        self.menu = True
        self.lobby = False
        self.game = False