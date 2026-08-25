"""
来場者が描いた花 PNG の読み込み

main.py → CanvasManager.save_image() が FlowerNose_Gallery/ に保存した
flower_*.png を列挙する。display_loop.py が定期的にここを呼び、
新しい花を花畑に追加します。
"""

import glob
import os

from gallery.settings import SAVE_DIR


def list_flower_images() -> list[str]:
    """FlowerNose_Gallery 内の PNG を更新日時順（古い順）で取得"""
    return list(snapshot_flower_images())


def snapshot_flower_images() -> dict[str, tuple[int, int]]:
    """PNGごとの更新時刻とサイズを、更新日時順で取得する。"""
    pattern = os.path.join(SAVE_DIR, "*.png")
    snapshots = []
    for path in glob.glob(pattern):
        try:
            stat = os.stat(path)
        except OSError:
            continue
        snapshots.append((path, (stat.st_mtime_ns, stat.st_size)))
    snapshots.sort(key=lambda item: (item[1][0], item[0]))
    return dict(snapshots)
