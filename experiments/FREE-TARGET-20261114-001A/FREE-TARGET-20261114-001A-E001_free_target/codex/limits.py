"""Cooperative computational limits; exhaustion never supplies a verdict."""
from __future__ import annotations

import os
from pathlib import Path
import resource
import time


class LimitReached(RuntimeError):
    def __init__(self, reason, detail):
        super().__init__(detail)
        self.reason = reason


def rss_bytes():
    return int(Path("/proc/self/statm").read_text().split()[1]) * os.sysconf("SC_PAGE_SIZE")


class Limits:
    def __init__(self, seconds=1650, memory_bytes=6_000_000_000):
        self.started = time.monotonic()
        self.seconds = float(seconds)
        self.memory_bytes = int(memory_bytes)
        self.peak_bytes = rss_bytes()
        self.calls = 0

    def checkpoint(self, force=False):
        self.calls += 1
        if not force and self.calls % 128:
            return
        current = rss_bytes()
        self.peak_bytes = max(self.peak_bytes, current)
        if current >= self.memory_bytes:
            raise LimitReached("memory", f"RSS {current} reached internal ceiling {self.memory_bytes}")
        if time.monotonic() - self.started >= self.seconds:
            raise LimitReached("cap", f"internal computation-time ceiling {self.seconds}s")

    def metrics(self):
        self.peak_bytes = max(self.peak_bytes, rss_bytes())
        return dict(seconds=round(time.monotonic() - self.started, 6),
                    peak_memory_bytes=self.peak_bytes,
                    process_peak_rss_bytes=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024)
