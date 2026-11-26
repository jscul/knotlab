"""Targeted joins of two rings on at most eight knots, with two move readings."""

import argparse
import json
import resource
from collections import Counter, deque
from itertools import combinations_with_replacement, product
from pathlib import Path
from time import perf_counter

from counterexample import (
    advance, check_stage, class_record, columns_of, construct, indices, kernel,
    mask, pivots, renumbered, ring_meetings, small_changes, through_each,
)


def constructions():
    # Try unequal funding where the two rings meet. The order gives the
    # double-meeting analogue first, with the ninth holder removed.
    for n_a, n_b in [(4, 4), (3, 4)]:
        rings = ring_meetings(n_a, 0) + ring_meetings(n_b, n_a)
        for multiplicity in (2, 1):
            for a, b in combinations_with_replacement((0, 1, 2, 3), 2):
                for ordinary in (2, 1):
                    loose = [ordinary] * (n_a + n_b)
                    loose[0], loose[n_a] = a, b
                    edges = rings + [(0, n_a)] * multiplicity
                    yield (f"{n_a}+{n_b} rings with {multiplicity} shared between their meeting knots, "
                           f"loose {a} and {b} there and {ordinary} elsewhere",
                           construct(n_a + n_b, edges, loose), n_a, n_b)
        # Two separate meetings between the rings, with possible repeated
        # sharing at each. Mirrored specifications are kept as the same case.
        for ha, hb in product((1, 2), repeat=2):
            if n_a == 3 and ha == 2:
                continue
            for multiplicity, joining, ordinary in product((1, 2), (0, 1, 2, 3), (1, 2)):
                loose = [ordinary] * (n_a + n_b)
                for k in (0, n_a, ha, n_a + hb):
                    loose[k] = joining
                edges = rings + [(0, n_a), (ha, n_a + hb)] * multiplicity
                yield (f"{n_a}+{n_b} rings meeting twice at positions {ha}/{hb}, {multiplicity} shared "
                       f"at each pair, {joining} loose at the meeting knots and {ordinary} elsewhere",
                       construct(n_a + n_b, edges, loose), n_a, n_b)

    # Identify one holder of one four-knot ring with one holder of the
    # other, optionally keeping the ninth holder from the known example.
    ring_edges = ring_meetings(4, 0) + ring_meetings(4, 4)
    for extra in (True, False):
        options = list(combinations_with_replacement(range(3), 2)) if extra else [(0, 0)]
        for a, b in options:
            for merged, ordinary in product((0, 1, 2, 3, 4), (1, 2)):
                def rename(h):
                    if h == 4 + b:
                        return a
                    return h if h < 4 + b else h - 1

                pairs = ring_edges + ([(0, 8)] * 2 + [(4, 8)] * 2 if extra else [])
                size = 8 if extra else 7
                loose = [ordinary] * size
                loose[a] = merged
                if extra:
                    loose[-1] = 0
                desc = ("the separate double-meeting knot retained" if extra else "no further knot")
                yield (f"two four-knot rings sharing positions {a}/{b}, {merged} loose there and "
                       f"{ordinary} on the other ring knots, {desc}",
                       construct(size, [(rename(x), rename(y)) for x, y in pairs], loose), 4, 4)

    # Shorten a ring of the double-meeting example by one knot.
    rings = ring_meetings(3, 0) + ring_meetings(4, 3)
    for ma, mb in product((1, 2), (1, 2)):
        for middle, other in product((0, 1, 2, 3), (1, 2)):
            if ma + mb + middle < 3:
                continue
            edges = rings + [(0, 7)] * ma + [(3, 7)] * mb
            yield (f"three- and four-knot rings joined through one knot, {ma}/{mb} shared with it, "
                   f"{middle} loose there and {other} at each ring knot",
                   construct(8, edges, [other] * 7 + [middle]), 3, 4)


def all_shortest(stage, small):
    columns = columns_of(stage)
    efficient, covered = through_each(small)
    edges = []
    loose_end = len(stage)
    adjacent = [[] for _ in range(loose_end + 1)]
    for d, column in enumerate(columns):
        ends = list(indices(column))
        if len(ends) == 1:
            ends.append(loose_end)
        a, b = ends
        edges.append((a, b))
        adjacent[a].append((b, d))
        adjacent[b].append((a, d))
    exact = set(efficient)
    for d, (a, b) in enumerate(edges):
        if (covered >> d) & 1:
            continue
        pending = deque([a])
        distances = {a: 0}
        parents = {a: []}
        while pending:
            u = pending.popleft()
            if b in distances and distances[u] >= distances[b]:
                continue
            for v, x in adjacent[u]:
                if x == d:
                    continue
                new_length = distances[u] + 1
                if v not in distances:
                    distances[v] = new_length
                    parents[v] = []
                    pending.append(v)
                if distances[v] == new_length:
                    parents[v].append((u, x))
        if b in parents:
            todo = [(b, 1 << d)]
            while todo:
                u, path = todo.pop()
                if u == a:
                    exact.add(path)
                else:
                    todo.extend((v, path | (1 << x)) for v, x in parents[u])
    return exact


