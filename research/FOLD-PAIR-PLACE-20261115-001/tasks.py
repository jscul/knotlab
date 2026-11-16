"""Fresh paired labelings of the sealed four-fold panel; no hint enters a public row."""

import hashlib
import json
import random
from collections import Counter, defaultdict
from functools import lru_cache
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PLACEMENT = ROOT / "artifacts/FOLD-PLACEMENT-20261115-001/FOLD-PLACEMENT-20261115-001-E001_fixed_inputs"
OLDER = (
    (ROOT / "artifacts/FOLD-DEPTH-20261115-001/FOLD-DEPTH-20261115-001-E001_supplied_fold/public.json",
     "7fc715766b16efa1bbf184b4a0cc10da652f75087e761fe228970f3527884a44"),
    (ROOT / "artifacts/FOLD-DISCOVERY-20261115-001/FOLD-DISCOVERY-20261115-001-E001_learned_library/held.json",
     "4f71ef1bd74bc5f416b56ae249f3d148ec11c9b9c12e37a193b734801eb3939c"),
)
PANEL_HASH = "6f8d14f15ff74559ba48cd1cece24b02e8046daf60e86da3e2ff2532aae94bc3"
GRADE_HASH = "1267752d0869fb5dfaa077a9f3be64b5ef71421cb7f5a09271acddecd401ebcf"
PAIR_ORDER_SEED, RELABEL_SEED, STREAM_SEED, ID_SEED, PAIR_ID_SEED = 731021, 731033, 731053, 731077, 731081


def _read(path, expected):
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != expected:
        raise ValueError(f"Predecessor target binding changed at {path}")
    return json.loads(raw)


@lru_cache(maxsize=1)
def _predecessors():
    public = {r["id"]: r for r in _read(PLACEMENT / "panel.json", PANEL_HASH)}
    grades = _read(PLACEMENT / "grades.json", GRADE_HASH)
    if set(public) != set(grades) or len(public) != 48:
        raise AssertionError("Predecessor identities do not match the sealed fixture")
    prohibited = {r["truth"] for r in public.values()}
    for path, digest in OLDER:
        prohibited.update(r["truth"] for r in _read(path, digest) if r["n"] == 9)
    return public, grades, frozenset(prohibited)


def _old_inputs(permutation):
    """For new input x, recover the original bits using new_position = permutation[old_position]."""
    return tuple(sum(((x >> new) & 1) << old for old, new in enumerate(permutation)) for x in range(512))


def _relabel_table(original, old_inputs):
    return sum(((original >> old) & 1) << new for new, old in enumerate(old_inputs))


def _relabel_source(source, permutation):
    if isinstance(source, int):
        return permutation[source]
    return (source[0], *(_relabel_source(child, permutation) for child in source[1:]))


@lru_cache(maxsize=1)
def _panel():
    public, grades, previous = _predecessors()
    pairs = defaultdict(list)
    for old_id, meta in grades.items():
        pairs[meta["pair"]].append(old_id)
    pair_order = sorted(pairs)
    random.Random(PAIR_ORDER_SEED).shuffle(pair_order)
    draws = random.Random(RELABEL_SEED)
    pair_ids = random.Random(PAIR_ID_SEED)
    used = set(previous)
    pending = []
    for original_pair in pair_order:
        first, second = sorted(pairs[original_pair])
        if grades[first]["partner"] != second or grades[second]["partner"] != first:
            raise AssertionError("Pairing disagrees with predecessor records")
        pair = f"{pair_ids.getrandbits(96):024x}"
        # Condition only on both exact targets being fresh. No predicate on
        # the hint, changed coordinates, truth density or learner is consulted.
        while True:
            permutation = tuple(draws.sample(range(9), 9))
            old_inputs = _old_inputs(permutation)
            tables = tuple(_relabel_table(public[key]["truth"], old_inputs) for key in (first, second))
            if len(set(tables)) == 2 and used.isdisjoint(tables):
                break
        used.update(tables)
        for old_id, table in zip((first, second), tables):
            former = grades[old_id]
            meta = {"depth": former["depth"], "kind": former["kind"], "pair": pair,
                    "stage1_id": old_id, "stage1_pair": original_pair, "permutation": permutation,
                    "source": _relabel_source(former["source"], permutation),
                    "normalized_structure": former["normalized_structure"], "edit_at_hint": former["edit_at_hint"],
                    "stage1_hint_in_new_coordinates": tuple(sorted(permutation[i] for i in public[old_id]["hint"])),
                    "max_gate_disjoint_F": former["max_gate_disjoint_F"], "output_ones": table.bit_count()}
            pending.append((table, meta))
    # Generate opaque IDs from a separate random stream *after* the independent
    # public shuffle. Neither ID bytes nor adjacency encodes the paired groups.
    random.Random(STREAM_SEED).shuffle(pending)
    ids = random.Random(ID_SEED)
    rows = []
    renamed_ids = {}
    for table, meta in pending:
        key = f"{ids.getrandbits(128):032x}"
        renamed_ids[meta["stage1_id"]] = key
        rows.append(({"id": key, "n": 9, "truth": table}, meta))
    for _, meta in rows:
        meta["partner"] = renamed_ids[grades[meta["stage1_id"]]["partner"]]
    return tuple(rows)


