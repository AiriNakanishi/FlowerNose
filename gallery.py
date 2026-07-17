"""
花畑ディスプレイ（gallery.py）

大きなディスプレイ用。来場者が main.py で描いて保存した花 PNG を読み込み、
地面から咲くアニメーション付きで 10〜30 本ランダムに配置して表示する。

使い方:
    python gallery.py   （main.py と別ターミナルで同時起動）

実装の詳細は gallery/ フォルダ内。構成は gallery/__init__.py を参照。
"""

from gallery.display_loop import main

if __name__ == "__main__":
    main()
