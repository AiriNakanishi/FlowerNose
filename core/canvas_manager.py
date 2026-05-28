# canvas_manager.py
import pygame
import os
from datetime import datetime
import config

class CanvasManager:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        
        # 透明なシートの作成
        self.drawing_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.clear_canvas()
        
        # 保存先フォルダの準備
        if not os.path.exists(config.System.SAVE_DIR):
            os.makedirs(config.System.SAVE_DIR)
            print(f"保存先フォルダ '{config.System.SAVE_DIR}' を作成しました。")

    def draw_line(self, start_pos, end_pos):
        """キャンバスに線を引く"""
        if start_pos and end_pos:
            pygame.draw.line(
                self.drawing_surface, 
                config.Colors.PEN_PINK, 
                start_pos, 
                end_pos, 
                config.Sizes.PEN_THICKNESS
            )

    def clear_canvas(self):
        """キャンバスを透明にリセットする"""
        self.drawing_surface.fill(config.Colors.TRANSPARENT)

    def save_image(self):
        """描かれた線画をPNGとして保存する"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"flower_{timestamp}.png"
        filepath = os.path.join(config.System.SAVE_DIR, filename)
        
        pygame.image.save(self.drawing_surface, filepath)
        print(f"🎉 絵を保存しました: {filepath}")
        self.clear_canvas() # 保存したらリセット

    def get_surface(self):
        """合成用の透明シートを返す"""
        return self.drawing_surface