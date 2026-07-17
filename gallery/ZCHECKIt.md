#### 新しい構成
gallery/
├── settings.py              … 設定値（花の本数・画面サイズ・咲く速さ）
├── animation_helpers.py     … イージング・色補間（数学関数）
├── saved_flower_loader.py   … 来場者が保存した花 PNG の読み込み
├── display_loop.py          … Pygame メインループ（キー操作・描画）
├── hot_reload.py            … 開発用: .py 保存で自動リロード
│
├── scenery/                 … 【背景】空・丘・草地・雲
│   ├── drifting_cloud.py        流れる雲
│   └── meadow_background.py     空・丘・草地・太陽
│
└── visitor_flowers/         … 【来場者の花】配置と咲き演出
    ├── blooming_flower.py       1 本の花を地面から咲かせる
    └── flower_field.py          10〜30 本の配置・追加・描画順

#### 変更の確認方法
- CI/CD（GitHub Actions 等）は未設定
- `python gallery.py` 起動中に `gallery/` 内の `.py` を保存すると自動で再読み込み
- 手動なら `R` キーでも同じ（背景＋花畑を作り直し）