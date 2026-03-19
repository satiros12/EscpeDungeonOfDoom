import math
import pygame as pg
from ..data.config import *


class RayCaster:
    def __init__(self, game):
        self.game = game
        self.ray_casting_result = []
        self.objects_to_render = []
        self.textures = game.renderer.wall_textures if game.renderer else {}
        self.world_map = {}
        self.torches = []
        self._build_world_map()

    def _build_world_map(self):
        self.world_map = {}
        if self.game.map:
            for j, row in enumerate(self.game.map.tiles):
                for i, value in enumerate(row):
                    if value:
                        self.world_map[(i, j)] = value

        self.torches = []
        if self.game.map:
            from ..data.entity import TorchDef

            for entity in self.game.map.entities:
                if isinstance(entity, TorchDef):
                    self.torches.append(entity)

    def get_objects_to_render(self):
        self.objects_to_render = []
        for ray, values in enumerate(self.ray_casting_result):
            depth, proj_height, texture, offset = values

            brightness = self._calculate_light(ray, depth)

            if proj_height < RES[1]:
                tex = self.textures.get(texture, self.textures.get(1))
                wall_column = tex.subsurface(
                    offset * (TEXTURE_SIZE - SCALE), 0, SCALE, TEXTURE_SIZE
                )
                wall_column = pg.transform.scale(wall_column, (SCALE, proj_height))
                wall_pos = (ray * SCALE, HALF_HEIGHT - proj_height // 2)
            else:
                texture_height = TEXTURE_SIZE * RES[1] / proj_height
                tex = self.textures.get(texture, self.textures.get(1))
                wall_column = tex.subsurface(
                    offset * (TEXTURE_SIZE - SCALE),
                    HALF_TEXTURE_SIZE - texture_height // 2,
                    SCALE,
                    texture_height,
                )
                wall_column = pg.transform.scale(wall_column, (SCALE, RES[1]))
                wall_pos = (ray * SCALE, 0)

            self.objects_to_render.append((depth, wall_column, wall_pos, brightness))

    def _calculate_light(self, ray, depth):
        if not self.torches:
            return 1.0

        ray_angle = self.game.player.angle - HALF_FOV + ray * DELTA_ANGLE
        ray_x = self.game.player.x + depth * math.cos(ray_angle)
        ray_y = self.game.player.y + depth * math.sin(ray_angle)

        max_brightness = 1.0
        for torch in self.torches:
            dist = math.hypot(torch.x - ray_x, torch.y - ray_y)
            if dist < torch.light_radius:
                if self._is_line_of_sight(torch.x, torch.y, ray_x, ray_y):
                    brightness = 1.0 - (dist / torch.light_radius)
                    brightness = max(brightness, 0.3)
                    max_brightness = max(max_brightness, brightness)

        return max_brightness

    def _is_line_of_sight(self, x1, y1, x2, y2):
        steps = int(math.hypot(x2 - x1, y2 - y1) * 2)
        if steps == 0:
            return True

        dx = (x2 - x1) / steps
        dy = (y2 - y1) / steps

        for i in range(steps):
            check_x = int(x1 + dx * i)
            check_y = int(y1 + dy * i)
            if (check_x, check_y) in self.world_map:
                return False
        return True

    def ray_cast(self):
        self.ray_casting_result = []
        texture_vert, texture_hor = 1, 1
        ox, oy = self.game.player.pos
        x_map, y_map = self.game.player.map_pos

        ray_angle = self.game.player.angle - HALF_FOV + 0.0001
        for ray in range(NUM_RAYS):
            sin_a = math.sin(ray_angle)
            cos_a = math.cos(ray_angle)

            y_hor, dy = (y_map + 1, 1) if sin_a > 0 else (y_map - 1e-6, -1)
            depth_hor = (y_hor - oy) / sin_a
            x_hor = ox + depth_hor * cos_a
            delta_depth = dy / sin_a
            dx = delta_depth * cos_a

            for i in range(MAX_DEPTH):
                tile_hor = int(x_hor), int(y_hor)
                if tile_hor in self.world_map:
                    texture_hor = self.world_map[tile_hor]
                    break
                x_hor += dx
                y_hor += dy
                depth_hor += delta_depth

            x_vert, dx = (x_map + 1, 1) if cos_a > 0 else (x_map - 1e-6, -1)
            depth_vert = (x_vert - ox) / cos_a
            y_vert = oy + depth_vert * sin_a
            delta_depth = dx / cos_a
            dy = delta_depth * sin_a

            for i in range(MAX_DEPTH):
                tile_vert = int(x_vert), int(y_vert)
                if tile_vert in self.world_map:
                    texture_vert = self.world_map[tile_vert]
                    break
                x_vert += dx
                y_vert += dy
                depth_vert += delta_depth

            if depth_vert < depth_hor:
                depth, texture = depth_vert, texture_vert
                y_vert %= 1
                offset = y_vert if cos_a > 0 else (1 - y_vert)
            else:
                depth, texture = depth_hor, texture_hor
                x_hor %= 1
                offset = (1 - x_hor) if sin_a > 0 else x_hor

            depth *= math.cos(self.game.player.angle - ray_angle)
            proj_height = SCREEN_DIST / (depth + 0.0001)
            self.ray_casting_result.append((depth, proj_height, texture, offset))
            ray_angle += DELTA_ANGLE

    def update(self):
        self._build_world_map()
        self.ray_cast()
        self.get_objects_to_render()
