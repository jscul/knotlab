"""Check shortest parity changes, what one knot can read, and one-round weights."""
import argparse
from collections import Counter
import gzip
from itertools import combinations
import json
from pathlib import Path
import random
import resource
import sys
import time

HERE = Path(__file__).resolve().parent
STUDY = HERE.parent
ROOT = STUDY.parents[1]
EXPERIMENTS = ROOT / "experiments"
SEED = 4112601
ARMS = ("ordinary", "one_fewer", "arity_floor")


def add_module_dir(prefix, pattern):
    directory, = (EXPERIMENTS / prefix).glob(pattern)
    sys.path.insert(0, str(directory))


# These predecessors supply the structures and growth rules only.
add_module_dir("NAE-GROWTH-20261119-001B", "*-E001_nae")
add_module_dir("FORBIDDING-JOIN-20261120-001B", "*-E001_free_readings")
add_module_dir("WHAT-A-BIRTH-CARRIES-20261125-001B", "*-E001_link_through_a_made_knot")
import naelib
from rival_growth import grow
import eng


def input_rows(record):
    n, meetings, loose_counts = record
    rows = [[] for _ in range(n)]
    label = 0
    for first, second, number in meetings:
        for _ in range(number):
            rows[first].append(label)
            rows[second].append(label)
            label += 1
    for row, number in zip(rows, loose_counts, strict=True):
        row.extend(range(label, label + number))
        label += number
    return tuple(map(tuple, rows))


def mask(labels):
    return sum(1 << d for d in labels)


def basis(words):
    """Binary elimination with the least occupied bit as pivot."""
    pivots = {}
    for value in words:
        while value:
            pivot = value & -value
            if pivot not in pivots:
                pivots[pivot] = value
                break
            value ^= pivots[pivot]
    return [pivots[p] for p in sorted(pivots)]


def remainder(value, generators):
    for word in generators:
        if value & (word & -word):
            value ^= word
    return value


def null_basis(rows, names):
    checks = basis(rows)
    pivots = {row & -row for row in checks}
    result = []
    for name in names:
        word = 1 << name
        if word in pivots:
            continue
        for row in reversed(checks):
            if (word & row).bit_count() % 2:
                word |= row & -row
        result.append(word)
    return result


def shortest_changes(names, checks, allowed):
    # Inspect all changes of each length before retiring its newly covered names.
    columns = {d: sum(1 << j for j, row in enumerate(checks) if row & (1 << d))
               for d in names}
    open_bits = 0
    for word in allowed:
        open_bits |= word
    moves, shortest = [], []
    for length in range(1, len(names) + 1):
        if not open_bits:
            break
        new_bits = 0
        for changed in combinations(names, length):
            syndrome = word = 0
            for d in changed:
                syndrome ^= columns[d]
                word |= 1 << d
            if not syndrome and word & open_bits:
                new_bits |= word
                moves.append(word)
        if new_bits and not shortest:
            shortest = moves.copy()
        open_bits &= ~new_bits
    assert not open_bits
    return moves, shortest


def analyse(rows):
    names = sorted(set().union(*rows))
    checks = list(map(mask, rows))
    allowed = null_basis(checks, names)
    moves, least = shortest_changes(names, checks, allowed)
    motion = basis(moves)
    class_bits = len(allowed) - len(motion)
    local_bits = [len(basis(word & places for word in allowed)) -
                  len(basis(word & places for word in motion)) for places in checks]
    held = Counter(d for row in rows for d in row)
    pinned = null_basis(checks + [1 << d for d, n in held.items() if n == 1], names)
    return {
        "rank_allowed": len(allowed), "rank_moves": len(motion),
        "classes": 1 << class_bits, "classes_shortest_overall": 1 << (len(allowed) - len(basis(least))),
        "readable_bits_each_knot": local_bits,
        "loose_preserving_class_bits": len(basis(motion + pinned)) - len(motion),
    }, motion


def literal_start(rows, result, motion):
    # The starts have at most 12 distinctions. Tabulate every state and each
    # knot's possible observations by class, including arbitrary nonlinear reads.
    places = list(map(mask, rows))
    width = (max(places)).bit_length()
    states = {x: remainder(x, motion) for x in range(1 << width)
              if all((r & x).bit_count() % 2 == 0 for r in places)}
    labels = sorted(set(states.values()))
    assert len(labels) == result["classes"]
    for knot, bits in zip(places, result["readable_bits_each_knot"], strict=True):
        patterns = {label: set() for label in labels}
        for x, label in states.items():
            patterns[label].add(x & knot)
        distinct = set(map(frozenset, patterns.values()))
        assert len(distinct) == 1 << bits
        assert sum(map(len, distinct)) == len(set.union(*(set(s) for s in distinct)))
    return states


