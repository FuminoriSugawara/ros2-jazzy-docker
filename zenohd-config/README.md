# Zenoh Router Configs

Place `zenohd.json` and TLS/ACL assets here. The `zenohd` service mounts this directory at `/etc/zenoh`.

## `zenoh_cli_sample.py`

This helper script lives alongside the router config so you can quickly test pub/sub against any zenohd instance. Typical workflow:

1. Copy `.env.example` to `.env`, set `ZENOH_CONNECT=tcp/<your-zenohd-ip>:7447`, then `source .env`.
2. Enter the zenohd container (or any environment with `eclipse-zenoh` installed) and run:
   ```bash
   python3 /etc/zenoh/zenoh_cli_sample.py sub --keyexpr rt/**
   python3 /etc/zenoh/zenoh_cli_sample.py pub --keyexpr rt/sample --payload "hello from cli"
   python3 /etc/zenoh/zenoh_cli_sample.py get --selector rt/**
   ```

At startup the script prints the active `ZENOH_CONNECT` value plus router IDs, making it easy to confirm which zenohd you are connected to.
