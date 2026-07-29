"""
流れる雲

scenery/meadow_background.py から使われる。
数個の円を重ねたシンプルな形で、右方向にゆっくり流れる。
"""

import random

import pygame


AA_SCALE = 3
REFERENCE_WIDTH = 1280
REFERENCE_HEIGHT = 720


class DriftingCloud:
    """ふわっと流れる雲"""

    def __init__(self, width: int, height: int, rng: random.Random):
        display_scale = min(width / REFERENCE_WIDTH, height / REFERENCE_HEIGHT)
        self.base_y = rng.randint(int(height * 0.06), int(height * 0.28))
        self.scale = rng.uniform(0.7, 1.4) * display_scale
        self.speed = rng.uniform(8, 18) * display_scale
        self.alpha = rng.randint(150, 210)
        self.x = rng.uniform(-width * 0.2, width * 1.1)

        # 雲の形は起動時に 1 枚だけ描いてキャッシュ
        blob_w = int(180 * self.scale)
        blob_h = int(70 * self.scale)
        hi = pygame.Surface((blob_w * AA_SCALE, blob_h * AA_SCALE), pygame.SRCALPHA).convert_alpha()
        puff_color = (255, 255, 255, self.alpha)
        offsets = [
            (int(blob_w * 0.28), int(blob_h * 0.55), int(34 * self.scale)),
            (int(blob_w * 0.50), int(blob_h * 0.42), int(42 * self.scale)),
            (int(blob_w * 0.72), int(blob_h * 0.58), int(30 * self.scale)),
            (int(blob_w * 0.42), int(blob_h * 0.68), int(26 * self.scale)),
        ]
        for cx, cy, radius in offsets:
            pygame.draw.circle(
                hi,
                puff_color,
                (cx * AA_SCALE, cy * AA_SCALE),
                radius * AA_SCALE,
            )
        self.image = pygame.transform.smoothscale(hi, (blob_w, blob_h))

    def draw(self, screen: pygame.Surface, time_sec: float, screen_width: int) -> None:
        x = (self.x + time_sec * self.speed) % (screen_width + self.image.get_width())
        x -= self.image.get_width()
        screen.blit(self.image, (int(x), self.base_y))
