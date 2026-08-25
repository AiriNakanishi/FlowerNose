import cv2
import pygame
import sys
import time

import config
from core.canvas_manager import CanvasManager
from core.drawing_guard import FaceExitDrawingGuard
from core.face_tracker import FaceTracker


INSTRUCTION_LINES = [
    ("鼻でお花を描こう", True),
    ("", False),
    ("顔を手で3秒隠す：保存", False),
    ("首を横に振る：ひとつ戻す", False),
    ("ウィンク：色を変える", False),
]


class FaceHideSaveTimer:
    def __init__(self, duration):
        self.duration = duration
        self.hidden_since = None
        self.save_latched = False

    def update(self, face_detected, has_drawing, now):
        if face_detected:
            was_counting = self.hidden_since is not None
            self.hidden_since = None
            self.save_latched = False
            return "canceled" if was_counting else None

        if self.save_latched or not has_drawing:
            self.hidden_since = None
            return None

        if self.hidden_since is None:
            self.hidden_since = now
            return "started"

        if now - self.hidden_since >= self.duration:
            self.hidden_since = None
            self.save_latched = True
            return "save"

        return None


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


def open_main_display(size, flags=0):
    display_count = pygame.display.get_num_displays()
    display_index = config.System.MAIN_DISPLAY_INDEX
    if display_index >= display_count:
        print(f"Display {display_index + 1} was not found. Using display 1 instead.")
        display_index = 0
    return pygame.display.set_mode(size, flags, display=display_index)


def get_japanese_font(size, bold=False):
    for name in ("yugothic", "meiryo", "msgothic", "notosanscjk"):
        path = pygame.font.match_font(name, bold=bold)
        if path:
            return pygame.font.Font(path, size)
    return pygame.font.Font(None, size)


def build_instruction_panel(width, height):
    scale = min(width / 1280, height / 720)
    padding = int(22 * scale)
    gap = int(8 * scale)
    title_font = get_japanese_font(max(26, int(34 * scale)), bold=True)
    body_font = get_japanese_font(max(22, int(28 * scale)))

    rendered_lines = []
    for text, is_title in INSTRUCTION_LINES:
        font = title_font if is_title else body_font
        if text:
            rendered = font.render(text, True, (35, 35, 35))
        else:
            rendered = pygame.Surface((1, max(10, int(14 * scale))), pygame.SRCALPHA)
        rendered_lines.append(rendered)

    panel_width = max(line.get_width() for line in rendered_lines) + padding * 2
    panel_height = sum(line.get_height() for line in rendered_lines) + gap * (len(rendered_lines) - 1) + padding * 2
    panel = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
    panel.fill((255, 255, 255, 218))
    pygame.draw.rect(panel, (255, 150, 185, 230), panel.get_rect(), max(2, int(3 * scale)))

    y = padding
    for line in rendered_lines:
        panel.blit(line, (padding, y))
        y += line.get_height() + gap

    return panel


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

    screen = open_main_display((w, h))
    pygame.display.set_caption("Flower Nose - AR Experience")
    clock = pygame.time.Clock()

    tracker = FaceTracker()
    canvas = CanvasManager(w, h)
    exit_drawing_guard = FaceExitDrawingGuard(
        w,
        h,
        config.Gestures.FACE_EXIT_HISTORY_SECONDS,
        config.Gestures.FACE_EXIT_MIN_DISTANCE,
    )
    instruction_panel = build_instruction_panel(w, h)

    prev_nose_pos = None
    face_lost_since = None
    pending_exit_rollback = None
    is_fullscreen = False
    face_hide_timer = FaceHideSaveTimer(config.Gestures.FACE_HIDE_SAVE_SECONDS)

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
                    flags = pygame.FULLSCREEN if is_fullscreen else 0
                    screen = open_main_display((w, h), flags)
                elif event.key in (pygame.K_w, pygame.K_RETURN, pygame.K_UP):
                    print("Saving drawing from keyboard...")
                    canvas.save_image()
                    exit_drawing_guard.clear()
                elif event.key in (pygame.K_z, pygame.K_BACKSPACE, pygame.K_DELETE, pygame.K_DOWN):
                    canvas.undo()
                    exit_drawing_guard.clear()
                elif event.key in (pygame.K_a, pygame.K_LEFT):
                    canvas.change_color("left")
                elif event.key in (pygame.K_d, pygame.K_RIGHT):
                    canvas.change_color("right")
                elif event.key in (pygame.K_c, pygame.K_ESCAPE):
                    print("キャンバスをクリアしました")
                    canvas.clear_canvas()
                    exit_drawing_guard.clear()

        image = cv2.flip(image, 1)
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        frame_surface = pygame.surfarray.make_surface(image_rgb.swapaxes(0, 1))

        player_data = tracker.get_nose_position(image_rgb, w, h)
        now = time.monotonic()

        hide_action = face_hide_timer.update(
            player_data["face_detected"],
            canvas.has_drawing(),
            now,
        )
        if hide_action == "started":
            print("Face hidden. Keep it covered for 3 seconds to save...")
        elif hide_action == "canceled":
            print("Face detected again. Save canceled.")
        elif hide_action == "save":
            print("Face hidden for 3 seconds. Saving drawing...")
            canvas.save_image()
            exit_drawing_guard.clear()

        if player_data["shaking"]:
            canvas.undo()
            exit_drawing_guard.clear()

        if player_data["wink"]:
            canvas.change_color(player_data["wink"])

        if player_data["pos"]:
            face_lost_since = None
            pending_exit_rollback = None
            exit_drawing_guard.record(
                now,
                player_data["pos"],
                canvas.point_count(),
            )
            canvas.add_point(player_data["pos"])
            prev_nose_pos = player_data["pos"]
        else:
            if prev_nose_pos is not None:
                face_lost_since = now
                pending_exit_rollback = exit_drawing_guard.rollback_point_count()
            if (
                pending_exit_rollback is not None
                and face_lost_since is not None
                and now - face_lost_since
                >= config.Gestures.FACE_EXIT_CONFIRM_SECONDS
            ):
                if canvas.truncate_to_point_count(pending_exit_rollback):
                    print("Removed the drawing trail made while leaving the screen.")
                pending_exit_rollback = None
            exit_drawing_guard.clear()
            canvas.end_stroke()
            prev_nose_pos = None

        screen.blit(frame_surface, (0, 0))

        if prev_nose_pos:
            pygame.draw.circle(screen, config.Colors.GUIDE_RED, prev_nose_pos, 10)

        canvas.draw(screen)
        canvas.draw_palette(screen)
        screen.blit(instruction_panel, (24, 24))

        pygame.display.flip()
        clock.tick(config.Sizes.FPS)

    cap.release()
    pygame.quit()


if __name__ == "__main__":
    main()
