"""Bloom animation for one saved flower image."""

import math
import random

import pygame

from gallery.animation_helpers import ease_out_back, ease_out_cubic
from gallery.settings import BLOOM_DURATION_MAX, BLOOM_DURATION_MIN


class BloomingFlower:
    """Grow a visitor flower from its baseline and then gently sway it."""

    def __init__(
        self,
        image: pygame.Surface,
        x: int,
        ground_y: int,
        scale: float,
        delay: float = 0.0,
        flip_x: bool = False,
    ):
        self.image = image
        self.x = x
        self.ground_y = ground_y
        self.scale = scale
        self.delay = delay
        self.flip_x = flip_x
        self.elapsed = 0.0
        self.duration = random.uniform(BLOOM_DURATION_MIN, BLOOM_DURATION_MAX)

        self.sway_phase = random.uniform(0, math.pi * 2)
        self.sway_speed = random.uniform(0.8, 1.4)
        self.sway_amount = random.uniform(2, 5)

    @property
    def progress(self) -> float:
        if self.delay > 0:
            return 0.0
        t = min(1.0, self.elapsed / self.duration)
        return ease_out_back(t)

    @property
    def is_bloomed(self) -> bool:
        return self.delay <= 0 and self.elapsed >= self.duration

    def update(self, dt: float) -> None:
        if self.delay > 0:
            self.delay -= dt
            return
        self.elapsed += dt

    def _draw_ground_shadow(
        self,
        screen: pygame.Surface,
        x: int,
        ground_y: int,
        width: int,
        progress: float,
    ) -> None:
        return

    def draw(self, screen: pygame.Surface, time_sec: float) -> None:
        progress = self.progress
        if progress <= 0:
            return

        src = pygame.transform.flip(self.image, self.flip_x, False) if self.flip_x else self.image
        base_w = max(1, int(src.get_width() * self.scale))
        base_h = max(1, int(src.get_height() * self.scale))

        grow = ease_out_cubic(min(1.0, progress * 1.15))
        draw_h = max(1, int(base_h * grow))
        draw_w = base_w

        scaled = pygame.transform.smoothscale(src, (draw_w, draw_h))

        sway_x = 0
        if self.is_bloomed:
            sway_x = int(math.sin(time_sec * self.sway_speed + self.sway_phase) * self.sway_amount)

        draw_x = self.x + sway_x
        self._draw_ground_shadow(screen, draw_x, self.ground_y, draw_w, progress)

        rect = scaled.get_rect(midbottom=(draw_x, self.ground_y))
        screen.blit(scaled, rect)
