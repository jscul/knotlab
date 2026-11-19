"""Shared-runner adapter for exact rooted-support lower-bound shards."""

from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from lower import DEFAULT_GENG, DEFAULT_LIBRARY, EXTEND_ROUND, ROOT, run_shard  # noqa: E402


params = {}


def setup(options):
    params.update(options)
    sys.path.insert(0, str(ROOT / "experiments" / EXTEND_ROUND))


def cases():
    minimum = int(params.get("min_junctions", 1))
    maximum = int(params.get("max_junctions", (2 * int(params["max_width"]) + 1) // 3 - 1))
    for ordinary in range(minimum, maximum + 1):
        parts = int(params.get("parts", 4)) if ordinary >= int(params.get("partition_from", 8)) else 1
        for part in range(parts):
            yield f"J{ordinary:02d}-{part:03d}-of-{parts:03d}", {"ordinary": ordinary, "part": part, "parts": parts}


def run(case_id, case):
    return run_shard(case["ordinary"], int(params["order"]), int(params.get("min_width", 1)), int(params["max_width"]),
                     params["mode"], params.get("geng", DEFAULT_GENG), params.get("library", DEFAULT_LIBRARY),
                     case["part"], case["parts"])
