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
    NOD_THRESHOLD = 0.04 
    NOD_COOLDOWN = 45 
    
    WINK_THRESHOLD = 0.02 
    WINK_COOLDOWN = 15     

    # ========================================================
    # ★ 首振り（反復カウント方式）の新しい設定
    # ========================================================
    # 方向転換とみなすための最低限の移動量（ノイズ除去用）
    SHAKE_MIN_MOVEMENT = 0.015 
    # 首振りが完了するまでの制限時間（フレーム数。45フレーム＝約1.5秒以内に振り終わる必要がある）
    SHAKE_TIMEOUT = 30
    # 必要とする方向転換の回数（左右の往復。3〜4回連続で「いやいや」と振ると発動）
    SHAKE_REQUIRED_SWITCHES = 3 
    # 発動後のクールダウン時間
    SHAKE_COOLDOWN = 45