def tasks():
    """Public rows for binding; bit x of truth is the label of assignment x."""
    return tuple(dict(row) for row, _ in _panel())


def grading():
    """Private source and pairing evidence, kept out of the solver invocation."""
    return {row["id"]: dict(meta) for row, meta in _panel()}


def _scalar(tree, x):
    if isinstance(tree, int):
        return (x >> tree) & 1
    op, first, second, third = tree
    a, b, c = (_scalar(sub, x) for sub in (first, second, third))
    if op == "F":
        return (a & b) ^ c
    if op == "R-a":
        return a & (b ^ c)
    if op == "R-b":
        return b & (a ^ c)
    raise ValueError(f"Unknown grading operation {op}")


def audit():
    previous_rows, previous_grades, excluded = _predecessors()
    rows, meta = tasks(), grading()
    if (len(rows), len(meta), len({r["truth"] for r in rows}), len(excluded)) != (48, 48, 48, 84):
        raise AssertionError("An output identity, truth or predecessor set was duplicated")
    if {m["stage1_id"] for m in meta.values()} != set(previous_rows):
        raise AssertionError("Missing a predecessor task")
    counts = Counter()
    for row in rows:
        m = meta[row["id"]]
        other = meta[m["partner"]]
        older = previous_rows[m["stage1_id"]]
        if set(row) != {"id", "n", "truth"} or row["n"] != 9 or row["truth"] in excluded:
            raise AssertionError("Unblinded schema or previously evaluated truth table")
        if (sorted(m["permutation"]) != list(range(9)) or m["permutation"] != other["permutation"]
                or other["pair"] != m["pair"] or other["partner"] != row["id"] or other["depth"] != m["depth"]):
            raise AssertionError("Pair renaming or linkage is inconsistent")
        if previous_grades[m["stage1_id"]]["partner"] != other["stage1_id"]:
            raise AssertionError("Paired members did not come from the same source pair")
        for old_x in range(512):
            new_x = sum(((old_x >> j) & 1) << p for j, p in enumerate(m["permutation"]))
            original = (older["truth"] >> old_x) & 1
            if original != ((row["truth"] >> new_x) & 1) or original != _scalar(m["source"], new_x):
                raise AssertionError("Relabeling or independent scalar source disagrees")
        counts[m["depth"], m["kind"]] += 1
    if counts != {(d, kind): 8 for d in (2, 3, 4) for kind in ("positive", "negative")}:
        raise AssertionError("The mathematical task mix changed")
    data = json.dumps(rows, sort_keys=True, separators=(",", ":")).encode()
    return {"public_sha256": hashlib.sha256(data).hexdigest(), "tasks": len(rows), "pairs": len({m["pair"] for m in meta.values()}),
            "excluded_earlier_nine_input_truths": len(excluded), "exact_overlaps": 0,
            "new_normalized_structures": 0, "scalar_truth_checks": len(rows) * 512,
            "positive_mechanisms_by_depth": {str(d): len({json.dumps(m["normalized_structure"]) for m in meta.values()
                                                             if m["kind"] == "positive" and m["depth"] == d}) for d in (2, 3, 4)}}


if __name__ == "__main__":
    print(json.dumps(audit(), sort_keys=True))
