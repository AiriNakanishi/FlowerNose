# core/face_tracker.py
import mediapipe as mp
import cv2
import config
from collections import deque

class FaceTracker:
    def __init__(self):
        BaseOptions = mp.tasks.BaseOptions
        FaceLandmarker = mp.tasks.vision.FaceLandmarker
        FaceLandmarkerOptions = mp.tasks.vision.FaceLandmarkerOptions
        VisionRunningMode = mp.tasks.vision.RunningMode

        options = FaceLandmarkerOptions(
            base_options=BaseOptions(model_asset_path=config.System.MODEL_PATH),
            running_mode=VisionRunningMode.IMAGE,
            num_faces=1
        )
        self.landmarker = FaceLandmarker.create_from_options(options)
        
        self.y_history = deque(maxlen=20)
        self.nod_cooldown = 0
        self.wink_cooldown = 0

    def get_nose_position(self, image_rgb, width, height):
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=image_rgb)
        detection_result = self.landmarker.detect(mp_image)

        is_nodding = False
        wink_direction = None

        if self.nod_cooldown > 0: self.nod_cooldown -= 1
        if self.wink_cooldown > 0: self.wink_cooldown -= 1

        if detection_result.face_landmarks:
            landmarks = detection_result.face_landmarks[0]
            
            nose_tip = landmarks[4]
            cx = int(nose_tip.x * width)
            cy = int(nose_tip.y * height)

            # --- うなずき検知ロジック ---
            self.y_history.append(nose_tip.y)
            if len(self.y_history) == 20 and self.nod_cooldown == 0:
                oldest_y, lowest_y, newest_y = self.y_history[0], max(self.y_history), self.y_history[-1]
                if (lowest_y - oldest_y) > config.Gestures.NOD_THRESHOLD and (lowest_y - newest_y) > config.Gestures.NOD_THRESHOLD:
                    is_nodding = True
                    self.nod_cooldown = config.Gestures.NOD_COOLDOWN
                    self.y_history.clear()

            # --- ウィンク検知ロジック ---
            if self.wink_cooldown == 0:
                left_eye_openness = abs(landmarks[159].y - landmarks[145].y)
                right_eye_openness = abs(landmarks[386].y - landmarks[374].y)
                ratio_threshold = 2.0
                
                # ★修正: カメラ反転を考慮し、返す方向（'left', 'right'）を入れ替えました
                if right_eye_openness < config.Gestures.WINK_THRESHOLD and left_eye_openness > right_eye_openness * ratio_threshold:
                    wink_direction = 'right' # 画面から見て右に進む
                    self.wink_cooldown = config.Gestures.WINK_COOLDOWN
                
                elif left_eye_openness < config.Gestures.WINK_THRESHOLD and right_eye_openness > left_eye_openness * ratio_threshold:
                    wink_direction = 'left' # 画面から見て左に進む
                    self.wink_cooldown = config.Gestures.WINK_COOLDOWN

            return (cx, cy), is_nodding, wink_direction
        
        self.y_history.clear()
        return None, False, None