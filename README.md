# FlowerNose

#### 1. リポジトリのクローン
```
git clone https://github.com/AiriNakanishi/FlowerNose.git
cd FlowerNose
```

### ↓Mac用

#### 2. 仮想環境のセットアップ
```
python3 -m venv venv
source venv/bin/activate
```

#### 3. ライブラリのインストール
```
pip install mediapipe opencv-python pygame
```

#### 4. AIモデルファイルの配置
```
mkdir -p assets
curl -o assets/face_landmarker.task https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/latest/face_landmarker.task
```

#### 5. アプリの実行方法
- ターミナルを2つ開き、それぞれを実行する
```
source venv/bin/activate
python gallery.py
```
```
source venv/bin/activate
python main.py
```
