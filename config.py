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
    MAIN_DISPLAY_INDEX = 2
    
class Gestures:
    # NOD_THRESHOLD = 0.04
    NOD_THRESHOLD = 0.03    # NOD_STILLNESS_THRESHOLD = 0.015 
    NOD_STILLNESS_THRESHOLD = 0.015
    NOD_COOLDOWN = 15
    
    WINK_THRESHOLD = 0.02 
    WINK_COOLDOWN = 15     

    # SHAKE_MIN_MOVEMENT = 0.015 
    SHAKE_MIN_MOVEMENT = 0.015
    SHAKE_TIMEOUT = 15
    SHAKE_REQUIRED_SWITCHES = 2
    SHAKE_COOLDOWN = 30
