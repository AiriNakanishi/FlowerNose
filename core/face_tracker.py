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
        
        # --- うなずき用（30フレーム＝約1秒分の履歴を保持） ---
        self.y_history = deque(maxlen=30)
        self.x_history = deque(maxlen=30)
        self.nod_cooldown = 0
        
        # --- ウィンク用 ---
        self.wink_cooldown = 0
        
        # --- 首振り用 ---
        self.last_x = None
        self.current_direction = 0
        self.switch_count = 0
        self.shake_timer = 0
        self.shake_cooldown = 0

    def get_nose_position(self, image_rgb, width, height):
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=image_rgb)
        detection_result = self.landmarker.detect(mp_image)

        is_nodding = False
        is_shaking = False
        wink_direction = None

        if self.nod_cooldown > 0: self.nod_cooldown -= 1
        if self.wink_cooldown > 0: self.wink_cooldown -= 1
        if self.shake_cooldown > 0: self.shake_cooldown -= 1
        
        if self.shake_timer > 0:
            self.shake_timer -= 1
            if self.shake_timer == 0:
                self.switch_count = 0
                self.current_direction = 0

        if detection_result.face_landmarks:
            landmarks = detection_result.face_landmarks[0]
            
            nose_tip = landmarks[4]
            cx = int(nose_tip.x * width)
            cy = int(nose_tip.y * height)

            # --- 1. うなずき検知ロジック（スピード＋静止 ハイブリッド型） ---
            self.y_history.append(nose_tip.y)
            self.x_history.append(nose_tip.x)

            if len(self.y_history) == 30 and self.nod_cooldown == 0:
                # 記憶をリスト化して「動く時間」と「止まる時間」に切り分ける
                y_list = list(self.y_history)
                x_list = list(self.x_history)

                # past_y: 約0.5秒前〜0.3秒前 (スピード判定枠：15フレーム)
                past_y = y_list[5:20]    
                # recent_y, x: 直近0.3秒 (静止判定枠：10フレーム)
                recent_y = y_list[20:30] 
                recent_x = x_list[20:30]

                # 【条件1: 静止】直近0.3秒間、縦にも横にもピタッと止まっているか？
                is_still = (max(recent_y) - min(recent_y) < config.Gestures.NOD_STILLNESS_THRESHOLD and
                            max(recent_x) - min(recent_x) < config.Gestures.NOD_STILLNESS_THRESHOLD)

                # 【条件2: スピード】静止する直前に、素早いV字の動き（うなずき）があったか？
                start_y = past_y[0]
                lowest_y = max(past_y)
                end_y = past_y[-1]
                
                is_fast_nod = (lowest_y - start_y > config.Gestures.NOD_THRESHOLD and
                               lowest_y - end_y > config.Gestures.NOD_THRESHOLD)

                # 両方を満たした瞬間だけ保存する！
                if is_still and is_fast_nod:
                    is_nodding = True
                    self.nod_cooldown = config.Gestures.NOD_COOLDOWN
                    self.y_history.clear()
                    self.x_history.clear()

            # --- 2. 首振り反復カウントロジック ---
            if self.shake_cooldown == 0:
                if self.last_x is not None:
                    movement_x = nose_tip.x - self.last_x
                    
                    if abs(movement_x) > config.Gestures.SHAKE_MIN_MOVEMENT:
                        new_direction = 1 if movement_x > 0 else -1
                        
                        if self.current_direction != 0 and new_direction != self.current_direction:
                            self.switch_count += 1
                            self.shake_timer = config.Gestures.SHAKE_TIMEOUT 
                            
                            if self.switch_count >= config.Gestures.SHAKE_REQUIRED_SWITCHES:
                                is_shaking = True
                                self.shake_cooldown = config.Gestures.SHAKE_COOLDOWN
                                self.switch_count = 0
                                self.current_direction = 0
                        
                        if self.current_direction == 0 or new_direction != self.current_direction:
                            self.current_direction = new_direction
                
                self.last_x = nose_tip.x
            else:
                self.last_x = None

            # --- 3. ウィンク検知ロジック ---
            if self.wink_cooldown == 0:
                left_eye_openness = abs(landmarks[159].y - landmarks[145].y)
                right_eye_openness = abs(landmarks[386].y - landmarks[374].y)
                ratio_threshold = 2.0
                
                if right_eye_openness < config.Gestures.WINK_THRESHOLD and left_eye_openness > right_eye_openness * ratio_threshold:
                    wink_direction = 'right'
                    self.wink_cooldown = config.Gestures.WINK_COOLDOWN
                elif left_eye_openness < config.Gestures.WINK_THRESHOLD and right_eye_openness > left_eye_openness * ratio_threshold:
                    wink_direction = 'left'
                    self.wink_cooldown = config.Gestures.WINK_COOLDOWN

            return (cx, cy), is_nodding, is_shaking, wink_direction
        
        # 顔を見失った場合はすべての履歴をリセット
        self.y_history.clear()
        self.x_history.clear()
        self.last_x = None
        self.switch_count = 0
        self.current_direction = 0
        return None, False, False, None