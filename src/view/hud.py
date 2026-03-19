import pygame as pg
from ..data.config import *


class HUD:
    def __init__(self, game):
        self.game = game
        self.font = pg.font.Font(None, 36)

    def draw(self):
        self._draw_health_bar()
        self._draw_weapon_info()

    def _draw_health_bar(self):
        health = self.game.player.health
        max_health = PLAYER_MAX_HEALTH

        bar_width = 200
        bar_height = 20
        bar_x = 20
        bar_y = RES[1] - 40

        pg.draw.rect(
            self.game.screen, (100, 0, 0), (bar_x, bar_y, bar_width, bar_height)
        )

        health_width = int(bar_width * (health / max_health))
        if health_width > 0:
            pg.draw.rect(
                self.game.screen, (255, 0, 0), (bar_x, bar_y, health_width, bar_height)
            )

        text = self.font.render(f"Health: {health}", True, (255, 255, 255))
        self.game.screen.blit(text, (bar_x, bar_y - 25))

    def _draw_weapon_info(self):
        if self.game.weapon.reloading:
            text = self.font.render("RELOADING...", True, (255, 255, 0))
            self.game.screen.blit(text, (RES[0] - 200, RES[1] - 40))
