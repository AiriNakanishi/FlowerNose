"""
花畑ディスプレイ（大画面投影用）

フォルダ構成:
  settings.py            … 設定値（花の本数・画面サイズなど）
  animation_helpers.py   … イージング・色補間の数学関数
  saved_flower_loader.py … 来場者が保存した花 PNG の読み込み
  display_loop.py        … Pygame メインループ（起動の入口）
  hot_reload.py          … 開発用: .py 保存で画面を自動更新
  scenery/               … 背景（空・丘・草地・雲）
  visitor_flowers/       … 来場者の花（配置・咲きアニメーション）
"""

from gallery.display_loop import main

__all__ = ["main"]
