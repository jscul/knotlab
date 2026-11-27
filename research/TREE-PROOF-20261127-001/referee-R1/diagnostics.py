"""Audit what the frozen summary fields could distinguish. Reads raw JSON lines."""
import argparse
from collections import Counter
from itertools import combinations
import json
from pathlib import Path
import resource
from time import perf_counter

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parents[1] / "SELECTED-KNOTS-20261127-001"


def tree_levels(m, distances):
    groups = {1 << i for i in range(m)}
    relations = []
    levels = []
    for weight in sorted(set(distances.values())):
        previous = groups.copy()
        for (a, b), d in distances.items():
            if d != weight:
                continue
            left = next(g for g in groups if g & (1 << a))
            right = next(g for g in groups if g & (1 << b))
            groups.discard(left)
            groups.discard(right)
            groups.add(left | right)
        added = groups - previous
        if not added:
            continue
        levels.append([weight, sorted(groups)])
        for parent in sorted(added):
            children = [g for g in sorted(previous) if g & parent]
            relations.append((parent, children))
    return levels, relations


def span(masks):
    result = {0}
    for mask in masks:
        result.update([mask ^ g for g in result])
    return result


def literal_local_reads(m, relations):
    """A fact is read by one knot exactly if its values agree within each view."""
    full = 2**m - 1
    places = sorted({g for _, children in relations for g in children})
    states = [s for s in range(full + 1) if s.bit_count() % 2 == 0]
    words = {s: sum((((s & place).bit_count() % 2) << i)
                    for i, place in enumerate(places)) for s in states}
    least = min(w.bit_count() for w in words.values() if w)
    changes = [s for s in states if words[s].bit_count() == least]
    # Complementary masks agree on every even tuple. Keep the representative
    # without the last family. This gives one mask per distinct linear fact.
    kept = {f for f in range(1 << (m - 1)) if all((f & s).bit_count() % 2 == 0 for s in changes)}
    local = set()
    for parent, children in relations:
        kn = children if parent == full else [parent, *children]
        view = sum(1 << places.index(g) for g in kn)
        # All words and all views are linear. Equality with the zero view
        # suffices by adding the two candidate words.
        same = [s for s in states if not (words[s] & view)]
        local.update(f for f in kept if all((f & s).bit_count() % 2 == 0 for s in same))
    return kept, local, span(local), least


def audit_start(row, counts, examples):
    counts["all roster entries"] += 1
    if "distances" not in row:
        return
    m = row["families"]
    counts["eligible starts"] += 1
    dist = {tuple(map(int, key.split("-"))): val for key, val in row["distances"].items()}
    levels, knots = tree_levels(m, dist)
    interior = len(levels) > 1
    counts["starts with a proper nonsingleton cluster"] += interior
    kept, single, generated, least = literal_local_reads(m, knots)
    sk4 = row["SK4"]
    dim = len(kept).bit_length() - 1
    assert dim == sk4["layer-three dimension"]
    assert least == sk4["least layer-two change"]
    assert len(kept).bit_length() - len(generated).bit_length() == sk4[
        "layer-three facts read by no single second-layer knot (dimension)"]
    counts["starts with any upper fact"] += int(dim > 0)
    counts["starts with at least two independent upper facts"] += int(dim > 1)
    counts["upper facts, counted once per start"] += len(kept) - 1
    counts["upper facts unread by any one knot"] += len(kept - single)
    counts["upper facts outside joint span of local facts"] += len(kept - generated)
    counts["starts with a fact unread by any one knot"] += int(kept != single)
    if kept != single and len(examples) < 4:
        examples.append({"start": row["start"], "number of families": m, "levels": levels,
                         "nonzero facts": sorted(kept - {0}), "read by some one knot": sorted(single - {0})})
    for stage in row["rounds"]:
        if "end" in stage:
            continue
        t = stage["round"]
        penalty = 2 * t + 2
        counts["stages read"] += 1
        counts["pair rows"] += len(dist)
        counts["pair rows allowing a third family"] += len(dist) if m >= 3 else 0
        counts["pair rows that might beat two minimum steps by length alone"] += sum(
            m >= 3 and d + penalty > 2 * (1 + penalty) for d in dist.values())
        counts["recorded direct cost exceptions"] += len(stage["SK1 failures"])
        if "shortest reading: kept sums" not in stage or t == 0:
            continue
        counts["positive-round stages with shortest reading"] += 1
        counts["positive-round stages with a proper nonsingleton cluster"] += interior
        positive = stage["shortest reading: kept sums"] > 0
        counts["positive-round stages keeping any sum"] += positive
        counts["positive-round stages keeping a sum without any proper nonsingleton cluster"] += positive and not interior
        counts["positive-round stages keeping a sum with a proper nonsingleton cluster"] += positive and interior


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot", action="store_true", help="first 12 entries of each roster")
    args = parser.parse_args()
    resource.setrlimit(resource.RLIMIT_AS, (512 << 20, 512 << 20))
    started = perf_counter()
    examples = []
    groups = {}
    total = Counter()
    for name in ("census", "heldout", "sampled", "built"):
        counts = Counter()
        with (SOURCE / f"frozen_{name}.jsonl").open() as file:
            for i, line in enumerate(file):
                if args.pilot and i == 12:
                    break
                audit_start(json.loads(line), counts, examples)
        groups[name] = dict(counts)
        total.update(counts)
    result = {"by roster": groups, "total": dict(total), "single-knot examples": examples,
              "elapsed seconds": round(perf_counter() - started, 5)}
    if args.pilot:
        print(json.dumps(result["total"]), result["elapsed seconds"])
    else:
        (HERE / "diagnostics.json").write_text(json.dumps(result, indent=2) + "\n")
        print(json.dumps(result["total"]), result["elapsed seconds"])


if __name__ == "__main__":
    main()
