"""
Floating light particles for the gallery background.

The particles are drawn behind the flowers to add a fresh, airy feeling without
adding noisy grass detail.
"""

import math
import random

import pygame


REFERENCE_WIDTH = 1280
REFERENCE_HEIGHT = 720
AA_SCALE = 3


class AtmosphereParticles:
    """Soft light motes drifting through the gallery scene."""

    def __init__(self, width: int, height: int, count: int | None = None):
        self.width = width
        self.height = height
        self.display_scale = min(width / REFERENCE_WIDTH, height / REFERENCE_HEIGHT)
        self.rng = random.Random(7)
        self.particles: list[dict] = []

        if count is None:
            count = int(14 * self.display_scale)

        for _ in range(count):
            large = self.rng.random() < 0.04
            if large:
                size = self.rng.uniform(1.8, 3.2) * self.display_scale
                alpha = self.rng.randint(14, 30)
            else:
                size = self.rng.uniform(0.6, 1.3) * self.display_scale
                alpha = self.rng.randint(14, 34)

            self.particles.append({
                "x": self.rng.uniform(0, width),
                "y": self.rng.uniform(height * 0.08, height * 0.58),
                "size": size,
                "vx": self.rng.uniform(9, 26) * self.display_scale,
                "vy": self.rng.uniform(-12, -2) * self.display_scale,
                "phase": self.rng.uniform(0, math.pi * 2),
                "wobble": self.rng.uniform(0.35, 1.1),
                "alpha": alpha,
                "large": large,
                "warm": self.rng.random() < 0.7,
            })

    def update(self, dt: float) -> None:
        margin = 24 * self.display_scale
        for p in self.particles:
            p["x"] += p["vx"] * dt
            p["y"] += p["vy"] * dt
            if p["x"] > self.width + margin or p["y"] < -margin:
                p["x"] = self.rng.uniform(-margin * 2, self.width * 0.22)
                p["y"] = self.rng.uniform(self.height * 0.36, self.height * 0.62)
            elif p["x"] < -margin:
                p["x"] = self.width + margin

    def _draw_glow(
        self,
        screen: pygame.Surface,
        x: int,
        y: int,
        size: int,
        color: tuple[int, int, int, int],
    ) -> None:
        glow_size = max(6, size * 5)
        hi_size = glow_size * AA_SCALE
        hi = pygame.Surface((hi_size, hi_size), pygame.SRCALPHA)
        center = hi_size // 2
        pygame.draw.circle(hi, (*color[:3], color[3] // 4), (center, center), size * AA_SCALE * 2)
        pygame.draw.circle(hi, color, (center, center), size * AA_SCALE)
        surf = pygame.transform.smoothscale(hi, (glow_size, glow_size))
        screen.blit(surf, (x - glow_size // 2, y - glow_size // 2), special_flags=pygame.BLEND_RGBA_ADD)

    def draw(self, screen: pygame.Surface, time_sec: float) -> None:
        for p in self.particles:
            wobble_y = math.sin(time_sec * p["wobble"] + p["phase"]) * 6 * self.display_scale
            shimmer = 0.66 + 0.34 * math.sin(time_sec * 1.2 + p["phase"])
            x = int(p["x"])
            y = int(p["y"] + wobble_y)
            size = max(1, int(p["size"]))

            if p["warm"]:
                color = (255, 252, 214, int(p["alpha"] * shimmer))
            else:
                color = (224, 248, 255, int(p["alpha"] * 0.75 * shimmer))

            if p["large"]:
                self._draw_glow(screen, x, y, size, color)
            else:
                surf = pygame.Surface((size * 2 + 2, size * 2 + 2), pygame.SRCALPHA)
                pygame.draw.circle(surf, color, (size + 1, size + 1), size)
                screen.blit(surf, (x - size, y - size), special_flags=pygame.BLEND_RGBA_ADD)
