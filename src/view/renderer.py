import pygame as pg
from ..data.config import *


class Renderer:
    def __init__(self, game):
        self.game = game
        self.wall_textures = {}
        self.floor_texture = None
        self._load_textures()

    def _load_textures(self):
        for i in range(1, 8):
            try:
                img = pg.image.load(f"resources/textures/{i}.png").convert()
                self.wall_textures[i] = img
            except:
                surf = pg.Surface((TEXTURE_SIZE, TEXTURE_SIZE))
                surf.fill((50 * i, 50 * i, 50 * i))
                self.wall_textures[i] = surf

        try:
            self.floor_texture = pg.image.load("resources/textures/floor.png").convert()
        except:
            self.floor_texture = pg.Surface((TEXTURE_SIZE, TEXTURE_SIZE))
            self.floor_texture.fill((30, 30, 30))

    def draw(self):
        self.game.screen.fill(FLOOR_COLOR)

        self._draw_walls()
        self._draw_sprites()

    def _draw_walls(self):
        for (
            depth,
            wall_image,
            wall_pos,
            brightness,
        ) in self.game.raycaster.objects_to_render:
            if wall_image.get_size() != (SCALE, RES[1]):
                continue

            if brightness < 1.0:
                wall_image = self._apply_brightness(wall_image, brightness)

            self.game.screen.blit(wall_image, wall_pos)

    def _apply_brightness(self, surface, factor):
        img = surface.copy()
        for x in range(img.get_width()):
            for y in range(img.get_height()):
                r, g, b, a = img.get_at((x, y))
                img.set_at(
                    (x, y), (int(r * factor), int(g * factor), int(b * factor), a)
                )
        return img

    def _draw_sprites(self):
        sprite_objects = sorted(
            self.game.raycaster.objects_to_render, key=lambda x: x[0], reverse=True
        )

        for depth, image, pos in sprite_objects:
            if image.get_size()[1] < RES[1]:
                self.game.screen.blit(image, pos)

    def player_damage(self):
        self.game.screen.fill((255, 0, 0))
        pg.display.flip()
        pg.time.delay(50)

    def game_over(self):
        self.game.screen.fill((100, 0, 0))
        font = pg.font.Font(None, 64)
        text = font.render("GAME OVER", True, (255, 0, 0))
        rect = text.get_rect(center=(HALF_WIDTH, HALF_HEIGHT))
        self.game.screen.blit(text, rect)
