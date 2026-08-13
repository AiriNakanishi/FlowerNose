# FlowerNose

FlowerNose は、カメラで顔を認識し、鼻の動きで花の絵を描く Python アプリです。
描いた画像はギャラリー画面で表示できます。

## 必要な環境

- Python 3.11
- カメラ
- Windows または macOS

このプロジェクトでは Python 3.11 を使ってください。Python のバージョンは `.python-version` にも書いてあります。

## セットアップ

### 1. リポジトリを取得

```bash
git clone https://github.com/AiriNakanishi/FlowerNose.git
cd FlowerNose
```

### 2. 仮想環境を作成

Windows:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

macOS:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
```

### 3. ライブラリをインストール

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 4. MediaPipe モデルを配置

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

## 実行方法

花を描く画面:

```bash
python main.py
```

ギャラリー画面:

```bash
python gallery.py
```

## VS Code で使う仮想環境

VS Code の Python インタープリターは、作成した仮想環境の Python を選んでください。

Windows:

```text
.venv\Scripts\python.exe
```

今この作業環境では `.venv311` が動作確認済みです。新しくセットアップする人は、上の手順どおり `.venv` を作れば大丈夫です。

