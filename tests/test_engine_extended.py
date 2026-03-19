import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.engine.physics import Physics


class TestAdvancedPhysics:
    def test_multiple_walls(self):
        world_map = {
            (0, 0): 1,
            (1, 0): 1,
            (2, 0): 1,
            (0, 1): 1,
            (2, 1): 1,
            (0, 2): 1,
            (1, 2): 1,
            (2, 2): 1,
        }

        assert Physics.check_collision(0, 0, world_map) is True
        assert Physics.check_collision(1, 1, world_map) is False
        assert Physics.check_collision(5, 5, world_map) is False

    def test_distance_various_points(self):
        assert Physics.calculate_distance(0, 0, 3, 4) == 5.0
        assert Physics.calculate_distance(1, 1, 4, 5) == 5.0
        assert Physics.calculate_distance(0, 0, 0, 10) == 10.0
        assert Physics.calculate_distance(0, 0, 10, 0) == 10.0

    def test_angle_normalization_edge_cases(self):
        import math

        assert Physics.normalize_angle(0) == 0
        assert Physics.normalize_angle(2 * math.pi) == pytest.approx(0, abs=0.01)
        assert Physics.normalize_angle(-2 * math.pi) == pytest.approx(0, abs=0.01)
        assert Physics.normalize_angle(3.14159) == pytest.approx(3.14159, rel=0.01)

    def test_line_of_sight_complex(self):
        world_map = {(2, 2): 1, (3, 3): 1}

        assert Physics.is_line_of_sight(0, 0, 5, 5, world_map) is False
        assert Physics.is_line_of_sight(0, 0, 1, 1, world_map) is True
        assert Physics.is_line_of_sight(5, 5, 10, 10, world_map) is True


class TestEntityManager:
    def test_entity_manager_init(self):
        from src.engine.entity_manager import EntityManager

        class MockGame:
            def __init__(self):
                self.map = type(
                    "obj", (object,), {"entities": [], "player_start": (1.5, 5.0, 0.0)}
                )()

        game = MockGame()
        manager = EntityManager(game)

        assert len(manager.sprites) == 0
        assert len(manager.npcs) == 0

    def test_entity_manager_with_npc(self):
        from src.engine.entity_manager import EntityManager
        from src.data.entity import NPCDef

        class MockGame:
            def __init__(self):
                self.map = type(
                    "obj",
                    (object,),
                    {
                        "entities": [NPCDef(type="soldier", x=5.5, y=5.5, patrol=[])],
                        "player_start": (1.5, 5.0, 0.0),
                    },
                )()
                self.raycaster = type("obj", (object,), {"objects_to_render": []})()
                self.player = type("obj", (object,), {"x": 1.5, "y": 5.0, "angle": 0})()

        game = MockGame()
        manager = EntityManager(game)

        assert len(manager.npcs) == 1


class TestRayCaster:
    def test_raycaster_init(self):
        from src.engine.raycaster import RayCaster

        class MockGame:
            def __init__(self):
                self.map = type(
                    "obj", (object,), {"tiles": [[1, 1], [1, 0]], "entities": []}
                )()
                self.player = type(
                    "obj", (object,), {"pos": (1.5, 1.5), "map_pos": (1, 1), "angle": 0}
                )()
                self.renderer = type("obj", (object,), {"wall_textures": {}})()

        game = MockGame()
        caster = RayCaster(game)

        assert caster.world_map is not None
        assert len(caster.ray_casting_result) == 0


class TestPathfinding:
    def test_pathfinding_a_star_simple(self):
        from src.engine.pathfinding import PathFinding

        class MockGame:
            def __init__(self):
                self.map = type(
                    "obj", (object,), {"tiles": [[0, 0, 0], [0, 0, 0], [0, 0, 0]]}
                )()

        game = MockGame()
        pf = PathFinding(game)

        result = pf.get_path((0, 0), (2, 2))
        assert result == (2, 2)

    def test_pathfinding_with_walls(self):
        from src.engine.pathfinding import PathFinding

        class MockGame:
            def __init__(self):
                self.map = type(
                    "obj", (object,), {"tiles": [[0, 0, 0], [1, 1, 1], [0, 0, 0]]}
                )()

        game = MockGame()
        pf = PathFinding(game)

        result = pf.get_path((0, 0), (2, 2))
        assert isinstance(result, tuple)

    def test_get_neighbors(self):
        from src.engine.pathfinding import PathFinding

        class MockGame:
            def __init__(self):
                self.map = None

        game = MockGame()
        pf = PathFinding(game)
        pf.world_map = {}

        neighbors = pf._get_neighbors((5, 5))
        assert (5, 6) in neighbors
        assert (6, 5) in neighbors
        assert (5, 4) in neighbors
        assert (4, 5) in neighbors

    def test_npc_state_detection(self):
        from src.engine.pathfinding import PathFinding

        class MockGame:
            def __init__(self):
                self.map = None

        game = MockGame()
        pf = PathFinding(game)

        class MockNPC:
            def __init__(self):
                self.x = 5.0
                self.y = 5.0

        npc = MockNPC()

        state = pf.get_npc_state(npc, (5.1, 5.1), [])
        assert state in ["idle", "chase"]

        state = pf.get_npc_state(npc, (1.0, 1.0), [(5, 5), (6, 5)])
        assert state == "patrol"


class TestConfig:
    def test_config_values(self):
        from src.data.config import (
            RES,
            FPS,
            FOV,
            MAX_DEPTH,
            PLAYER_MAX_HEALTH,
            NPC_DETECTION_RANGE,
            DEFAULT_LIGHT_RADIUS,
        )

        assert RES == (1600, 900)
        assert FPS == 60
        assert FOV > 0
        assert MAX_DEPTH > 0
        assert PLAYER_MAX_HEALTH > 0
        assert NPC_DETECTION_RANGE > 0
        assert DEFAULT_LIGHT_RADIUS > 0

    def test_raycasting_calculations(self):
        from src.data.config import (
            HALF_WIDTH,
            HALF_HEIGHT,
            NUM_RAYS,
            HALF_NUM_RAYS,
            DELTA_ANGLE,
            SCREEN_DIST,
            SCALE,
        )

        assert HALF_WIDTH == 800
        assert HALF_HEIGHT == 450
        assert NUM_RAYS == 800
        assert SCALE == 2
        assert SCREEN_DIST > 0
        assert DELTA_ANGLE > 0
