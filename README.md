# FlowerNose

FlowerNose は、カメラで顔を認識し、鼻の動きで花の絵を描く Python アプリです。
描いた花は PNG として保存され、別画面のギャラリーに咲くように表示できます。

## できること

- 鼻先を動かして画面上に線を描く
- ウィンクでペンの色を変える
- 顔を手で3秒以上隠す、またはキー操作で絵を保存する
- 首振り、またはキー操作で 1 ストローク戻す
- 保存された花をギャラリー画面で自動表示する

## 必要なもの

- Python 3.11
- Web カメラ、または iVCam などの仮想カメラ
- Windows または macOS

このプロジェクトは Python 3.11 を想定しています。使用するバージョンは `.python-version` にも書いてあります。

## セットアップ

### 1. リポジトリを取得する

```bash
git clone https://github.com/AiriNakanishi/FlowerNose.git
cd FlowerNose
```

### 2. 仮想環境を作る

Windows PowerShell:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

macOS:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
```

### 3. ライブラリをインストールする

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 4. MediaPipe の顔認識モデルを配置する

`assets/face_landmarker.task` がない場合は、次のコマンドで取得します。

Windows PowerShell:

```powershell
New-Item -ItemType Directory -Force assets
Invoke-WebRequest -Uri "https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/latest/face_landmarker.task" -OutFile "assets/face_landmarker.task"
```

macOS:

```bash
mkdir -p assets
curl -L -o assets/face_landmarker.task https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/latest/face_landmarker.task
```

## 起動方法

花を描く画面:

```bash
python main.py
```

ギャラリー画面:

```bash
python gallery.py
```

展示では、`main.py` と `gallery.py` を別々のターミナルで同時に起動すると、来場者が描いた花がギャラリー画面に順番に咲きます。

## 操作方法

| 操作 | 顔の動き | キーボード |
| --- | --- | --- |
| 描く | 鼻先を動かす | - |
| 保存 | 顔を手で3秒以上隠す | `W` / `Enter` / `↑` |
| 1 ストローク戻す | 首を横に振る | `Z` / `Backspace` / `Delete` / `↓` |
| 色を左へ変える | 左ウィンク | `A` / `←` |
| 色を右へ変える | 右ウィンク | `D` / `→` |
| キャンバスを消す | - | `C` / `Esc` |
| フルスクリーン切り替え | - | `F` |

保存された画像は `FlowerNose_Gallery/flower_YYYYMMDD_HHMMSS.png` に入ります。保存後、描画画面のキャンバスは自動で空になります。

## ギャラリー画面

`gallery.py` は `FlowerNose_Gallery/` を約0.25秒ごとに確認します。画像の追加・削除・差し替えは、自動でギャラリー画面へ反映されます。

ギャラリー画面のキー操作:

| キー | 動作 |
| --- | --- |
| `F` | フルスクリーン切り替え |
| `R` | ギャラリーを再読み込み |
| `Esc` | 終了 |

ギャラリーのサイズ、表示先ディスプレイ、花の数、アニメーション速度などは `gallery/settings.py` で調整できます。

## よく変更する設定

主な設定は `config.py` にあります。

| 設定 | 内容 |
| --- | --- |
| `System.CAMERA_INDEX` | 使用するカメラ番号 |
| `System.MAIN_DISPLAY_INDEX` | 描画画面を出すディスプレイ番号 |
| `System.SAVE_DIR` | 花 PNG の保存先 |
| `Sizes.WINDOW_WIDTH` / `Sizes.WINDOW_HEIGHT` | 描画画面のサイズ |
| `Sizes.PEN_THICKNESS` | 線の太さ |
| `Gestures.*` | 顔を隠す時間、ウィンク、首振り検出のしきい値 |

カメラ番号がわからないときは、次の補助スクリプトで確認できます。

```bash
python scripts/check_cameras.py
```

## VS Code で使うとき

VS Code の Python インタープリターには、作成した仮想環境の Python を選んでください。

Windows:

```text
.venv\Scripts\python.exe
```

macOS:

```text
.venv/bin/python
```

この作業環境では `.venv311` でも動作確認済みです。新しくセットアップする場合は、上の手順どおり `.venv` を作れば大丈夫です。

## 困ったとき

### カメラが開かない

- iVCam を使う場合は、スマホ側と PC 側のアプリを両方起動します。
- `python scripts/check_cameras.py` で使えるカメラ番号を確認します。
- 見つかった番号を `config.py` の `System.CAMERA_INDEX` に入れます。

### 顔が認識されない

- `assets/face_landmarker.task` が存在するか確認します。
- 顔が明るく映るようにします。
- カメラに顔全体が入る位置に立ちます。

### ギャラリーに花が出ない

- `main.py` で保存した PNG が `FlowerNose_Gallery/` にあるか確認します。
- `gallery.py` の画面で `R` を押して再読み込みします。
- `config.py` と `gallery/settings.py` の保存先が同じか確認します。

## フォルダ構成

```text
FlowerNose/
├── main.py                 # 鼻で花を描くメイン画面
├── gallery.py              # 保存された花を表示するギャラリー画面
├── config.py               # カメラ、保存先、ジェスチャーなどの設定
├── requirements.txt        # Python ライブラリ
├── assets/                 # MediaPipe モデルや画像素材
├── core/                   # 顔認識と描画キャンバス
├── gallery/                # ギャラリー画面の背景、花、演出
├── scripts/                # 補助スクリプト
└── FlowerNose_Gallery/     # 保存された花 PNG
```
