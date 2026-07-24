"""Subtle decorative cloud puffs."""

import random

import pygame


class DriftingCloud:
    """Very soft clouds that read as poster decoration, not blue-sky scenery."""

    def __init__(self, width: int, height: int, rng: random.Random):
        self.base_y = rng.randint(int(height * 0.12), int(height * 0.32))
        self.scale = rng.uniform(0.45, 0.85)
        self.speed = rng.uniform(4, 10)
        self.alpha = rng.randint(65, 120)
        self.x = rng.uniform(-width * 0.2, width * 1.1)

        blob_w = int(180 * self.scale)
        blob_h = int(70 * self.scale)
        self.image = pygame.Surface((blob_w, blob_h), pygame.SRCALPHA)
        puff_color = (255, 250, 246, self.alpha)
        offsets = [
            (int(blob_w * 0.28), int(blob_h * 0.55), int(34 * self.scale)),
            (int(blob_w * 0.50), int(blob_h * 0.42), int(42 * self.scale)),
            (int(blob_w * 0.72), int(blob_h * 0.58), int(30 * self.scale)),
            (int(blob_w * 0.42), int(blob_h * 0.68), int(26 * self.scale)),
        ]
        for cx, cy, radius in offsets:
            pygame.draw.circle(self.image, puff_color, (cx, cy), radius)

    def draw(self, screen: pygame.Surface, time_sec: float, screen_width: int) -> None:
        x = (self.x + time_sec * self.speed) % (screen_width + self.image.get_width())
        x -= self.image.get_width()
        screen.blit(self.image, (int(x), self.base_y))
