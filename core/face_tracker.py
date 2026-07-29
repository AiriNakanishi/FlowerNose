from collections import deque

import mediapipe as mp

import config


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
        if self.nod_cooldown > 0:
            self.nod_cooldown -= 1
        if self.wink_cooldown > 0:
            self.wink_cooldown -= 1
        if self.shake_cooldown > 0:
            self.shake_cooldown -= 1

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
            num_faces=1,
        )
        self.landmarker = FaceLandmarker.create_from_options(options)
        self.state = PlayerState()

    def get_nose_position(self, image_rgb, width, height):
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=image_rgb)
        detection_result = self.landmarker.detect(mp_image)

        self.state.update_cooldowns()
        output = {"pos": None, "nodding": False, "shaking": False, "wink": None}

        if not detection_result.face_landmarks:
            self.state.reset()
            return output

        landmarks = detection_result.face_landmarks[0]
        st = self.state

        nose_tip = landmarks[4]
        cx = int(nose_tip.x * width)
        cy = int(nose_tip.y * height)
        output["pos"] = (cx, cy)

        st.y_history.append(nose_tip.y)
        st.x_history.append(nose_tip.x)

        if len(st.y_history) == 30 and st.nod_cooldown == 0:
            y_list = list(st.y_history)
            x_list = list(st.x_history)
            past_y = y_list[5:20]
            recent_y = y_list[20:30]
            recent_x = x_list[20:30]

            is_still = (
                max(recent_y) - min(recent_y) < config.Gestures.NOD_STILLNESS_THRESHOLD
                and max(recent_x) - min(recent_x) < config.Gestures.NOD_STILLNESS_THRESHOLD
            )

            start_y = past_y[0]
            lowest_y = max(past_y)
            end_y = past_y[-1]
            is_fast_nod = (
                lowest_y - start_y > config.Gestures.NOD_THRESHOLD
                and lowest_y - end_y > config.Gestures.NOD_THRESHOLD
            )

            if is_still and is_fast_nod:
                output["nodding"] = True
                st.nod_cooldown = config.Gestures.NOD_COOLDOWN
                st.y_history.clear()
                st.x_history.clear()

        if st.shake_cooldown == 0:
            if st.last_x is not None:
                movement_x = nose_tip.x - st.last_x
                if abs(movement_x) > config.Gestures.SHAKE_MIN_MOVEMENT:
                    new_direction = 1 if movement_x > 0 else -1
                    if st.current_direction != 0 and new_direction != st.current_direction:
                        st.switch_count += 1
                        st.shake_timer = config.Gestures.SHAKE_TIMEOUT
                        if st.switch_count >= config.Gestures.SHAKE_REQUIRED_SWITCHES:
                            output["shaking"] = True
                            st.shake_cooldown = config.Gestures.SHAKE_COOLDOWN
                            st.switch_count = 0
                            st.current_direction = 0
                    if st.current_direction == 0 or new_direction != st.current_direction:
                        st.current_direction = new_direction
            st.last_x = nose_tip.x
        else:
            st.last_x = None

        if st.wink_cooldown == 0:
            left_eye_openness = abs(landmarks[159].y - landmarks[145].y)
            right_eye_openness = abs(landmarks[386].y - landmarks[374].y)
            ratio_threshold = 2.0

            if (
                right_eye_openness < config.Gestures.WINK_THRESHOLD
                and left_eye_openness > right_eye_openness * ratio_threshold
            ):
                output["wink"] = "right"
                st.wink_cooldown = config.Gestures.WINK_COOLDOWN
            elif (
                left_eye_openness < config.Gestures.WINK_THRESHOLD
                and right_eye_openness > left_eye_openness * ratio_threshold
            ):
                output["wink"] = "left"
                st.wink_cooldown = config.Gestures.WINK_COOLDOWN

        return output
