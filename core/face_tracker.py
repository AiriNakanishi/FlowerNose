# core/face_tracker.py
import mediapipe as mp
import cv2
import config
from collections import deque

# ★ プレイヤーごとの記憶（状態）を独立して管理するためのクラス
class PlayerState:
    def __init__(self):
        self.y_history = deque(maxlen=30)
        self.x_history = deque(maxlen=30)
        self.nod_cooldown = 0
        self.wink_cooldown = 0
        
        self.last_x = None
        self.current_direction = 0
        self.switch_count = 0
        self.shake_timer = 0
        self.shake_cooldown = 0

    def update_cooldowns(self):
        if self.nod_cooldown > 0: self.nod_cooldown -= 1
        if self.wink_cooldown > 0: self.wink_cooldown -= 1
        if self.shake_cooldown > 0: self.shake_cooldown -= 1
        
        if self.shake_timer > 0:
            self.shake_timer -= 1
            if self.shake_timer == 0:
                self.switch_count = 0
                self.current_direction = 0

    def reset(self):
        self.y_history.clear()
        self.x_history.clear()
        self.last_x = None
        self.switch_count = 0
        self.current_direction = 0


class FaceTracker:
    def __init__(self):
        BaseOptions = mp.tasks.BaseOptions
        FaceLandmarker = mp.tasks.vision.FaceLandmarker
        FaceLandmarkerOptions = mp.tasks.vision.FaceLandmarkerOptions
        VisionRunningMode = mp.tasks.vision.RunningMode

        options = FaceLandmarkerOptions(
            base_options=BaseOptions(model_asset_path=config.System.MODEL_PATH),
            running_mode=VisionRunningMode.IMAGE,
            # ★ 検出上限を「2人」に変更
            num_faces=2
        )
        self.landmarker = FaceLandmarker.create_from_options(options)
        
        # ★ 左右のプレイヤーの状態をディクショナリで保持
        self.states = {
            'left': PlayerState(),
            'right': PlayerState()
        }

    def get_nose_position(self, image_rgb, width, height):
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=image_rgb)
        detection_result = self.landmarker.detect(mp_image)

        # 全プレイヤーのタイマーを毎フレーム進める
        for state in self.states.values():
            state.update_cooldowns()

        # 最終的にmain.pyへ返す2人分のデータ構造
        output = {
            'left': {'pos': None, 'nodding': False, 'shaking': False, 'wink': None},
            'right': {'pos': None, 'nodding': False, 'shaking': False, 'wink': None}
        }

        if detection_result.face_landmarks:
            faces = detection_result.face_landmarks
            
            # --- 左右の仕分けロジック ---
            targeted_faces = [] # (プレイヤーキー, ランドマーク) のリスト
            
            if len(faces) == 1:
                # 1人しかいない場合は、画面の左右どちらにいるかで判定
                landmarks = faces[0]
                side = 'left' if landmarks[4].x < 0.5 else 'right'
                targeted_faces.append((side, landmarks))
                # 反対側のプレイヤーは画面外（ロスト状態）なのでリセット
                other_side = 'right' if side == 'left' else 'left'
                self.states[other_side].reset()
                
            elif len(faces) >= 2:
                # 2人以上いる場合は、X座標を比較して左にある方を 'left'、右にある方を 'right' に確定
                sorted_faces = sorted(faces, key=lambda lm: lm[4].x)
                targeted_faces.append(('left', sorted_faces[0]))
                targeted_faces.append(('right', sorted_faces[1]))

            # --- 仕分けされた各プレイヤーのジェスチャー判定 ---
            for side, landmarks in targeted_faces:
                st = self.states[side]
                
                nose_tip = landmarks[4]
                cx = int(nose_tip.x * width)
                cy = int(nose_tip.y * height)
                output[side]['pos'] = (cx, cy)

                # 1. うなずき検知
                st.y_history.append(nose_tip.y)
                st.x_history.append(nose_tip.x)

                if len(st.y_history) == 30 and st.nod_cooldown == 0:
                    y_list = list(st.y_history)
                    x_list = list(st.x_history)
                    past_y = y_list[5:20]    
                    recent_y = y_list[20:30] 
                    recent_x = x_list[20:30]

                    is_still = (max(recent_y) - min(recent_y) < config.Gestures.NOD_STILLNESS_THRESHOLD and
                                max(recent_x) - min(recent_x) < config.Gestures.NOD_STILLNESS_THRESHOLD)

                    start_y = past_y[0]
                    lowest_y = max(past_y)
                    end_y = past_y[-1]
                    is_fast_nod = (lowest_y - start_y > config.Gestures.NOD_THRESHOLD and
                                   lowest_y - end_y > config.Gestures.NOD_THRESHOLD)

                    if is_still and is_fast_nod:
                        output[side]['nodding'] = True
                        st.nod_cooldown = config.Gestures.NOD_COOLDOWN
                        st.y_history.clear()
                        st.x_history.clear()

                # 2. 首振り検知
                if st.shake_cooldown == 0:
                    if st.last_x is not None:
                        movement_x = nose_tip.x - st.last_x
                        if abs(movement_x) > config.Gestures.SHAKE_MIN_MOVEMENT:
                            new_direction = 1 if movement_x > 0 else -1
                            if st.current_direction != 0 and new_direction != st.current_direction:
                                st.switch_count += 1
                                st.shake_timer = config.Gestures.SHAKE_TIMEOUT 
                                if st.switch_count >= config.Gestures.SHAKE_REQUIRED_SWITCHES:
                                    output[side]['shaking'] = True
                                    st.shake_cooldown = config.Gestures.SHAKE_COOLDOWN
                                    st.switch_count = 0
                                    st.current_direction = 0
                            if st.current_direction == 0 or new_direction != st.current_direction:
                                st.current_direction = new_direction
                    st.last_x = nose_tip.x
                else:
                    st.last_x = None

                # 3. ウィンク検知
                if st.wink_cooldown == 0:
                    left_eye_openness = abs(landmarks[159].y - landmarks[145].y)
                    right_eye_openness = abs(landmarks[386].y - landmarks[374].y)
                    ratio_threshold = 2.0
                    
                    if right_eye_openness < config.Gestures.WINK_THRESHOLD and left_eye_openness > right_eye_openness * ratio_threshold:
                        output[side]['wink'] = 'right'
                        st.wink_cooldown = config.Gestures.WINK_COOLDOWN
                    elif left_eye_openness < config.Gestures.WINK_THRESHOLD and right_eye_openness > left_eye_openness * ratio_threshold:
                        output[side]['wink'] = 'left'
                        st.wink_cooldown = config.Gestures.WINK_COOLDOWN

            return output
        
        # 誰も見つからない場合は全員の状態をクリア
        for side in self.states:
            self.states[side].reset()
        return output