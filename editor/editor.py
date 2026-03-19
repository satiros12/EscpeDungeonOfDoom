import pygame as pg
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data.map import MapData
from src.data.entity import (
    NPCDef,
    StaticDef,
    TorchDef,
    DoorDef,
    NPC_TYPES,
    STATIC_SPRITES,
    TORCH_COLORS,
)


class Editor:
    def __init__(self):
        pg.init()
        self.screen = pg.display.set_mode((1280, 800))
        pg.display.set_caption("EscapeDoom Map Editor")
        self.clock = pg.time.Clock()

        self.maps_dir = Path("maps")
        self.current_map = self._create_new_map("level1")

        self.tile_size = 32
        self.canvas_offset_x = 200
        self.canvas_offset_y = 60

        self.selected_tile = 1
        self.selected_entity_type = None
        self.selected_entity_data = None

        self.mode = "paint"
        self.path_mode = False
        self.selected_npc_for_path = None
        self.npc_paths = {}

        self.font = pg.font.Font(None, 24)

    def _create_new_map(self, name):
        tiles = [[0 for _ in range(16)] for _ in range(16)]

        for i in range(16):
            tiles[0][i] = 1
            tiles[15][i] = 1
            tiles[i][0] = 1
            tiles[i][15] = 1

        return MapData(
            name=name,
            width=16,
            height=16,
            tiles=tiles,
            entities=[],
            player_start=(1.5, 5.0, 0.0),
            exit_door=None,
            is_final=False,
        )

    def run(self):
        running = True
        while running:
            self.handle_events()
            self.draw()
            pg.display.flip()
            self.clock.tick(60)

    def handle_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
                pg.quit()

            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    self.path_mode = False
                    self.selected_npc_for_path = None
                elif event.key == pg.K_s and pg.key.get_mods() & pg.KMOD_CTRL:
                    self.save_map()
                elif event.key == pg.K_1:
                    self.mode = "paint"
                    self.path_mode = False
                elif event.key == pg.K_2:
                    self.mode = "entity"
                    self.path_mode = False
                elif event.key == pg.K_3:
                    self.mode = "path"
                elif event.key == pg.K_4:
                    self.mode = "door"
                elif event.key == pg.K_p:
                    self.toggle_preview()
                elif event.key == pg.K_n:
                    self.current_map = self._create_new_map("level1")
                    self.npc_paths = {}

            elif event.type == pg.MOUSEBUTTONDOWN:
                x, y = event.pos

                if event.button == 1:
                    self._handle_left_click(x, y)
                elif event.button == 3:
                    self._handle_right_click(x, y)

    def _handle_left_click(self, x, y):
        grid_x = (x - self.canvas_offset_x) // self.tile_size
        grid_y = (y - self.canvas_offset_y) // self.tile_size

        if (
            0 <= grid_x < self.current_map.width
            and 0 <= grid_y < self.current_map.height
        ):
            if self.mode == "paint":
                self.current_map.tiles[grid_y][grid_x] = self.selected_tile

            elif self.mode == "entity" and self.selected_entity_type:
                entity_x = grid_x + 0.5
                entity_y = grid_y + 0.5

                if self.selected_entity_type in NPC_TYPES:
                    patrol = self.npc_paths.get((grid_x, grid_y), [])
                    entity = NPCDef(
                        type=self.selected_entity_type,
                        x=entity_x,
                        y=entity_y,
                        patrol=patrol,
                    )
                elif self.selected_entity_type == "torch":
                    entity = TorchDef(x=entity_x, y=entity_y)
                elif self.selected_entity_type in STATIC_SPRITES:
                    entity = StaticDef(
                        sprite=self.selected_entity_type,
                        x=entity_x,
                        y=entity_y,
                    )

                if entity:
                    self.current_map.entities.append(entity)

            elif self.mode == "path" and self.selected_npc_for_path:
                key = (
                    int(self.selected_npc_for_path[0]),
                    int(self.selected_npc_for_path[1]),
                )
                if key not in self.npc_paths:
                    self.npc_paths[key] = []
                self.npc_paths[key].append((grid_x, grid_y))

    def _handle_right_click(self, x, y):
        grid_x = (x - self.canvas_offset_x) // self.tile_size
        grid_y = (y - self.canvas_offset_y) // self.tile_size

        if (
            0 <= grid_x < self.current_map.width
            and 0 <= grid_y < self.current_map.height
        ):
            if self.mode == "paint":
                self.current_map.tiles[grid_y][grid_x] = 0
            elif self.mode in ("entity", "door"):
                for i, entity in enumerate(self.current_map.entities):
                    ex, ey = int(entity.x), int(entity.y)
                    if ex == grid_x and ey == grid_y:
                        del self.current_map.entities[i]
                        break

    def save_map(self):
        self.maps_dir.mkdir(exist_ok=True)
        path = self.maps_dir / f"{self.current_map.name}.json"
        self.current_map.save(str(path))
        print(f"Map saved to {path}")

    def toggle_preview(self):
        pass

    def draw(self):
        self.screen.fill((40, 40, 50))

        self._draw_toolbar()
        self._draw_canvas()
        self._draw_info_panel()

    def _draw_toolbar(self):
        pg.draw.rect(self.screen, (60, 60, 70), (0, 0, 200, 800))

        y_offset = 10

        title = self.font.render("TOOLS", True, (255, 255, 255))
        self.screen.blit(title, (10, y_offset))
        y_offset += 30

        modes = [
            ("1 - Paint", self.mode == "paint"),
            ("2 - Entities", self.mode == "entity"),
            ("3 - Path", self.mode == "path"),
            ("4 - Door", self.mode == "door"),
        ]

        for label, selected in modes:
            color = (255, 255, 0) if selected else (200, 200, 200)
            text = self.font.render(label, True, color)
            self.screen.blit(text, (10, y_offset))
            y_offset += 25

        y_offset += 20
        if self.mode == "paint":
            tiles = [
                ("Wall (1)", 1),
                ("Wall (2)", 2),
                ("Wall (3)", 3),
                ("Floor (0)", 0),
            ]
            for label, tile_id in tiles:
                color = (
                    (255, 255, 0) if self.selected_tile == tile_id else (200, 200, 200)
                )
                text = self.font.render(label, True, color)
                self.screen.blit(text, (10, y_offset))
                y_offset += 25

        elif self.mode == "entity":
            y_offset += 10
            sub_title = self.font.render("NPCs:", True, (150, 150, 150))
            self.screen.blit(sub_title, (10, y_offset))
            y_offset += 25

            for npc_type in NPC_TYPES:
                color = (
                    (255, 255, 0)
                    if self.selected_entity_type == npc_type
                    else (200, 200, 200)
                )
                text = self.font.render(npc_type, True, color)
                self.screen.blit(text, (10, y_offset))
                y_offset += 25

            y_offset += 10
            sub_title = self.font.render("Torches:", True, (150, 150, 150))
            self.screen.blit(sub_title, (10, y_offset))
            y_offset += 25

            for color in TORCH_COLORS:
                color_sel = (
                    (255, 255, 0)
                    if self.selected_entity_type == "torch"
                    and self.selected_entity_data == color
                    else (200, 200, 200)
                )
                text = self.font.render(f"{color} torch", True, color_sel)
                self.screen.blit(text, (10, y_offset))
                y_offset += 25

            y_offset += 10
            sub_title = self.font.render("Objects:", True, (150, 150, 150))
            self.screen.blit(sub_title, (10, y_offset))
            y_offset += 25

            for sprite in STATIC_SPRITES:
                color = (
                    (255, 255, 0)
                    if self.selected_entity_type == sprite
                    else (200, 200, 200)
                )
                text = self.font.render(sprite, True, color)
                self.screen.blit(text, (10, y_offset))
                y_offset += 25

        elif self.mode == "door":
            text = self.font.render("Click to place exit door", True, (200, 200, 200))
            self.screen.blit(text, (10, y_offset))

    def _draw_canvas(self):
        pg.draw.rect(
            self.screen,
            (0, 0, 0),
            (
                self.canvas_offset_x,
                self.canvas_offset_y,
                self.current_map.width * self.tile_size,
                self.current_map.height * self.tile_size,
            ),
        )

        for y, row in enumerate(self.current_map.tiles):
            for x, tile in enumerate(row):
                if tile > 0:
                    color = (100, 100, 100)
                    if tile == 2:
                        color = (80, 80, 100)
                    elif tile == 3:
                        color = (100, 80, 80)
                    elif tile == 4:
                        color = (80, 100, 80)
                    pg.draw.rect(
                        self.screen,
                        color,
                        (
                            self.canvas_offset_x + x * self.tile_size,
                            self.canvas_offset_y + y * self.tile_size,
                            self.tile_size,
                            self.tile_size,
                        ),
                    )
                else:
                    pg.draw.rect(
                        self.screen,
                        (30, 30, 30),
                        (
                            self.canvas_offset_x + x * self.tile_size,
                            self.canvas_offset_y + y * self.tile_size,
                            self.tile_size,
                            self.tile_size,
                        ),
                        1,
                    )

        for entity in self.current_map.entities:
            ex = int(entity.x)
            ey = int(entity.y)

            color = (255, 200, 0)
            if isinstance(entity, NPCDef):
                color = (255, 0, 0)
            elif isinstance(entity, TorchDef):
                color = (255, 150, 0) if entity.color == "red" else (0, 255, 0)
            elif isinstance(entity, StaticDef):
                color = (0, 200, 255)

            pg.draw.circle(
                self.screen,
                color,
                (
                    self.canvas_offset_x + ex * self.tile_size + self.tile_size // 2,
                    self.canvas_offset_y + ey * self.tile_size + self.tile_size // 2,
                ),
                10,
            )

        if self.current_map.exit_door:
            dx = int(self.current_map.exit_door.x)
            dy = int(self.current_map.exit_door.y)
            pg.draw.rect(
                self.screen,
                (255, 255, 0),
                (
                    self.canvas_offset_x + dx * self.tile_size,
                    self.canvas_offset_y + dy * self.tile_size,
                    self.tile_size,
                    self.tile_size,
                ),
                3,
            )

        for npc_pos, path in self.npc_paths.items():
            for i, point in enumerate(path):
                px, py = point
                pg.draw.circle(
                    self.screen,
                    (0, 255, 255),
                    (
                        self.canvas_offset_x
                        + px * self.tile_size
                        + self.tile_size // 2,
                        self.canvas_offset_y
                        + py * self.tile_size
                        + self.tile_size // 2,
                    ),
                    5,
                )
                if i > 0:
                    prev = path[i - 1]
                    pg.draw.line(
                        self.screen,
                        (0, 255, 255),
                        (
                            self.canvas_offset_x
                            + prev[0] * self.tile_size
                            + self.tile_size // 2,
                            self.canvas_offset_y
                            + prev[1] * self.tile_size
                            + self.tile_size // 2,
                        ),
                        (
                            self.canvas_offset_x
                            + px * self.tile_size
                            + self.tile_size // 2,
                            self.canvas_offset_y
                            + py * self.tile_size
                            + self.tile_size // 2,
                        ),
                        2,
                    )

    def _draw_info_panel(self):
        info_y = 10
        info_x = self.canvas_offset_x + self.current_map.width * self.tile_size + 20

        text = self.font.render(f"Mode: {self.mode.upper()}", True, (255, 255, 255))
        self.screen.blit(text, (info_x, info_y))
        info_y += 25

        text = self.font.render("Controls:", True, (200, 200, 200))
        self.screen.blit(text, (info_x, info_y))
        info_y += 25

        controls = [
            "1-4: Switch tools",
            "Left click: Place",
            "Right click: Remove",
            "Ctrl+S: Save map",
            "N: New map",
            "P: Preview",
            "ESC: Cancel path",
        ]
        for ctrl in controls:
            text = self.font.render(ctrl, True, (150, 150, 150))
            self.screen.blit(text, (info_x, info_y))
            info_y += 20


if __name__ == "__main__":
    editor = Editor()
    editor.run()
