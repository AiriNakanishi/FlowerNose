import cv2
import pygame
import sys

import config
from core.canvas_manager import CanvasManager
from core.face_tracker import FaceTracker


def initialize_camera():
    index = config.System.CAMERA_INDEX
    print(f"Opening iVCam camera: index {index}")

    cap = cv2.VideoCapture(index, cv2.CAP_DSHOW)
    if cap.isOpened():
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, config.Sizes.WINDOW_WIDTH)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.Sizes.WINDOW_HEIGHT)
        ret, _ = cap.read()
        if ret:
            print(f"iVCam camera connected: {index}")
            return cap
        cap.release()

    print("iVCam camera was not available. Start the iVCam app on the phone and PC, then run again.")
    sys.exit()


def main():
    pygame.init()
    cap = initialize_camera()

    ret, frame = cap.read()
    if not ret:
        print("Failed to read from camera.")
        cap.release()
        pygame.quit()
        sys.exit()

    h, w, _ = frame.shape

    screen = pygame.display.set_mode((w, h))
    pygame.display.set_caption("Flower Nose - AR Experience")
    clock = pygame.time.Clock()

    tracker = FaceTracker()
    canvas = CanvasManager(w, h)

    prev_nose_pos = None
    is_fullscreen = False

    while cap.isOpened():
        success, image = cap.read()
        if not success:
            break

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
                elif event.key in (pygame.K_w, pygame.K_RETURN, pygame.K_UP):
                    print("Saving drawing from keyboard...")
                    canvas.save_image()
                elif event.key in (pygame.K_z, pygame.K_BACKSPACE, pygame.K_DELETE, pygame.K_DOWN):
                    canvas.undo()
                elif event.key in (pygame.K_a, pygame.K_LEFT):
                    canvas.change_color("left")
                elif event.key in (pygame.K_d, pygame.K_RIGHT):
                    canvas.change_color("right")
                elif event.key == pygame.K_c:
                    print("キャンバスをクリアしました")
                    canvas.clear_canvas()

        image = cv2.flip(image, 1)
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        frame_surface = pygame.surfarray.make_surface(image_rgb.swapaxes(0, 1))

        player_data = tracker.get_nose_position(image_rgb, w, h)

        if player_data["nodding"]:
            print("Nod detected. Saving drawing...")
            canvas.save_image()

        if player_data["shaking"]:
            canvas.undo()

        if player_data["wink"]:
            canvas.change_color(player_data["wink"])

        if player_data["pos"]:
            canvas.add_point(player_data["pos"])
            prev_nose_pos = player_data["pos"]
        else:
            canvas.end_stroke()
            prev_nose_pos = None

        screen.blit(frame_surface, (0, 0))

        if prev_nose_pos:
            pygame.draw.circle(screen, config.Colors.GUIDE_RED, prev_nose_pos, 10)

        screen.blit(canvas.get_surface(), (0, 0))
        canvas.draw_palette(screen)

        pygame.display.flip()
        clock.tick(config.Sizes.FPS)

    cap.release()
    pygame.quit()


if __name__ == "__main__":
    main()
