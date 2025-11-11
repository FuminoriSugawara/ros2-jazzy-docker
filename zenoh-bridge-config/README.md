# Zenoh Bridge Configs

Drop your `bridge.json` or other zenoh-bridge-dds configuration files here. This directory is mounted to `/etc/zenoh` inside the `zenoh-bridge` service.

The default `bridge.json` uses `${ZENOH_CONNECT}` so the container can pick up the remote router address from your `.env`. Copy `.env.example` to `.env`, set `ZENOH_CONNECT=tcp/<zenohd-ip>:7447`, and `docker compose up zenoh-bridge` will render the template automatically.
