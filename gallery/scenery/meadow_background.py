"""
花畑の背景（空・丘・草地）

静止部分は起動時に 1 枚の Surface へ描き込み、毎フレームは雲だけ流す。
来場者の花（visitor_flowers/）より背面に描画される。
"""

import math
import random

import pygame

from gallery.animation_helpers import lerp_color
from gallery.scenery.drifting_cloud import DriftingCloud


class MeadowBackground:
    """空・丘・草地・太陽・雲をまとめて描画する背景"""

    # 空: 上は澄んだ青、地平付近は暖かい色
    SKY_TOP = (92, 168, 228)
    SKY_MID = (168, 210, 245)
    SKY_HORIZON = (255, 232, 198)
    SUN_CORE = (255, 248, 210)
    SUN_GLOW = (255, 220, 150)

    # 丘・草地: 遠景ほど青みがかった薄い色（空気遠近法）
    HILL_FAR = (118, 156, 138)
    HILL_MID = (96, 148, 104)
    HILL_NEAR = (78, 132, 82)
    FIELD_BACK = (104, 162, 88)
    FIELD_MID = (88, 146, 74)
    FIELD_FRONT = (62, 122, 58)
    FIELD_SHADOW = (48, 98, 46)

    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.horizon_y = int(height * 0.52)
        self.rng = random.Random(42)
        self.static = self._build_static()
        self.clouds = [DriftingCloud(width, height, self.rng) for _ in range(5)]

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
            if t < 0.55:
                color = lerp_color(top, mid, t / 0.55)
            else:
                color = lerp_color(mid, bottom, (t - 0.55) / 0.45)
            pygame.draw.line(surface, color, (0, y), (self.width, y))

    def _draw_hill_layer(
        self,
        surface: pygame.Surface,
        base_y: int,
        color: tuple[int, int, int],
        amplitude: float,
        frequency: float,
        phase: float,
    ) -> None:
        points = [(0, self.height)]
        step = 24
        for x in range(0, self.width + step, step):
            wave = math.sin(x * frequency + phase) * amplitude
            wave += math.sin(x * frequency * 2.1 + phase * 1.7) * amplitude * 0.35
            y = base_y + wave
            points.append((x, y))
        points.append((self.width, self.height))
        pygame.draw.polygon(surface, color, points)

    def _draw_grass_texture(
        self,
        surface: pygame.Surface,
        y_start: int,
        y_end: int,
        density: int,
    ) -> None:
        for _ in range(density):
            x = self.rng.randint(0, self.width)
            y = self.rng.randint(y_start, y_end)
            depth = (y - y_start) / max(1, y_end - y_start)
            length = self.rng.randint(4, 10 + int(depth * 10))
            angle = self.rng.uniform(-0.55, 0.55)
            dx = int(math.sin(angle) * length)
            dy = -int(math.cos(abs(angle)) * length)
            shade = lerp_color((96, 150, 78), self.FIELD_SHADOW, depth * 0.6)
            if self.rng.random() < 0.25:
                shade = lerp_color(shade, (130, 176, 92), 0.35)
            pygame.draw.line(surface, shade, (x, y), (x + dx, y + dy), 1)

    def _draw_sun(self, surface: pygame.Surface) -> None:
        sun_x = int(self.width * 0.78)
        sun_y = int(self.height * 0.14)
        glow = pygame.Surface((260, 260), pygame.SRCALPHA)
        for radius, alpha in ((120, 18), (90, 32), (60, 48), (36, 70)):
            color = (*self.SUN_GLOW, alpha)
            pygame.draw.circle(glow, color, (130, 130), radius)
        surface.blit(glow, (sun_x - 130, sun_y - 130))
        pygame.draw.circle(surface, self.SUN_CORE, (sun_x, sun_y), 26)

    def _build_static(self) -> pygame.Surface:
        surface = pygame.Surface((self.width, self.height))

        self._draw_vertical_gradient(
            surface, self.SKY_TOP, self.SKY_MID, self.SKY_HORIZON, 0, self.horizon_y
        )
        self._draw_sun(surface)

        self._draw_hill_layer(surface, self.horizon_y - 10, self.HILL_FAR, 26, 0.0045, 0.8)
        self._draw_hill_layer(surface, self.horizon_y + 8, self.HILL_MID, 32, 0.0055, 2.1)
        self._draw_hill_layer(surface, self.horizon_y + 28, self.HILL_NEAR, 38, 0.0065, 4.0)

        field_top = self.horizon_y + 18
        self._draw_vertical_gradient(
            surface, self.FIELD_BACK, self.FIELD_MID, self.FIELD_FRONT, field_top, self.height
        )

        light_patch = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        for i in range(3):
            cx = int(self.width * (0.18 + i * 0.22))
            cy = int(self.height * (0.72 + i * 0.05))
            radius = int(self.width * 0.18)
            alpha = 22 + i * 6
            pygame.draw.circle(light_patch, (210, 240, 160, alpha), (cx, cy), radius)
        shadow_patch = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        pygame.draw.ellipse(
            shadow_patch,
            (20, 50, 25, 35),
            (int(self.width * 0.55), int(self.height * 0.62), int(self.width * 0.5), int(self.height * 0.38)),
        )
        surface.blit(light_patch, (0, 0))
        surface.blit(shadow_patch, (0, 0))

        self._draw_grass_texture(surface, field_top, int(self.height * 0.72), 500)
        self._draw_grass_texture(surface, int(self.height * 0.68), self.height, 900)

        haze = pygame.Surface((self.width, 80), pygame.SRCALPHA)
        for y in range(80):
            alpha = int(38 * (1 - abs(y - 40) / 40))
            pygame.draw.line(haze, (255, 245, 220, alpha), (0, y), (self.width, y))
        surface.blit(haze, (0, self.horizon_y - 40))

        return surface.convert()

    def draw(self, screen: pygame.Surface, time_sec: float) -> None:
        screen.blit(self.static, (0, 0))
        for cloud in self.clouds:
            cloud.draw(screen, time_sec, self.width)
