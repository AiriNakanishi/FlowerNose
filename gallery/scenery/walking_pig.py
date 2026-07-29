import math
import random
import os
import pygame

from gallery.settings import (
    PIG_IMAGE_PATH,
    PIG_SCALE_MIN,
    PIG_SCALE_MAX,
    PIG_SPEED_MIN,
    PIG_SPEED_MAX,
    GROUND_Y_MIN,
    GROUND_Y_MAX,
    WINDOW_WIDTH
)

class WalkingPig:
    """草原をトコトコ歩く豚さん"""

    def __init__(self):
        self.image_original = None
        if os.path.exists(PIG_IMAGE_PATH):
            try:
                self.image_original = pygame.image.load(PIG_IMAGE_PATH).convert_alpha()
            except pygame.error:
                print(f"豚の画像読み込みエラー: {PIG_IMAGE_PATH}")

        self.width = WINDOW_WIDTH
        self.reset()

    def reset(self):
        """画面外から新しいスピードと高さで再出発する"""
        # 方向: 1 (右向き), -1 (左向き)
        self.direction = random.choice([1, -1])
        self.speed = random.uniform(PIG_SPEED_MIN, PIG_SPEED_MAX) * self.direction
        
        # 画面の端のさらに奥からスタートさせる
        if self.direction == 1:
            self.x = -150.0
        else:
            self.x = self.width + 150.0

        # 草原の範囲内に配置 (花と同じか少し奥を歩かせる)
        self.ground_y = random.randint(GROUND_Y_MIN, GROUND_Y_MAX) 
        
        # Y座標(奥行き)に合わせてスケールを調整
        depth = (self.ground_y - GROUND_Y_MIN) / max(1, GROUND_Y_MAX - GROUND_Y_MIN)
        self.scale = PIG_SCALE_MIN + (PIG_SCALE_MAX - PIG_SCALE_MIN) * depth
        
        self.image = None
        if self.image_original:
            w = int(self.image_original.get_width() * self.scale)
            h = int(self.image_original.get_height() * self.scale)
            scaled = pygame.transform.smoothscale(self.image_original, (max(1, w), max(1, h)))
            
            # 元画像が「左向き」なので、右向きに歩く時は画像を左右反転
            flip_x = (self.direction == 1)
            self.image = pygame.transform.flip(scaled, flip_x, False)

    def update(self, dt: float) -> None:
        self.x += self.speed * dt
        
        # 画面外に完全に出たらリセットして再登場
        if self.direction == 1 and self.x > self.width + 200:
            self.reset()
        elif self.direction == -1 and self.x < -200:
            self.reset()

    def draw(self, screen: pygame.Surface, time_sec: float) -> None:
        if not self.image:
            return
        
        # ゆっくり大きくジャンプする調整（残してあります）
        bounce = abs(math.sin(time_sec * 3.0)) * 200.0 * self.scale
        
        draw_x = int(self.x)
        draw_y = int(self.ground_y - bounce + (150 * self.scale))
        
        rect = self.image.get_rect(midbottom=(draw_x, draw_y))
        
        # ちょっとした足元の影
        shadow_w = int(self.image.get_width() * 0.6)
        shadow_h = int(shadow_w * 0.2)
        shadow_surf = pygame.Surface((shadow_w, shadow_h), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow_surf, (30, 60, 30, 40), shadow_surf.get_rect())
        
        # 影はコメントアウトした状態のままにしてあります
        # screen.blit(shadow_surf, (draw_x - shadow_w // 2, self.ground_y - shadow_h // 2))

        # 豚本体の描画
        screen.blit(self.image, rect)