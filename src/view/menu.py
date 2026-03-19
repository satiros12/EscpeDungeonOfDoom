import pygame as pg
from ..data.config import *


class Menu:
    def __init__(self, game):
        self.game = game
        self.options = ["Start Game", "Map Editor", "Quit"]
        self.selected = 0
        self.font_title = None
        self.font_options = None
        self._init_fonts()

    def _init_fonts(self):
        self.font_title = pg.font.Font(None, 128)
        self.font_options = pg.font.Font(None, 64)

    def handle_input(self, events=None):
        if events is None:
            events = pg.event.get()

        for event in events:
            if event.type == pg.QUIT:
                pg.quit()
                exit()
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_UP:
                    self.selected = (self.selected - 1) % len(self.options)
                elif event.key == pg.K_DOWN:
                    self.selected = (self.selected + 1) % len(self.options)
                elif event.key == pg.K_RETURN:
                    self._select_option()
                elif event.key == pg.K_w:
                    self.selected = (self.selected - 1) % len(self.options)
                elif event.key == pg.K_s:
                    self.selected = (self.selected + 1) % len(self.options)

    def _select_option(self):
        if self.selected == 0:
            self._start_game()
        elif self.selected == 1:
            self._open_editor()
        elif self.selected == 2:
            pg.quit()
            exit()

    def _start_game(self):
        map_path = self.game.maps_dir / "level1.json"
        if map_path.exists():
            self.game.load_map(str(map_path))
            self.game.set_state("game")
        else:
            print(f"Map not found: {map_path}")

    def _open_editor(self):
        self.game.set_state("editor")

    def draw(self, screen):
        screen.fill((20, 20, 30))

        title = self.font_title.render("ESCAPE DOOM", True, (200, 50, 50))
        title_rect = title.get_rect(center=(HALF_WIDTH, 150))
        screen.blit(title, title_rect)

        for i, option in enumerate(self.options):
            color = (255, 255, 0) if i == self.selected else (200, 200, 200)
            text = self.font_options.render(option, True, color)
            rect = text.get_rect(center=(HALF_WIDTH, 350 + i * 70))
            screen.blit(text, rect)

        hint = pg.font.Font(None, 32).render(
            "Use UP/DOWN to navigate, ENTER to select", True, (100, 100, 100)
        )
        hint_rect = hint.get_rect(center=(HALF_WIDTH, RES[1] - 50))
        screen.blit(hint, hint_rect)
