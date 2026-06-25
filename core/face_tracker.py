# core/face_tracker.py
import mediapipe as mp
import cv2
import config

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
        
        # うなずき用
        self.y_history = []
        self.nod_cooldown = 0
        
        # ウィンク用
        self.wink_cooldown = 0
        
        # ★新規：首振りカウント用の状態管理
        self.last_x = None             # 1フレーム前のX座標
        self.current_direction = 0     # 現在の移動方向 (1: 右移動, -1: 左移動, 0: 静止)
        self.switch_count = 0          # 方向転換が起きた回数
        self.shake_timer = 0           # 首振りの制限時間タイマー
        self.shake_cooldown = 0        # 発動後クールダウン

    def get_nose_position(self, image_rgb, width, height):
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=image_rgb)
        detection_result = self.landmarker.detect(mp_image)

        is_nodding = False
        is_shaking = False
        wink_direction = None

        # 各種タイマーのカウントダウン
        if self.nod_cooldown > 0: self.nod_cooldown -= 1
        if self.wink_cooldown > 0: self.wink_cooldown -= 1
        if self.shake_cooldown > 0: self.shake_cooldown -= 1
        
        # 首振り制限時間タイマーの進捗
        if self.shake_timer > 0:
            self.shake_timer -= 1
            if self.shake_timer == 0:
                # 時間切れになったらカウントをリセット
                self.switch_count = 0
                self.current_direction = 0

        if detection_result.face_landmarks:
            landmarks = detection_result.face_landmarks[0]
            
            nose_tip = landmarks[4]
            cx = int(nose_tip.x * width)
            cy = int(nose_tip.y * height)

            # --- うなずき検知ロジック ---
            self.y_history.append(nose_tip.y)
            if len(self.y_history) > 20:
                self.y_history.pop(0)
            
            if len(self.y_history) == 20 and self.nod_cooldown == 0:
                oldest_y, lowest_y, newest_y = self.y_history[0], max(self.y_history), self.y_history[-1]
                if (lowest_y - oldest_y) > config.Gestures.NOD_THRESHOLD and (lowest_y - newest_y) > config.Gestures.NOD_THRESHOLD:
                    is_nodding = True
                    self.nod_cooldown = config.Gestures.NOD_COOLDOWN
                    self.y_history.clear()

            # --- ★改良：首振り反復カウントロジック ---
            if self.shake_cooldown == 0:
                if self.last_x is not None:
                    movement_x = nose_tip.x - self.last_x
                    
                    # 手ブレなどの微小な動き（ノイズ）を除外するため、一定以上の移動のみを対象にする
                    if abs(movement_x) > config.Gestures.SHAKE_MIN_MOVEMENT:
                        # 今回の移動方向を決定 (1 = 右方向、-1 = 左方向)
                        new_direction = 1 if movement_x > 0 else -1
                        
                        # 前回の移動方向が存在し、かつ方向が「反転」した場合
                        if self.current_direction != 0 and new_direction != self.current_direction:
                            self.switch_count += 1
                            self.shake_timer = config.Gestures.SHAKE_TIMEOUT # タイマーをリフレッシュ
                            
                            # 目標の反転回数（例: 4回＝2往復）に達したか判定
                            if self.switch_count >= config.Gestures.SHAKE_REQUIRED_SWITCHES:
                                is_shaking = True
                                self.shake_cooldown = config.Gestures.SHAKE_COOLDOWN
                                self.switch_count = 0
                                self.current_direction = 0
                        
                        # 方向を更新
                        if self.current_direction == 0 or new_direction != self.current_direction:
                            self.current_direction = new_direction
                
                self.last_x = nose_tip.x
            else:
                self.last_x = None

            # --- ウィンク検知ロジック ---
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
        
        # 顔を見失った場合は状態を初期化
        self.y_history.clear()
        self.last_x = None
        self.switch_count = 0
        self.current_direction = 0
        return None, False, False, None