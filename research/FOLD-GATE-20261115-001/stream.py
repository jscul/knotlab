"""Six-input task streams, separated by mechanisms before sampling labeled targets.

``training_tasks()`` and ``held_tasks()`` yield integer truth tables to the
respective label oracles. Bit x is the answer on input x. A learner receives
the available labeled rows of its target, never a target table or a class ID.
"""

import argparse
import hashlib
import json
import random
import struct
import tempfile
from collections import Counter
from functools import lru_cache
from itertools import combinations
from pathlib import Path


N = 6
TARGET_COUNTS = {"train": 1024, "held": 32768}
PARTITION_SEED = 6202611
SAMPLE_SEEDS = {"train": 6202612, "held": 6202613}
ORDERED_TRUTH_SHA256 = {
    "train": "238be6bbb8ca3005f32785ad4d323f2f5cb382ccc1ad8a1b3cbd7772738874df",
    "held": "4b7ac63aac335dfaaca43ec05820ee44ce685fabb6721e71d95393a29802e811",
}
FORMAT = "fold-gate-truth-u64le-v1"
WORD = struct.Struct("<Q")
ALL_BITS = (1 << 64) - 1
COLUMNS = tuple(sum(1 << x for x in range(64) if x & (1 << i)) for i in range(N))
ATOM = (0,)
AND, OR, XOR = 1, 2, 3


# The first eight rows were chosen without any target labels. They are the
# first sample in the stated Hamming-weight strata (seed 6202601) with full
# affine rank, all pairwise bit configurations, two or more adjacent pairs,
# and two to six ones per input column. Further rows use a separate seed.
INITIAL = (16, 47, 3, 29, 35, 40, 38, 63)


def _further_order():
    remaining = [row for row in range(64) if row not in INITIAL]
    random.Random(6202602).shuffle(remaining)
    return tuple(remaining)


FURTHER = _further_order()
ROW_ORDER = INITIAL + FURTHER
STAGES = (8, 12, 16, 24, 32, 48, 64)


def _join(gate, left, right):
    children = []
    for node in (left, right):
        children.extend(node[1:] if node[0] == gate else (node,))
    return (gate, *sorted(children))