def weights(old, grown, states):
    # Fresh distinctions at different new knots are disjoint. Count their
    # literal assignments under both parities and multiply only after checking.
    old_mask = mask(set().union(*old))
    seen = set()
    factors = []
    for row in grown[len(old):]:
        fresh = {d for d in row if not ((1 << d) & old_mask)}
        assert seen.isdisjoint(fresh)
        seen.update(fresh)
        frequencies = Counter(x.bit_count() % 2 for x in range(1 << len(fresh)))
        factors.append((mask(row) & old_mask, frequencies))
    masses = Counter()
    counts = Counter()
    example = {}
    for x, label in states.items():
        ways = 1
        for part, frequencies in factors:
            ways *= frequencies[(x & part).bit_count() % 2]
        counts[ways] += 1
        masses[label] += ways
        if len(example) < 2 or ways in example:
            example.setdefault(ways, x)
    return {"class_masses": sorted(masses.values()), "old_states_by_completions": dict(sorted(counts.items())),
            "example_old_state_per_count": example}


def fold_round(old):
    stage = eng.from_stars(old)
    try:
        rec = eng.play_round(stage, eng.Law("ORD", "CANCEL-WAIT", None, "parity"), eng.Guard(4))
    except eng.GuardStop:
        return None
    return tuple(map(tuple, stage.places)) if rec["births"] else None


def check_start(index, record):
    rows = input_rows(record)
    old, motion = analyse(rows)
    states = literal_start(rows, old, motion)
    out = {"index": index, "holdings": rows, "start": old, "growth": {}}
    old_mask = mask(set().union(*rows))
    for arm in (*ARMS, "fold_ordinary"):
        if arm == "fold_ordinary":
            grown = fold_round(rows)
        else:
            grown, _ = grow(rows, "parity", arm, naelib)
        if grown is None:
            out["growth"][arm] = None
            continue
        assert tuple(grown[:len(rows)]) == rows
        trial = weights(rows, grown, states)
        if arm in ("ordinary", "fold_ordinary"):
            stage, grown_moves = analyse(grown)
            stage["old_classes_preserved"] = all(
                remainder(word & old_mask, motion) == 0 for word in grown_moves)
            trial["stage"] = stage
        out["growth"][arm] = trial
    return out


def archived(name):
    with gzip.open(STUDY / (name + ".jsonl.gz"), "rt") as file:
        return {int(row["structure"].split()[1]): row for row in map(json.loads, file)}


def run(args):
    records = json.loads((ROOT / "research/FORBID-EDITS-20261126-001/starts.json").read_text())
    canonical = archived("census_canonical")
    fold = archived("census_fold")
    checks = archived("census_checks")
    groups = {}
    for i, row in canonical.items():
        groups.setdefault(row["start"]["loose free"]["classes"], []).append(i)
    rng = random.Random(SEED)
    chosen = {k: rng.sample(sorted(groups[k]), min(len(groups[k]), n))
              for k, n in [(1, 48), (2, 80), (4, 24), (8, 2)]}
    selected = [i for group in chosen.values() for i in (group[:2] if args.pilot else group)]
    observations = []
    for i in selected:
        row = check_start(i, records[i])
        assert row["start"]["classes"] == canonical[i]["start"]["loose free"]["classes"]
        for arm, archive in [("ordinary", canonical), ("fold_ordinary", fold)]:
            trial = row["growth"][arm]
            reference = archive[i]["after one round"]
            if isinstance(reference, str):
                assert trial is None
            else:
                assert trial and trial["stage"]["classes"] == reference["loose free"]["classes"]
        if i in checks:
            for stage_name in ("start", "after one round"):
                a = checks[i][stage_name]
                if not isinstance(a, dict):
                    continue
                b = row["start"] if stage_name == "start" else row["growth"]["ordinary"]["stage"]
                c = a["shortest through each distinction"]
                assert b["classes"] == c["classes"] and b["loose_preserving_class_bits"] == c["dim (S0+H)/H"]
                assert bool(max(b["readable_bits_each_knot"])) == c["the class read inside one knot"]
                assert b["classes_shortest_overall"] == a["shortest overall"]["classes"]
                if stage_name == "after one round":
                    assert b["old_classes_preserved"] == checks[i]["old classes kept by the grown moves"]
        observations.append(row)
    return {"seed": SEED, "pilot": args.pilot, "rows": observations}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot", action="store_true")
    options = parser.parse_args()
    start = time.monotonic()
    results = run(options)
    results["seconds_after_imports"] = time.monotonic() - start
    results["peak_rss_kib"] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    print(json.dumps(results))
