import math
import os
import random

import pygame

from gallery.settings import (
    GROUND_Y_MAX,
    GROUND_Y_MIN,
    PIG_ANIMATION_FPS,
    PIG_IMAGE_PATH,
    PIG_JUMP_CHANCE,
    PIG_JUMP_DURATION,
    PIG_JUMP_HEIGHT,
    PIG_SCALE_MAX,
    PIG_SCALE_MIN,
    PIG_SIT_CHANCE,
    PIG_SIT_DURATION_MAX,
    PIG_SIT_DURATION_MIN,
    PIG_SPEED_MAX,
    PIG_SPEED_MIN,
    PIG_SPONTANEOUS_ACTION_MAX,
    PIG_SPONTANEOUS_ACTION_MIN,
    PIG_WAIT_MAX,
    PIG_WAIT_MIN,
    WALKPIG_ASSET_DIR,
    WINDOW_WIDTH,
)


class WalkingPig:
    """A pig that wanders around the flower field with a simple walk cycle."""

    def __init__(self):
        self.width = WINDOW_WIDTH
        self.animation_sets = self._load_animation_sets()
        self.frames_original = random.choice(self.animation_sets)
        self.frame_time = 0.0
        self.direction = -1
        self.action = "walk"
        self.action_timer = 0.0
        self.action_duration = 0.0
        self.next_spontaneous_action = random.uniform(PIG_SPONTANEOUS_ACTION_MIN, PIG_SPONTANEOUS_ACTION_MAX)
        self._image_cache: dict[tuple[int, int, int, int, int], pygame.Surface] = {}
        self._shadow_cache: dict[tuple[int, int], pygame.Surface] = {}
        self.reset()

    def _load_animation_sets(self) -> list[list[pygame.Surface]]:
        animation_sets = []

        if os.path.isdir(WALKPIG_ASSET_DIR):
            variant_dirs = sorted(
                os.path.join(WALKPIG_ASSET_DIR, name)
                for name in os.listdir(WALKPIG_ASSET_DIR)
                if name.startswith("variant_")
            )
            for variant_dir in variant_dirs:
                frames = []
                for frame_name in sorted(os.listdir(variant_dir)):
                    if not frame_name.lower().endswith(".png"):
                        continue
                    path = os.path.join(variant_dir, frame_name)
                    try:
                        frames.append(pygame.image.load(path).convert_alpha())
                    except pygame.error:
                        print(f"Pig frame load error: {path}")
                if frames:
                    animation_sets.append(frames)

        if animation_sets:
            return animation_sets

        if os.path.exists(PIG_IMAGE_PATH):
            try:
                return [[pygame.image.load(PIG_IMAGE_PATH).convert_alpha()]]
            except pygame.error:
                print(f"Pig image load error: {PIG_IMAGE_PATH}")

        fallback = pygame.Surface((1, 1), pygame.SRCALPHA)
        return [[fallback]]

    def reset(self):
        self.frames_original = random.choice(self.animation_sets)
        self.x = random.uniform(self.width * 0.15, self.width * 0.85)
        self.ground_y = random.randint(GROUND_Y_MIN, GROUND_Y_MAX)
        self._choose_target()

    def _choose_target(self):
        self.target_x = random.uniform(self.width * 0.08, self.width * 0.92)
        self.target_y = random.randint(GROUND_Y_MIN, GROUND_Y_MAX)
        self.speed = random.uniform(PIG_SPEED_MIN, PIG_SPEED_MAX)

        if random.random() < 0.25:
            self.frames_original = random.choice(self.animation_sets)

    def _current_scale(self) -> float:
        depth = (self.ground_y - GROUND_Y_MIN) / max(1, GROUND_Y_MAX - GROUND_Y_MIN)
        return PIG_SCALE_MIN + (PIG_SCALE_MAX - PIG_SCALE_MIN) * depth

    def _begin_wait(self) -> None:
        self.action = "wait"
        self.action_timer = 0.0
        self.action_duration = random.uniform(PIG_WAIT_MIN, PIG_WAIT_MAX)

    def _begin_jump(self) -> None:
        self.action = "jump"
        self.action_timer = 0.0
        self.action_duration = PIG_JUMP_DURATION

    def _begin_sit(self) -> None:
        self.action = "sit"
        self.action_timer = 0.0
        self.action_duration = random.uniform(PIG_SIT_DURATION_MIN, PIG_SIT_DURATION_MAX)

    def _begin_pause_action(self) -> None:
        roll = random.random()
        if roll < PIG_SIT_CHANCE:
            self._begin_sit()
        elif roll < PIG_SIT_CHANCE + PIG_JUMP_CHANCE:
            self._begin_jump()
        else:
            self._begin_wait()

    def _finish_action(self) -> None:
        self.action = "walk"
        self.action_timer = 0.0
        self.action_duration = 0.0
        self.next_spontaneous_action = random.uniform(PIG_SPONTANEOUS_ACTION_MIN, PIG_SPONTANEOUS_ACTION_MAX)
        if self._distance_to_target() < 6.0:
            self._choose_target()

    def _distance_to_target(self) -> float:
        return math.hypot(self.target_x - self.x, self.target_y - self.ground_y)

    def _move_toward_target(self, dt: float) -> bool:
        dx = self.target_x - self.x
        dy = self.target_y - self.ground_y
        distance = math.hypot(dx, dy)

        if distance < 6.0:
            return True

        move = min(self.speed * dt, distance)
        self.x += dx / distance * move
        self.ground_y += dy / distance * move
        self.direction = 1 if dx > 0 else -1
        self.frame_time += dt
        return False

    def _get_scaled_frame(
        self,
        frame_index: int,
        direction: int,
        width: int,
        height: int,
    ) -> pygame.Surface:
        cache_key = (id(self.frames_original), frame_index, direction, width, height)
        image = self._image_cache.get(cache_key)
        if image is not None:
            return image

        frame = self.frames_original[frame_index]
        image = pygame.transform.smoothscale(frame, (width, height))
        if direction == 1:
            image = pygame.transform.flip(image, True, False)
        self._image_cache[cache_key] = image
        return image

    def _get_shadow(self, width: int) -> pygame.Surface:
        shadow_w = max(1, int(width * 0.55))
        shadow_h = max(1, int(shadow_w * 0.18))
        cache_key = (shadow_w, shadow_h)
        shadow = self._shadow_cache.get(cache_key)
        if shadow is not None:
            return shadow

        shadow = pygame.Surface((shadow_w, shadow_h), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow, (30, 60, 30, 35), shadow.get_rect())
        self._shadow_cache[cache_key] = shadow
        return shadow

    def update(self, dt: float) -> None:
        if self.action in ("wait", "sit"):
            self.action_timer += dt
            if self.action_timer >= self.action_duration:
                self._finish_action()
            return

        if self.action == "jump":
            self.action_timer += dt
            reached_target = self._move_toward_target(dt)
            if self.action_timer >= self.action_duration:
                if reached_target:
                    self._begin_pause_action()
                else:
                    self._finish_action()
            return

        self.next_spontaneous_action -= dt
        if self.next_spontaneous_action <= 0:
            self._begin_jump()
            return

        if self._move_toward_target(dt):
            self._begin_pause_action()

    def _action_progress(self) -> float:
        if self.action_duration <= 0:
            return 0.0
        return min(1.0, self.action_timer / self.action_duration)

    def _pose(self, scale: float) -> tuple[float, float, float, float]:
        if self.action == "jump":
            t = self._action_progress()
            air = math.sin(math.pi * t)
            squash = 0.0
            if t < 0.18:
                squash = math.sin((1.0 - t / 0.18) * math.pi / 2)
            elif t > 0.82:
                squash = math.sin(((t - 0.82) / 0.18) * math.pi / 2)
            stretch_y = 1.0 + 0.10 * air - 0.08 * squash
            stretch_x = 1.0 - 0.04 * air + 0.08 * squash
            jump_y = -PIG_JUMP_HEIGHT * scale * air
            return stretch_x, stretch_y, jump_y, air

        if self.action == "sit":
            t = self._action_progress()
            if t < 0.28:
                sit = 1.0 - math.cos((t / 0.28) * math.pi / 2)
            elif t > 0.78:
                sit = math.cos(((t - 0.78) / 0.22) * math.pi / 2)
            else:
                sit = 1.0
            return 1.09 + 0.05 * sit, 1.0 - 0.24 * sit, 0.0, 0.0

        return 1.0, 1.0, 0.0, 0.0

    def draw(self, screen: pygame.Surface, time_sec: float) -> None:
        if not self.frames_original:
            return

        if self.action in ("wait", "sit"):
            frame_index = 0
        else:
            frame_index = int(self.frame_time * PIG_ANIMATION_FPS) % len(self.frames_original)

        frame = self.frames_original[frame_index]
        scale = self._current_scale()
        stretch_x, stretch_y, action_y, air = self._pose(scale)
        width = max(1, int(round(frame.get_width() * scale * stretch_x / 4) * 4))
        height = max(1, int(round(frame.get_height() * scale * stretch_y / 4) * 4))
        image = self._get_scaled_frame(frame_index, self.direction, width, height)

        bob = 0.0 if self.action in ("wait", "sit") else abs(math.sin(time_sec * 8.0)) * 8.0 * scale
        draw_x = int(self.x)
        draw_y = int(self.ground_y - bob + action_y)

        shadow = self._get_shadow(int(width * (1.0 - air * 0.28)))
        shadow_w = shadow.get_width()
        shadow_h = shadow.get_height()
        screen.blit(shadow, (draw_x - shadow_w // 2, int(self.ground_y - shadow_h // 2)))

        rect = image.get_rect(midbottom=(draw_x, draw_y))
        screen.blit(image, rect)
