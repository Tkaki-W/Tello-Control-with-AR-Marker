# Tello Control with AR Marker

Tello のカメラで ArUco マーカーを検出し、**距離・向き・横位置** を推定。
マーカーの正面・一定距離を保つように、ドローンが自動で位置を合わせ続けます。

<!-- デモ動画：GitHub の編集画面に mp4 をドラッグ&ドロップすると URL が生成されるので、下の行と置き換えてください -->
<p align="center">
  <a href="https://youtu.be/qgd4qfcZtI">
    <img src="https://i9.ytimg.com/vi/qgd4qfcZtIM/mqdefault.jpg?sqp=CNDMgdYG-oaymwEmCMACELQB8quKqQMa8AEB-AH-CYAC0AWKAgwIABABGGMgYyhjMA8=&rs=AOn4CLB-Uq9qK2Eu2MliSgMbBelKWVo2rg" width="640" alt="デモ動画">
  </a>
</p>

## 仕組み

```mermaid
flowchart TD
    A[Tello のカメラ映像] --> B[ArUco マーカー検出]
    B --> C{マーカーあり?}
    C -- No --> A
    C -- Yes --> D["姿勢推定<br/>距離 / 横位置 x / 角度 yaw"]
    D --> E{"距離<br/>60〜110 cm?"}
    E -- 近い --> E1[back]
    E -- 遠い --> E2[forward]
    E -- OK --> F{"角度<br/>-20〜20°?"}
    E1 & E2 --> F
    F -- "-20°未満" --> F1[ccw]
    F -- "20°超" --> F2[cw]
    F -- OK --> G{"横位置<br/>-25〜15?"}
    F1 & F2 --> G
    G -- マーカーが左 --> G1[left]
    G -- マーカーが右 --> G2[right]
    G -- OK --> H[100ms 後に再判定]
    G1 & G2 --> H
    H --> A
```

映像処理・移動制御・UDP 通信を別スレッドに分け、映像の遅延を抑えています。

## 使い方

```bash
pip install opencv-contrib-python numpy
# PC を Tello の Wi-Fi に接続してから、リポジトリ直下で実行
python move/move.py
```

| `j` | `k` | `w` / `s` | `h` / `l` | **`b`** | `q` |
|:---:|:---:|:---:|:---:|:---:|:---:|
| 離陸 | 着陸 | 前進 / 後退 | 上昇 / 下降 | **自動追従 ON/OFF** | 終了 |
