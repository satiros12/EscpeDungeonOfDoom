import math


class Physics:
    @staticmethod
    def check_collision(x, y, world_map):
        return (int(x), int(y)) in world_map

    @staticmethod
    def check_entity_collision(x, y, entities, exclude=None):
        for entity in entities:
            if entity is exclude:
                continue
            dist = math.hypot(entity.x - x, entity.y - y)
            if dist < 0.5:
                return True
        return False

    @staticmethod
    def is_line_of_sight(x1, y1, x2, y2, world_map):
        steps = int(math.hypot(x2 - x1, y2 - y1) * 2)
        if steps == 0:
            return True

        dx = (x2 - x1) / steps
        dy = (y2 - y1) / steps

        for i in range(steps):
            check_x = int(x1 + dx * i)
            check_y = int(y1 + dy * i)
            if (check_x, check_y) in world_map:
                return False
        return True

    @staticmethod
    def calculate_distance(x1, y1, x2, y2):
        return math.hypot(x2 - x1, y2 - y1)

    @staticmethod
    def normalize_angle(angle):
        TWO_PI = 2 * math.pi
        angle = angle % TWO_PI
        if angle < 0:
            angle += TWO_PI
        if abs(angle - TWO_PI) < 0.001:
            angle = 0.0
        return angle
