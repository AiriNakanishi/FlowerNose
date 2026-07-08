# main.py
import cv2
import pygame
import sys
import config
from core.face_tracker import FaceTracker
from core.canvas_manager import CanvasManager

def initialize_camera():
    print("カメラを探索しています...")
    camera_indices = [1, 0, 2] 
    
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
    pygame.display.set_caption('Flower Nose - AR Experience (Dual Player)')
    clock = pygame.time.Clock()

    tracker = FaceTracker()
    canvas = CanvasManager(w, h)
    
    prev_nose_pos = {'left': None, 'right': None}
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
                if event.key == pygame.K_f:
                    is_fullscreen = not is_fullscreen
                    if is_fullscreen:
                        screen = pygame.display.set_mode((w, h), pygame.FULLSCREEN)
                    else:
                        screen = pygame.display.set_mode((w, h))
                
                # デバッグ用：キーボードでの強制Undoは両画面同時に適用
                elif event.key == pygame.K_BACKSPACE or event.key == pygame.K_DELETE:
                    canvas.undo('left')
                    canvas.undo('right')

        image = cv2.flip(image, 1)
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        frame_surface = pygame.surfarray.make_surface(image_rgb.swapaxes(0, 1))

        # ★ 2人分のデータが辞書形式で返ってくる
        player_data = tracker.get_nose_position(image_rgb, w, h)

        # ★ 左右それぞれのプレイヤーに対して処理を行う
        for side in ['left', 'right']:
            data = player_data[side]
            
            if data['nodding']:
                print(f"👀 {side}側のうなずきを検知！絵を保存します。")
                canvas.save_image(side)
                
            if data['shaking']:
                canvas.undo(side)

            if data['wink']:
                canvas.change_color(side, data['wink'])

            if data['pos']:
                canvas.add_point(side, data['pos'])
                prev_nose_pos[side] = data['pos']
            else:
                canvas.end_stroke(side)
                prev_nose_pos[side] = None

        # --- 描画処理 ---
        screen.blit(frame_surface, (0, 0))
        
        # 中央の境界線を描画
        pygame.draw.line(
            screen, 
            config.Colors.CENTER_LINE, 
            (w // 2, 0), 
            (w // 2, h), 
            config.Sizes.CENTER_LINE_WIDTH
        )

        # ガイド（赤い点）の描画
        for side in ['left', 'right']:
            if prev_nose_pos[side]:
                pygame.draw.circle(screen, config.Colors.GUIDE_RED, prev_nose_pos[side], 10)
            
        screen.blit(canvas.get_surface(), (0, 0))
        canvas.draw_palette(screen)

        pygame.display.flip()
        clock.tick(config.Sizes.FPS)

if __name__ == "__main__":
    main()