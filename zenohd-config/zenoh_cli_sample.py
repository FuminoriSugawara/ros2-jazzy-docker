#!/usr/bin/env python3
"""
Simple zenoh CLI-like helpers using the official zenoh Python API.

Usage examples (run inside the zenohd container or any environment where
`pip install eclipse-zenoh` has been executed):

  python3 zenoh_cli_sample.py sub --keyexpr rt/**
  python3 zenoh_cli_sample.py pub --keyexpr rt/sample --payload "hello"
  python3 zenoh_cli_sample.py get --selector rt/**
"""
import argparse
import json
import os
import signal
import sys
import threading
from typing import Optional

import zenoh


def open_session() -> zenoh.Session:
    """Open a zenoh session with default configuration."""
    connect_env = os.environ.get("ZENOH_CONNECT")
    if connect_env:
        endpoints = [endpoint.strip() for endpoint in connect_env.split(",") if endpoint.strip()]
        if not endpoints:
            raise RuntimeError("ZENOH_CONNECT must contain at least one endpoint.")
    else:
        # When running inside the zenohd container, default to the local router.
        endpoints = ["tcp/127.0.0.1:7447"]
    config = zenoh.Config()
    config.insert_json5("mode", '"client"')
    config.insert_json5("scouting/multicast/enabled", "false")
    config.insert_json5("listen/endpoints", "[]")
    config.insert_json5("connect/endpoints", json.dumps(endpoints))
    return zenoh.open(config)


def describe_session(session: zenoh.Session, action: str) -> None:
    """Log basic information about the current zenoh session."""
    info = session.info
    get = getattr
    zid = get(info, "zid", lambda: "unknown")()
    routers = list(get(info, "routers_zid", lambda: [])())
    peers = list(get(info, "peers_zid", lambda: [])())
    connect_env = os.environ.get("ZENOH_CONNECT")
    print(f"[session] {action}")
    print(f"[session] local zid: {zid}")
    if connect_env:
        print(f"[session] ZENOH_CONNECT={connect_env}")
    print(f"[session] routers: {routers if routers else '[none]'}")
    print(f"[session] peers: {peers if peers else '[none]'}")
    sys.stdout.flush()


def setup_signal_handlers(stop_event: threading.Event) -> None:
    """Handle SIGINT/SIGTERM so long-running subs stop gracefully."""

    def _handler(_signum, _frame):
        stop_event.set()

    signal.signal(signal.SIGINT, _handler)
    signal.signal(signal.SIGTERM, _handler)


def command_sub(args: argparse.Namespace) -> None:
    session = open_session()
    describe_session(session, f"subscriber to {args.keyexpr}")
    stop_event = threading.Event()
    setup_signal_handlers(stop_event)

    def _callback(sample: zenoh.Sample) -> None:
        payload = bytes(sample.payload).decode("utf-8", errors="replace")
        print(f"[zenoh] {sample.key_expr}: {payload}")
        sys.stdout.flush()

    subscriber = session.declare_subscriber(args.keyexpr, _callback)
    print(f"Subscribed to '{args.keyexpr}'. Press Ctrl+C to stop.")

    try:
        if args.timeout:
            stop_event.wait(args.timeout)
        else:
            stop_event.wait()
    finally:
        subscriber.undeclare()
        session.close()


def command_pub(args: argparse.Namespace) -> None:
    session = open_session()
    describe_session(session, f"publisher to {args.keyexpr}")
    payload = args.payload.encode("utf-8")
    session.put(args.keyexpr, payload, encoding=args.encoding)
    print(f"Published '{args.payload}' to '{args.keyexpr}'.")
    session.close()


def command_get(args: argparse.Namespace) -> None:
    session = open_session()
    describe_session(session, f"query for {args.selector}")
    target = {
        "BEST_MATCHING": zenoh.QueryTarget.BEST_MATCHING,
        "ALL": zenoh.QueryTarget.ALL,
        "ALL_COMPLETE": zenoh.QueryTarget.ALL_COMPLETE,
    }[args.target]
    payload: Optional[bytes] = args.payload.encode("utf-8") if args.payload else None
    replies = session.get(args.selector, target=target, payload=payload, timeout=args.timeout)
    for reply in replies:
        if reply.ok is not None:
            print(f"[ok] {reply.ok.key_expr}: {reply.ok.payload.to_string()}")
        else:
            print(f"[err] {reply.err.payload.to_string()}")
    session.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Minimal zenoh CLI sample using zenoh-python.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    sub_parser = subparsers.add_parser("sub", help="Subscribe to a key expression")
    sub_parser.add_argument("--keyexpr", "-k", required=True, help="Key expression to subscribe to (e.g., rt/**)")
    sub_parser.add_argument("--timeout", type=float, help="Stop after N seconds (default: run until Ctrl+C)")
    sub_parser.set_defaults(func=command_sub)

    pub_parser = subparsers.add_parser("pub", help="Publish a payload once")
    pub_parser.add_argument("--keyexpr", "-k", required=True, help="Key expression to publish to")
    pub_parser.add_argument("--payload", "-p", required=True, help="Payload string to send")
    pub_parser.add_argument("--encoding", default="text/plain", help="Zenoh encoding (default: text/plain)")
    pub_parser.set_defaults(func=command_pub)

    get_parser = subparsers.add_parser("get", help="Perform a zenoh query")
    get_parser.add_argument("--selector", "-s", required=True, help="Selector to query (e.g., rt/**)")
    get_parser.add_argument("--target", "-t", choices=["BEST_MATCHING", "ALL", "ALL_COMPLETE"], default="BEST_MATCHING")
    get_parser.add_argument("--payload", "-p", help="Optional payload to attach to the query")
    get_parser.add_argument("--timeout", "-o", type=float, default=10.0, help="Query timeout in seconds")
    get_parser.set_defaults(func=command_get)

    args = parser.parse_args()
    zenoh.init_log_from_env_or("error")
    args.func(args)


if __name__ == "__main__":
    main()
