import pygame as pg
from ..data.config import *


class Weapon:
    def __init__(self, game):
        self.game = game
        self.reloading = False
        self.reload_time = 1000
        self.animation_time = 200
        self.time_prev = 0
        self.frame_index = 0

        self.weapon_sprites = []
        self._load_weapon_sprites()

    def _load_weapon_sprites(self):
        try:
            for i in range(5):
                img = pg.image.load(
                    f"resources/sprites/weapon/shotgun/{i}.png"
                ).convert_alpha()
                self.weapon_sprites.append(img)
        except:
            self.weapon_sprites = [pg.Surface((200, 200))]

    def draw(self):
        if not self.weapon_sprites:
            return

        if self.reloading:
            frame = min(self.frame_index, len(self.weapon_sprites) - 1)
            sprite = self.weapon_sprites[frame]
            self.game.screen.blit(sprite, (HALF_WIDTH - 100, RES[1] - 200))

    def update(self):
        if self.reloading:
            time_now = pg.time.get_ticks()
            if time_now - self.time_prev > self.animation_time:
                self.time_prev = time_now
                self.frame_index += 1
                if self.frame_index >= len(self.weapon_sprites):
                    self.reloading = False
                    self.frame_index = 0
