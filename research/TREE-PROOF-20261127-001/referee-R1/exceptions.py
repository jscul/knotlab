"""Enumerate actual parity changes on the three original exceptional starts."""
import argparse
from collections import Counter
import json
from pathlib import Path
import resource
from time import perf_counter

from growth_roster import load_starts

HERE = Path(__file__).resolve().parent
TARGETS = {"heldout": {"held out 8-50": (1, 2)},
           "sampled": {"sampled 12-35": (0, 1), "sampled 12-56": (0, 2)}}


def parity_basis(rows, names):
    # Eliminate every other row at the new pivot. One freely chosen distinction
    # then forces the pivot distinctions in precisely the displayed rows.
    equations = rows.copy()
    pivots = []
    for i in range(len(names)):
        where = next((j for j in range(len(pivots), len(rows))
                      if equations[j] & (1 << i)), None)
        if where is None:
            continue
        k = len(pivots)
        equations[k], equations[where] = equations[where], equations[k]
        for j in range(len(equations)):
            if k != j and equations[j] & (1 << i):
                equations[j] ^= equations[k]
        pivots.append(i)
    generators = []
    for free in sorted(set(range(len(names))) - set(pivots)):
        value = 1 << free
        for pivot, row in zip(pivots, equations):
            if row & (1 << free):
                value |= 1 << pivot
        assert all((value & r).bit_count() % 2 == 0 for r in rows)
        generators.append(value)
    return generators


def prepare(start):
    ns = sorted({x for row in start for x in row})
    ix = {x: i for i, x in enumerate(ns)}
    owners = [[k for k, row in enumerate(start) if x in row] for x in ns]
    assert all(len(group) in (1, 2) for group in owners)
    loose = [sum(1 << i for i, owner in enumerate(owners) if owner == [k]) for k in range(len(start))]
    near = [set() for row in start]
    for owner in owners:
        if len(owner) == 2:
            a, b = owner
            near[a].add(b)
            near[b].add(a)
    undiscovered = {k for k, mask in enumerate(loose) if mask}
    families = []
    while undiscovered:
        first = min(undiscovered)
        grouped = {first}
        stack = [first]
        while stack:
            k = stack.pop()
            for j in undiscovered - grouped:
                if near[j] & near[k]:
                    grouped.add(j)
                    stack.append(j)
        families.append(sorted(grouped))
        undiscovered -= grouped
    rows = [sum(1 << ix[x] for x in row) for row in start]
    facts = [sum(loose[i] for i in family) for family in families]
    return ns, rows, families, facts


def enumerate_changes(label, start, pair, pilot):
    names, rows, families, masks = prepare(start)
    generators = parity_basis(rows, names)
    signatures = [sum(((basis & f).bit_count() % 2) << i for i, f in enumerate(masks)) for basis in generators]
    size = 1 << len(generators)
    limit = min(size, 1024) if pilot else size
    costs, ties, supports = {}, Counter(), {}
    loose_counts = {}
    z = signature = 0
    started = perf_counter()
    for i in range(limit):
        if i:
            changed = (i & -i).bit_length() - 1
            z ^= generators[changed]
            signature ^= signatures[changed]
        cost = z.bit_count()
        if cost < costs.get(signature, len(names) + 1):
            costs[signature] = cost
            ties[signature] = 0
            supports[signature] = z
            loose_counts[signature] = Counter()
        if cost == costs[signature]:
            ties[signature] += 1
            loose_counts[signature][tuple((z & f).bit_count() for f in masks)] += 1
    seconds = perf_counter() - started
    if not pilot:
        assert set(costs) == {m for m in range(1 << len(masks)) if m.bit_count() % 2 == 0}
    target = sum(1 << i for i in pair)
    def labelled(mask):
        return [x for i, x in enumerate(names) if mask & (1 << i)]
    return {"start": label, "knots": len(start), "distinctions": len(names),
            "families, by their starting knots": families, "family loose distinctions": list(map(labelled, masks)),
            "changes enumerated": limit, "number of allowed states": size, "elapsed seconds": round(seconds, 6),
            "estimated seconds for all states": round(seconds * size / limit, 5),
            "affected families": pair, "minimum cost by even family mask": costs, "number of minimum supports": ties,
            "affected pair example, distinction names": labelled(supports[target]) if target in costs else None,
            "loose counts by family among its minimum supports":
                [[list(key), multiplicity] for key, multiplicity in loose_counts.get(target, {}).items()]}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot", action="store_true")
    args = parser.parse_args()
    resource.setrlimit(resource.RLIMIT_AS, (512 << 20, 512 << 20))
    evidence = []
    for roster, targets in TARGETS.items():
        for name, supports in load_starts(roster):
            if name in targets:
                evidence.append(enumerate_changes(name, supports, targets[name], args.pilot))
    assert len(evidence) == 3
    if not args.pilot:
        (HERE / "exceptions.json").write_text(json.dumps(evidence, indent=2) + "\n")
    print([(r["start"], r["changes enumerated"], r["number of allowed states"],
            r["elapsed seconds"], r["estimated seconds for all states"]) for r in evidence])
