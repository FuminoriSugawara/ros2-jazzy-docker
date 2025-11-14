# ROS 2 Jazzy docker workspace

このリポジトリは ROS 2 Jazzy ベースの開発・検証環境を Docker Compose で提供します。ホスト側のワークスペースをコンテナへマウントし、日常的な colcon ビルドや rosbag2 を使った検証を行えます。

## 主要サービス

- `dev`: 汎用的な開発シェル。`/workspaces/ros2` に現在のリポジトリをマウントします。
- `rosbag2`: rosbag2 に特化した軽量イメージ。`dev` と同じボリューム設定です。

## 使い方

```bash
# イメージをビルド
docker compose build

# 開発用コンテナに入る
docker compose run --rm dev bash
# --- コンテナ内 ---
source /opt/ros/jazzy/setup.bash
cd /workspaces/ros2
colcon build --symlink-install
source install/setup.bash
```

### サービスの起動例

```bash
# 収録用コンテナ
docker compose run --rm rosbag2 bash
```

## 終了

```bash
docker compose down
```
