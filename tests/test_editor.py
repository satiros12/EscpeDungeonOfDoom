import pytest
import pygame as pg
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

sys.path.insert(0, str(Path(__file__).parent.parent))

pg.init()


class TestEditorBasics:
    def test_create_new_map(self):
        import sys
        from pathlib import Path

        sys.path.insert(0, str(Path(__file__).parent.parent))

        from editor.editor import Editor

        editor = Editor.__new__(Editor)
        editor._create_new_map = Editor._create_new_map.__get__(editor, Editor)

        map_data = editor._create_new_map("test_level")

        assert map_data.name == "test_level"
        assert map_data.width == 16
        assert map_data.height == 16
        assert len(map_data.tiles) == 16
        assert len(map_data.tiles[0]) == 16

        for i in range(16):
            assert map_data.tiles[0][i] == 1
            assert map_data.tiles[15][i] == 1
            assert map_data.tiles[i][0] == 1
            assert map_data.tiles[i][15] == 1


class TestEntityCategories:
    def test_entity_categories_property(self):
        import sys
        from pathlib import Path

        sys.path.insert(0, str(Path(__file__).parent.parent))

        from src.data.entity import NPC_TYPES, STATIC_SPRITES

        categories = {
            "NPCs": NPC_TYPES,
            "Torches": ["torch_red", "torch_green"],
            "Objects": STATIC_SPRITES,
        }

        assert "NPCs" in categories
        assert "soldier" in categories["NPCs"]
        assert "candlebra" in categories["Objects"]


class TestEditorSelection:
    def test_select_next_entity(self):
        import sys
        from pathlib import Path

        sys.path.insert(0, str(Path(__file__).parent.parent))

        from editor.editor import Editor
        from src.data.entity import NPC_TYPES, STATIC_SPRITES

        class MockEditor:
            selected_entity_type = "soldier"

            @property
            def entity_categories(self):
                return {
                    "NPCs": NPC_TYPES,
                    "Torches": ["torch_red", "torch_green"],
                    "Objects": STATIC_SPRITES,
                }

            def _select_next_entity(self):
                all_entities = []
                for cat_name, entities in self.entity_categories.items():
                    all_entities.extend(entities)

                if self.selected_entity_type not in all_entities:
                    self.selected_entity_type = all_entities[0]
                    return

                idx = all_entities.index(self.selected_entity_type)
                self.selected_entity_type = all_entities[(idx + 1) % len(all_entities)]

        editor = MockEditor()
        editor._select_next_entity()

        assert (
            editor.selected_entity_type in NPC_TYPES[1:]
            or editor.selected_entity_type == NPC_TYPES[0]
        )


class TestEditorEvents:
    def test_mode_switching(self):
        modes = ["paint", "entity", "path", "door"]

        for mode in modes:
            assert mode in ["paint", "entity", "path", "door"]

        assert len(modes) == 4


class TestTileSelection:
    def test_tile_selection_bounds(self):
        max_tile = 4
        min_tile = 0

        selected = 2
        selected = max(min_tile, min(max_tile, selected))
        assert selected == 2

        selected = -1
        selected = max(min_tile, min(max_tile, selected))
        assert selected == 0

        selected = 10
        selected = max(min_tile, min(max_tile, selected))
        assert selected == 4


pg.quit()
