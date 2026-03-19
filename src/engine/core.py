import pygame as pg
import sys
from pathlib import Path
from ..data.config import *
from ..data.map import MapData


class Game:
    def __init__(self):
        pg.init()
        self.screen = pg.display.set_mode(RES)
        pg.mouse.set_visible(False)
        pg.event.set_grab(True)
        self.clock = pg.time.Clock()
        self.delta_time = 1

        self.state = "menu"
        self.map: MapData = None
        self.maps_dir = Path("maps")

        self.global_trigger = False
        self.global_event = pg.USEREVENT + 0
        pg.time.set_timer(self.global_event, 40)

        self.player = None
        self.raycaster = None
        self.entity_manager = None
        self.pathfinding = None
        self.weapon = None
        self.sound = None
        self.renderer = None
        self.hud = None
        self.menu = None

        self.object_renderer = None

    def load_map(self, map_path: str):
        self.map = MapData.load(map_path)
        self.init_game_objects()

    def init_game_objects(self):
        from .player import Player
        from .raycaster import RayCaster
        from .entity_manager import EntityManager
        from .pathfinding import PathFinding
        from .weapon import Weapon
        from .sound import Sound
        from ..view.renderer import Renderer
        from ..view.hud import HUD

        self.player = Player(self)
        self.raycaster = RayCaster(self)
        self.entity_manager = EntityManager(self)
        self.pathfinding = PathFinding(self)
        self.weapon = Weapon(self)
        self.sound = Sound(self)
        self.renderer = Renderer(self)
        self.hud = HUD(self)

        if self.sound.music:
            self.sound.music.play(-1)

    def set_state(self, new_state: str):
        self.state = new_state
        if new_state == "menu":
            pg.mouse.set_visible(True)
        elif new_state in ("game", "preview"):
            pg.mouse.set_visible(False)

    def check_events(self):
        self.global_trigger = False
        events = pg.event.get()

        for event in events:
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    if self.state == "game":
                        self.set_state("menu")
                    elif self.state == "preview":
                        self.set_state("editor")
                    elif self.state == "win":
                        self.set_state("menu")
                    elif self.state == "menu":
                        pg.quit()
                        sys.exit()
            elif event.type == self.global_event:
                self.global_trigger = True

            if self.state == "game" and self.player:
                self.player.single_fire_event(event)

        return events

    def update(self):
        if self.state in ("game", "preview"):
            self.player.update()
            self.raycaster.update()
            self.entity_manager.update()
            self.weapon.update()

        self.delta_time = self.clock.tick(FPS)
        pg.display.set_caption(f"{self.clock.get_fps():.1f}")

    def draw(self):
        if self.state in ("game", "preview"):
            self.renderer.draw()
            if self.state == "game":
                self.weapon.draw()
                self.hud.draw()

    def run(self):
        while True:
            events = self.check_events()

            if self.state == "menu":
                if not self.menu:
                    from ..view.menu import Menu

                    self.menu = Menu(self)
                self.menu.handle_input(events)
                self.menu.draw(self.screen)
            elif self.state == "game":
                self.update()
                self.draw()
            elif self.state == "editor":
                self.run_editor()
            elif self.state == "win":
                self.draw_win_screen()

            pg.display.flip()

    def run_editor(self):
        from pathlib import Path
        import sys

        sys.path.insert(0, str(Path(__file__).parent.parent))
        from editor.editor import Editor

        editor = Editor()
        editor.run()

    def draw_win_screen(self):
        self.screen.fill((0, 0, 0))
        font = pg.font.Font(None, 128)
        text = font.render("YOU WIN!", True, (255, 255, 0))
        text_rect = text.get_rect(center=(HALF_WIDTH, HALF_HEIGHT - 50))
        self.screen.blit(text, text_rect)

        font_small = pg.font.Font(None, 48)
        hint = font_small.render("Press ESC to return to menu", True, (200, 200, 200))
        hint_rect = hint.get_rect(center=(HALF_WIDTH, HALF_HEIGHT + 50))
        self.screen.blit(hint, hint_rect)

    def new_game(self):
        self.init_game_objects()
        if self.sound.music:
            self.sound.music.play(-1)
