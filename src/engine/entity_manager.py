import math
import random
from ..data.entity import NPCDef, StaticDef


class EntityManager:
    def __init__(self, game):
        self.game = game
        self.sprites = []
        self.npcs = []

        if game.map:
            self._spawn_entities()

    def _spawn_entities(self):
        for entity in self.game.map.entities:
            if isinstance(entity, NPCDef):
                npc = NPC(self.game, entity)
                self.npcs.append(npc)
            elif isinstance(entity, StaticDef):
                if entity.animated:
                    sprite = AnimatedSprite(self.game, entity)
                else:
                    sprite = SpriteObject(self.game, entity)
                self.sprites.append(sprite)

    def update(self):
        for sprite in self.sprites:
            sprite.update()

        for npc in self.npcs:
            npc.update()

    def get_visible_objects(self, player):
        all_objects = []

        for sprite in self.sprites:
            sprite.get_sprite()
            all_objects.extend(
                self.game.raycaster.objects_to_render[-len(self.sprites) :]
            )

        for npc in self.npcs:
            npc.get_sprite()
            all_objects.extend(self.game.raycaster.objects_to_render[-1:])

        return all_objects

    def check_npc_attacks(self):
        for npc in self.npcs:
            if npc.state == "attack":
                dist = math.hypot(
                    npc.x - self.game.player.x, npc.y - self.game.player.y
                )
                if dist < 1.0:
                    self.game.player.get_damage(npc.attack_damage)


class SpriteObject:
    def __init__(self, game, entity):
        self.game = game
        self.player = game.player
        self.x = entity.x
        self.y = entity.y

        sprite_path = f"resources/sprites/static_sprites/{entity.sprite}.png"
        try:
            import pygame as pg

            self.image = pg.image.load(sprite_path).convert_alpha()
        except:
            self.image = None

        if self.image:
            self.image_width = self.image.get_width()
            self.image_half_width = self.image.get_width() // 2
            self.image_ratio = self.image_width / self.image.get_height()
        else:
            self.image_width = 64
            self.image_half_width = 32
            self.image_ratio = 1.0

        self.dx = 0
        self.dy = 0
        self.theta = 0
        self.screen_x = 0
        self.dist = 1
        self.norm_dist = 1
        self.sprite_half_width = 0

        self.scale = 0.7
        self.height_shift = 0.27

    def get_sprite_projection(self):
        proj = SCREEN_DIST / self.norm_dist * self.scale
        proj_width = proj * self.image_ratio
        proj_height = proj

        if self.image:
            image = pg.transform.scale(self.image, (proj_width, proj_height))
        else:
            import pygame as pg

            image = pg.Surface((proj_width, proj_height))
            image.fill((100, 100, 100))

        self.sprite_half_width = proj_width // 2
        height_shift = proj_height * self.height_shift
        pos = (
            self.screen_x - self.sprite_half_width,
            HALF_HEIGHT - proj_height // 2 + height_shift,
        )

        self.game.raycaster.objects_to_render.append((self.norm_dist, image, pos))

    def get_sprite(self):
        self.dx = self.x - self.player.x
        self.dy = self.y - self.player.y
        self.theta = math.atan2(self.dy, self.dx)

        delta = self.theta - self.player.angle
        if (self.dx > 0 and self.player.angle > math.pi) or (
            self.dx < 0 and self.dy < 0
        ):
            delta += 2 * math.pi

        delta_rays = delta / DELTA_ANGLE
        self.screen_x = (HALF_NUM_RAYS + delta_rays) * SCALE

        self.dist = math.hypot(self.dx, self.dy)
        self.norm_dist = self.dist * math.cos(delta)

        if (
            -self.image_half_width < self.screen_x < (RES[0] + self.image_half_width)
            and self.norm_dist > 0.5
        ):
            self.get_sprite_projection()

    def update(self):
        self.get_sprite()


class AnimatedSprite(SpriteObject):
    def __init__(self, game, entity):
        super().__init__(game, entity)
        self.animation_time = 120
        self.path = f"resources/sprites/animated_sprites/{entity.color}_light"
        self.scale = 0.8
        self.height_shift = 0.16

        try:
            import pygame as pg
            from collections import deque

            self.images = self._get_images(self.path)
            self.images = deque(self.images)
            self.image = self.images[0]
            self.image_width = self.image.get_width()
            self.image_half_width = self.image.get_width() // 2
            self.image_ratio = self.image_width / self.image.get_height()
        except:
            self.images = []

        self.animation_time_prev = 0
        self.animation_trigger = False

    def _get_images(self, path):
        import pygame as pg

        images = []
        for i in range(4):
            try:
                img = pg.image.load(f"{path}/{i}.png").convert_alpha()
                images.append(img)
            except:
                pass
        return images if images else [pg.Surface((64, 64))]

    def update(self):
        super().update()
        self._check_animation_time()
        self._animate()

    def _check_animation_time(self):
        import pygame as pg

        self.animation_trigger = False
        time_now = pg.time.get_ticks()
        if time_now - self.animation_time_prev > self.animation_time:
            self.animation_time_prev = time_now
            self.animation_trigger = True

    def _animate(self):
        if self.animation_trigger and self.images:
            self.images.rotate(-1)
            self.image = self.images[0]


