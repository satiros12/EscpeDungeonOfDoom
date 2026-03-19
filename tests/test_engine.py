import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.engine.physics import Physics


class TestPhysics:
    def test_check_collision_empty_map(self):
        world_map = {}
        assert Physics.check_collision(5, 5, world_map) is False

    def test_check_collision_with_wall(self):
        world_map = {(5, 5): 1, (6, 5): 1}
        assert Physics.check_collision(5, 5, world_map) is True
        assert Physics.check_collision(5, 6, world_map) is False

    def test_check_collision_outside_map(self):
        world_map = {(0, 0): 1}
        assert Physics.check_collision(-1, 0, world_map) is False

    def test_calculate_distance(self):
        dist = Physics.calculate_distance(0, 0, 3, 4)
        assert dist == 5.0

    def test_calculate_distance_same_point(self):
        dist = Physics.calculate_distance(5, 5, 5, 5)
        assert dist == 0.0

    def test_normalize_angle(self):
        assert Physics.normalize_angle(0) == 0
        assert Physics.normalize_angle(3.14) == pytest.approx(3.14, rel=0.01)
        assert Physics.normalize_angle(7) == pytest.approx(7 - 2 * 3.14159, rel=0.01)

    def test_normalize_angle_negative(self):
        result = Physics.normalize_angle(-3.14)
        assert result >= 0
        assert result < 6.28318

    def test_is_line_of_sight_clear(self):
        world_map = {}
        assert Physics.is_line_of_sight(0, 0, 5, 5, world_map) is True

    def test_is_line_of_sight_blocked(self):
        world_map = {(2, 2): 1}
        assert Physics.is_line_of_sight(0, 0, 5, 5, world_map) is False

    def test_is_line_of_sight_same_point(self):
        world_map = {}
        assert Physics.is_line_of_sight(5, 5, 5, 5, world_map) is True


class TestPathfindingLogic:
    def test_straight_line_path(self):
        from src.engine.pathfinding import PathFinding

        class MockGame:
            def __init__(self):
                self.map = None
                self.map_data = type(
                    "obj", (object,), {"tiles": [[0, 0, 0], [0, 0, 0], [0, 0, 0]]}
                )()

        pf = PathFinding.__new__(PathFinding)
        pf.world_map = {}
        pf._update_world_map = lambda: None

        result = pf.get_path((0, 0), (2, 2))
        assert result == (2, 2)

    def test_path_blocked_by_wall(self):
        from src.engine.pathfinding import PathFinding

        class MockGame:
            def __init__(self):
                self.map = None

        game = MockGame()
        pf = PathFinding(game)
        pf.world_map = {(1, 0): 1, (1, 1): 1, (1, 2): 1}

        result = pf.get_path((0, 0), (2, 2))
        assert isinstance(result, tuple)
        assert len(result) == 2


class TestPlayerLogic:
    def test_player_initialization(self):
        from src.engine.player import Player

        class MockGame:
            def __init__(self):
                self.map = type("obj", (object,), {"player_start": (1.5, 5.0, 0.0)})()
                self.delta_time = 1
                self.weapon = type("obj", (object,), {"reloading": False})()
                self.sound = type(
                    "obj", (object,), {"player_pain": None, "shotgun": None}
                )()

        game = MockGame()
        player = Player(game)

        assert player.x == 1.5
        assert player.y == 5.0
        assert player.angle == 0.0
        assert player.health == 100

    def test_player_pos_property(self):
        from src.engine.player import Player

        class MockGame:
            def __init__(self):
                self.map = type("obj", (object,), {"player_start": (1.5, 5.0, 0.0)})()
                self.delta_time = 1
                self.weapon = type("obj", (object,), {"reloading": False})()
                self.sound = type(
                    "obj", (object,), {"player_pain": None, "shotgun": None}
                )()

        player = Player(MockGame())

        pos = player.pos
        assert pos == (player.x, player.y)

    def test_player_map_pos_property(self):
        from src.engine.player import Player

        class MockGame:
            def __init__(self):
                self.map = type("obj", (object,), {"player_start": (1.5, 5.0, 0.0)})()
                self.delta_time = 1
                self.weapon = type("obj", (object,), {"reloading": False})()
                self.sound = type(
                    "obj", (object,), {"player_pain": None, "shotgun": None}
                )()

        player = Player(MockGame())

        map_pos = player.map_pos
        assert map_pos == (1, 5)
