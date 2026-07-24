"""Gallery display settings."""

import config

SAVE_DIR = config.System.SAVE_DIR
WINDOW_WIDTH = config.Sizes.WINDOW_WIDTH
WINDOW_HEIGHT = config.Sizes.WINDOW_HEIGHT

# Keep the layout airy so the poster-like background stays visible.
MIN_FLOWERS = 8
MAX_FLOWERS = 24

GROUND_Y_MIN = int(WINDOW_HEIGHT * 0.56)
GROUND_Y_MAX = int(WINDOW_HEIGHT * 0.90)

FLOWER_SCALE_MIN = 0.11
FLOWER_SCALE_MAX = 0.31

BLOOM_DURATION_MIN = 1.2
BLOOM_DURATION_MAX = 2.4
BLOOM_STAGGER_MAX = 4.0

FOLDER_CHECK_INTERVAL = 2.0
FPS = 60