class NPC:
    def __init__(self, game, entity: NPCDef):
        self.game = game
        self.type = entity.type
        self.x = entity.x
        self.y = entity.y
        self.health = entity.health
        self.patrol_points = entity.patrol
        self.current_patrol_idx = 0
        self.state = "idle"

        self.speed = 0.03
        self.size = 20
        self.attack_damage = 10
        self.alive = True

        self._load_sprites()

    def _load_sprites(self):
        import pygame as pg
        from collections import deque

        base_path = f"resources/sprites/npc/{self.type}"

        self.idle_images = self._load_animation_frames(f"{base_path}/idle")
        self.walk_images = self._load_animation_frames(f"{base_path}/walk")
        self.attack_images = self._load_animation_frames(f"{base_path}/attack")
        self.death_images = self._load_animation_frames(f"{base_path}/death")

        self.images = (
            deque(self.idle_images) if self.idle_images else [pg.Surface((64, 128))]
        )
        self.image = self.images[0]

        self.animation_time = 180
        self.animation_time_prev = 0

        self.image_width = self.image.get_width()
        self.image_half_width = self.image.get_width() // 2
        self.image_ratio = self.image_width / self.image.get_height()

        self.scale = 0.6
        self.height_shift = 0.38

    def _load_animation_frames(self, path):
        import pygame as pg

        frames = []
        for i in range(8):
            try:
                img = pg.image.load(f"{path}/{i}.png").convert_alpha()
                frames.append(img)
            except:
                try:
                    img = pg.image.load(f"{path}/0.png").convert_alpha()
                    frames.append(img)
                except:
                    pass
        return frames

    def get_sprite(self):
        import pygame as pg
        from ..data.config import (
            SCREEN_DIST,
            HALF_HEIGHT,
            HALF_NUM_RAYS,
            DELTA_ANGLE,
            RES,
            SCALE,
            RES as RESOLUTION,
        )

        dx = self.x - self.game.player.x
        dy = self.y - self.game.player.y
        theta = math.atan2(dy, dx)

        delta = theta - self.game.player.angle
        if (dx > 0 and self.game.player.angle > math.pi) or (dx < 0 and dy < 0):
            delta += 2 * math.pi

        delta_rays = delta / DELTA_ANGLE
        screen_x = (HALF_NUM_RAYS + delta_rays) * SCALE

        dist = math.hypot(dx, dy)
        norm_dist = dist * math.cos(delta)

        if (
            -self.image_half_width < screen_x < (RES[0] + self.image_half_width)
            and norm_dist > 0.5
        ):
            proj = SCREEN_DIST / norm_dist * self.scale
            proj_width = proj * self.image_ratio
            proj_height = proj

            image = pg.transform.scale(self.image, (proj_width, proj_height))
            sprite_half_width = proj_width // 2
            height_shift = proj_height * self.height_shift
            pos = (
                screen_x - sprite_half_width,
                HALF_HEIGHT - proj_height // 2 + height_shift,
            )

            self.game.raycaster.objects_to_render.append((norm_dist, image, pos))

    def update(self):
        self._check_animation_time()
        self._run_logic()
        self._animate()
        self.get_sprite()

    def _check_animation_time(self):
        import pygame as pg

        time_now = pg.time.get_ticks()
        if time_now - self.animation_time_prev > self.animation_time:
            self.animation_time_prev = time_now
            self.animation_trigger = True
        else:
            self.animation_trigger = False

    def _animate(self):
        if self.animation_trigger and hasattr(self, "images") and self.images:
            self.images.rotate(-1)
            self.image = self.images[0]

    def _run_logic(self):
        player_pos = self.game.player.pos

        if self.patrol_points:
            dist_to_player = math.hypot(player_pos[0] - self.x, player_pos[1] - self.y)

            if dist_to_player < 5:
                self.state = "chase"
                self._move_toward(player_pos[0], player_pos[1])
            else:
                self.state = "patrol"
                self._follow_patrol()
        else:
            dist_to_player = math.hypot(player_pos[0] - self.x, player_pos[1] - self.y)
            if dist_to_player < 5:
                self.state = "chase"
                self._move_toward(player_pos[0], player_pos[1])

    def _move_toward(self, target_x, target_y):
        angle = math.atan2(target_y - self.y, target_x - self.x)
        dx = math.cos(angle) * self.speed
        dy = math.sin(angle) * self.speed

        if not self._check_wall(int(self.x + dx * self.size), int(self.y)):
            self.x += dx
        if not self._check_wall(int(self.x), int(self.y + dy * self.size)):
            self.y += dy

    def _follow_patrol(self):
        if not self.patrol_points:
            return

        target = self.patrol_points[self.current_patrol_idx]
        dist = math.hypot(target[0] - self.x, target[1] - self.y)

        if dist < 0.5:
            self.current_patrol_idx = (self.current_patrol_idx + 1) % len(
                self.patrol_points
            )
            target = self.patrol_points[self.current_patrol_idx]

        self._move_toward(target[0], target[1])

    def _check_wall(self, x, y):
        return (x, y) in self.game.raycaster.world_map


SCREEN_DIST = None
HALF_HEIGHT = None
HALF_NUM_RAYS = None
DELTA_ANGLE = None
RES = None
SCALE = None


def _init_constants():
    global SCREEN_DIST, HALF_HEIGHT, HALF_NUM_RAYS, DELTA_ANGLE, RES, SCALE
    from ..data.config import (
        SCREEN_DIST as SD,
        HALF_HEIGHT as HH,
        HALF_NUM_RAYS as HNR,
        DELTA_ANGLE as DA,
        RES as R,
        SCALE as S,
    )

    SCREEN_DIST, HALF_HEIGHT, HALF_NUM_RAYS, DELTA_ANGLE, RES, SCALE = (
        SD,
        HH,
        HNR,
        DA,
        R,
        S,
    )


import pygame as pg

_init_constants()
del _init_constants
