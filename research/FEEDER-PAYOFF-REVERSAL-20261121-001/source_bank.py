"""Draw and verify structurally disjoint founder banks without playing games."""

import argparse
import json
from dataclasses import asdict, dataclass
from functools import cache
from hashlib import blake2s, sha256
from pathlib import Path
from random import Random

from paired_game import B306, HERE, recode_world, sample_world, source_key
from survival_sources import archived_excluded_keys


SCOPE = "FEEDER-PAYOFF-REVERSAL-20261121-001"
SOURCE_LIMIT = 16_384
TARGETS = {"train": 96, "mechanism": 48, "heldout": 128}
LAWS = ("parity", "nae")
BANK_PATH = HERE / "source_bank.json"
PREDECESSOR = HERE.parent / "SECOND-FEEDER-CUE-20261121-001"
PRIOR_BANKS = (PREDECESSOR / "bank.json", PREDECESSOR / "return_cue" / "bank.json")


@dataclass(frozen=True, slots=True)
class Start:
    candidate_index: int
    source_key: str
    seed: int


def derive_seed(domain, *parts):
    raw = json.dumps([SCOPE, domain, *parts], ensure_ascii=True, separators=(",", ":")).encode("ascii")
    return int.from_bytes(blake2s(raw, digest_size=8, person=b"FDRBANK1").digest(), "big")


def source_fold(key):
    return ("train", "mechanism", "heldout", "heldout")[derive_seed("fold", key) % 4]


@cache
def excluded_keys():
    keys = set(archived_excluded_keys())
    for path in sorted(B306.glob("history_results*.json")) + [B306 / "survival_results.json"]:
        keys.update(row["source_key"] for row in json.loads(path.read_bytes())["starts"])
    for path in PRIOR_BANKS:
        prior = json.loads(path.read_bytes())
        keys.update(prior["excluded_keys"])
        keys.update(row["source_key"] for fold in prior["folds"].values() for row in fold)
    return frozenset(keys)


@cache
def _draw_folds():
    seen = set(excluded_keys())
    folds = {fold: [] for fold in TARGETS}
    for index in range(SOURCE_LIMIT):
        seed = derive_seed("source", index)
        key = source_key(seed)
        if key in seen:
            continue
        seen.add(key)
        fold = source_fold(key)
        if len(folds[fold]) < TARGETS[fold]:
            folds[fold].append(Start(index, key, seed))
        if all(len(rows) == TARGETS[name] for name, rows in folds.items()):
            return {name: tuple(rows) for name, rows in folds.items()}, index + 1
    counts = {fold: len(rows) for fold, rows in folds.items()}
    raise RuntimeError(f"Source cap reached with counts {counts}.")


def select_starts(fold):
    return _draw_folds()[0][fold]


def movement_tape(fold, key, replicate):
    return derive_seed("movement", fold, key, replicate)


def sample_pair(start, fold):
    """Grow both laws on one founder and rename distinctions in the evaluation folds."""
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
    folds, candidates = _draw_folds()
    archive = {str(path.relative_to(HERE.parent)): sha256(path.read_bytes()).hexdigest()
               for path in PRIOR_BANKS}
    return {
        "schema": "feeder-payoff-founder-bank-v1", "scope": SCOPE,
        "source_limit": SOURCE_LIMIT, "candidates": candidates, "targets": TARGETS,
        "counts": {fold: len(rows) for fold, rows in folds.items()},
        "excluded_keys": sorted(excluded_keys()), "prior_bank_sha256": archive,
        "folds": {fold: [asdict(start) for start in rows] for fold, rows in folds.items()},
    }


def load_bank(path=BANK_PATH):
    payload = Path(path).read_bytes()
    manifest = json.loads(payload)
    if manifest != _manifest():
        raise ValueError(f"Bank {path} differs from the frozen source recipe.")
    folds = {fold: tuple(Start(**row) for row in rows) for fold, rows in manifest["folds"].items()}
    return folds, sha256(payload).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default=BANK_PATH, type=Path)
    args = parser.parse_args()
    manifest = _manifest()
    with args.output.open("x", encoding="utf-8") as handle:
        json.dump(manifest, handle, indent=2, sort_keys=True)
        handle.write("\n")
    print(f"Frozen counts {manifest['counts']} and {len(manifest['excluded_keys'])} excluded archived keys.")


if __name__ == "__main__":
    main()
