from collections import deque
import math


class FaceExitDrawingGuard:
    def __init__(self, width, height, history_seconds, min_distance):
        self.width = width
        self.height = height
        self.history_seconds = history_seconds
        self.min_distance = min_distance
        self.samples = deque()

    def record(self, now, position, point_count_before_add):
        normalized_position = (
            position[0] / self.width,
            position[1] / self.height,
        )
        self.samples.append((now, normalized_position, point_count_before_add))
        self._discard_expired(now)

    def rollback_point_count(self):
        if len(self.samples) < 2:
            return None

        _, start_position, start_point_count = self.samples[0]
        _, end_position, _ = self.samples[-1]
        distance = math.dist(start_position, end_position)
        if distance < self.min_distance:
            return None
        return start_point_count

    def clear(self):
        self.samples.clear()

    def _discard_expired(self, now):
        cutoff = now - self.history_seconds
        while self.samples and self.samples[0][0] < cutoff:
            self.samples.popleft()
