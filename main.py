# main.py
import cv2
import pygame
import sys
import config
from core.face_tracker import FaceTracker
from core.canvas_manager import CanvasManager

def initialize_camera():
    print("カメラを探索しています...")
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
    
    screen = pygame.display.set_mode((w, h))
    pygame.display.set_caption('Flower Nose - AR Experience')
    clock = pygame.time.Clock()

    tracker = FaceTracker()
    canvas = CanvasManager(w, h)
    
    prev_nose_pos = None
    is_fullscreen = False

    while cap.isOpened():
        success, image = cap.read()
        if not success: break

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
                elif event.key == pygame.K_f:
                    is_fullscreen = not is_fullscreen
                    if is_fullscreen:
                        screen = pygame.display.set_mode((w, h), pygame.FULLSCREEN)
                    else:
                        screen = pygame.display.set_mode((w, h))

        image = cv2.flip(image, 1)
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        frame_surface = pygame.surfarray.make_surface(image_rgb.swapaxes(0, 1))

        # --- 顔認識と描画の連携 ---
        # ★修正: 返り値に is_shaking が追加された
        current_nose_pos, is_nodding, is_shaking, wink_direction = tracker.get_nose_position(image_rgb, w, h)

        if is_nodding:
            print("👀 うなずきジェスチャーを検知しました！")
            canvas.save_image()
            
        # ★新規追加: 首振りを検知したらUndoを実行
        if is_shaking:
            canvas.undo()

        if wink_direction:
            canvas.change_color(wink_direction)

        if current_nose_pos:
            # 鼻が見つかっている間は、キャンバスに「点」を追加し続ける
            canvas.add_point(current_nose_pos)
            prev_nose_pos = current_nose_pos
        else:
            # ★新規追加: 顔を見失ったら、そこで「一筆」を終了（区切る）
            canvas.end_stroke()
            prev_nose_pos = None

        # --- 画面の合成 ---
        screen.blit(frame_surface, (0, 0))
        if prev_nose_pos:
            pygame.draw.circle(screen, config.Colors.GUIDE_RED, prev_nose_pos, 10)
            
        # get_surface() が呼ばれるタイミングで、記憶しているすべての線が一気に描画される
        screen.blit(canvas.get_surface(), (0, 0))
        
        canvas.draw_palette(screen)

        pygame.display.flip()
        clock.tick(config.Sizes.FPS)

if __name__ == "__main__":
    main()