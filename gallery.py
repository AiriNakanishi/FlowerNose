import pygame
import os
import glob
import time
import sys

# ============================================
# 1. 初期設定
# ============================================
SAVE_DIR = "FlowerNose_Gallery"
if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)

pygame.init()

# 閲覧用ディスプレイのサイズ（プロジェクターやモニターに合わせて変更してください）
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Flower Nose - Live Gallery")

# ギャラリーの背景色（透明な線画が映えるように真っ白に設定）
BG_COLOR = (255, 255, 255)

# 画像を並べるグリッド（マス目）の設定
GRID_COLS = 3
GRID_ROWS = 2
MAX_IMAGES = GRID_COLS * GRID_ROWS
IMAGE_WIDTH = WINDOW_WIDTH // GRID_COLS
IMAGE_HEIGHT = WINDOW_HEIGHT // GRID_ROWS

# 最後にフォルダを確認した時間
last_check_time = 0

print("ギャラリーを起動しました。フォルダを監視しています...")

# ============================================
# 2. メインループ
# ============================================
running = True
while running:
    # 「✕」ボタンやESCキーで終了
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            running = False

    current_time = time.time()
    
    # 2秒ごとにフォルダの中身をチェックする
    if current_time - last_check_time > 2.0:
        last_check_time = current_time
        
        # フォルダ内のPNG画像を取得し、更新日時順（新しい順）に並べ替え
        search_pattern = os.path.join(SAVE_DIR, "*.png")
        image_files = glob.glob(search_pattern)
        image_files.sort(key=os.path.getmtime, reverse=True)
        
        # 最新の画像を最大6枚取得
        latest_files = image_files[:MAX_IMAGES]
        
        # 画面を白で塗りつぶす（リセット）
        screen.fill(BG_COLOR)
        
        # 画像を読み込んでグリッド状に配置
        for i, file_path in enumerate(latest_files):
            try:
                # 画像を読み込み
                img = pygame.image.load(file_path)
                # 画像をマス目のサイズに綺麗に縮小（アスペクト比は無視してぴったり埋める）
                img = pygame.transform.smoothscale(img, (IMAGE_WIDTH, IMAGE_HEIGHT))
                
                # 描画するX, Y座標を計算
                col = i % GRID_COLS
                row = i // GRID_COLS
                x = col * IMAGE_WIDTH
                y = row * IMAGE_HEIGHT
                
                # 画像を画面に貼り付け
                screen.blit(img, (x, y))
            except Exception as e:
                print(f"画像読み込みエラー: {file_path}")
        
        # 画面を更新
        pygame.display.flip()

    # CPUの負荷を下げるために少し待機
    pygame.time.wait(100)

pygame.quit()
sys.exit()