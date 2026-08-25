import math
import random

import pygame

from gallery.animation_helpers import ease_out_back, ease_out_cubic
from gallery.settings import BLOOM_DURATION_MAX, BLOOM_DURATION_MIN


AA_SCALE = 3


class BloomingFlower:
    """One saved flower that blooms from the ground and then sways."""

    def __init__(
        self,
        image: pygame.Surface,
        source_path: str,
        x: int,
        ground_y: int,
        scale: float,
        delay: float = 0.0,
        flip_x: bool = False,
    ):
        self.image = image
        self.source_path = source_path
        self.x = x
        self.ground_y = ground_y
        self.scale = scale
        self.delay = delay
        self.flip_x = flip_x
        self.src_image = pygame.transform.flip(image, True, False) if flip_x else image
        self.base_w = max(1, int(self.src_image.get_width() * self.scale))
        self.base_h = max(1, int(self.src_image.get_height() * self.scale))
        self._scaled_cache: dict[int, pygame.Surface] = {}
        self._shadow_cache: dict[tuple[int, int, int], pygame.Surface] = {}
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
        if progress < 0.15:
            return

        shadow_w = max(8, int(width * 0.55 * min(1.0, progress)))
        shadow_h = max(3, int(shadow_w * 0.22))
        alpha = int(55 * min(1.0, progress))
        cache_key = (shadow_w, shadow_h, alpha)

        shadow = self._shadow_cache.get(cache_key)
        if shadow is None:
            shadow_hi = pygame.Surface((shadow_w * AA_SCALE, shadow_h * AA_SCALE), pygame.SRCALPHA).convert_alpha()
            pygame.draw.ellipse(shadow_hi, (20, 45, 22, alpha), shadow_hi.get_rect())
            shadow = pygame.transform.smoothscale(shadow_hi, (shadow_w, shadow_h))
            self._shadow_cache[cache_key] = shadow

        screen.blit(shadow, (x - shadow_w // 2, ground_y - shadow_h // 2 + 2))

    def draw(self, screen: pygame.Surface, time_sec: float) -> None:
        progress = self.progress
        if progress <= 0:
            return

        grow = ease_out_cubic(min(1.0, progress * 1.15))
        draw_h = max(1, int(self.base_h * grow))
        draw_w = self.base_w

        scaled = self._scaled_cache.get(draw_h)
        if scaled is None:
            scaled = pygame.transform.smoothscale(self.src_image, (draw_w, draw_h))
            self._scaled_cache[draw_h] = scaled

        sway_x = 0
        if self.is_bloomed:
            sway_x = int(math.sin(time_sec * self.sway_speed + self.sway_phase) * self.sway_amount)

        draw_x = self.x + sway_x
        rect = scaled.get_rect(midbottom=(draw_x, self.ground_y))
        screen.blit(scaled, rect)
