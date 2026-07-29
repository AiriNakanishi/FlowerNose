import math
import os
import random

import pygame

from gallery.settings import (
    GROUND_Y_MAX,
    GROUND_Y_MIN,
    PIG_ANIMATION_FPS,
    PIG_IMAGE_PATH,
    PIG_SCALE_MAX,
    PIG_SCALE_MIN,
    PIG_SPEED_MAX,
    PIG_SPEED_MIN,
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
        self.wait_timer = 0.0
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
        if self.wait_timer > 0:
            self.wait_timer = max(0.0, self.wait_timer - dt)
            if self.wait_timer == 0:
                self._choose_target()
            return

        dx = self.target_x - self.x
        dy = self.target_y - self.ground_y
        distance = math.hypot(dx, dy)

        if distance < 6.0:
            self.wait_timer = random.uniform(PIG_WAIT_MIN, PIG_WAIT_MAX)
            return

        move = min(self.speed * dt, distance)
        self.x += dx / distance * move
        self.ground_y += dy / distance * move
        self.direction = 1 if dx > 0 else -1
        self.frame_time += dt

    def draw(self, screen: pygame.Surface, time_sec: float) -> None:
        if not self.frames_original:
            return

        if self.wait_timer > 0:
            frame_index = 0
        else:
            frame_index = int(self.frame_time * PIG_ANIMATION_FPS) % len(self.frames_original)

        frame = self.frames_original[frame_index]
        scale = self._current_scale()
        width = max(1, int(frame.get_width() * scale))
        height = max(1, int(frame.get_height() * scale))
        image = self._get_scaled_frame(frame_index, self.direction, width, height)

        bob = 0.0 if self.wait_timer > 0 else abs(math.sin(time_sec * 8.0)) * 8.0 * scale
        draw_x = int(self.x)
        draw_y = int(self.ground_y - bob)

        shadow = self._get_shadow(width)
        shadow_w = shadow.get_width()
        shadow_h = shadow.get_height()
        screen.blit(shadow, (draw_x - shadow_w // 2, int(self.ground_y - shadow_h // 2)))

        rect = image.get_rect(midbottom=(draw_x, draw_y))
        screen.blit(image, rect)
