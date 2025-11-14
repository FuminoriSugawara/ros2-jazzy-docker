# ROS 2 Jazzy docker workspace

このリポジトリは ROS 2 Jazzy ベースの開発・検証環境を Docker Compose で提供します。ホスト側のワークスペースをコンテナへマウントし、日常的な colcon ビルドや Zenoh を用いた通信テストを行えます。

## 主要サービス

- `dev`: 汎用的な開発シェル。`/workspaces/ros2` に現在のリポジトリをマウントします。
- `rosbag2`: rosbag2 に特化した軽量イメージ。`dev` と同じボリューム設定です。
- `zenoh-bridge`: Zenoh <-> ROS 2 ブリッジ。
- `zenohd`: Zenoh ブローカー。`zenoh-bridge` と組み合わせて利用します。

## 使い方

```bash
# 必要に応じて .env を調整（Zenoh 連携時）
cp .env.example .env

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
# Zenoh ブローカーとブリッジを起動
docker compose up -d zenohd zenoh-bridge

# 収録用コンテナ
docker compose run --rm rosbag2 bash
```

## 終了

```bash
docker compose down
```
