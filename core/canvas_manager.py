import os
from datetime import datetime

import pygame

import config


class CanvasManager:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.drawing_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.preview_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

        self.strokes = []
        self.current_stroke = None
        self.current_segment = None

        if not os.path.exists(config.System.SAVE_DIR):
            os.makedirs(config.System.SAVE_DIR)

        self.palette = [
            config.Colors.PASTEL_BLUE,
            config.Colors.PASTEL_PURPLE,
            config.Colors.PEN_PINK,
            config.Colors.PASTEL_RED,
            config.Colors.PASTEL_ORANGE,
            config.Colors.PASTEL_YELLOW,
            config.Colors.PASTEL_GREEN,
        ]
        self.current_color_index = 2

    def get_catmull_rom_points(self, p0, p1, p2, p3, num_points=10):
        points = []
        for i in range(num_points):
            t = i / float(num_points - 1)
            t2 = t * t
            t3 = t2 * t
            x = 0.5 * (
                (2 * p1[0])
                + (-p0[0] + p2[0]) * t
                + (2 * p0[0] - 5 * p1[0] + 4 * p2[0] - p3[0]) * t2
                + (-p0[0] + 3 * p1[0] - 3 * p2[0] + p3[0]) * t3
            )
            y = 0.5 * (
                (2 * p1[1])
                + (-p0[1] + p2[1]) * t
                + (2 * p0[1] - 5 * p1[1] + 4 * p2[1] - p3[1]) * t2
                + (-p0[1] + 3 * p1[1] - 3 * p2[1] + p3[1]) * t3
            )
            points.append((int(x), int(y)))
        return points

    def _draw_curve(self, surface, color, p0, p1, p2, p3):
        p_curve = self.get_catmull_rom_points(p0, p1, p2, p3)
        for start, end in zip(p_curve, p_curve[1:]):
            pygame.draw.line(
                surface,
                color,
                start,
                end,
                config.Sizes.PEN_THICKNESS,
            )
            pygame.draw.circle(
                surface,
                color,
                start,
                config.Sizes.PEN_THICKNESS // 2,
            )

    def _draw_segment(self, surface, segment):
        points = segment["points"]
        color = segment["color"]

        if len(points) < 2:
            for point in points:
                pygame.draw.circle(
                    surface,
                    color,
                    point,
                    config.Sizes.PEN_THICKNESS // 2,
                )
            return

        padded_points = [points[0]] + points + [points[-1]]
        for i in range(len(padded_points) - 3):
            self._draw_curve(
                surface,
                color,
                padded_points[i],
                padded_points[i + 1],
                padded_points[i + 2],
                padded_points[i + 3],
            )

    def _update_preview(self):
        self.preview_surface.fill(config.Colors.TRANSPARENT)
        if self.current_segment is None:
            return

        points = self.current_segment["points"]
        color = self.current_segment["color"]
        if len(points) == 1:
            pygame.draw.circle(
                self.preview_surface,
                color,
                points[0],
                config.Sizes.PEN_THICKNESS // 2,
            )
        elif len(points) >= 2:
            p0 = points[-3] if len(points) >= 3 else points[-2]
            self._draw_curve(
                self.preview_surface,
                color,
                p0,
                points[-2],
                points[-1],
                points[-1],
            )

    def _commit_preview(self):
        self.drawing_surface.blit(self.preview_surface, (0, 0))
        self.preview_surface.fill(config.Colors.TRANSPARENT)

    def change_color(self, direction):
        if direction == "left":
            self.current_color_index = (self.current_color_index - 1) % len(self.palette)
        elif direction == "right":
            self.current_color_index = (self.current_color_index + 1) % len(self.palette)

        if (
            self.current_stroke is not None
            and self.current_segment is not None
            and len(self.current_segment["points"]) > 0
        ):
            self._commit_preview()
            last_point = self.current_segment["points"][-1]
            self.current_segment = {
                "color": self.palette[self.current_color_index],
                "points": [last_point],
            }
            self.current_stroke.append(self.current_segment)
            self._update_preview()

    def add_point(self, pos):
        if self.current_stroke is None:
            self.current_segment = {
                "color": self.palette[self.current_color_index],
                "points": [pos],
            }
            self.current_stroke = [self.current_segment]
            self.strokes.append(self.current_stroke)
        else:
            self.current_segment["points"].append(pos)

        points = self.current_segment["points"]
        if len(points) >= 3:
            p0 = points[-4] if len(points) >= 4 else points[-3]
            self._draw_curve(
                self.drawing_surface,
                self.current_segment["color"],
                p0,
                points[-3],
                points[-2],
                points[-1],
            )
        self._update_preview()

    def end_stroke(self):
        if self.current_stroke is not None:
            self._commit_preview()
        self.current_stroke = None
        self.current_segment = None

    def undo(self):
        if len(self.strokes) > 0:
            self.strokes.pop()
            self.current_stroke = None
            self.current_segment = None
            self.redraw()

    def redraw(self):
        self.drawing_surface.fill(config.Colors.TRANSPARENT)
        self.preview_surface.fill(config.Colors.TRANSPARENT)
        for stroke in self.strokes:
            for segment in stroke:
                self._draw_segment(self.drawing_surface, segment)

    def draw(self, screen):
        screen.blit(self.drawing_surface, (0, 0))
        screen.blit(self.preview_surface, (0, 0))

    def draw_palette(self, screen):
        box_size = 40
        margin = 10
        start_x = 20
        start_y = self.height - box_size - 20

        # --- ここから白い背景を追加 ---
        padding = 10  # 白い背景の余白（パレットの周りにどれくらい白枠を広げるか）
        # パレット全体の横幅を計算
        total_width = (box_size * len(self.palette)) + (margin * (len(self.palette) - 1))
        
        # 背景の座標とサイズ
        bg_x = start_x - padding
        bg_y = start_y - padding
        bg_w = total_width + (padding * 2)
        bg_h = box_size + (padding * 2)
        
        # 白い背景を描画 (255, 255, 255 は白色)
        # 最後の border_radius=10 で角を丸くして柔らかい印象にしています
        pygame.draw.rect(screen, (255, 255, 255), (bg_x, bg_y, bg_w, bg_h), border_radius=10)
        # --- 追加ここまで ---

        for i, color in enumerate(self.palette):
            x = start_x + i * (box_size + margin)
            pygame.draw.rect(screen, color, (x, start_y, box_size, box_size))
            if i == self.current_color_index:
                pygame.draw.rect(
                    screen,
                    config.Colors.BLACK,
                    (x - 4, start_y - 4, box_size + 8, box_size + 8),
                    5,
                )
            else:
                pygame.draw.rect(screen, config.Colors.BLACK, (x, start_y, box_size, box_size), 1)

    def clear_canvas(self):
        self.strokes = []
        self.current_stroke = None
        self.current_segment = None
        self.drawing_surface.fill(config.Colors.TRANSPARENT)
        self.preview_surface.fill(config.Colors.TRANSPARENT)

    def has_drawing(self):
        return any(
            segment["points"]
            for stroke in self.strokes
            for segment in stroke
        )

    def save_image(self):
        self.redraw()

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = os.path.join(config.System.SAVE_DIR, f"flower_{timestamp}.png")

        pygame.image.save(self.drawing_surface, filepath)
        print(f"Saved drawing: {filepath}")

        self.clear_canvas()

    def get_surface(self):
        surface = self.drawing_surface.copy()
        surface.blit(self.preview_surface, (0, 0))
        return surface
