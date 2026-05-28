# main.py
import cv2
import pygame
import sys
import config
from core.face_tracker import FaceTracker
from core.canvas_manager import CanvasManager

def initialize_camera():
    """
    利用可能なカメラを自動で探索して起動する。
    iPhoneの連携カメラ(Mac)や仮想カメラ(Windows)など、外部カメラを優先的に探す。
    """
    print("カメラを探索しています...")
    # 探すカメラ番号の順番。
    # 一般的に 1 や 2 が外部カメラ（iPhone）、0 が内蔵カメラ。外部カメラを優先する。
    camera_indices = [1, 2, 0] 
    
    for index in camera_indices:
        cap = cv2.VideoCapture(index)
        if cap.isOpened():
            # カメラが開けた場合、試しに1フレーム読み込んでみる
            ret, _ = cap.read()
            if ret:
                print(f"✅ カメラ(番号: {index})の接続に成功しました！")
                return cap
            else:
                cap.release()
                
    # どの番号でもカメラが見つからなかった場合
    print("❌ 利用可能なカメラが見つかりません。")
    print("PCにカメラが接続されているか、またはiPhoneの連携アプリが起動しているか確認してください。")
    sys.exit()

def main():
    # 1. 初期化
    pygame.init()
    
    # 修正: カメラの初期化を、新しく作った自動探索関数に任せる
    cap = initialize_camera()
    
    ret, frame = cap.read()
    h, w, _ = frame.shape
    
    screen = pygame.display.set_mode((w, h))
    pygame.display.set_caption('Flower Nose - AR Experience')
    clock = pygame.time.Clock()

    # モジュール（部品）の準備
    tracker = FaceTracker()
    canvas = CanvasManager(w, h)
    
    prev_nose_pos = None

    # 2. メインループ
    while cap.isOpened():
        success, image = cap.read()
        if not success:
            print("カメラからの映像が途絶えました。")
            break

        # --- イベント処理 ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                cap.release()
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    canvas.save_image() # Enterで保存

        # --- 画像の準備 ---
        image = cv2.flip(image, 1)
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        frame_surface = pygame.surfarray.make_surface(image_rgb.swapaxes(0, 1))

        # --- 顔認識と描画の連携 ---
        current_nose_pos = tracker.get_nose_position(image_rgb, w, h)

        if current_nose_pos:
            # 鼻が動いていれば線を引く
            if prev_nose_pos is not None:
                canvas.draw_line(prev_nose_pos, current_nose_pos)
            prev_nose_pos = current_nose_pos
        else:
            prev_nose_pos = None

        # --- 画面の合成 ---
        screen.blit(frame_surface, (0, 0)) # カメラ映像
        if prev_nose_pos:
            pygame.draw.circle(screen, config.Colors.GUIDE_RED, prev_nose_pos, 10) # ガイド
        screen.blit(canvas.get_surface(), (0, 0)) # 線画シート

        pygame.display.flip()
        clock.tick(config.Sizes.FPS)

if __name__ == "__main__":
    main()