def shared_generators(stage, min_bits=2):
    columns = columns_of(stage)
    rows = [mask(k) for k in stage]
    allowed = len(columns) - len(pivots(rows))
    small = small_changes(columns)
    small_rank = len(pivots(small))
    if allowed - small_rank < min_bits:
        return None
    five = class_record(stage, rows, allowed, small, [])
    if five["whole_held_modulo_single_knot_span"] < min_bits:
        return None
    short = all_shortest(stage, small)
    tight = class_record(stage, rows, allowed, short, [])
    if tight["whole_held_modulo_single_knot_span"] < min_bits:
        return None
    # The same pair must survive both readings, modulo the combination of
    # single-knot class reads admitted under either move choice.
    local_labels = []
    for moves in (short, small):
        for knot in stage:
            positions = sorted(knot)
            projections = (sum(((m >> x) & 1) << j for j, x in enumerate(positions)) for m in moves)
            for local in kernel(projections, len(positions)):
                local_labels.append(mask(positions[i] for i in indices(local)))
    combined = list(set(small).union(short))
    basis = pivots(rows + local_labels)
    labels = []
    for word in kernel(combined, len(columns)):
        tentative = pivots([*basis.values(), word])
        if len(tentative) > len(basis):
            basis = tentative
            labels.append(word)
    if len(labels) < min_bits:
        return None
    return {"shortest": tight, "up_to_five": five, "shared_independent_labels": labels}


def search(pilot):
    family = list(constructions())
    used = family[:2] if pilot else family
    totals = Counter()
    within18 = Counter()
    candidates = []
    for description, source, n_a, n_b in used:
        if any(len(row) < 3 for row in source):
            raise ValueError(description)
        stage = source
        profile = []
        counters = [totals] + ([within18] if len(columns_of(source)) <= 18 else [])
        for counts in counters:
            counts["prepared_starts"] += 1
        for t in range(1, 4):
            stage, status, _ = advance(stage)
            for counts in counters:
                counts[f"round_{t}_{status}"] += 1
            if status != "funded":
                break
            result = shared_generators(stage)
            if result is None:
                continue
            labels = result.pop("shared_independent_labels")
            old_rings = [mask(range(n_a)), mask(range(n_a, n_a + n_b))]
            named = old_rings
            try:
                checked = check_stage(stage, named)
            except ValueError:
                # Some mobile distinctions require more than five changes.
                # all_shortest above exhausts their ties.
                checked = None
            result["round"] = t
            result["knots"] = len(stage)
            result["distinctions"] = len(columns_of(stage))
            result["independent_under_both_modulo_both_single_knot_spans"] = [list(indices(l)) for l in labels]
            result["named_old_ring_parities"] = [list(indices(l)) for l in old_rings]
            result["old_ring_certificates"] = checked
            profile.append(result)
            for counts in counters:
                counts[f"round_{t}_same_pair_under_both"] += 1
        if profile:
            candidates.append({"construction": description, "source": renumbered(source), "stages": profile})
    return {
        "weighting": "One entry per specified placement of meetings and supply of loose distinctions. "
                     "The list is targeted and includes isomorphic parameter settings.",
        "all_specifications": len(family), "run": len(used), "through_round": 3,
        "counts": dict(sorted(totals.items())), "source_distinctions_at_most_18": dict(sorted(within18.items())),
        "candidates": candidates,
    }


if __name__ == "__main__":
    cap = 2 * 1024**3
    resource.setrlimit(resource.RLIMIT_AS, (cap, cap))
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot", action="store_true")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    start = perf_counter()
    summary = search(args.pilot)
    summary["seconds"] = round(perf_counter() - start, 6)
    summary["peak_resident_KiB"] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    args.output.write_text(json.dumps(summary, indent=1) + "\n")
    print(json.dumps({k: summary[k] for k in ("run", "counts", "seconds", "peak_resident_KiB")}))
