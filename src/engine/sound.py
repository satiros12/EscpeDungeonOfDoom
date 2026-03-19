import pygame as pg
import os


class Sound:
    def __init__(self, game):
        pg.mixer.init()

        self.shotgun = None
        self.player_pain = None
        self.music = None

        self._load_sounds()

    def _load_sounds(self):
        try:
            self.shotgun = pg.mixer.Sound("resources/sound/shotgun.wav")
        except:
            pass

        try:
            self.player_pain = pg.mixer.Sound("resources/sound/player_pain.wav")
        except:
            pass

        try:
            pg.mixer.music.load("resources/sound/theme.mp3")
            self.music = pg.mixer.music
        except:
            pass
