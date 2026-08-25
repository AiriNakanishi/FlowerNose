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
    # ★追加：中央の境界線の色

class Sizes:
    WINDOW_WIDTH = 1280
    WINDOW_HEIGHT = 720
    PEN_THICKNESS = 20
    FPS = 30
    # ★追加：中央の境界線の太さ

class System:
    SAVE_DIR = os.path.join(BASE_DIR, "FlowerNose_Gallery")
    MODEL_PATH = os.path.join(BASE_DIR, "assets", "face_landmarker.task")
    CAMERA_INDEX = 0
    MAIN_DISPLAY_INDEX = 1
    
class Gestures:
    FACE_HIDE_SAVE_SECONDS = 3.0
    FACE_EXIT_HISTORY_SECONDS = 1.0
    FACE_EXIT_MIN_DISTANCE = 0.08
    FACE_EXIT_CONFIRM_SECONDS = 0.25
    
    WINK_CLOSED_SCORE = 0.28
    WINK_OTHER_EYE_MAX_SCORE = 0.50
    WINK_SCORE_DIFFERENCE = 0.15
    WINK_RELEASE_SCORE = 0.22
    WINK_CLOSED_RATIO = 0.58
    WINK_OTHER_EYE_MIN_RATIO = 0.72
    WINK_RATIO_DIFFERENCE = 0.20
    WINK_HOLD_FRAMES = 2
    WINK_ARM_FRAMES = 3
    WINK_RELEASE_FRAMES = 2
    WINK_COOLDOWN = 10

    SHAKE_MIN_MOVEMENT = 0.020
    SHAKE_TIMEOUT = 15
    SHAKE_REQUIRED_SWITCHES = 2
    SHAKE_COOLDOWN = 30
