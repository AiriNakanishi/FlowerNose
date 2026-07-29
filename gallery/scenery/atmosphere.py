"""
空中を漂う光の粒（花粉・ちり）

画面全体にゆっくり流れる小さな点で、静止した背景に奥行きと空気感を足す。
花より背面に描画する。
"""

import math
import random

import pygame


class AtmosphereParticles:
    """夕方の光に浮かぶ微粒子"""

    def __init__(self, width: int, height: int, count: int = 55):
        self.width = width
        self.height = height
        self.rng = random.Random(7)
        self.particles: list[dict] = []

        for _ in range(count):
            self.particles.append({
                "x": self.rng.uniform(0, width),
                "y": self.rng.uniform(0, height * 0.82),
                "size": self.rng.uniform(1.2, 3.5),
                "vx": self.rng.uniform(6, 22),
                "vy": self.rng.uniform(-6, 6),
                "phase": self.rng.uniform(0, math.pi * 2),
                "wobble": self.rng.uniform(0.6, 1.4),
                "alpha": self.rng.randint(35, 100),
                "warm": self.rng.random() < 0.65,
            })

    def update(self, dt: float) -> None:
        for p in self.particles:
            p["x"] += p["vx"] * dt
            p["y"] += p["vy"] * dt
            if p["x"] > self.width + 10:
                p["x"] = -10
                p["y"] = self.rng.uniform(0, self.height * 0.82)
            elif p["x"] < -10:
                p["x"] = self.width + 10

    def draw(self, screen: pygame.Surface, time_sec: float) -> None:
        for p in self.particles:
            wobble_y = math.sin(time_sec * p["wobble"] + p["phase"]) * 4
            x = int(p["x"])
            y = int(p["y"] + wobble_y)
            size = int(p["size"])

            if p["warm"]:
                color = (255, 248, 210, p["alpha"])
            else:
                color = (220, 240, 255, p["alpha"] // 2)

            surf = pygame.Surface((size * 2 + 2, size * 2 + 2), pygame.SRCALPHA)
            pygame.draw.circle(surf, color, (size + 1, size + 1), size)
            screen.blit(surf, (x - size, y - size), special_flags=pygame.BLEND_PREMULTIPLIED)
