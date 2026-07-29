"""
1 本の花の咲きアニメーション

来場者が描いた PNG 1 枚を、地面（ground_y）を根元として
高さ 0 → 100% に伸ばし、咲き終わったら風で揺らす。
"""

import math
import random

import pygame

from gallery.animation_helpers import ease_out_back, ease_out_cubic
from gallery.settings import BLOOM_DURATION_MAX, BLOOM_DURATION_MIN


AA_SCALE = 3


class BloomingFlower:
    """来場者が描いた 1 枚の花を、地面から咲かせる"""

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

        # 咲き終わったあとの風による揺れ
        self.sway_phase = random.uniform(0, math.pi * 2)
        self.sway_speed = random.uniform(0.8, 1.4)
        self.sway_amount = random.uniform(2, 5)

    @property
    def progress(self) -> float:
        """咲き具合 0.0（地面に埋まっている）〜 1.0（咲き終わり）"""
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
        """根元の楕円影で、花が地面に立っている感じを出す"""
        if progress < 0.15:
            return

        shadow_w = max(8, int(width * 0.55 * min(1.0, progress)))
        shadow_h = max(3, int(shadow_w * 0.22))
        alpha = int(55 * min(1.0, progress))

        shadow_hi = pygame.Surface((shadow_w * AA_SCALE, shadow_h * AA_SCALE), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow_hi, (20, 45, 22, alpha), shadow_hi.get_rect())
        shadow = safe_scale(shadow_hi, (shadow_w, shadow_h))
        screen.blit(shadow, (x - shadow_w // 2, ground_y - shadow_h // 2 + 2), special_flags=pygame.BLEND_PREMULTIPLIED)

    def draw(self, screen: pygame.Surface, time_sec: float) -> None:
        progress = self.progress
        if progress <= 0:
            return

        src = pygame.transform.flip(self.image, self.flip_x, False) if self.flip_x else self.image
        base_w = max(1, int(src.get_width() * self.scale))
        base_h = max(1, int(src.get_height() * self.scale))

        # 高さだけ伸ばして「地面から生えてくる」表現
        grow = ease_out_cubic(min(1.0, progress * 1.15))
        draw_h = max(1, int(base_h * grow))
        draw_w = base_w

        scaled = safe_scale(src, (draw_w, draw_h))

        sway_x = 0
        if self.is_bloomed:
            sway_x = int(math.sin(time_sec * self.sway_speed + self.sway_phase) * self.sway_amount)

        draw_x = self.x + sway_x
        self._draw_ground_shadow(screen, draw_x, self.ground_y, draw_w, progress)

        rect = scaled.get_rect(midbottom=(draw_x, self.ground_y))
        screen.blit(scaled, rect, special_flags=pygame.BLEND_PREMULTIPLIED)
