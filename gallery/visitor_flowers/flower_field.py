"""
花畑全体の管理

保存済み PNG から花を選び、10〜30 本ランダム配置する。
新しい花が保存されたら追加で咲かせ、背景（scenery/）の上に描画する。

描画順（奥 → 手前）:
  背景 → 光の粒 → 花（根元に影）
"""

import random
import pygame

from gallery.scenery.atmosphere import AtmosphereParticles
from gallery.frame_decor import GardenFrame
from gallery.scenery.meadow_background import MeadowBackground
from gallery.settings import (
    ATMOSPHERE_PARTICLES,
    BLOOM_STAGGER_MAX,
    FLOWER_SCALE_MAX,
    FLOWER_SCALE_MIN,
    GROUND_Y_MAX,
    GROUND_Y_MIN,
    MAX_FLOWERS,
    WINDOW_HEIGHT,
    WINDOW_WIDTH,
)
from gallery.visitor_flowers.blooming_flower import BloomingFlower
from gallery.scenery.walking_pig import WalkingPig


class FlowerField:
    """花畑の配置・更新・描画を一手に担う"""

    def __init__(self):
        self.flowers: list[BloomingFlower] = []
        self.known_files: set[str] = set()
        self._cached_images: dict[str, pygame.Surface] = {}
        self.background = MeadowBackground(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.atmosphere = AtmosphereParticles(WINDOW_WIDTH, WINDOW_HEIGHT, ATMOSPHERE_PARTICLES)
        self.frame = GardenFrame(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.pig = WalkingPig()

    def _load_image(self, path: str) -> pygame.Surface | None:
        if path in self._cached_images:
            return self._cached_images[path]
        try:
            img = pygame.image.load(path).convert_alpha()
            bounds = img.get_bounding_rect(1)
            if bounds.width > 0 and bounds.height > 0:
                img = img.subsurface(bounds).copy()
            self._cached_images[path] = img
            return img
        except pygame.error:
            print(f"画像読み込みエラー: {path}")
            return None

    def _pick_image(self, paths: list[str]) -> pygame.Surface | None:
        if not paths:
            return None
        path = random.choice(paths)
        return self._load_image(path)

    def _make_flower(
        self,
        image: pygame.Surface,
        stagger: bool = True,
        immediate: bool = False,
    ) -> BloomingFlower:
        margin = int(WINDOW_WIDTH * 0.08)
        x = random.randint(margin, WINDOW_WIDTH - margin)
        ground_y = random.randint(GROUND_Y_MIN, GROUND_Y_MAX)

        # 手前（y が大きい）ほど花を大きく
        depth = (ground_y - GROUND_Y_MIN) / max(1, GROUND_Y_MAX - GROUND_Y_MIN)
        scale = FLOWER_SCALE_MIN + (FLOWER_SCALE_MAX - FLOWER_SCALE_MIN) * (0.35 + 0.65 * depth)

        delay = 0.0 if immediate else random.uniform(0, BLOOM_STAGGER_MAX)
        return BloomingFlower(
            image=image,
            x=x,
            ground_y=ground_y,
            scale=scale,
            delay=delay,
            flip_x=random.choice([True, False]),
        )

    def _trim_to_max(self) -> None:
        if len(self.flowers) <= MAX_FLOWERS:
            return
        self.flowers = self.flowers[-MAX_FLOWERS:]

    def populate(self, paths: list[str]) -> None:
        """起動時 or R キー: 10〜30 本をランダム配置して時間差で咲かせる"""
        if not paths:
            self.flowers.clear()
            return

        self.flowers = []
        for path in paths[-MAX_FLOWERS:]:
            img = self._load_image(path)
            if img:
                self.flowers.append(self._make_flower(img, stagger=True))

        # 奥から手前の順に描画
        self.known_files = set(paths)

    def add_new_flowers(self, paths: list[str]) -> None:
        """新しく保存された花だけを追加で咲かせる"""
        new_paths = [p for p in paths if p not in self.known_files]
        self.known_files = set(paths)

        for path in new_paths:
            img = self._load_image(path)
            if img is None:
                continue
            self.flowers.append(self._make_flower(img, stagger=False, immediate=False))
            self.flowers[-1].delay = random.uniform(0.2, 1.0)

        self._trim_to_max()

    def update(self, dt: float) -> None:
        for flower in self.flowers:
            flower.update(dt)
        self.atmosphere.update(dt)
        self.pig.update(dt)

    def draw_background(self, screen: pygame.Surface, time_sec: float) -> None:
        self.background.draw(screen, time_sec)
        self.atmosphere.draw(screen, time_sec)

    def draw(self, screen: pygame.Surface, time_sec: float) -> None:
        render_objects = []
            
        # 花をリストに追加 (Y座標, オブジェクト種別, オブジェクト本体)
        for flower in self.flowers:
            render_objects.append((flower.ground_y, 'flower', flower))
            
        # 豚をリストに追加
        render_objects.append((self.pig.ground_y, 'pig', self.pig))
        
        # 奥（Y座標が小さい）から手前（Y座標が大きい）の順に並び替え
        render_objects.sort(key=lambda item: item[0])
        
        # 順番に描画
        for ground_y, obj_type, obj in render_objects:
            obj.draw(screen, time_sec)
        self.frame.draw(screen, time_sec)
