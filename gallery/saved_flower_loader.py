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
    pattern = os.path.join(SAVE_DIR, "*.png")
    files = glob.glob(pattern)
    files.sort(key=os.path.getmtime)
    return files
