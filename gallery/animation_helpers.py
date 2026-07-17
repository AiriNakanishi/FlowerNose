"""
アニメーション用の数学関数

花の咲き方（ease_out_back）や背景の色グラデーション（lerp_color）で使う。
描画ロジックそのものは scenery/ や visitor_flowers/ にあります。
"""


def lerp_color(a: tuple[int, int, int], b: tuple[int, int, int], t: float) -> tuple[int, int, int]:
    """2 色の間を t (0〜1) で補間する"""
    return (
        int(a[0] + (b[0] - a[0]) * t),
        int(a[1] + (b[1] - a[1]) * t),
        int(a[2] + (b[2] - a[2]) * t),
    )


def ease_out_back(t: float) -> float:
    """イージング: 地面から勢いよく伸び、少しだけ戻る咲き方"""
    c1 = 1.70158
    c3 = c1 + 1
    return 1 + c3 * (t - 1) ** 3 + c1 * (t - 1) ** 2


def ease_out_cubic(t: float) -> float:
    """イージング: 最初は速く、終わりに向けてゆっくり減速"""
    return 1 - (1 - t) ** 3
