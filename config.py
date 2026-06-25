# config.py
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class Colors:
    PASTEL_BLUE   = (173, 216, 230)
    PASTEL_PURPLE = (221, 160, 221)
    PEN_PINK      = (255, 100, 150)
    PASTEL_RED    = (255, 153, 153)
    PASTEL_ORANGE = (255, 204, 153)
    PASTEL_YELLOW = (255, 255, 153)
    PASTEL_GREEN  = (144, 238, 144)

    GUIDE_RED = (255, 0, 0)
    TRANSPARENT = (0, 0, 0, 0)
    BLACK = (50, 50, 50)

class Sizes:
    WINDOW_WIDTH = 1280
    WINDOW_HEIGHT = 720
    PEN_THICKNESS = 20
    FPS = 30

class System:
    SAVE_DIR = os.path.join(BASE_DIR, "FlowerNose_Gallery")
    MODEL_PATH = os.path.join(BASE_DIR, "assets", "face_landmarker.task")
    
class Gestures:
    # ========================================================
    # ★ うなずき（スピード＋静止方式）の新しい設定
    # ========================================================
    NOD_THRESHOLD = 0.04            # うなずきの深さ（4%）
    NOD_STILLNESS_THRESHOLD = 0.015 # 静止とみなす最大ブレ幅（1.5%。人間が止まれる限界の微小な揺れ）
    NOD_COOLDOWN = 15
    
    # --- ウィンク設定 ---
    WINK_THRESHOLD = 0.02 
    WINK_COOLDOWN = 15     

    # --- 首振り設定 ---
    SHAKE_MIN_MOVEMENT = 0.015 
    SHAKE_TIMEOUT = 15
    SHAKE_REQUIRED_SWITCHES = 4 
    SHAKE_COOLDOWN = 30