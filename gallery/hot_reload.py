"""
開発用ホットリロード

gallery/ 配下の .py を保存すると、実行中のアプリがモジュールを読み直し、
背景・花畑を作り直す。毎回 python gallery.py を再起動しなくてよい。
"""

from __future__ import annotations

import importlib
import os
import sys
from pathlib import Path

# 読み直し対象（依存の深い順 → 浅い順に reload する）
_RELOAD_MODULES = (
    "gallery.settings",
    "gallery.animation_helpers",
    "gallery.saved_flower_loader",
    "gallery.scenery.drifting_cloud",
    "gallery.scenery.meadow_background",
    "gallery.scenery.atmosphere",
    "gallery.scenery.walking_pig",
    "gallery.scenery",
    "gallery.visitor_flowers.blooming_flower",
    "gallery.visitor_flowers.flower_field",
    "gallery.visitor_flowers",
)

_GALLERY_ROOT = Path(__file__).resolve().parent


def _iter_python_files() -> list[Path]:
    files: list[Path] = []
    for path in _GALLERY_ROOT.rglob("*.py"):
        if "__pycache__" in path.parts:
            continue
        files.append(path)
    return files


def snapshot_mtimes() -> dict[str, float]:
    """監視対象ファイルの更新時刻スナップショット"""
    result: dict[str, float] = {}
    for path in _iter_python_files():
        try:
            result[str(path)] = os.path.getmtime(path)
        except OSError:
            continue
    return result


def has_changed(previous: dict[str, float]) -> bool:
    current = snapshot_mtimes()
    if set(current) != set(previous):
        return True
    return any(current[path] != previous[path] for path in current)


def reload_gallery_modules() -> None:
    """gallery 配下のモジュールを依存順に読み直す"""
    for name in _RELOAD_MODULES:
        module = sys.modules.get(name)
        if module is not None:
            importlib.reload(module)


def rebuild_flower_field(known_paths: list[str] | None = None):
    """
    モジュール再読込後に FlowerField を新規生成する。
    known_paths があればそのまま populate する。
    """
    reload_gallery_modules()
    from gallery.saved_flower_loader import list_flower_images
    from gallery.visitor_flowers import FlowerField

    field = FlowerField()
    paths = known_paths if known_paths is not None else list_flower_images()
    field.populate(paths)
    return field, paths
