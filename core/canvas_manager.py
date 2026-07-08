# core/canvas_manager.py
import pygame
import os
from datetime import datetime
import config

class CanvasManager:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.drawing_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        # ★ 左右で別々の記憶を持つように変更
        self.strokes = {'left': [], 'right': []}            
        self.current_stroke = {'left': None, 'right': None}   
        self.current_segment = {'left': None, 'right': None}  

        if not os.path.exists(config.System.SAVE_DIR):
            os.makedirs(config.System.SAVE_DIR)
            
        self.palette = [
            config.Colors.PASTEL_BLUE, config.Colors.PASTEL_PURPLE,
            config.Colors.PEN_PINK, config.Colors.PASTEL_RED,
            config.Colors.PASTEL_ORANGE, config.Colors.PASTEL_YELLOW,
            config.Colors.PASTEL_GREEN
        ]
        # 初期色を左右で変えておく
        self.current_color_index = {'left': 2, 'right': 4} 

    def get_catmull_rom_points(self, p0, p1, p2, p3, num_points=10):
        points = []
        for i in range(num_points):
            t = i / float(num_points - 1)
            t2 = t * t
            t3 = t2 * t
            x = 0.5 * ((2 * p1[0]) + (-p0[0] + p2[0]) * t + (2 * p0[0] - 5 * p1[0] + 4 * p2[0] - p3[0]) * t2 + (-p0[0] + 3 * p1[0] - 3 * p2[0] + p3[0]) * t3)
            y = 0.5 * ((2 * p1[1]) + (-p0[1] + p2[1]) * t + (2 * p0[1] - 5 * p1[1] + 4 * p2[1] - p3[1]) * t2 + (-p0[1] + 3 * p1[1] - 3 * p2[1] + p3[1]) * t3)
            points.append((int(x), int(y)))
        return points

    def change_color(self, side, direction):
        if direction == 'left':
            self.current_color_index[side] = (self.current_color_index[side] - 1) % len(self.palette)
        elif direction == 'right':
            self.current_color_index[side] = (self.current_color_index[side] + 1) % len(self.palette)
        
        if self.current_stroke[side] is not None and self.current_segment[side] is not None and len(self.current_segment[side]['points']) > 0:
            last_point = self.current_segment[side]['points'][-1]
            self.current_segment[side] = {
                'color': self.palette[self.current_color_index[side]],
                'points': [last_point] 
            }
            self.current_stroke[side].append(self.current_segment[side])

    def add_point(self, side, pos):
        # ★ 見えない壁（境界線）の判定
        x, y = pos
        if side == 'left' and x > self.width // 2: return
        if side == 'right' and x < self.width // 2: return

        if self.current_stroke[side] is None:
            self.current_segment[side] = {'color': self.palette[self.current_color_index[side]], 'points': [pos]}
            self.current_stroke[side] = [self.current_segment[side]] 
            self.strokes[side].append(self.current_stroke[side])     
        else:
            self.current_segment[side]['points'].append(pos)

    def end_stroke(self, side):
        self.current_stroke[side] = None
        self.current_segment[side] = None

    def undo(self, side):
        if len(self.strokes[side]) > 0:
            self.strokes[side].pop()
            self.end_stroke(side)

    def redraw(self):
        self.drawing_surface.fill(config.Colors.TRANSPARENT)
        for side in ['left', 'right']:
            for stroke in self.strokes[side]:
                for segment in stroke:
                    points = segment['points']
                    color = segment['color']
                    
                    if len(points) < 2:
                        for pt in points:
                            pygame.draw.circle(self.drawing_surface, color, pt, config.Sizes.PEN_THICKNESS // 2)
                        continue

                    padded_points = [points[0]] + points + [points[-1]]
                    for i in range(len(padded_points) - 3):
                        p_curve = self.get_catmull_rom_points(
                            padded_points[i], padded_points[i+1],
                            padded_points[i+2], padded_points[i+3]
                        )
                        for j in range(len(p_curve) - 1):
                            pygame.draw.line(self.drawing_surface, color, p_curve[j], p_curve[j+1], config.Sizes.PEN_THICKNESS)
                            pygame.draw.circle(self.drawing_surface, color, p_curve[j], config.Sizes.PEN_THICKNESS // 2)

    def draw_palette(self, screen):
        box_size = 40; margin = 10; start_y = self.height - box_size - 20
        
        # 左右それぞれのパレットを描画
        for side in ['left', 'right']:
            start_x = 20 if side == 'left' else self.width // 2 + 20
            
            for i, color in enumerate(self.palette):
                x = start_x + i * (box_size + margin)
                pygame.draw.rect(screen, color, (x, start_y, box_size, box_size))
                if i == self.current_color_index[side]:
                    pygame.draw.rect(screen, config.Colors.BLACK, (x-4, start_y-4, box_size+8, box_size+8), 5)
                else:
                    pygame.draw.rect(screen, config.Colors.BLACK, (x, start_y, box_size, box_size), 1)

    def clear_canvas(self, side):
        self.strokes[side] = []
        self.current_stroke[side] = None
        self.current_segment[side] = None

    def save_image(self, side):
        self.redraw() # 保存前に最新状態を描画
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = os.path.join(config.System.SAVE_DIR, f"flower_{side}_{timestamp}.png")
        
        # ★ 案Aの実現：保存した人の側の「半分の画面」だけを切り取って保存
        rect = pygame.Rect(0, 0, self.width // 2, self.height) if side == 'left' else pygame.Rect(self.width // 2, 0, self.width // 2, self.height)
        sub_surface = self.drawing_surface.subsurface(rect)
        
        pygame.image.save(sub_surface, filepath)
        print(f"🎉 {side}側の絵を保存しました: {filepath}")
        
        # 保存した側の絵だけを消去
        self.clear_canvas(side)

    def get_surface(self):
        self.redraw()
        return self.drawing_surface