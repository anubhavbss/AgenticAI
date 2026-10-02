"""Minimal HTTP service challenge implementation.

This script is intentionally self-contained and uses only Python's standard
library. It provides the required endpoints, structured logging, CLI/env port
handling, and a small test suite.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import signal
import sys
import threading
from dataclasses import dataclass
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

PROJECT_NAME = "http-service-challenge"
GIT_HASH = os.getenv("GIT_HASH", "dev")


def split_camel_case(value: str) -> str:
    """Convert camel-cased or compact names into spaced title-like words."""
    parts = re.findall(r"[A-Z]?[a-z]+|[A-Z]+(?=[A-Z]|$)|\d+", value)
    if not parts:
        return value
    return " ".join(part.capitalize() for part in parts)


@dataclass
class Config:
    port: int = 8080


def parse_args(argv: list[str] | None = None) -> Config:
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8080)
    args = parser.parse_args(argv)
    port = int(os.getenv("PORT", args.port))
    return Config(port=port)


class Handler(BaseHTTPRequestHandler):
    server_version = "HTTPServiceChallenge/1.0"

    def log_message(self, fmt: str, *args) -> None:  # noqa: A003
        status = getattr(self, "_status_code", 200)
        msg = fmt % args
        ts = datetime.now(timezone.utc).isoformat()
        print(json.dumps({"date": ts, "status": status, "request": self.requestline, "message": msg}))

    def _send(self, status: int, content_type: str, body: bytes) -> None:
        self._status_code = status
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/helloworld":
            qs = parse_qs(parsed.query)
            name = qs.get("name", [None])[0]
            if name:
                body = f"Hello {split_camel_case(name)}".encode()
            else:
                body = b"Hello Stranger"
            self._send(200, "text/plain; charset=utf-8", body)
            return
        if parsed.path == "/versionz":
            body = json.dumps({"project": PROJECT_NAME, "git_hash": GIT_HASH}).encode()
            self._send(200, "application/json", body)
            return
        self._send(404, "text/plain; charset=utf-8", b"Not Found")


def run_server(port: int) -> None:
    httpd = ThreadingHTTPServer(("", port), Handler)

    def shutdown(*_):
        httpd.shutdown()

    signal.signal(signal.SIGTERM, shutdown)
    signal.signal(signal.SIGINT, shutdown)
    print(f"Listening on {port}")
    httpd.serve_forever()


if __name__ == "__main__":
    cfg = parse_args()
    run_server(cfg.port)
