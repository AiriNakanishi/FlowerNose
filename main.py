import cv2
import mediapipe as mp
import pygame
import sys
import os
from datetime import datetime

# ============================================
# 1. 保存先フォルダの準備 (新規追加)
# ============================================
SAVE_DIR = "FlowerNose_Gallery"
if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)
    print(f"保存先フォルダ '{SAVE_DIR}' を作成しました。")

# ============================================
# 2. MediaPipeの準備
# ============================================
BaseOptions = mp.tasks.BaseOptions
FaceLandmarker = mp.tasks.vision.FaceLandmarker
FaceLandmarkerOptions = mp.tasks.vision.FaceLandmarkerOptions
VisionRunningMode = mp.tasks.vision.RunningMode

options = FaceLandmarkerOptions(
    base_options=BaseOptions(model_asset_path='face_landmarker.task'),
    running_mode=VisionRunningMode.IMAGE,
    num_faces=1)

# ============================================
# 3. カメラとPygameの初期化
# ============================================
pygame.init()

cap = cv2.VideoCapture(0)
ret, frame = cap.read()
if not ret:
    print("カメラが見つかりません。")
    sys.exit()

h, w, _ = frame.shape
CANVAS_WIDTH = w
CANVAS_HEIGHT = h

screen = pygame.display.set_mode((CANVAS_WIDTH, CANVAS_HEIGHT))
pygame.display.set_caption('Flower Nose - AR Experience')

# 線を描き続けるための「透明なシート」
drawing_surface = pygame.Surface((CANVAS_WIDTH, CANVAS_HEIGHT), pygame.SRCALPHA)
drawing_surface.fill((0, 0, 0, 0))

PEN_COLOR = (255, 100, 150)
PEN_THICKNESS = 8
prev_nose_pos = None

clock = pygame.time.Clock()

# ============================================
# 4. メインループ
# ============================================
with FaceLandmarker.create_from_options(options) as landmarker:
    while cap.isOpened():
        success, image = cap.read()
        if not success:
            break

        # --- イベント処理（キーボード入力など） ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                cap.release()
                pygame.quit()
                sys.exit()
                
            # キーボードのキーが押された時の処理 (新規追加)
            if event.type == pygame.KEYDOWN:
                # Enterキー（Returnキー）が押されたら保存する
                if event.key == pygame.K_RETURN:
                    # 今の時刻をファイル名にする（例: 20260528_102030.png）
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"flower_{timestamp}.png"
                    filepath = os.path.join(SAVE_DIR, filename)
                    
                    # 透明なシート（drawing_surface）だけを保存
                    pygame.image.save(drawing_surface, filepath)
                    print(f"🎉 絵を保存しました: {filepath}")
                    
                    # 保存後、キャンバスをリセット（透明に塗りつぶす）して次のお客さんへ
                    drawing_surface.fill((0, 0, 0, 0))

        image = cv2.flip(image, 1)
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        frame_surface = pygame.surfarray.make_surface(image_rgb.swapaxes(0, 1))

        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=image_rgb)
        detection_result = landmarker.detect(mp_image)

        if detection_result.face_landmarks:
            nose_tip = detection_result.face_landmarks[0][4]
            cx, cy = int(nose_tip.x * w), int(nose_tip.y * h)
            current_nose_pos = (cx, cy)

            if prev_nose_pos is not None:
                pygame.draw.line(drawing_surface, PEN_COLOR, prev_nose_pos, current_nose_pos, PEN_THICKNESS)
            
            prev_nose_pos = current_nose_pos
        else:
            prev_nose_pos = None

        # --- 画面の合成 ---
        screen.blit(frame_surface, (0, 0))
        
        if prev_nose_pos:
            pygame.draw.circle(screen, (255, 0, 0), prev_nose_pos, 10)

        screen.blit(drawing_surface, (0, 0))

        pygame.display.flip()
        clock.tick(30)

cap.release()
pygame.quit()
print("プログラムを終了しました。")