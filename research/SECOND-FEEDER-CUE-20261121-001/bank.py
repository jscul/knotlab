"""Build the prospectively separated canonical founder banks for the feeder-cue study."""

import argparse
from dataclasses import asdict, dataclass
from functools import lru_cache
from hashlib import blake2s, sha256
from itertools import islice
import json
from pathlib import Path
from random import Random
import sys


HERE = Path(__file__).resolve().parent
B306 = HERE.parent / "FEEDER-MEMORY-20261121-001"
if str(B306) not in sys.path:
    sys.path.append(str(B306))

from feeder_game import recode_world, sample_world, source_key
from survival_sources import archived_excluded_keys, candidate_starts as b306_candidates


SCOPE = "SECOND-FEEDER-CUE-20261121-001"
SCHEMA = "second-feeder-cue-banks-v1"
SOURCE_LIMIT = 8192
TARGETS = {"train": 32, "mechanism": 32, "survival": 64}
LAWS = ("parity", "nae")
TAPES = 8


@dataclass(frozen=True, slots=True)
class Start:
    candidate_index: int
    source_key: str
    seed: int


def derive_seed(domain, *parts):
    raw = json.dumps([SCOPE, domain, *parts], sort_keys=True, separators=(",", ":"),
                     ensure_ascii=True).encode("ascii")
    return int.from_bytes(blake2s(raw, digest_size=8, person=b"FDCUE261").digest(), "big")


def source_fold(key):
    return ("train", "mechanism", "survival", "survival")[derive_seed("fold", key) % 4]


@lru_cache(maxsize=1)
def excluded_keys():
    prior = set(archived_excluded_keys())
    for path in sorted(B306.glob("history_results*.json")) + [B306 / "survival_results.json"]:
        prior.update(row["source_key"] for row in json.loads(path.read_bytes())["starts"])
    prior.update(start.source_key for start in islice(b306_candidates("mechanism"), 48))
    return frozenset(prior)


def candidate_starts(fold):
    if fold not in TARGETS:
        raise ValueError(f"Unknown founder fold {fold!r}")
    used = set(excluded_keys())
    for index in range(SOURCE_LIMIT):
        seed = derive_seed("source", index)
        key = source_key(seed)
        if key in used:
            continue
        used.add(key)
        if source_fold(key) == fold:
            yield Start(index, key, seed)


@lru_cache(maxsize=len(TARGETS))
def select_starts(fold):
    return tuple(islice(candidate_starts(fold), TARGETS[fold]))


def movement_tape(fold, key, replicate):
    return derive_seed("movement", fold, key, replicate)


def sample_pair(start, fold):
    """Return both archived-law worlds, with a shared fresh naming for held-out folds."""
    if fold != source_fold(start.source_key):
        raise ValueError(f"Founder key {start.source_key!r} is outside {fold!r}.")
    worlds = {law: sample_world(start.seed, law, rounds=2) for law in LAWS}
    if (any(world.source_key != start.source_key for world in worlds.values())
            or worlds["parity"].stages[0] != worlds["nae"].stages[0]):
        raise RuntimeError(f"Paired founder record differs at seed {start.seed}.")
    if fold == "train":
        return worlds

    law_names = {law: {name for stage in world.stages for row in stage.holdings for name in row}
                 for law, world in worlds.items()}
    names = sorted(set().union(*law_names.values()))
    shuffled = names.copy()
    Random(derive_seed("rename", fold, start.source_key)).shuffle(shuffled)
    rename = dict(zip(names, shuffled, strict=True))
    return {law: recode_world(world, {old: rename[old] for old in law_names[law]})[0]
            for law, world in worlds.items()}


def _manifest():
    folds = {fold: [asdict(start) for start in select_starts(fold)] for fold in TARGETS}
    counts = {fold: len(rows) for fold, rows in folds.items()}
    return {
        "schema": SCHEMA, "scope": SCOPE, "source_limit": SOURCE_LIMIT, "targets": TARGETS,
        "counts": counts, "targets_reached": counts == TARGETS, "tapes": TAPES,
        "excluded_keys": sorted(excluded_keys()), "folds": folds,
    }


def load_bank(path):
    payload = Path(path).read_bytes()
    manifest = json.loads(payload)
    if manifest != _manifest():
        raise ValueError(f"Bank {path} differs from the frozen source recipe.")
    return {fold: tuple(Start(**row) for row in rows) for fold, rows in manifest["folds"].items()}, sha256(payload).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=HERE / "bank.json")
    args = parser.parse_args()
    manifest = _manifest()
    with args.output.open("x", encoding="utf-8") as handle:
        json.dump(manifest, handle, indent=2, sort_keys=True)
        handle.write("\n")
    print(f"Frozen bank counts {manifest['counts']}; {len(manifest['excluded_keys'])} archived keys excluded.")


if __name__ == "__main__":
    main()
