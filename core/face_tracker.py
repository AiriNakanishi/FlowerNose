# face_tracker.py
import mediapipe as mp
import cv2
import config

class FaceTracker:
    def __init__(self):
        # MediaPipeの初期化
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

    def get_nose_position(self, image_rgb, width, height):
        """画像から鼻の頭の座標(cx, cy)を取得して返す。見つからない場合はNoneを返す。"""
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=image_rgb)
        detection_result = self.landmarker.detect(mp_image)

        if detection_result.face_landmarks:
            nose_tip = detection_result.face_landmarks[0][4]
            cx = int(nose_tip.x * width)
            cy = int(nose_tip.y * height)
            return (cx, cy)
        return None