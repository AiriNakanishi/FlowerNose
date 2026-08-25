"""
花畑ディスプレイの設定値

画面サイズ・花の本数・咲く速さなど、演出全体のパラメータをまとめたファイル。
数値を変えたいときは、まずここを見てください。
"""

import config

# --- 保存先・画面 ---
SAVE_DIR = config.System.SAVE_DIR          # main.py が花 PNG を保存するフォルダ
WINDOW_WIDTH = 3840
WINDOW_HEIGHT = 2160
GALLERY_DISPLAY_INDEX = 2
DISPLAY_SCALE = min(WINDOW_WIDTH / 1280, WINDOW_HEIGHT / 720)

# --- 花畑に咲かせる本数 ---
MIN_FLOWERS = 10   # 最小本数
MAX_FLOWERS = 30   # 最大本数（超えた分は奥の花から削除）

# --- 花の配置範囲（画面下側が地面）---
GROUND_Y_MIN = int(WINDOW_HEIGHT * 0.55)   # 奥の列
GROUND_Y_MAX = int(WINDOW_HEIGHT * 0.88)   # 手前の列

# --- 花の大きさ ---
FLOWER_SCALE_MIN = 0.12 * DISPLAY_SCALE
FLOWER_SCALE_MAX = 0.35 * DISPLAY_SCALE

# --- 咲きアニメーション ---
BLOOM_DURATION_MIN = 1.2   # 1 本が咲き終わる最短秒数
BLOOM_DURATION_MAX = 2.4   # 1 本が咲き終わる最長秒数
BLOOM_STAGGER_MAX = 4.0    # 起動時、花ごとの咲き始め時間差（最大秒）

# --- 背景の光の粒 ---
ATMOSPHERE_PARTICLES = int(18 * DISPLAY_SCALE)

# --- 実行 ---
FOLDER_CHECK_INTERVAL = 2.0  # 新しい花 PNG を何秒ごとにチェックするか
FPS = 60

# --- 豚のアニメーション ---
import os
import config

PIG_IMAGE_PATH = os.path.join(config.BASE_DIR, "assets", "pig.png")
PIG_SCALE_MIN = 0.30   # 奥にいるときのサイズ
PIG_SCALE_MAX = 0.60   # 手前にいるときのサイズ
PIG_SPEED_MIN = 30.0   # 歩く最低スピード
PIG_SPEED_MAX = 70.0   # 歩く最高スピード
WALKPIG_ASSET_DIR = os.path.join(config.BASE_DIR, "assets", "walkpig")
PIG_ANIMATION_FPS = 7.0
PIG_WAIT_MIN = 0.8
PIG_WAIT_MAX = 2.2
PIG_JUMP_DURATION = 0.55
PIG_JUMP_HEIGHT = 110.0
PIG_SIT_DURATION_MIN = 1.2
PIG_SIT_DURATION_MAX = 2.8
PIG_SIT_CHANCE = 0.45
PIG_JUMP_CHANCE = 0.25
PIG_SPONTANEOUS_ACTION_MIN = 4.0
PIG_SPONTANEOUS_ACTION_MAX = 9.0
