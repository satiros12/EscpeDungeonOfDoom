import pytest
import json
import tempfile
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data.map import MapData
from src.data.entity import NPCDef, StaticDef, TorchDef, DoorDef


class TestMapData:
    def test_create_empty_map(self):
        tiles = [[0 for _ in range(5)] for _ in range(5)]
        map_data = MapData(
            name="test",
            width=5,
            height=5,
            tiles=tiles,
            entities=[],
            player_start=(1.0, 1.0, 0.0),
            exit_door=None,
            is_final=False,
        )

        assert map_data.name == "test"
        assert map_data.width == 5
        assert map_data.height == 5
        assert len(map_data.entities) == 0

    def test_map_to_dict(self):
        tiles = [[1, 1], [1, 0]]
        map_data = MapData(
            name="test",
            width=2,
            height=2,
            tiles=tiles,
            entities=[],
            player_start=(0.5, 0.5, 0.0),
            is_final=False,
        )

        result = map_data.to_dict()

        assert result["name"] == "test"
        assert result["width"] == 2
        assert result["height"] == 2
        assert result["tiles"] == tiles
        assert result["player_start"] == [0.5, 0.5, 0.0]

    def test_save_and_load_map(self):
        tiles = [[1, 1], [1, 0]]
        map_data = MapData(
            name="test",
            width=2,
            height=2,
            tiles=tiles,
            entities=[
                NPCDef(type="soldier", x=1.5, y=1.5, patrol=[]),
                TorchDef(x=2.5, y=2.5, light_radius=5.0, color="red"),
            ],
            player_start=(0.5, 0.5, 0.0),
            exit_door=DoorDef(x=1.5, y=0.5, next_map="level2.json"),
            is_final=False,
        )

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            temp_path = f.name

        try:
            map_data.save(temp_path)

            loaded_map = MapData.load(temp_path)

            assert loaded_map.name == "test"
            assert loaded_map.width == 2
            assert loaded_map.height == 2
            assert len(loaded_map.entities) == 2
            assert isinstance(loaded_map.entities[0], NPCDef)
            assert isinstance(loaded_map.entities[1], TorchDef)
            assert loaded_map.exit_door.next_map == "level2.json"
        finally:
            os.unlink(temp_path)

    def test_final_map(self):
        tiles = [[1]]
        map_data = MapData(
            name="final",
            width=1,
            height=1,
            tiles=tiles,
            entities=[],
            player_start=(0.5, 0.5, 0.0),
            is_final=True,
        )

        result = map_data.to_dict()

        assert result["is_final"] is True


class TestEntityDef:
    def test_npc_def_creation(self):
        npc = NPCDef(
            type="soldier",
            x=5.0,
            y=10.0,
            patrol=[(5, 10), (6, 10), (6, 11)],
            health=100,
        )

        assert npc.type == "soldier"
        assert npc.x == 5.0
        assert npc.y == 10.0
        assert len(npc.patrol) == 3
        assert npc.health == 100

    def test_torch_def_creation(self):
        torch = TorchDef(
            x=3.0,
            y=4.0,
            light_radius=5.0,
            color="red",
        )

        assert torch.x == 3.0
        assert torch.y == 4.0
        assert torch.light_radius == 5.0
        assert torch.color == "red"

    def test_static_def_creation(self):
        static = StaticDef(
            sprite="candlebra",
            x=2.0,
            y=3.0,
            animated=False,
        )

        assert static.sprite == "candlebra"
        assert static.x == 2.0
        assert static.y == 3.0
        assert static.animated is False

    def test_door_def_creation(self):
        door = DoorDef(
            x=5.0,
            y=5.0,
            next_map="level2.json",
        )

        assert door.x == 5.0
        assert door.y == 5.0
        assert door.next_map == "level2.json"

    def test_door_def_final(self):
        door = DoorDef(
            x=5.0,
            y=5.0,
            next_map=None,
        )

        assert door.next_map is None


class TestMapSerialization:
    def test_complex_map_serialization(self):
        tiles = [
            [1, 1, 1],
            [1, 0, 1],
            [1, 1, 1],
        ]
        map_data = MapData(
            name="complex",
            width=3,
            height=3,
            tiles=tiles,
            entities=[
                NPCDef(type="caco_demon", x=1.5, y=1.5, patrol=[(1, 1), (2, 1)]),
                TorchDef(x=0.5, y=0.5, light_radius=3.0, color="green"),
                StaticDef(sprite="barrel", x=2.5, y=2.5),
            ],
            player_start=(1.5, 1.0, 0.0),
            exit_door=DoorDef(x=2.5, y=0.5, next_map=None),
            is_final=True,
        )

        result = map_data.to_dict()

        assert len(result["entities"]) == 3
        assert result["entities"][0]["type"] == "caco_demon"
        assert result["entities"][0]["patrol"] == [(1, 1), (2, 1)]
        assert result["entities"][1]["type"] == "torch"
        assert result["entities"][1]["light_radius"] == 3.0
        assert result["entities"][1]["color"] == "green"
        assert result["entities"][2]["type"] == "static"
        assert result["exit_door"]["x"] == 2.5
        assert result["is_final"] is True
