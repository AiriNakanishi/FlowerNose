"""
花畑の背景（空・丘・草地）

静止部分は起動時に 1 枚の Surface へ描き込み、毎フレームは雲だけ流す。
来場者の花（visitor_flowers/）より背面に描画される。
"""

import math
import random

import pygame
import pygame.gfxdraw

from gallery.animation_helpers import lerp_color
from gallery.scenery.drifting_cloud import DriftingCloud


AA_SCALE = 3
REFERENCE_WIDTH = 1280
REFERENCE_HEIGHT = 720


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
    FIELD_DEEP_SHADOW = (38, 82, 44)
    FIELD_LIGHT = (144, 184, 92)
    TREE_TRUNK = (92, 76, 54)
    TREE_SHADOW = (58, 82, 52)
    TREE_LIGHT = (104, 142, 82)

    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.display_scale = min(width / REFERENCE_WIDTH, height / REFERENCE_HEIGHT)
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
        step = max(24, int(24 * self.display_scale))
        for x in range(0, self.width + step, step):
            wave = math.sin(x * frequency + phase) * amplitude * self.display_scale
            wave += math.sin(x * frequency * 2.1 + phase * 1.7) * amplitude * self.display_scale * 0.35
            y = base_y + wave
            points.append((x, y))
        points.append((self.width, self.height))
        self._draw_smooth_polygon(surface, color, points)

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
            length = int(self.rng.randint(2, 5 + int(depth * 5)) * self.display_scale)
            angle = self.rng.uniform(-0.38, 0.38)
            dx = int(math.sin(angle) * length)
            dy = -int(math.cos(abs(angle)) * length)
            shade = lerp_color((102, 148, 82), self.FIELD_SHADOW, depth * 0.45)
            if self.rng.random() < 0.25:
                shade = lerp_color(shade, (130, 176, 92), 0.35)
            pygame.draw.aaline(surface, shade, (x, y), (x + dx, y + dy))

    def _blit_smooth_shape(
        self,
        surface: pygame.Surface,
        rect: pygame.Rect,
        draw_func,
    ) -> None:
        if rect.width <= 0 or rect.height <= 0:
            return

        scale = AA_SCALE if rect.width * rect.height < 420_000 else 1
        hi_size = (rect.width * scale, rect.height * scale)
        hi = pygame.Surface(hi_size, pygame.SRCALPHA)
        draw_func(hi, scale)
        smoothed = pygame.transform.smoothscale(hi, rect.size)
        surface.blit(smoothed, rect)

    def _draw_smooth_circle(
        self,
        surface: pygame.Surface,
        color: tuple[int, int, int] | tuple[int, int, int, int],
        center: tuple[int, int],
        radius: int,
    ) -> None:
        pygame.gfxdraw.filled_circle(surface, center[0], center[1], radius, color)
        pygame.gfxdraw.aacircle(surface, center[0], center[1], radius, color)

    def _draw_smooth_ellipse(
        self,
        surface: pygame.Surface,
        color: tuple[int, int, int] | tuple[int, int, int, int],
        rect: pygame.Rect | tuple[int, int, int, int],
    ) -> None:
        rect = pygame.Rect(rect)

        def draw(hi: pygame.Surface, scale: int) -> None:
            pygame.draw.ellipse(hi, color, hi.get_rect())

        self._blit_smooth_shape(surface, rect, draw)

    def _draw_soft_ellipse(
        self,
        surface: pygame.Surface,
        color: tuple[int, int, int],
        rect: pygame.Rect | tuple[int, int, int, int],
        max_alpha: int,
        rings: int = 18,
    ) -> None:
        rect = pygame.Rect(rect)
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        for i in range(rings, 0, -1):
            t = i / rings
            eased = t * t
            current = pygame.Rect(0, 0, int(rect.width * t), int(rect.height * t))
            current.center = rect.center
            alpha = int(max_alpha * eased / rings * 1.8)
            self._draw_smooth_ellipse(overlay, (*color, alpha), current)
        surface.blit(overlay, (0, 0))

    def _draw_smooth_polygon(
        self,
        surface: pygame.Surface,
        color: tuple[int, int, int] | tuple[int, int, int, int],
        points: list[tuple[int, int]],
    ) -> None:
        min_x = min(x for x, _ in points)
        max_x = max(x for x, _ in points)
        min_y = min(y for _, y in points)
        max_y = max(y for _, y in points)
        rect = pygame.Rect(min_x, min_y, max_x - min_x + 1, max_y - min_y + 1)

        def draw(hi: pygame.Surface, scale: int) -> None:
            scaled_points = [((x - rect.x) * scale, (y - rect.y) * scale) for x, y in points]
            pygame.draw.polygon(hi, color, scaled_points)

        self._blit_smooth_shape(surface, rect, draw)

    def _draw_meadow_swales(self, surface: pygame.Surface, field_top: int) -> None:
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        band_count = 7
        for i in range(band_count):
            t = i / max(1, band_count - 1)
            y = int(field_top + (self.height - field_top) * (0.12 + t * 0.86))
            amplitude = (5 + int(t * 10)) * self.display_scale
            phase = 0.7 + i * 0.72
            points = []
            step = max(28, int(28 * self.display_scale))
            for x in range(-40, self.width + 44, step):
                curve = math.sin(x * 0.006 + phase) * amplitude
                curve += math.sin(x * 0.013 + phase * 1.8) * amplitude * 0.32
                points.append((x, int(y + curve)))

            shadow = (*lerp_color(self.FIELD_SHADOW, self.FIELD_DEEP_SHADOW, t), 14 + int(t * 22))
            highlight = (*lerp_color(self.FIELD_LIGHT, (188, 202, 124), t * 0.5), 12 + int((1 - t) * 10))
            pygame.draw.aalines(overlay, shadow, False, points)
            highlight_points = [(x, py - int((5 + t * 4) * self.display_scale)) for x, py in points]
            pygame.draw.aalines(overlay, highlight, False, highlight_points)
        surface.blit(overlay, (0, 0))

    def _draw_meadow_color_grain(self, surface: pygame.Surface, field_top: int) -> None:
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        area_scale = self.width * self.height / (REFERENCE_WIDTH * REFERENCE_HEIGHT)
        grain_count = min(6200, int(700 * area_scale))
        colors = (
            ((184, 210, 112), (226, 236, 150), 0.34),
            ((78, 138, 94), (64, 116, 92), 0.27),
            ((44, 96, 48), (30, 70, 42), 0.25),
            ((130, 170, 78), (164, 196, 96), 0.14),
        )

        for _ in range(grain_count):
            y = self.rng.randint(field_top, self.height - 1)
            depth = (y - field_top) / max(1, self.height - field_top)
            x = self.rng.randint(-12, self.width + 12)
            roll = self.rng.random()
            running = 0.0
            low_color = colors[-1][0]
            high_color = colors[-1][1]
            for color_a, color_b, weight in colors:
                running += weight
                if roll <= running:
                    low_color = color_a
                    high_color = color_b
                    break

            color = lerp_color(high_color, low_color, min(1.0, depth * 1.15))
            if depth > 0.65 and self.rng.random() < 0.32:
                color = lerp_color(color, self.FIELD_DEEP_SHADOW, 0.28)

            length = int(self.rng.uniform(6, 18 + depth * 26) * self.display_scale)
            lean = self.rng.uniform(-0.9, 0.9) + math.sin(x * 0.004 + y * 0.009) * 0.45
            dx = int(lean * length * (0.34 + depth * 0.38))
            dy = -int(length * self.rng.uniform(0.10, 0.42))
            alpha = int(12 + depth * 24 + self.rng.random() * 10)
            if roll < 0.34:
                alpha = int(alpha * (0.72 + (1.0 - depth) * 0.36))
            pygame.draw.aaline(overlay, (*color, alpha), (x, y), (x + dx, y + dy))

        pool_count = min(90, int(12 * area_scale))
        for _ in range(pool_count):
            depth = self.rng.uniform(0.18, 0.94)
            cx = self.rng.randint(0, self.width)
            cy = int(field_top + (self.height - field_top) * depth)
            width = int(self.rng.uniform(26, 76 + depth * 96) * self.display_scale)
            height = max(2, int(width * self.rng.uniform(0.10, 0.22)))
            palette = self.rng.choice(
                (
                    (204, 222, 126, 13),
                    (124, 170, 92, 11),
                    (38, 86, 54, 15),
                    (76, 130, 104, 10),
                )
            )
            rect = pygame.Rect(0, 0, width, height)
            rect.center = (cx, cy)
            self._draw_smooth_ellipse(overlay, palette, rect)

        surface.blit(overlay, (0, 0))

    def _draw_meadow_volume(self, surface: pygame.Surface, field_top: int) -> None:
        depth_overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        for y in range(field_top, self.height):
            depth = (y - field_top) / max(1, self.height - field_top)
            if depth < 0.32:
                alpha = int((0.32 - depth) / 0.32 * 18)
                color = (220, 230, 170, alpha)
            else:
                alpha = int((depth - 0.32) / 0.68 * 44)
                color = (18, 58, 32, alpha)
            pygame.draw.line(depth_overlay, color, (0, y), (self.width, y))
        surface.blit(depth_overlay, (0, 0))

        self._draw_soft_ellipse(
            surface,
            (188, 210, 124),
            (int(self.width * -0.08), int(self.height * 0.50), int(self.width * 0.68), int(self.height * 0.46)),
            72,
            24,
        )
        self._draw_soft_ellipse(
            surface,
            (168, 198, 104),
            (int(self.width * 0.30), int(self.height * 0.48), int(self.width * 0.48), int(self.height * 0.34)),
            48,
            20,
        )
        self._draw_soft_ellipse(
            surface,
            (28, 82, 42),
            (int(self.width * 0.54), int(self.height * 0.63), int(self.width * 0.60), int(self.height * 0.38)),
            70,
            24,
        )
        self._draw_soft_ellipse(
            surface,
            (24, 74, 36),
            (int(self.width * -0.12), int(self.height * 0.72), int(self.width * 0.72), int(self.height * 0.42)),
            52,
            22,
        )
        self._draw_soft_ellipse(
            surface,
            (34, 86, 42),
            (int(self.width * 0.36), int(self.height * 0.78), int(self.width * 0.80), int(self.height * 0.34)),
            46,
            20,
        )

        terrace = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        for y_ratio, alpha in ((0.61, 16), (0.71, 13), (0.82, 10)):
            y = int(self.height * y_ratio)
            points = []
            step = max(24, int(24 * self.display_scale))
            for x in range(-30, self.width + 32, step):
                wave = math.sin(x * 0.0048 + y_ratio * 8) * 8 * self.display_scale
                points.append((x, y + int(wave)))
            lower_points = [(x, py + int(self.height * 0.045)) for x, py in reversed(points)]
            self._draw_smooth_polygon(terrace, (142, 176, 88, alpha), points + lower_points)
        surface.blit(terrace, (0, 0))

    def _draw_grass_clumps(
        self,
        surface: pygame.Surface,
        y_start: int,
        y_end: int,
        count: int,
    ) -> None:
        for _ in range(count):
            x = self.rng.randint(-10, self.width + 10)
            y = self.rng.randint(y_start, y_end)
            depth = (y - y_start) / max(1, y_end - y_start)
            blade_count = self.rng.randint(2, 4)
            base_color = lerp_color((94, 138, 72), self.FIELD_DEEP_SHADOW, depth * 0.58)
            if self.rng.random() < 0.18:
                base_color = lerp_color(base_color, self.FIELD_LIGHT, 0.2)
            for blade in range(blade_count):
                offset = blade - blade_count // 2
                length = int(self.rng.randint(5, 12 + int(depth * 14)) * self.display_scale)
                lean = (offset * self.rng.uniform(1.8, 3.4) + self.rng.uniform(-3, 3)) * self.display_scale
                tip = (int(x + lean), y - length)
                pygame.draw.aaline(surface, base_color, (x + offset, y), tip)

    def _draw_tree(
        self,
        surface: pygame.Surface,
        x: int,
        ground_y: int,
        scale: float,
        lean: float = 0.0,
    ) -> None:
        scale *= self.display_scale
        trunk_h = int(64 * scale)
        trunk_w = max(3, int(10 * scale))
        top_x = int(x + lean * scale)
        trunk_points = [
            (x - trunk_w // 2, ground_y),
            (x + trunk_w // 2, ground_y),
            (top_x + trunk_w // 3, ground_y - trunk_h),
            (top_x - trunk_w // 3, ground_y - trunk_h),
        ]
        self._draw_smooth_polygon(surface, self.TREE_TRUNK, trunk_points)

        shadow = pygame.Surface((int(92 * scale), int(22 * scale)), pygame.SRCALPHA)
        self._draw_smooth_ellipse(shadow, (34, 72, 36, 38), shadow.get_rect())
        surface.blit(shadow, (x - shadow.get_width() // 2, ground_y - shadow.get_height() // 2 + 4))

        crown_size = (int(128 * scale), int(98 * scale))
        crown_hi = pygame.Surface((crown_size[0] * AA_SCALE, crown_size[1] * AA_SCALE), pygame.SRCALPHA)
        cx = crown_size[0] // 2
        cy = int(crown_size[1] * 0.54)
        blobs = (
            (-28, 2, 34, self.TREE_SHADOW),
            (0, -14, 40, self.TREE_LIGHT),
            (30, 2, 32, (82, 126, 72)),
            (-4, 12, 42, (76, 118, 68)),
            (-18, -20, 26, (118, 152, 92)),
        )
        for ox, oy, radius, color in blobs:
            pygame.draw.circle(
                crown_hi,
                (*color, 220),
                ((cx + int(ox * scale)) * AA_SCALE, (cy + int(oy * scale)) * AA_SCALE),
                int(radius * scale * AA_SCALE),
            )
        crown = pygame.transform.smoothscale(crown_hi, crown_size)
        crown.set_alpha(210)
        surface.blit(crown, (top_x - cx, ground_y - trunk_h - int(crown_size[1] * 0.78)))

    def _draw_background_trees(self, surface: pygame.Surface) -> None:
        trees = (
            (0.08, 0.52, 0.48, -12),
            (0.17, 0.51, 0.36, 8),
            (0.91, 0.53, 0.43, 10),
            (0.82, 0.515, 0.31, -6),
        )
        for x_ratio, y_ratio, scale, lean in trees:
            self._draw_tree(surface, int(self.width * x_ratio), int(self.height * y_ratio), scale, lean)

    def _draw_sun(self, surface: pygame.Surface) -> None:
        sun_x = int(self.width * 0.78)
        sun_y = int(self.height * 0.14)
        sun_scale = self.display_scale
        glow_size = int(260 * sun_scale)
        glow_center = glow_size // 2
        glow = pygame.Surface((glow_size, glow_size), pygame.SRCALPHA)
        for radius, alpha in ((120, 18), (90, 32), (60, 48), (36, 70)):
            color = (*self.SUN_GLOW, alpha)
            self._draw_smooth_circle(glow, color, (glow_center, glow_center), int(radius * sun_scale))
        surface.blit(glow, (sun_x - glow_center, sun_y - glow_center))
        self._draw_smooth_circle(surface, self.SUN_CORE, (sun_x, sun_y), int(26 * sun_scale))

    def _draw_bird(
        self,
        screen: pygame.Surface,
        x: int,
        y: int,
        size: float,
        wing_phase: float,
        alpha: int,
    ) -> None:
        wing = 0.5 + 0.5 * math.sin(wing_phase)
        span = max(24, int(size))
        lift = int(size * (0.26 + 0.16 * wing))
        canvas_pad = int(span * 0.42)
        canvas_w = (span * 2 + canvas_pad * 2) * AA_SCALE
        canvas_h = (lift + canvas_pad * 2 + int(size * 0.5)) * AA_SCALE
        bird = pygame.Surface((canvas_w, canvas_h), pygame.SRCALPHA)
        origin_x = canvas_w // 2
        origin_y = canvas_h // 2 + int(size * 0.14 * AA_SCALE)
        stroke = max(2, int(size * 0.07 * AA_SCALE))
        wing_color = (248, 252, 246, alpha)
        shadow_color = (106, 135, 132, max(12, alpha // 3))

        def scale_point(px: float, py: float) -> tuple[int, int]:
            return (int(origin_x + px * AA_SCALE), int(origin_y + py * AA_SCALE))

        def wing_curve(side: int) -> list[tuple[int, int]]:
            points = []
            for step in range(7):
                t = step / 6
                px = side * span * t
                py = -lift * math.sin(t * math.pi) + size * 0.10 * t
                points.append(scale_point(px, py))
            return points

        left = wing_curve(-1)
        right = wing_curve(1)
        for points in (left, right):
            shadow_points = [(px, py + max(1, AA_SCALE)) for px, py in points]
            pygame.draw.lines(bird, shadow_color, False, shadow_points, stroke)
            pygame.draw.lines(bird, wing_color, False, points, stroke)

        body_w = max(3, int(size * 0.20 * AA_SCALE))
        body_h = max(2, int(size * 0.09 * AA_SCALE))
        pygame.draw.ellipse(
            bird,
            (250, 252, 246, alpha),
            (origin_x - body_w // 2, origin_y - body_h // 2, body_w, body_h),
        )

        smooth = pygame.transform.smoothscale(
            bird,
            (max(1, canvas_w // AA_SCALE), max(1, canvas_h // AA_SCALE)),
        )
        screen.blit(smooth, (x - smooth.get_width() // 2, y - smooth.get_height() // 2))

    def _draw_birds(self, screen: pygame.Surface, time_sec: float) -> None:
        cycle = 24.0
        visible_time = 7.5
        cycle_t = time_sec % cycle
        if cycle_t > visible_time:
            return

        cycle_index = int(time_sec // cycle)
        rng = random.Random(300 + cycle_index)
        flock_size = 1 if rng.random() < 0.8 else 2
        direction = -1 if rng.random() < 0.5 else 1
        start_x = -int(self.width * 0.08) if direction > 0 else int(self.width * 1.08)
        travel = self.width * 1.16
        progress = cycle_t / visible_time
        base_y = rng.uniform(self.height * 0.20, self.height * 0.32)
        base_size = rng.uniform(34, 44) * self.display_scale

        for i in range(flock_size):
            spacing = i * rng.uniform(180, 260) * self.display_scale
            x = start_x + direction * (travel * progress - spacing)
            y = base_y + math.sin(progress * math.pi + i * 0.8) * 18 * self.display_scale
            y += (i % 2) * 24 * self.display_scale
            if x < -80 * self.display_scale or x > self.width + 80 * self.display_scale:
                continue
            alpha = int(82 * math.sin(progress * math.pi))
            wing_phase = time_sec * 2.6 + i * 0.8
            self._draw_bird(screen, int(x), int(y), base_size * (1 - i * 0.1), wing_phase, alpha)

    def _build_static(self) -> pygame.Surface:
        surface = pygame.Surface((self.width, self.height))

        self._draw_vertical_gradient(
            surface, self.SKY_TOP, self.SKY_MID, self.SKY_HORIZON, 0, self.horizon_y
        )
        self._draw_sun(surface)

        self._draw_hill_layer(surface, self.horizon_y - int(46 * self.display_scale), self.HILL_FAR, 42, 0.0045 / self.display_scale, 0.8)
        self._draw_hill_layer(surface, self.horizon_y - int(22 * self.display_scale), self.HILL_MID, 48, 0.0055 / self.display_scale, 2.1)
        self._draw_hill_layer(surface, self.horizon_y + int(10 * self.display_scale), self.HILL_NEAR, 52, 0.0065 / self.display_scale, 4.0)
        pygame.draw.rect(
            surface,
            (132, 172, 98),
            (0, self.horizon_y + int(14 * self.display_scale), self.width, int(18 * self.display_scale)),
        )
        haze_band = pygame.Surface((self.width, int(42 * self.display_scale)), pygame.SRCALPHA)
        haze_band.fill((234, 226, 182, 24))
        surface.blit(haze_band, (0, self.horizon_y + int(4 * self.display_scale)))
        self._draw_background_trees(surface)

        field_top = self.horizon_y + int(18 * self.display_scale)
        self._draw_vertical_gradient(
            surface, self.FIELD_BACK, self.FIELD_MID, self.FIELD_FRONT, field_top, self.height
        )
        self._draw_meadow_volume(surface, field_top)
        self._draw_meadow_swales(surface, field_top)

        light_patch = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        for i in range(3):
            cx = int(self.width * (0.18 + i * 0.22))
            cy = int(self.height * (0.72 + i * 0.05))
            radius = int(self.width * 0.18)
            alpha = 22 + i * 6
            self._draw_smooth_circle(light_patch, (210, 240, 160, alpha), (cx, cy), radius)
        shadow_patch = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self._draw_smooth_ellipse(
            shadow_patch,
            (20, 50, 25, 35),
            (int(self.width * 0.55), int(self.height * 0.62), int(self.width * 0.5), int(self.height * 0.38)),
        )
        surface.blit(light_patch, (0, 0))
        surface.blit(shadow_patch, (0, 0))

        self._draw_meadow_color_grain(surface, field_top)
        self._draw_grass_texture(surface, field_top, int(self.height * 0.72), int(76 * self.display_scale))
        self._draw_grass_texture(surface, int(self.height * 0.66), self.height, int(96 * self.display_scale))
        self._draw_grass_clumps(surface, int(self.height * 0.62), int(self.height * 0.76), int(4 * self.display_scale))
        self._draw_grass_clumps(surface, int(self.height * 0.76), self.height, int(6 * self.display_scale))

        haze_height = int(80 * self.display_scale)
        haze = pygame.Surface((self.width, haze_height), pygame.SRCALPHA)
        for y in range(haze_height):
            center = haze_height / 2
            alpha = int(38 * (1 - abs(y - center) / center))
            pygame.draw.line(haze, (255, 245, 220, alpha), (0, y), (self.width, y))
        surface.blit(haze, (0, self.horizon_y - haze_height // 2))

        return surface.convert()

    def draw(self, screen: pygame.Surface, time_sec: float) -> None:
        screen.blit(self.static, (0, 0))
        for cloud in self.clouds:
            cloud.draw(screen, time_sec, self.width)
        self._draw_birds(screen, time_sec)
