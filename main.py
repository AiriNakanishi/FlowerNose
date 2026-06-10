# main.py
import cv2
import pygame
import sys
import config
from core.face_tracker import FaceTracker
from core.canvas_manager import CanvasManager

def initialize_camera():
    print("カメラを探索しています...")
    # camera_indices = [1, 2, 0] 
    camera_indices = [0, 1, 2] 
    
    for index in camera_indices:
        cap = cv2.VideoCapture(index)
        if cap.isOpened():
            ret, _ = cap.read()
            if ret:
                print(f"✅ カメラ(番号: {index})の接続に成功しました！")
                return cap
            else:
                cap.release()
                
    print("❌ 利用可能なカメラが見つかりません。")
    sys.exit()

def main():
    pygame.init()
    cap = initialize_camera()
    
    ret, frame = cap.read()
    h, w, _ = frame.shape
    
    # 最初の画面設定（ウィンドウモード）
    screen = pygame.display.set_mode((w, h))
    pygame.display.set_caption('Flower Nose - AR Experience')
    clock = pygame.time.Clock()

    tracker = FaceTracker()
    canvas = CanvasManager(w, h)
    
    prev_nose_pos = None
    
    # ★フルスクリーン状態を管理する変数
    is_fullscreen = False

    while cap.isOpened():
        success, image = cap.read()
        if not success: break

        # --- イベント処理 ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                cap.release()
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    canvas.save_image()
                elif event.key == pygame.K_LEFT:
                    canvas.change_color('left')
                elif event.key == pygame.K_RIGHT:
                    canvas.change_color('right')
                
                # ★「F」キーが押されたらフルスクリーンを切り替える
                elif event.key == pygame.K_f:
                    is_fullscreen = not is_fullscreen
                    if is_fullscreen:
                        # フルスクリーンモードにする
                        screen = pygame.display.set_mode((w, h), pygame.FULLSCREEN)
                    else:
                        # 通常のウィンドウモードに戻す
                        screen = pygame.display.set_mode((w, h))

        image = cv2.flip(image, 1)
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        frame_surface = pygame.surfarray.make_surface(image_rgb.swapaxes(0, 1))

        # --- 顔認識と描画の連携 ---
        current_nose_pos, is_nodding, wink_direction = tracker.get_nose_position(image_rgb, w, h)

        if is_nodding:
            print("👀 うなずきジェスチャーを検知しました！")
            canvas.save_image()

        if wink_direction:
            canvas.change_color(wink_direction)

        if current_nose_pos:
            if prev_nose_pos is not None:
                canvas.draw_line(prev_nose_pos, current_nose_pos)
            prev_nose_pos = current_nose_pos
        else:
            prev_nose_pos = None

        # --- 画面の合成 ---
        screen.blit(frame_surface, (0, 0))
        if prev_nose_pos:
            pygame.draw.circle(screen, config.Colors.GUIDE_RED, prev_nose_pos, 10)
        screen.blit(canvas.get_surface(), (0, 0))
        
        # カラーパレットを画面に描画
        canvas.draw_palette(screen)

        pygame.display.flip()
        clock.tick(config.Sizes.FPS)

if __name__ == "__main__":
    main()