"""Transport state manager with heartbeat and fallback logic.

Manages automatic Socket -> IPC fallback when the HyperMesh GUI socket
listener becomes unresponsive. A background heartbeat thread periodically
checks socket availability and recovers to socket mode when possible.
"""

from __future__ import annotations

import socket
import threading
import time
from dataclasses import dataclass, field

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 47882

MAX_FAILURES = 3
HEARTBEAT_INTERVAL = 5


@dataclass
class TransportState:
    """Tracks socket vs IPC transport health."""

    socket_active: bool = True
    ipc_active: bool = False
    consecutive_failures: int = 0
    consecutive_successes: int = 0
    last_heartbeat: float = 0.0
    fallback_count: int = 0

    def should_use_socket(self) -> bool:
        """Return True if socket transport should be attempted."""
        return self.socket_active

    def record_failure(self) -> None:
        """Record a socket failure. After MAX_FAILURES, switch to IPC."""
        self.consecutive_failures += 1
        self.consecutive_successes = 0
        if self.consecutive_failures >= MAX_FAILURES:
            self.socket_active = False
            self.ipc_active = True
            self.fallback_count += 1

    def record_success(self) -> None:
        """Record a socket success. Resets failure counter."""
        self.consecutive_failures = 0
        self.consecutive_successes += 1

    def recover_socket(self) -> None:
        """Switch back to socket mode (called by heartbeat when socket alive)."""
        self.socket_active = True
        self.ipc_active = False
        self.consecutive_failures = 0


# --- Module-level singleton ---

_state = TransportState()
_heartbeat_thread: threading.Thread | None = None


def get_state() -> TransportState:
    """Return the global transport state singleton."""
    return _state


def reset_state() -> None:
    """Reset to default socket-first state (useful for testing)."""
    global _state
    _state = TransportState()


# --- Socket health check ---


def check_socket_alive(
    host: str = DEFAULT_HOST, port: int = DEFAULT_PORT, timeout: float = 2.0
) -> bool:
    """Probe whether the HyperMesh GUI socket listener is accepting connections."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except Exception:
        return False


# --- Heartbeat ---


def heartbeat_loop(interval: float = HEARTBEAT_INTERVAL) -> None:
    """Background loop: when in IPC mode, probe socket to detect recovery."""
    global _state
    while True:
        if not _state.socket_active:
            if check_socket_alive():
                _state.recover_socket()
        _state.last_heartbeat = time.time()
        time.sleep(interval)


def start_heartbeat() -> None:
    """Start the background heartbeat thread (idempotent)."""
    global _heartbeat_thread
    if _heartbeat_thread is None or not _heartbeat_thread.is_alive():
        _heartbeat_thread = threading.Thread(
            target=heartbeat_loop, daemon=True, name="transport-heartbeat"
        )
        _heartbeat_thread.start()
