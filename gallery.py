import glob
import os
import random
import sys
import time

import pygame


# ============================================
# 1. 初期設定
# ============================================
# main.py / CanvasManager が保存したPNGを、このフォルダから読み込む。
SAVE_DIR = "FlowerNose_Gallery"
if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)

pygame.init()

# ギャラリー表示用ウィンドウのサイズ。
# 展示するモニターやプロジェクターに合わせてここを変える。
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Flower Nose - Live Gallery")

# 背景色と、絵を重ねたときの影の色。
# 絵そのものの背景は透明にするので、白いカードは敷かない。
BG_COLOR = (248, 246, 240)
SHADOW_COLOR = (205, 197, 184, 95)

# 表示する絵の枚数と、ランダム配置の見た目を決める設定。
MAX_IMAGES = 100
MIN_ART_SIZE = 110
MAX_ART_SIZE = 245
MAX_ROTATION = 9
EDGE_MARGIN = 24

# 白背景として扱う明るさのしきい値。
# 古いPNGなどに白い背景が残っていても、ギャラリー上では透明に近づける。
WHITE_ALPHA_THRESHOLD = 248

# 画像ごとのランダムな位置・サイズ・角度を覚えておく。
# 2秒ごとの再読み込みで毎回シャッフルされないようにするため。
layout_cache = {}

# 白抜き・縮小・回転済みの画像を覚えておく。
# 100枚表示でも、同じ画像を毎回処理し直さないため。
surface_cache = {}

# 最後に保存フォルダを確認した時刻。
last_check_time = 0


def get_layout(file_path):
    """画像ごとのランダム配置を作る。作成済みなら同じ配置を使い回す。"""
    if file_path not in layout_cache:
        art_size = random.randint(MIN_ART_SIZE, MAX_ART_SIZE)
        max_x = max(EDGE_MARGIN, WINDOW_WIDTH - art_size - EDGE_MARGIN)
        max_y = max(EDGE_MARGIN, WINDOW_HEIGHT - art_size - EDGE_MARGIN)
        x = random.randint(EDGE_MARGIN, max_x)
        y = random.randint(EDGE_MARGIN, max_y)
        angle = random.uniform(-MAX_ROTATION, MAX_ROTATION)
        layout_cache[file_path] = (x, y, art_size, angle)

    return layout_cache[file_path]


def make_white_pixels_transparent(surface):
    """白い背景だけを透明にする。

    CanvasManagerの新しい保存画像は最初から透明だが、
    過去に白背景で保存されたPNGが混ざっても展示になじむようにする。
    """
    width, height = surface.get_size()
    transparent = pygame.Color(255, 255, 255, 0)

    for y in range(height):
        for x in range(width):
            color = surface.get_at((x, y))
            if (
                color.r >= WHITE_ALPHA_THRESHOLD
                and color.g >= WHITE_ALPHA_THRESHOLD
                and color.b >= WHITE_ALPHA_THRESHOLD
            ):
                surface.set_at((x, y), transparent)

    return surface


def make_art_surface(file_path, art_size, angle):
    """PNGを読み込み、白背景を抜いて、ランダムな角度に回転する。"""
    cache_key = (file_path, os.path.getmtime(file_path), art_size, angle)
    if cache_key in surface_cache:
        return surface_cache[cache_key]

    img = pygame.image.load(file_path).convert_alpha()
    img_w, img_h = img.get_size()
    scale = min(art_size / img_w, art_size / img_h)
    scaled_size = (max(1, int(img_w * scale)), max(1, int(img_h * scale)))
    img = pygame.transform.smoothscale(img, scaled_size)
    img = make_white_pixels_transparent(img)

    art = pygame.transform.rotate(img, angle)
    surface_cache[cache_key] = art
    return art


def draw_soft_shadow(target, art, x, y):
    """透過した絵の後ろに、控えめな影だけを置く。"""
    shadow = pygame.Surface(art.get_size(), pygame.SRCALPHA)
    shadow.blit(art, (0, 0))
    shadow.fill(SHADOW_COLOR, special_flags=pygame.BLEND_RGBA_MULT)
    target.blit(shadow, (x + 7, y + 9))


print("ギャラリーを起動しました。フォルダを監視しています...")

# ============================================
# 2. メインループ
# ============================================
running = True
while running:
    # ウィンドウの閉じるボタン、またはESCキーで終了する。
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            running = False

    current_time = time.time()

    # 2秒ごとに保存フォルダを見に行く。
    # main.py側で新しい絵が保存されたら、自動でここに追加表示される。
    if current_time - last_check_time > 2.0:
        last_check_time = current_time

        # 新しいPNGほど手前に表示したいので、更新日時の新しい順に並べる。
        search_pattern = os.path.join(SAVE_DIR, "*.png")
        image_files = glob.glob(search_pattern)
        image_files.sort(key=os.path.getmtime, reverse=True)
        latest_files = image_files[:MAX_IMAGES]

        screen.fill(BG_COLOR)

        # 画面から消えた古い画像のレイアウト情報を掃除する。
        visible_files = set(latest_files)
        for cached_file in list(layout_cache):
            if cached_file not in visible_files:
                del layout_cache[cached_file]
        for cache_key in list(surface_cache):
            if cache_key[0] not in visible_files:
                del surface_cache[cache_key]

        # 古い絵から先に描くことで、新しい絵が自然に上へ重なる。
        for file_path in reversed(latest_files):
            try:
                x, y, art_size, angle = get_layout(file_path)
                art = make_art_surface(file_path, art_size, angle)
                draw_soft_shadow(screen, art, x, y)
                screen.blit(art, (x, y))
            except Exception:
                print(f"画像読み込みエラー: {file_path}")

        pygame.display.flip()

    # CPU使用率を下げるため、短く待機する。
    pygame.time.wait(100)

pygame.quit()
sys.exit()
