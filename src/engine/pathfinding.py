from collections import deque
from functools import lru_cache
import math
from ..data.config import *


class PathFinding:
    def __init__(self, game):
        self.game = game
        self.world_map = {}
        self._update_world_map()

    def _update_world_map(self):
        self.world_map = {}
        if self.game.map:
            for j, row in enumerate(self.game.map.tiles):
                for i, value in enumerate(row):
                    if value:
                        self.world_map[(i, j)] = value

    @lru_cache(maxsize=128)
    def get_path(self, start, target):
        self._update_world_map()

        start = (int(start[0]), int(start[1]))
        target = (int(target[0]), int(target[1]))

        if target not in self.world_map:
            return target

        queue = deque([start])
        visited = {start: None}

        while queue:
            current = queue.popleft()

            if current == target:
                break

            for neighbor in self._get_neighbors(current):
                if neighbor not in visited and neighbor not in self.world_map:
                    visited[neighbor] = current
                    queue.append(neighbor)

        if target not in visited:
            return start

        path = []
        current = target
        while current != start:
            path.append(current)
            current = visited[current]

        path.reverse()
        return path[0] if path else start

    def _get_neighbors(self, pos):
        x, y = pos
        neighbors = []

        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            nx, ny = x + dx, y + dy
            neighbors.append((nx, ny))

        for dx, dy in [(1, 1), (1, -1), (-1, 1), (-1, -1)]:
            nx, ny = x + dx, y + dy
            if (x + dx, y) not in self.world_map and (x, y + dy) not in self.world_map:
                neighbors.append((nx, ny))

        return neighbors

    def get_npc_state(self, npc, player_pos, patrol_points):
        if not patrol_points:
            dist = math.hypot(player_pos[0] - npc.x, player_pos[1] - npc.y)
            if dist < NPC_DETECTION_RANGE:
                return "chase"
            return "idle"

        dist = math.hypot(player_pos[0] - npc.x, player_pos[1] - npc.y)
        if dist < NPC_DETECTION_RANGE:
            return "chase"

        return "patrol"

    def get_next_patrol_point(self, current_idx, patrol_points):
        if not patrol_points:
            return None
        next_idx = (current_idx + 1) % len(patrol_points)
        return patrol_points[next_idx]
