import math
import pygame as pg
from ..data.config import *


class Player:
    def __init__(self, game):
        self.game = game
        self.x, self.y, self.angle = game.map.player_start
        self.health = PLAYER_MAX_HEALTH
        self.shot = False
        self.reloading = False
        self.health_recovery_delay = 700
        self.time_prev = pg.time.get_ticks()
        self.diag_move_corr = 1 / math.sqrt(2)

    def recover_health(self):
        if self.check_health_recovery_delay() and self.health < PLAYER_MAX_HEALTH:
            self.health += 1

    def check_health_recovery_delay(self):
        time_now = pg.time.get_ticks()
        if time_now - self.time_prev > self.health_recovery_delay:
            self.time_prev = time_now
            return True

    def check_game_over(self):
        if self.health < 1:
            self.game.renderer.game_over()
            pg.display.flip()
            pg.time.delay(1500)
            self.game.set_state("menu")

    def get_damage(self, damage):
        self.health -= damage
        self.game.renderer.player_damage()
        if self.game.sound.player_pain:
            self.game.sound.player_pain.play()
        self.check_game_over()

    def single_fire_event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN:
            if event.button == 1 and not self.shot and not self.game.weapon.reloading:
                if self.game.sound.shotgun:
                    self.game.sound.shotgun.play()
                self.shot = True
                self.game.weapon.reloading = True
                self.check_door_activation()

    def check_door_activation(self):
        if not self.game.map.exit_door:
            return

        door = self.game.map.exit_door
        dist = math.hypot(door.x - self.x, door.y - self.y)

        if dist < 1.5:
            if door.next_map:
                next_map_path = self.game.maps_dir / door.next_map
                if next_map_path.exists():
                    self.game.load_map(str(next_map_path))
            elif self.game.map.is_final:
                self.game.set_state("win")

    def movement(self):
        sin_a = math.sin(self.angle)
        cos_a = math.cos(self.angle)
        dx, dy = 0, 0
        speed = PLAYER_SPEED * self.game.delta_time
        speed_sin = speed * sin_a
        speed_cos = speed * cos_a

        keys = pg.key.get_pressed()
        num_key_pressed = -1
        if keys[pg.K_w]:
            num_key_pressed += 1
            dx += speed_cos
            dy += speed_sin
        if keys[pg.K_s]:
            num_key_pressed += 1
            dx += -speed_cos
            dy += -speed_sin
        if keys[pg.K_a]:
            num_key_pressed += 1
            dx += speed_sin
            dy += -speed_cos
        if keys[pg.K_d]:
            num_key_pressed += 1
            dx += -speed_sin
            dy += speed_cos

        if num_key_pressed:
            dx *= self.diag_move_corr
            dy *= self.diag_move_corr

        self.check_wall_collision(dx, dy)
        self.angle %= 2 * math.pi

    def check_wall(self, x, y):
        return (x, y) not in self.game.raycaster.world_map

    def check_wall_collision(self, dx, dy):
        scale = PLAYER_SIZE_SCALE / self.game.delta_time
        if self.check_wall(int(self.x + dx * scale), int(self.y)):
            self.x += dx
        if self.check_wall(int(self.x), int(self.y + dy * scale)):
            self.y += dy

    def mouse_control(self):
        mx, my = pg.mouse.get_pos()
        if mx < MOUSE_BORDER_LEFT or mx > MOUSE_BORDER_RIGHT:
            pg.mouse.set_pos([HALF_WIDTH, HALF_HEIGHT])
        self.rel = pg.mouse.get_rel()[0]
        self.rel = max(-MOUSE_MAX_REL, min(MOUSE_MAX_REL, self.rel))
        self.angle += self.rel * MOUSE_SENSITIVITY * self.game.delta_time

    def update(self):
        self.movement()
        self.mouse_control()
        self.recover_health()

    @property
    def pos(self):
        return self.x, self.y

    @property
    def map_pos(self):
        return int(self.x), int(self.y)
