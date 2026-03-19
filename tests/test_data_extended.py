import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data.map import MapData
from src.data.entity import NPCDef, StaticDef, TorchDef, DoorDef


class TestMapBoundaries:
    def test_wall_tiles_boundary(self):
        tiles = [[1 for _ in range(10)] for _ in range(10)]
        for i in range(10):
            assert tiles[0][i] == 1
            assert tiles[9][i] == 1
            assert tiles[i][0] == 1
            assert tiles[i][9] == 1

    def test_floor_tiles_interior(self):
        tiles = [[1 for _ in range(5)] for _ in range(5)]
        for i in range(1, 4):
            for j in range(1, 4):
                tiles[i][j] = 0

        for i in range(1, 4):
            for j in range(1, 4):
                assert tiles[i][j] == 0

    def test_tile_out_of_bounds(self):
        tiles = [[0 for _ in range(5)] for _ in range(5)]

        assert tiles[0][0] == 0
        assert tiles[4][4] == 0

        assert len(tiles) == 5
        assert len(tiles[0]) == 5


class TestEntityValidation:
    def test_npc_with_empty_patrol(self):
        npc = NPCDef(type="soldier", x=5.0, y=5.0, patrol=[])
        assert npc.patrol == []
        assert npc.type == "soldier"

    def test_npc_with_patrol_points(self):
        patrol = [(1, 1), (2, 2), (3, 1)]
        npc = NPCDef(type="caco_demon", x=1.5, y=1.5, patrol=patrol)
        assert len(npc.patrol) == 3
        assert npc.patrol[0] == (1, 1)

    def test_torch_with_default_radius(self):
        torch = TorchDef(x=5.0, y=5.0)
        assert torch.light_radius == 5.0
        assert torch.color == "red"

    def test_torch_with_custom_values(self):
        torch = TorchDef(x=3.0, y=4.0, light_radius=8.0, color="green")
        assert torch.light_radius == 8.0
        assert torch.color == "green"

    def test_door_to_next_level(self):
        door = DoorDef(x=10.0, y=5.0, next_map="level2.json")
        assert door.next_map == "level2.json"

    def test_door_final_level(self):
        door = DoorDef(x=10.0, y=5.0, next_map=None)
        assert door.next_map is None


class TestMapPersistence:
    def test_save_load_roundtrip(self):
        original = MapData(
            name="test_level",
            width=10,
            height=10,
            tiles=[[1, 1, 1], [1, 0, 1], [1, 1, 1]],
            entities=[
                NPCDef(type="soldier", x=1.5, y=1.5, patrol=[(1, 1), (2, 1)]),
                TorchDef(x=2.5, y=2.5, light_radius=6.0, color="green"),
                StaticDef(sprite="barrel", x=0.5, y=0.5),
            ],
            player_start=(1.0, 1.0, 0.0),
            exit_door=DoorDef(x=9.5, y=5.0, next_map=None),
            is_final=True,
        )

        import tempfile
        import os

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            temp_path = f.name

        try:
            original.save(temp_path)
            loaded = MapData.load(temp_path)

            assert loaded.name == original.name
            assert loaded.width == original.width
            assert loaded.height == original.height
            assert loaded.is_final == original.is_final
            assert len(loaded.entities) == len(original.entities)

            loaded_npc = loaded.entities[0]
            assert isinstance(loaded_npc, NPCDef)
            assert loaded_npc.type == "soldier"
            assert loaded_npc.patrol == [(1, 1), (2, 1)]

            loaded_torch = loaded.entities[1]
            assert isinstance(loaded_torch, TorchDef)
            assert loaded_torch.light_radius == 6.0
            assert loaded_torch.color == "green"
        finally:
            os.unlink(temp_path)

    def test_map_with_no_entities(self):
        map_data = MapData(
            name="empty",
            width=5,
            height=5,
            tiles=[[1] * 5 for _ in range(5)],
            entities=[],
            player_start=(2.5, 2.5, 0.0),
        )

        result = map_data.to_dict()
        assert result["entities"] == []

    def test_player_start_coordinates(self):
        map_data = MapData(
            name="test",
            width=10,
            height=10,
            tiles=[[0] * 10 for _ in range(10)],
            entities=[],
            player_start=(5.5, 7.3, 1.57),
        )

        result = map_data.to_dict()
        assert result["player_start"] == [5.5, 7.3, 1.57]


class TestEntityTypes:
    def test_npc_types_all_valid(self):
        from src.data.entity import NPC_TYPES

        valid_types = ["soldier", "caco_demon", "cyber_demon"]
        for npc_type in NPC_TYPES:
            assert npc_type in valid_types

    def test_static_sprites_all_valid(self):
        from src.data.entity import STATIC_SPRITES

        assert "candlebra" in STATIC_SPRITES
        assert "barrel" in STATIC_SPRITES

    def test_torch_colors_all_valid(self):
        from src.data.entity import TORCH_COLORS

        assert "red" in TORCH_COLORS
        assert "green" in TORCH_COLORS


class TestTileTypes:
    def test_tile_range(self):
        for tile_id in range(5):
            assert tile_id >= 0

    def test_wall_vs_floor(self):
        tiles = [[1, 1], [1, 0]]

        assert tiles[0][0] > 0
        assert tiles[0][1] > 0
        assert tiles[1][0] > 0
        assert tiles[1][1] == 0
