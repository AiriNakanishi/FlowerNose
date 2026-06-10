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
        self.clear_canvas()
        
        if not os.path.exists(config.System.SAVE_DIR):
            os.makedirs(config.System.SAVE_DIR)
            
        # カラーパレットの準備
        self.palette = [
            config.Colors.PASTEL_BLUE,
            config.Colors.PASTEL_PURPLE,
            config.Colors.PEN_PINK,
            config.Colors.PASTEL_RED,
            config.Colors.PASTEL_ORANGE,
            config.Colors.PASTEL_YELLOW,
            config.Colors.PASTEL_GREEN
        ]
        self.current_color_index = 2 # 初期色はピンク(インデックス2)

    def change_color(self, direction):
        """色を左右に変更する"""
        if direction == 'left':
            self.current_color_index = (self.current_color_index - 1) % len(self.palette)
        elif direction == 'right':
            self.current_color_index = (self.current_color_index + 1) % len(self.palette)
        print(f"🎨 ペンの色を変更しました")

    def draw_line(self, start_pos, end_pos):
        if start_pos and end_pos:
            pygame.draw.line(
                self.drawing_surface, 
                self.palette[self.current_color_index], # 現在選択中の色を使用
                start_pos, 
                end_pos, 
                config.Sizes.PEN_THICKNESS
            )

    def draw_palette(self, screen):
        """画面左下にカラーパレットを描画する"""
        box_size = 40
        margin = 10
        start_x = 20
        start_y = self.height - box_size - 20

        for i, color in enumerate(self.palette):
            x = start_x + i * (box_size + margin)
            
            # 色の四角を描画
            pygame.draw.rect(screen, color, (x, start_y, box_size, box_size))
            
            # 現在選択されている色には枠線をつける
            if i == self.current_color_index:
                pygame.draw.rect(screen, config.Colors.BLACK, (x-4, start_y-4, box_size+8, box_size+8), 5)
            else:
                pygame.draw.rect(screen, config.Colors.BLACK, (x, start_y, box_size, box_size), 1)

    def clear_canvas(self):
        self.drawing_surface.fill(config.Colors.TRANSPARENT)

    def save_image(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"flower_{timestamp}.png"
        filepath = os.path.join(config.System.SAVE_DIR, filename)
        pygame.image.save(self.drawing_surface, filepath)
        print(f"🎉 絵を保存しました: {filepath}")
        self.clear_canvas()

    def get_surface(self):
        return self.drawing_surface