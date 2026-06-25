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
        
        self.strokes = [] 
        self.current_stroke = None

        if not os.path.exists(config.System.SAVE_DIR):
            os.makedirs(config.System.SAVE_DIR)
            
        self.palette = [
            config.Colors.PASTEL_BLUE,
            config.Colors.PASTEL_PURPLE,
            config.Colors.PEN_PINK,
            config.Colors.PASTEL_RED,
            config.Colors.PASTEL_ORANGE,
            config.Colors.PASTEL_YELLOW,
            config.Colors.PASTEL_GREEN
        ]
        self.current_color_index = 2

    def change_color(self, direction):
        """色を切り替え、描画中ならその場で新しいストロークに分割する"""
        if direction == 'left':
            self.current_color_index = (self.current_color_index - 1) % len(self.palette)
        elif direction == 'right':
            self.current_color_index = (self.current_color_index + 1) % len(self.palette)
        
        # もし線を描いている最中なら、現在の座標を引き継いで新しい色のストロークをその場から開始する
        if self.current_stroke is not None and len(self.current_stroke['points']) > 0:
            last_point = self.current_stroke['points'][-1]
            self.end_stroke()
            self.add_point(last_point)

        print(f"🎨 ペンの色を変更しました")

    def add_point(self, pos):
        if self.current_stroke is None:
            self.current_stroke = {
                'color': self.palette[self.current_color_index],
                'points': [pos]
            }
            self.strokes.append(self.current_stroke)
        else:
            self.current_stroke['points'].append(pos)

    def end_stroke(self):
        self.current_stroke = None

    def undo(self):
        if len(self.strokes) > 0:
            self.strokes.pop()
            self.end_stroke()
            print("↩️ Undo（一手戻る）を実行しました！")

    def redraw(self):
        """記憶しているすべてのストロークを透明シートに描き直す"""
        self.drawing_surface.fill(config.Colors.TRANSPARENT)
        for stroke in self.strokes:
            points = stroke['points']
            color = stroke['color']
            
            # ★バグ対策: 点が1つしかなくても、その場所に丸を描画することで色変更を即座に視覚化する
            # 同時に、太い線の継ぎ目や角が滑らかに丸くなる効果もあります
            for pt in points:
                pygame.draw.circle(
                    self.drawing_surface, 
                    color, 
                    pt, 
                    config.Sizes.PEN_THICKNESS // 2
                )
            
            # 2点以上あれば、それらを線で繋ぐ
            if len(points) >= 2:
                for i in range(1, len(points)):
                    pygame.draw.line(
                        self.drawing_surface, 
                        color, 
                        points[i-1], 
                        points[i], 
                        config.Sizes.PEN_THICKNESS
                    )

    def draw_palette(self, screen):
        box_size = 40
        margin = 10
        start_x = 20
        start_y = self.height - box_size - 20

        for i, color in enumerate(self.palette):
            x = start_x + i * (box_size + margin)
            pygame.draw.rect(screen, color, (x, start_y, box_size, box_size))
            if i == self.current_color_index:
                pygame.draw.rect(screen, config.Colors.BLACK, (x-4, start_y-4, box_size+8, box_size+8), 5)
            else:
                pygame.draw.rect(screen, config.Colors.BLACK, (x, start_y, box_size, box_size), 1)

    def clear_canvas(self):
        self.strokes = []
        self.current_stroke = None
        self.drawing_surface.fill(config.Colors.TRANSPARENT)

    def save_image(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"flower_{timestamp}.png"
        filepath = os.path.join(config.System.SAVE_DIR, filename)
        
        self.redraw()
        pygame.image.save(self.drawing_surface, filepath)
        print(f"🎉 絵を保存しました: {filepath}")
        self.clear_canvas()

    def get_surface(self):
        self.redraw()
        return self.drawing_surface