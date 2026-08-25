import math

import mediapipe as mp

import config


class PlayerState:
    def __init__(self):
        self.wink_cooldown = 0
        self.wink_candidate = None
        self.wink_hold_frames = 0
        self.wink_latched = False
        self.left_eye_open_baseline = None
        self.right_eye_open_baseline = None

        self.last_x = None
        self.current_direction = 0
        self.switch_count = 0
        self.shake_timer = 0
        self.shake_cooldown = 0

    def update_cooldowns(self):
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
        self.wink_candidate = None
        self.wink_hold_frames = 0
        self.last_x = None
        self.switch_count = 0
        self.current_direction = 0

    @staticmethod
    def _update_open_baseline(baseline, openness):
        if openness is None:
            return baseline
        if baseline is None or openness > baseline:
            return openness
        if openness >= baseline * 0.75:
            return baseline * 0.995 + openness * 0.005
        return baseline

    @staticmethod
    def _merge_wink_candidates(blendshape_candidate, geometry_candidate):
        if blendshape_candidate and geometry_candidate:
            return blendshape_candidate if blendshape_candidate == geometry_candidate else None
        return blendshape_candidate or geometry_candidate

    def update_wink(
        self,
        left_blink_score,
        right_blink_score,
        left_eye_openness,
        right_eye_openness,
    ):
        self.left_eye_open_baseline = self._update_open_baseline(
            self.left_eye_open_baseline,
            left_eye_openness,
        )
        self.right_eye_open_baseline = self._update_open_baseline(
            self.right_eye_open_baseline,
            right_eye_openness,
        )

        left_open_ratio = None
        right_open_ratio = None
        if self.left_eye_open_baseline and left_eye_openness is not None:
            left_open_ratio = left_eye_openness / self.left_eye_open_baseline
        if self.right_eye_open_baseline and right_eye_openness is not None:
            right_open_ratio = right_eye_openness / self.right_eye_open_baseline

        if self.wink_latched:
            scores_released = (
                left_blink_score is not None
                and right_blink_score is not None
                and max(left_blink_score, right_blink_score)
                <= config.Gestures.WINK_RELEASE_SCORE
            )
            geometry_released = (
                left_open_ratio is not None
                and right_open_ratio is not None
                and min(left_open_ratio, right_open_ratio)
                >= config.Gestures.WINK_OTHER_EYE_MIN_RATIO
            )
            if scores_released or geometry_released:
                self.wink_latched = False
            return None

        blendshape_candidate = None
        if left_blink_score is not None and right_blink_score is not None and (
            left_blink_score >= config.Gestures.WINK_CLOSED_SCORE
            and right_blink_score <= config.Gestures.WINK_OTHER_EYE_MAX_SCORE
            and left_blink_score - right_blink_score >= config.Gestures.WINK_SCORE_DIFFERENCE
        ):
            # 入力映像を左右反転しているため、ユーザーから見た右目に対応する。
            blendshape_candidate = "right"
        elif left_blink_score is not None and right_blink_score is not None and (
            right_blink_score >= config.Gestures.WINK_CLOSED_SCORE
            and left_blink_score <= config.Gestures.WINK_OTHER_EYE_MAX_SCORE
            and right_blink_score - left_blink_score >= config.Gestures.WINK_SCORE_DIFFERENCE
        ):
            blendshape_candidate = "left"

        geometry_candidate = None
        if left_open_ratio is not None and right_open_ratio is not None:
            if (
                left_open_ratio <= config.Gestures.WINK_CLOSED_RATIO
                and right_open_ratio >= config.Gestures.WINK_OTHER_EYE_MIN_RATIO
                and right_open_ratio - left_open_ratio >= config.Gestures.WINK_RATIO_DIFFERENCE
            ):
                geometry_candidate = "right"
            elif (
                right_open_ratio <= config.Gestures.WINK_CLOSED_RATIO
                and left_open_ratio >= config.Gestures.WINK_OTHER_EYE_MIN_RATIO
                and left_open_ratio - right_open_ratio >= config.Gestures.WINK_RATIO_DIFFERENCE
            ):
                geometry_candidate = "left"

        candidate = self._merge_wink_candidates(
            blendshape_candidate,
            geometry_candidate,
        )

        if candidate is None:
            self.wink_candidate = None
            self.wink_hold_frames = 0
            return None

        if candidate == self.wink_candidate:
            self.wink_hold_frames += 1
        else:
            self.wink_candidate = candidate
            self.wink_hold_frames = 1

        if (
            self.wink_hold_frames >= config.Gestures.WINK_HOLD_FRAMES
            and self.wink_cooldown == 0
        ):
            self.wink_candidate = None
            self.wink_hold_frames = 0
            self.wink_latched = True
            self.wink_cooldown = config.Gestures.WINK_COOLDOWN
            return candidate

        return None


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
            output_face_blendshapes=True,
        )
        self.landmarker = FaceLandmarker.create_from_options(options)
        self.state = PlayerState()

    @staticmethod
    def _landmark_distance(first, second, width, height):
        return math.hypot(
            (first.x - second.x) * width,
            (first.y - second.y) * height,
        )

    @classmethod
    def get_eye_openness(cls, landmarks, width, height):
        left_width = cls._landmark_distance(landmarks[362], landmarks[263], width, height)
        right_width = cls._landmark_distance(landmarks[33], landmarks[133], width, height)
        if left_width < 1.0 or right_width < 1.0:
            return None, None

        left_height = (
            cls._landmark_distance(landmarks[386], landmarks[374], width, height)
            + cls._landmark_distance(landmarks[385], landmarks[380], width, height)
        ) * 0.5
        right_height = (
            cls._landmark_distance(landmarks[159], landmarks[145], width, height)
            + cls._landmark_distance(landmarks[158], landmarks[153], width, height)
        ) * 0.5
        return left_height / left_width, right_height / right_width

    def get_nose_position(self, image_rgb, width, height):
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=image_rgb)
        detection_result = self.landmarker.detect(mp_image)

        self.state.update_cooldowns()
        output = {
            "pos": None,
            "face_detected": False,
            "shaking": False,
            "wink": None,
        }

        if not detection_result.face_landmarks:
            self.state.reset()
            return output

        landmarks = detection_result.face_landmarks[0]
        st = self.state

        nose_tip = landmarks[4]
        cx = int(nose_tip.x * width)
        cy = int(nose_tip.y * height)
        output["pos"] = (cx, cy)
        output["face_detected"] = True

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

        blendshape_scores = {}
        if detection_result.face_blendshapes:
            blendshape_scores = {
                category.category_name: category.score
                for category in detection_result.face_blendshapes[0]
            }
        left_eye_openness, right_eye_openness = self.get_eye_openness(
            landmarks,
            width,
            height,
        )
        output["wink"] = st.update_wink(
            blendshape_scores.get("eyeBlinkLeft"),
            blendshape_scores.get("eyeBlinkRight"),
            left_eye_openness,
            right_eye_openness,
        )

        return output
