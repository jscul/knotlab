"""Frozen structural separation for the B306 history and survival samples."""

from dataclasses import dataclass
from functools import lru_cache
from hashlib import blake2s
import json

from feeder_game import PRIOR, source_key


SOURCE_LIMIT = 8192


@dataclass(frozen=True, slots=True)
class Start:
    candidate_index: int
    source_key: str
    seed: int


def derive_seed(domain, *parts):
    payload = json.dumps([20261121, "B306", domain, *parts], separators=(",", ":"),
                         sort_keys=True, ensure_ascii=True).encode("ascii")
    return int.from_bytes(blake2s(payload, digest_size=8, person=b"B306BANK").digest(), "big")


def source_fold(key):
    return "mechanism" if derive_seed("fold", key) % 4 == 0 else "survival"


@lru_cache(maxsize=1)
def archived_excluded_keys():
    model = json.loads((PRIOR / "model.json").read_bytes())
    results = json.loads((PRIOR / "results.json").read_bytes())
    excluded = {start["source_key"] for start in model["training_starts"]}
    excluded.update(start["source_key"] for start in results["evaluation"]["starts"])
    for field in ("development_seed_range", "spectator_seed_range"):
        first, last = results["selection"][field]
        excluded.update(source_key(seed) for seed in range(first, last + 1))
    return frozenset(excluded)


def candidate_starts(fold):
    """Yield each fresh canonical founder key once, in its prespecified fold."""
    if fold not in ("mechanism", "survival"):
        raise ValueError(f"Unknown founder fold {fold!r}")
    seen = set(archived_excluded_keys())
    for index in range(SOURCE_LIMIT):
        seed = derive_seed("source", index)
        key = source_key(seed)
        if key in seen:
            continue
        seen.add(key)
        if source_fold(key) == fold:
            yield Start(index, key, seed)
