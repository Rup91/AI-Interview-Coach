"""Interview ID generation.

Produces IDs like "INT-10001", matching the format shown in
API_CONTRACT.md. Purely in-memory and process-local for now; replaced by
a persistence-backed strategy once a real database is introduced.
"""

import threading


class SequentialIdGenerator:
    """Generates unique, incrementing interview IDs with a fixed prefix.

    Thread-safe: FastAPI runs synchronous route handlers in a thread
    pool, so concurrent requests could otherwise race on the counter.
    """

    def __init__(self, prefix: str = "INT-", start: int = 10001) -> None:
        self._prefix = prefix
        self._next_value = start
        self._lock = threading.Lock()

    def generate(self) -> str:
        """Return the next unique ID."""
        with self._lock:
            value = self._next_value
            self._next_value += 1
        return f"{self._prefix}{value}"
