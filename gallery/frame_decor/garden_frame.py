"""Decorative foliage around the screen edge."""

from __future__ import annotations

import math
import os
import random

import pygame

import config


REFERENCE_WIDTH = 1280
REFERENCE_HEIGHT = 720
AA_SCALE = 3
TREE_TARGET_WIDTH_RATIO = 0.60
TREE_MAX_HEIGHT_RATIO = 0.55
LEFT_TREE_X_INSET_RATIO = 0.16
RIGHT_TREE_X_INSET_RATIO = 0.08
TREE_Y_INSET_RATIO = 0.05


class GardenFrame:
    """Leafy foreground frame inspired by picture-book meadow illustrations."""

    GRASS_DARK = (158, 204, 132)
    GRASS_MID = (184, 224, 146)
    GRASS_LIGHT = (220, 240, 172)
    WHITE_FLOWER = (252, 254, 246)
    FLOWER_PINK = (246, 158, 202)
    FLOWER_YELLOW = (250, 226, 104)

    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.display_scale = min(width / REFERENCE_WIDTH, height / REFERENCE_HEIGHT)
        self.rng = random.Random(431)
        self.left_tree = self._load_tree_image("fefttree.png", "lefttree.png")
        self.right_tree = self._load_tree_image("righttree.png")
        self.static = self._build_static()

    def _s(self, value: float) -> int:
        return max(1, int(value * self.display_scale))

    def _draw_smooth_ellipse(
        self,
        surface: pygame.Surface,
        color: tuple[int, int, int, int] | tuple[int, int, int],
        rect: pygame.Rect | tuple[int, int, int, int],
    ) -> None:
        rect = pygame.Rect(rect)
        if rect.width <= 0 or rect.height <= 0:
            return
        hi = pygame.Surface((rect.width * AA_SCALE, rect.height * AA_SCALE), pygame.SRCALPHA)
        pygame.draw.ellipse(hi, color, hi.get_rect())
        smooth = pygame.transform.smoothscale(hi, rect.size)
        surface.blit(smooth, rect.topleft)

    def _draw_rotated_petal(
        self,
        surface: pygame.Surface,
        center: tuple[int, int],
        size: tuple[int, int],
        angle: float,
        color: tuple[int, int, int],
    ) -> None:
        petal = pygame.Surface((size[0] * 2, size[1] * 2), pygame.SRCALPHA)
        rect = pygame.Rect(size[0] // 2, size[1] // 2, size[0], size[1])
        self._draw_smooth_ellipse(petal, (*color, 232), rect)
        self._draw_smooth_ellipse(
            petal,
            (255, 255, 255, 62),
            (rect.x + size[0] // 5, rect.y + size[1] // 6, max(2, size[0] // 2), max(2, size[1] // 3)),
        )
        rotated = pygame.transform.rotozoom(petal, -math.degrees(angle), 1.0)
        surface.blit(rotated, (center[0] - rotated.get_width() // 2, center[1] - rotated.get_height() // 2))

    def _draw_flower(
        self,
        surface: pygame.Surface,
        x: int,
        y: int,
        radius: int,
        petal_color: tuple[int, int, int],
    ) -> None:
        petal_count = 6 if radius < self._s(16) else 8
        for i in range(petal_count):
            angle = math.tau * i / petal_count
            wobble = math.sin(i * 1.7 + radius) * 0.13
            petal_len = int(radius * (1.08 + 0.12 * math.sin(i * 2.1)))
            petal_w = max(3, int(radius * (0.58 + 0.08 * math.cos(i * 1.3))))
            distance = radius * (0.42 + 0.05 * math.cos(i))
            px = x + int(math.cos(angle + wobble) * distance)
            py = y + int(math.sin(angle + wobble) * distance)
            self._draw_rotated_petal(surface, (px, py), (petal_len, petal_w), angle + wobble, petal_color)

        center_r = max(2, int(radius * 0.26))
        pygame.draw.circle(surface, (*self.FLOWER_YELLOW, 238), (x, y), center_r)
        pygame.draw.circle(surface, (255, 244, 148, 220), (x - center_r // 3, y - center_r // 3), max(1, center_r // 2))

    def _load_tree_image(self, *names: str) -> pygame.Surface | None:
        for name in names:
            path = os.path.join(config.BASE_DIR, "assets", name)
            if os.path.exists(path):
                return pygame.image.load(path).convert_alpha()
        return None

    def _draw_tree_image(self, surface: pygame.Surface, image: pygame.Surface | None, side: str) -> None:
        if image is None:
            return
        target_w = int(self.width * TREE_TARGET_WIDTH_RATIO)
        max_h = int(self.height * TREE_MAX_HEIGHT_RATIO)
        scale = min(target_w / image.get_width(), max_h / image.get_height())
        size = (max(1, int(image.get_width() * scale)), max(1, int(image.get_height() * scale)))
        tree = pygame.transform.smoothscale(image, size)
        x_inset_ratio = LEFT_TREE_X_INSET_RATIO if side == "left" else RIGHT_TREE_X_INSET_RATIO
        inset_x = int(tree.get_width() * x_inset_ratio)
        inset_y = int(tree.get_height() * TREE_Y_INSET_RATIO)
        x = -inset_x if side == "left" else self.width - tree.get_width() + inset_x
        y = -inset_y
        surface.blit(tree, (x, y))

    def _draw_bottom_grass(self, surface: pygame.Surface) -> None:
        base_y = self.height + self._s(8)
        for _ in range(280):
            x = self.rng.randint(0, self.width)
            edge_bias = min(x, self.width - x) / max(1, self.width / 2)
            height = self.rng.randint(self._s(34), self._s(112))
            if edge_bias > 0.66:
                height = int(height * self.rng.uniform(0.45, 0.78))
            lean = self.rng.uniform(-18, 18) * self.display_scale
            color = self.rng.choice((self.GRASS_DARK, self.GRASS_MID, self.GRASS_LIGHT))
            pygame.draw.aaline(surface, (*color, self.rng.randint(205, 245)), (x, base_y), (int(x + lean), base_y - height))

        flower_specs = (
            (0.06, 0.89, 22, self.FLOWER_PINK),
            (0.12, 0.92, 17, (248, 184, 212)),
            (0.86, 0.89, 21, self.FLOWER_PINK),
            (0.94, 0.87, 24, self.FLOWER_YELLOW),
            (0.78, 0.94, 14, self.WHITE_FLOWER),
            (0.25, 0.95, 13, self.FLOWER_PINK),
        )
        for xr, yr, radius, color in flower_specs:
            self._draw_flower(surface, int(self.width * xr), int(self.height * yr), self._s(radius), color)

        for _ in range(36):
            x = self.rng.choice((
                self.rng.randint(0, self._s(340)),
                self.rng.randint(self.width - self._s(340), self.width),
            ))
            y = self.rng.randint(int(self.height * 0.82), self.height - self._s(24))
            self._draw_flower(surface, x, y, self.rng.randint(self._s(5), self._s(9)), self.rng.choice((self.WHITE_FLOWER, self.FLOWER_PINK, self.FLOWER_YELLOW)))

    def _build_static(self) -> pygame.Surface:
        surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self._draw_tree_image(surface, self.left_tree, "left")
        self._draw_tree_image(surface, self.right_tree, "right")
        self._draw_bottom_grass(surface)
        return surface

    def draw(self, screen: pygame.Surface, _time_sec: float) -> None:
        screen.blit(self.static, (0, 0))