@lru_cache(maxsize=None)
def _shapes(n):
    """All unlabeled formula trees, flattened and sorted at each associative gate."""
    if n == 1:
        return (ATOM,)
    return tuple(sorted({_join(gate, left, right) for size in range(1, n // 2 + 1)
                         for left in _shapes(size) for right in _shapes(n - size)
                         for gate in (AND, OR, XOR)}))


def _representative(shape):
    leaves = iter(COLUMNS)

    def run(node):
        if node == ATOM:
            return next(leaves)
        gate, first, *others = node
        value = run(first)
        for other in others:
            right = run(other)
            if gate == AND:
                value &= right
            elif gate == OR:
                value |= right
            else:
                value ^= right
        return value

    return run(shape)


def _has_fold(shape):
    children = shape[1:]
    return ((shape[0] == XOR and any(child[0] == AND for child in children))
            or any(_has_fold(child) for child in children))


# Adjacent transpositions generate every input permutation. For each swap,
# shift the two unmatched row groups into one another, retaining equal bits.
SWAPS = tuple((a & (ALL_BITS ^ b), b & (ALL_BITS ^ a), ALL_BITS ^ (a ^ b), 1 << i)
              for i, (a, b) in enumerate(zip(COLUMNS, COLUMNS[1:])))


def _permutation_class(shape):
    first = _representative(shape)
    pending = [first]
    found = {first}
    for table in pending:
        for lower, upper, equal, distance in SWAPS:
            swapped = (table & equal) | ((table & lower) << distance) | ((table & upper) >> distance)
            if swapped not in found:
                found.add(swapped)
                pending.append(swapped)
    return tuple(sorted(found))


@lru_cache(maxsize=2)
def _class_ids(split):
    if split not in TARGET_COUNTS:
        raise ValueError(f"Unknown split {split!r}")
    ids = list(range(len(_shapes(N))))
    random.Random(PARTITION_SEED).shuffle(ids)
    end = len(ids) // 4
    return tuple(sorted(ids[:end] if split == "train" else ids[end:]))


def _digest(words):
    result = hashlib.sha256()
    for word in words:
        result.update(WORD.pack(word))
    return result.hexdigest()


@lru_cache(maxsize=2)
def _sample(split):
    """Generate exactly one split. Tables from the other split are never expanded here."""
    ids = _class_ids(split)
    shapes = _shapes(N)
    foldable = {i for i in ids if _has_fold(shapes[i])}
    pool = []
    for mechanism in ids:
        pool.extend((truth, mechanism) for truth in _permutation_class(shapes[mechanism]))
    selected = tuple(random.Random(SAMPLE_SEEDS[split]).sample(pool, TARGET_COUNTS[split]))
    counts = Counter(mechanism for _, mechanism in selected)
    stats = {
        "split": split, "format": FORMAT, "n": N, "row_order": ROW_ORDER, "stages": STAGES,
        "sampling": "uniform labeled truth without replacement within a uniformly partitioned mechanism pool",
        "pool_mechanisms": len(ids), "pool_foldable_mechanisms": len(foldable),
        "pool_labeled": len(pool), "pool_foldable_labeled": sum(m in foldable for _, m in pool),
        "count": len(selected), "sample_mechanisms": len(counts),
        "sample_foldable_mechanisms": len(foldable.intersection(counts)),
        "sample_foldable_tasks": sum(counts[m] for m in foldable),
        "sample_recodings_after_first": len(selected) - len(counts), "max_tasks_per_mechanism": max(counts.values()),
        "partition_mechanisms_sha256": _digest(ids), "sample_mechanisms_sha256": _digest(sorted(counts)),
        "ordered_truths_sha256": _digest(truth for truth, _ in selected),
        "ordered_mechanisms_sha256": _digest(m for _, m in selected),
    }
    if stats["ordered_truths_sha256"] != ORDERED_TRUTH_SHA256[split]:
        raise AssertionError("Generation differs from the preselected order of targets")
    return selected, stats


def training_tasks():
    return (truth for truth, _ in _sample("train")[0])


def held_tasks():
    return (truth for truth, _ in _sample("held")[0])


def grading_rows(split):
    """Post-fit accounting only. Stream order is identical to the label-oracle input."""
    selected, _ = _sample(split)
    shapes = _shapes(N)
    return ({"truth": truth, "mechanism": m, "foldable": _has_fold(shapes[m])} for truth, m in selected)


def split_summary(split):
    return dict(_sample(split)[1])


def save_split(split, path):
    """Save one JSON header line and exactly one unsigned little-endian word per task."""
    selected, stats = _sample(split)
    target = Path(path)
    out = tempfile.NamedTemporaryFile(dir=target.parent, delete=False)
    temporary = Path(out.name)
    try:
        with out:
            out.write(json.dumps(stats, sort_keys=True, separators=(",", ":")).encode() + b"\n")
            out.writelines(WORD.pack(truth) for truth, _ in selected)
        temporary.replace(target)
    finally:
        temporary.unlink(missing_ok=True)
    return dict(stats)


def load_split(path, expected_split):
    """A wrong split, unknown row order or damaged stream is rejected before use."""
    if expected_split not in TARGET_COUNTS:
        raise ValueError(f"Unknown split {expected_split!r}")
    with Path(path).open("rb") as source:
        header = json.loads(source.readline())
        if (header["split"] != expected_split or header["format"] != FORMAT or header["n"] != N
                or header["row_order"] != list(ROW_ORDER) or header["stages"] != list(STAGES)
                or header["count"] != TARGET_COUNTS[expected_split]
                or header["ordered_truths_sha256"] != ORDERED_TRUTH_SHA256[expected_split]):
            raise ValueError("The stream header does not match the requested split and public protocol")
        payload = source.read()
    if len(payload) != WORD.size * header["count"] or hashlib.sha256(payload).hexdigest() != header["ordered_truths_sha256"]:
        raise ValueError("Stream length or ordered truth fingerprint is incorrect")
    return (word[0] for word in WORD.iter_unpack(payload))


def _affine_rank(rows):
    basis = {}
    for row in rows[1:]:
        difference = row ^ rows[0]
        while difference:
            bit = difference.bit_length() - 1
            if bit not in basis:
                basis[bit] = difference
                break
            difference ^= basis[bit]
    return len(basis)


def audit():
    """Joint post-selection fixture check, distinct from single-split generation and fitting."""
    shapes = _shapes(N)
    seen = set()
    positive = set()
    for shape in shapes:
        orbit = _permutation_class(shape)
        if not seen.isdisjoint(orbit):
            raise AssertionError("Distinct normalized trees share a function after input renaming")
        representative = orbit[0]
        for i in range(N):
            if ((representative ^ (representative >> (1 << i))) & (ALL_BITS ^ COLUMNS[i])) == 0:
                raise AssertionError("A normalized mechanism uses fewer than six essential inputs")
        seen.update(orbit)
        if _has_fold(shape):
            positive.update(orbit)
    if (len(shapes), sum(map(_has_fold, shapes)), len(seen), len(positive)) != (651, 277, 81819, 39671):
        raise AssertionError("Normalized inventory disagrees with independent semantic enumeration")
    train, held = _sample("train")[0], _sample("held")[0]
    train_names, held_names = set(_class_ids("train")), set(_class_ids("held"))
    if not train_names.isdisjoint(held_names) or len(train_names | held_names) != len(shapes):
        raise AssertionError("Mechanism partition is not disjoint and complete")
    union = tuple(train) + tuple(held)
    if len({t for t, _ in union}) != sum(TARGET_COUNTS.values()):
        raise AssertionError("A labeled target was repeated")
    pairs = tuple(combinations(INITIAL, 2))
    projections = [len({((x >> i) & 1, (x >> j) & 1) for x in INITIAL}) for i, j in combinations(range(N), 2)]
    if set(ROW_ORDER) != set(range(64)) or len(ROW_ORDER) != 64 or _affine_rank(INITIAL) != 6 or min(projections) != 4:
        raise AssertionError("Invalid public row order")
    return {"mechanisms": len(shapes), "foldable_mechanisms": sum(map(_has_fold, shapes)),
            "labeled": len(seen), "foldable_labeled": len(positive), "essential_inputs": N,
            "initial_affine_rank": _affine_rank(INITIAL), "initial_one_flip_pairs": sum((a ^ b).bit_count() == 1 for a, b in pairs),
            "initial_comparable_pairs": sum((a & b) in (a, b) for a, b in pairs),
            "initial_answer_patterns_in_population": len({sum(((t >> x) & 1) << j for j, x in enumerate(INITIAL)) for t in seen}),
            "train": split_summary("train"), "held": split_summary("held")}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("split", choices=("train", "held", "audit"))
    parser.add_argument("--out", type=Path, help="save this split's evaluator-only truth words")
    args = parser.parse_args()
    if args.split == "audit":
        if args.out:
            parser.error("audit prints its report to stdout")
        result = audit()
    elif args.out:
        result = save_split(args.split, args.out)
    else:
        result = split_summary(args.split)
    print(json.dumps(result, sort_keys=True))
