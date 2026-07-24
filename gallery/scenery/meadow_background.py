"""Poster-inspired background for the gallery display."""

import math
import random

import pygame

from gallery.animation_helpers import lerp_color
from gallery.scenery.drifting_cloud import DriftingCloud


class MeadowBackground:
    """Soft pink poster paper, watercolor hills, flowers, ribbon, and title."""

    PAPER_TOP = (255, 235, 232)
    PAPER_MID = (255, 226, 224)
    PAPER_BOTTOM = (255, 242, 236)
    ROSE = (199, 94, 104)
    ROSE_DEEP = (161, 75, 84)
    ROSE_PALE = (250, 185, 188)
    CREAM = (255, 249, 240)
    LEAF = (95, 128, 83)
    LEAF_PALE = (145, 169, 112)
    HILL_FAR = (218, 225, 164)
    HILL_MID = (185, 203, 112)
    HILL_NEAR = (146, 176, 70)

    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.horizon_y = int(height * 0.52)
        self.rng = random.Random(42)
        self.static = self._build_static()
        self.clouds = [DriftingCloud(width, height, self.rng) for _ in range(4)]

    def _draw_vertical_gradient(
        self,
        surface: pygame.Surface,
        top: tuple[int, int, int],
        mid: tuple[int, int, int],
        bottom: tuple[int, int, int],
        y_start: int,
        y_end: int,
    ) -> None:
        span = max(1, y_end - y_start)
        for y in range(y_start, y_end):
            t = (y - y_start) / span
            if t < 0.52:
                color = lerp_color(top, mid, t / 0.52)
            else:
                color = lerp_color(mid, bottom, (t - 0.52) / 0.48)
            pygame.draw.line(surface, color, (0, y), (self.width, y))

    def _draw_paper_texture(self, surface: pygame.Surface) -> None:
        texture = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        for _ in range(1500):
            x = self.rng.randrange(self.width)
            y = self.rng.randrange(self.height)
            alpha = self.rng.randint(5, 14)
            color = (255, 255, 255, alpha) if self.rng.random() < 0.55 else (214, 143, 145, alpha)
            texture.set_at((x, y), color)
        surface.blit(texture, (0, 0))

    def _draw_border(self, surface: pygame.Surface) -> None:
        inset = 24
        pygame.draw.rect(surface, (255, 250, 246), (inset, inset, self.width - inset * 2, self.height - inset * 2), 2)
        pygame.draw.rect(
            surface,
            (225, 134, 143),
            (inset + 8, inset + 8, self.width - (inset + 8) * 2, self.height - (inset + 8) * 2),
            1,
        )

    def _draw_hill_layer(
        self,
        surface: pygame.Surface,
        base_y: int,
        color: tuple[int, int, int],
        amplitude: float,
        frequency: float,
        phase: float,
        alpha: int,
    ) -> None:
        layer = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        points = [(0, self.height)]
        step = 28
        for x in range(0, self.width + step, step):
            wave = math.sin(x * frequency + phase) * amplitude
            wave += math.sin(x * frequency * 2.0 + phase * 1.4) * amplitude * 0.28
            points.append((x, base_y + wave))
        points.append((self.width, self.height))
        pygame.draw.polygon(layer, (*color, alpha), points)
        surface.blit(layer, (0, 0))

    def _draw_flower(self, surface: pygame.Surface, cx: int, cy: int, scale: float, angle: float = 0.0) -> None:
        flower = pygame.Surface((int(140 * scale), int(140 * scale)), pygame.SRCALPHA)
        center = (flower.get_width() // 2, flower.get_height() // 2)
        petal_color = (247, 155, 158, 96)
        petal_edge = (214, 103, 113, 86)
        for i in range(7):
            theta = angle + i * math.tau / 7
            px = center[0] + int(math.cos(theta) * 22 * scale)
            py = center[1] + int(math.sin(theta) * 18 * scale)
            rect = pygame.Rect(0, 0, int(48 * scale), int(24 * scale))
            rect.center = (px, py)
            pygame.draw.ellipse(flower, petal_color, rect)
            pygame.draw.ellipse(flower, petal_edge, rect, 1)
        pygame.draw.circle(flower, (219, 159, 67, 170), center, max(4, int(9 * scale)))
        surface.blit(flower, (cx - center[0], cy - center[1]))

    def _draw_leaf(self, surface: pygame.Surface, x: int, y: int, w: int, h: int, color: tuple[int, int, int]) -> None:
        leaf = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.ellipse(leaf, (*color, 130), leaf.get_rect())
        surface.blit(leaf, (x, y))

    def _draw_floral_corner(self, surface: pygame.Surface, left: bool, top: bool) -> None:
        cluster = pygame.Surface((310, 250), pygame.SRCALPHA)
        origin_x = 42 if left else 250
        origin_y = 42 if top else 196
        stem_color = (*self.LEAF, 110)

        for i in range(8):
            x1 = origin_x + (-1 if not left else 1) * self.rng.randint(0, 110)
            y1 = origin_y + (-1 if not top else 1) * self.rng.randint(0, 90)
            x2 = x1 + (-1 if not left else 1) * self.rng.randint(36, 96)
            y2 = y1 + (-1 if not top else 1) * self.rng.randint(18, 64)
            pygame.draw.line(cluster, stem_color, (x1, y1), (x2, y2), 2)
            self._draw_leaf(cluster, min(x1, x2), min(y1, y2), 30, 13, self.LEAF_PALE)

        flowers = [(68, 58, 0.92), (125, 44, 0.58), (54, 132, 0.50), (178, 86, 0.42)]
        if not left:
            flowers = [(310 - x, y, s) for x, y, s in flowers]
        if not top:
            flowers = [(x, 250 - y, s) for x, y, s in flowers]
        for x, y, scale in flowers:
            self._draw_flower(cluster, x, y, scale, self.rng.random() * math.tau)

        x = 0 if left else self.width - cluster.get_width()
        y = 0 if top else self.height - cluster.get_height()
        surface.blit(cluster, (x, y))

    def _draw_ribbon(self, surface: pygame.Surface) -> None:
        y = int(self.height * 0.19)
        x = int(self.width * 0.5)
        ribbon = pygame.Surface((470, 70), pygame.SRCALPHA)
        pygame.draw.polygon(ribbon, (252, 206, 202, 120), [(20, 36), (84, 10), (370, 16), (450, 40), (368, 62), (88, 56)])
        pygame.draw.line(ribbon, (218, 103, 114, 150), (74, 13), (376, 18), 2)
        pygame.draw.line(ribbon, (218, 103, 114, 120), (88, 55), (364, 61), 2)
        font = pygame.font.SysFont(["Georgia", "Times New Roman", "serif"], 30, bold=True)
        label = font.render("Flower Gallery", True, self.ROSE_DEEP)
        ribbon.blit(label, label.get_rect(center=(235, 36)))
        surface.blit(ribbon, (x - 235, y))

    def _draw_title(self, surface: pygame.Surface) -> None:
        font = pygame.font.SysFont(["Georgia", "Times New Roman", "serif"], 76, bold=True)
        text = "Flower Nose"
        shadow = font.render(text, True, (236, 174, 179))
        title = font.render(text, True, self.ROSE)
        rect = title.get_rect(center=(self.width // 2, int(self.height * 0.105)))
        surface.blit(shadow, rect.move(3, 3))
        surface.blit(title, rect)

    def _build_static(self) -> pygame.Surface:
        surface = pygame.Surface((self.width, self.height))
        self._draw_vertical_gradient(surface, self.PAPER_TOP, self.PAPER_MID, self.PAPER_BOTTOM, 0, self.height)
        self._draw_paper_texture(surface)
        self._draw_border(surface)
        self._draw_title(surface)
        self._draw_ribbon(surface)

        field_top = int(self.height * 0.58)
        wash = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        pygame.draw.rect(wash, (255, 228, 224, 120), (70, field_top - 32, self.width - 140, self.height - field_top + 12), border_radius=8)
        surface.blit(wash, (0, 0))

        self._draw_hill_layer(surface, field_top + 24, self.HILL_FAR, 16, 0.0045, 0.8, 85)
        self._draw_hill_layer(surface, field_top + 54, self.HILL_MID, 22, 0.0055, 2.1, 100)
        self._draw_hill_layer(surface, field_top + 88, self.HILL_NEAR, 26, 0.0065, 4.0, 112)

        self._draw_floral_corner(surface, left=True, top=True)
        self._draw_floral_corner(surface, left=False, top=False)
        self._draw_flower(surface, int(self.width * 0.47), int(self.height * 0.93), 0.42, 0.3)
        self._draw_flower(surface, int(self.width * 0.53), int(self.height * 0.91), 0.34, 1.1)

        return surface.convert()

    def draw(self, screen: pygame.Surface, time_sec: float) -> None:
        screen.blit(self.static, (0, 0))
        for cloud in self.clouds:
            cloud.draw(screen, time_sec, self.width)
