"""Small drifting light particles for the poster-like gallery."""

import math
import random

import pygame


class AtmosphereParticles:
    """Soft dust and blush sparkle over the paper background."""

    def __init__(self, width: int, height: int, count: int = 42):
        self.width = width
        self.height = height
        self.rng = random.Random(7)
        self.particles: list[dict] = []

        for _ in range(count):
            self.particles.append({
                "x": self.rng.uniform(0, width),
                "y": self.rng.uniform(0, height * 0.88),
                "size": self.rng.uniform(1.0, 3.0),
                "vx": self.rng.uniform(3, 12),
                "vy": self.rng.uniform(-4, 4),
                "phase": self.rng.uniform(0, math.pi * 2),
                "wobble": self.rng.uniform(0.45, 1.0),
                "alpha": self.rng.randint(22, 72),
                "warm": self.rng.random() < 0.7,
            })

    def update(self, dt: float) -> None:
        for p in self.particles:
            p["x"] += p["vx"] * dt
            p["y"] += p["vy"] * dt
            if p["x"] > self.width + 10:
                p["x"] = -10
                p["y"] = self.rng.uniform(0, self.height * 0.88)
            elif p["x"] < -10:
                p["x"] = self.width + 10

    def draw(self, screen: pygame.Surface, time_sec: float) -> None:
        for p in self.particles:
            wobble_y = math.sin(time_sec * p["wobble"] + p["phase"]) * 4
            x = int(p["x"])
            y = int(p["y"] + wobble_y)
            size = int(p["size"])

            color = (255, 226, 230, p["alpha"]) if p["warm"] else (255, 248, 244, p["alpha"])
            surf = pygame.Surface((size * 2 + 2, size * 2 + 2), pygame.SRCALPHA)
            pygame.draw.circle(surf, color, (size + 1, size + 1), size)
            screen.blit(surf, (x - size, y - size))
