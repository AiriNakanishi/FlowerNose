"""
Pygame のメインループ

やること:
  1. 画面を初期化する
  2. キー操作（全画面 / 花畑リセット / 終了）を受け付ける
  3. 定期的に saved_flower_loader で新しい花 PNG を確認する
  4. 背景（scenery）→ 花（visitor_flowers）の順に描画する
  5. gallery/ の .py 変更を検知したらホットリロードする（開発用）
"""

import os
import sys
import time

import pygame

from gallery import hot_reload
from gallery.saved_flower_loader import snapshot_flower_images
from gallery.settings import (
    FOLDER_CHECK_INTERVAL,
    FPS,
    GALLERY_DISPLAY_INDEX,
    SAVE_DIR,
    WINDOW_HEIGHT,
    WINDOW_WIDTH,
)
from gallery.visitor_flowers import FlowerField

# コード変更の監視間隔（秒）
CODE_WATCH_INTERVAL = 0.5


def open_gallery_display(flags: int = 0) -> pygame.Surface:
    display_count = pygame.display.get_num_displays()
    display_index = GALLERY_DISPLAY_INDEX
    if display_index >= display_count:
        print(f"Display {display_index + 1} was not found. Using display 1 instead.")
        display_index = 0
    return pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), flags, display=display_index)


def main() -> None:
    os.makedirs(SAVE_DIR, exist_ok=True)

    pygame.init()
    screen = open_gallery_display()
    pygame.display.set_caption("Flower Nose - 花畑")
    clock = pygame.time.Clock()

    field = FlowerField()
    folder_snapshot = snapshot_flower_images()
    paths = list(folder_snapshot)
    field.populate(paths)

    last_check = 0.0
    last_code_check = 0.0
    code_mtimes = hot_reload.snapshot_mtimes()
    start_time = time.time()
    is_fullscreen = False

    print("花畑ディスプレイを起動しました。FlowerNose_Gallery を監視しています...")
    print("開発: gallery/ 内の .py を保存すると自動で再読み込みします（手動は R）")

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0
        now = time.time()
        elapsed = now - start_time

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_f:
                    is_fullscreen = not is_fullscreen
                    flags = pygame.FULLSCREEN if is_fullscreen else 0
                    screen = open_gallery_display(flags)
                elif event.key == pygame.K_r:
                    # コードも読み直してから花畑を作り直す
                    try:
                        field, paths = hot_reload.rebuild_flower_field()
                        code_mtimes = hot_reload.snapshot_mtimes()
                        start_time = time.time()
                        print("ホットリロードしました（R）")
                    except Exception as exc:
                        print(f"ホットリロード失敗: {exc}")

        # gallery/ のソース変更を検知 → 自動リロード
        if now - last_code_check >= CODE_WATCH_INTERVAL:
            last_code_check = now
            if hot_reload.has_changed(code_mtimes):
                try:
                    field, paths = hot_reload.rebuild_flower_field()
                    code_mtimes = hot_reload.snapshot_mtimes()
                    start_time = time.time()
                    print("コード変更を検知 → ホットリロードしました")
                except Exception as exc:
                    code_mtimes = hot_reload.snapshot_mtimes()
                    print(f"ホットリロード失敗: {exc}")

        if now - last_check >= FOLDER_CHECK_INTERVAL:
            last_check = now
            current_snapshot = snapshot_flower_images()
            paths = list(current_snapshot)
            modified_paths = {
                path
                for path in current_snapshot.keys() & folder_snapshot.keys()
                if current_snapshot[path] != folder_snapshot[path]
            }
            field.sync_files(paths, modified_paths)
            folder_snapshot = current_snapshot

        field.update(dt)
        field.draw_background(screen, elapsed)
        field.draw(screen, elapsed)
        pygame.display.flip()

    pygame.quit()
    sys.exit()
