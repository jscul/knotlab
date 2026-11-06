#!/usr/bin/env python3
"""Producer for KNOT-LOOPS-20261019-001A-E001: rings of knots, an exact census.

Every knot on three and four Boolean variables (excluded states: a nonempty set
with no two at Hamming distance one), every ordered witness pair, rings of
k = 1..8 (three variables) or 1..6 (four variables), chains of k = 1..4 and
mixed rings of two three-variable placements. Each composite is classified and
its excluded set compared with the transfer-table prediction of contract.json.

Self-contained; the checker uses separate code and knotlab.

    python3 -B run.py    writes raw_rows.jsonl and result.json under artifacts/
"""

from __future__ import annotations

import json
import resource
import time
from itertools import combinations, product
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUT = ROOT / "artifacts" / "KNOT-LOOPS-20261019-001A" / HERE.name
RING_LENGTHS = {3: range(1, 9), 4: range(1, 7)}
CHAIN_LENGTHS = range(1, 5)
MIXED_LENGTHS = (2, 4)

# A transfer is a 4-bit mask: bit 2*a + b is set when (witness in a, witness out b) is allowed.
IDENTITY, SWAP = 0b1001, 0b0110


def compose(s: int, t: int) -> int:
    out = 0
    for a, c in product((0, 1), repeat=2):
        if any(s >> (2 * a + b) & 1 and t >> (2 * b + c) & 1 for b in (0, 1)):
            out |= 1 << (2 * a + c)
    return out


TABLE = [[compose(s, t) for t in range(16)] for s in range(16)]


def closes(mask: int) -> bool:
    return bool(mask & IDENTITY)


def adjacent(p: tuple, q: tuple) -> bool:
    return sum(x != y for x, y in zip(p, q)) == 1


def knots(n: int) -> list[frozenset]:
    """All nonempty independent sets of the n-cube, as excluded-state sets."""
    cube = list(product((0, 1), repeat=n))
    out = []
    for mask in range(1, 1 << len(cube)):
        states = [cube[i] for i in range(len(cube)) if mask >> i & 1]
        if all(not adjacent(p, q) for p, q in combinations(states, 2)):
            out.append(frozenset(states))
    return out


def transfers(excluded: frozenset, n: int, win: int, wout: int) -> dict[tuple, int]:
    middle = [i for i in range(n) if i not in (win, wout)]
    table = {}
    for m in product((0, 1), repeat=len(middle)):
        mask = 0
        for a, b in product((0, 1), repeat=2):
            state = [0] * n
            state[win], state[wout] = a, b
            for i, v in zip(middle, m):
                state[i] = v
            if tuple(state) not in excluded:
                mask |= 1 << (2 * a + b)
        table[m] = mask
    return table


def classify(excluded: set, n_vars: int) -> str:
    if not excluded:
        return "free"
    if len(excluded) == 2 ** n_vars:
        return "contradiction"
    for p in excluded:
        for i in range(n_vars):
            q = p[:i] + (1 - p[i],) + p[i + 1:]
            if q in excluded:
                return "other"
    return "knot" if n_vars >= 3 else "small"


def ring_excluded(tables: list[dict[tuple, int]]) -> set:
    """Excluded middle patterns of a ring, by composing transfers in order."""
    level = {(): IDENTITY}
    for table in tables:
        level = {pattern + (m,): TABLE[mask][t] for pattern, mask in level.items() for m, t in table.items()}
    excluded = set()
    for pattern, mask in level.items():
        if not closes(mask):
            excluded.add(tuple(bit for m in pattern for bit in m))
    return excluded


def ring_excluded_brute(excluded_sets: list[frozenset], n: int, placements: list[tuple[int, int]]) -> set:
    """The same by brute force over witness assignments (short rings only)."""
    k = len(placements)
    sizes = [n - 2] * k
    out = set()
    for pattern in product((0, 1), repeat=sum(sizes)):
        ms = [pattern[i * (n - 2):(i + 1) * (n - 2)] for i in range(k)]
        ok = False
        for w in product((0, 1), repeat=k):
            good = True
            for i, (win, wout) in enumerate(placements):
                state = [0] * n
                state[win], state[wout] = w[i], w[(i + 1) % k]
                for pos, v in zip([j for j in range(n) if j not in (win, wout)], ms[i]):
                    state[pos] = v
                if tuple(state) in excluded_sets[i]:
                    good = False
                    break
            if good:
                ok = True
                break
        if not ok:
            out.add(pattern)
    return out


def predicted(tables: list[dict[tuple, int]], odd: bool = True) -> set:
    out = set()
    for pattern in product(*[list(t) for t in tables]):
        masks = [t[m] for t, m in zip(tables, pattern)]
        if all(mask in (IDENTITY, SWAP) for mask in masks):
            swaps = sum(mask == SWAP for mask in masks)
            if (swaps % 2 == 1) == odd:
                out.add(tuple(bit for m in pattern for bit in m))
    return out


def chain_excluded(excluded: frozenset, n: int, win: int, wout: int, k: int) -> tuple[set, int]:
    """Chain of k copies; variables (w_0, middles..., w_k); internal witnesses forgotten."""
    middle = [i for i in range(n) if i not in (win, wout)]
    n_vars = 2 + k * len(middle)
    out = set()
    for pattern in product((0, 1), repeat=n_vars):
        w0, wk, ms = pattern[0], pattern[1], pattern[2:]
        ok = False
        for inner in product((0, 1), repeat=k - 1):
            w = (w0,) + inner + (wk,)
            if all(_state_allowed(excluded, n, win, wout, middle, w[i], ms[i * len(middle):(i + 1) * len(middle)], w[i + 1])
                   for i in range(k)):
                ok = True
                break
        if not ok:
            out.add(pattern)
    return out, n_vars


def _state_allowed(excluded, n, win, wout, middle, a, m, b) -> bool:
    state = [0] * n
    state[win], state[wout] = a, b
    for pos, v in zip(middle, m):
        state[pos] = v
    return tuple(state) not in excluded


def homology_top(allowed: set, n_vars: int) -> dict[int, int]:
    """Reduced GF(2) Betti numbers of the shape (free sets) of a relation on n_vars variables."""
    faces = []
    for size in range(n_vars + 1):
        for S in combinations(range(n_vars), size):
            if len({tuple(p[i] for i in S) for p in allowed}) == 2 ** size:
                faces.append(S)
    index = {}
    for f in faces:
        index.setdefault(len(f), {})[f] = len(index.get(len(f), {}))

    def rank(rows):
        pivots = {}
        for row in rows:
            r = set(row)
            while r:
                top = max(r)
                if top in pivots:
                    r ^= pivots[top]
                else:
                    pivots[top] = r
                    break
        return len(pivots)

    ranks = {}
    for size, by in index.items():
        if size == 0:
            continue
        ranks[size] = rank([{index[size - 1][tuple(v for v in f if v != x)] for x in f} for f in by])
    betti = {}
    for size, by in index.items():
        b = len(by) - ranks.get(size, 0) - ranks.get(size + 1, 0)
        if b:
            betti[size - 1] = b
    return betti


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    started = time.time()
    rows = []
    summary = {"P1_violations": 0, "P2_mismatches": 0, "brute_vs_composition_mismatches": 0, "rings": 0}
    memory_profile = {}

    for n in (3, 4):
        for excluded in knots(n):
            for win, wout in ((i, j) for i in range(n) for j in range(n) if i != j):
                table = transfers(excluded, n, win, wout)
                record = {"part": "ring", "n": n, "excluded": sorted(excluded), "win": win, "wout": wout,
                          "transfers": {"".join(map(str, m)): t for m, t in table.items()},
                          "all_permutations": all(t in (IDENTITY, SWAP) for t in table.values()),
                          "parity_knot": len(excluded) == 2 ** (n - 1) and len({sum(s) % 2 for s in excluded}) == 1,
                          "by_length": {}}
                for k in RING_LENGTHS[n]:
                    tables = [table] * k
                    ex = ring_excluded(tables)
                    n_vars = k * (n - 2)
                    cls = classify(ex, n_vars)
                    agrees = ex == predicted(tables)
                    entry = {"class": cls, "excluded": len(ex), "agrees_P2": agrees}
                    if k <= 3:
                        brute = ring_excluded_brute([excluded] * k, n, [(win, wout)] * k)
                        entry["brute_agrees"] = brute == ex
                        summary["brute_vs_composition_mismatches"] += brute != ex
                    if n == 3:
                        allowed = set(product((0, 1), repeat=n_vars)) - ex
                        entry["holes"] = {str(d): b for d, b in homology_top(allowed, n_vars).items()}
                    record["by_length"][str(k)] = entry
                    summary["rings"] += 1
                    summary["P1_violations"] += cls in ("other", "contradiction")
                    summary["P2_mismatches"] += not agrees
                constrained = tuple(k for k in RING_LENGTHS[n] if record["by_length"][str(k)]["class"] != "free")
                record["constrained_lengths"] = list(constrained)
                rows.append(record)
                memory_profile.setdefault(n, {}).setdefault(str(list(constrained)), 0)
                memory_profile[n][str(list(constrained))] += 1

    # chains (three-variable placements)
    chain_classes = {}
    for excluded in knots(3):
        for win, wout in ((i, j) for i in range(3) for j in range(3) if i != j):
            entry = {"part": "chain", "excluded": sorted(excluded), "win": win, "wout": wout, "by_length": {}}
            for k in CHAIN_LENGTHS:
                ex, n_vars = chain_excluded(excluded, 3, win, wout, k)
                cls = classify(ex, n_vars)
                entry["by_length"][str(k)] = {"class": cls, "excluded": len(ex)}
                chain_classes[cls] = chain_classes.get(cls, 0) + 1
            rows.append(entry)

    # mixed rings of two three-variable placements
    placements3 = [(e, i, j) for e in knots(3) for i in range(3) for j in range(3) if i != j]
    table3 = {p: transfers(p[0], 3, p[1], p[2]) for p in placements3}
    mixed = {"cases": 0, "P1_violations": 0, "P2_mismatches": 0, "classes": {}}
    for (e1, i1, j1), (e2, i2, j2) in ((p, q) for p in placements3 for q in placements3 if p != q):
        t1, t2 = table3[(e1, i1, j1)], table3[(e2, i2, j2)]
        for k in MIXED_LENGTHS:
            tables = [t1 if i % 2 == 0 else t2 for i in range(k)]
            ex = ring_excluded(tables)
            cls = classify(ex, k)
            mixed["cases"] += 1
            mixed["classes"][cls] = mixed["classes"].get(cls, 0) + 1
            mixed["P1_violations"] += cls in ("other", "contradiction")
            mixed["P2_mismatches"] += ex != predicted(tables)

    # controls
    not_knot = frozenset({(0, 0, 0, 0), (1, 0, 0, 1), (0, 0, 1, 0), (1, 0, 1, 1)})  # swap at m1 = 0, any m2: adjacent excluded
    control_other = classify(ring_excluded([transfers(not_knot, 4, 0, 3)]), 2)
    swap_both = frozenset({(0, 0, 0), (1, 0, 1), (0, 1, 0), (1, 1, 1)})  # swap for every middle value: not a knot
    control_contradiction = classify(ring_excluded([transfers(swap_both, 3, 0, 2)]), 1)
    even_prediction_fails = any(
        ring_excluded([table3[p]] * k) != predicted([table3[p]] * k, odd=False)
        for p in placements3 for k in (1, 3))

    with (OUT / "raw_rows.jsonl").open("w") as handle:
        for row in rows:
            handle.write(json.dumps(row, sort_keys=True) + "\n")

    ring_rows = [r for r in rows if r["part"] == "ring"]
    three = [r for r in ring_rows if r["n"] == 3]
    four = [r for r in ring_rows if r["n"] == 4]

    def split(records, max_k):
        every = sum(1 for r in records if len(r["constrained_lengths"]) == max_k)
        odd_only = sum(1 for r in records if r["constrained_lengths"] and
                       r["constrained_lengths"] == [k for k in range(1, max_k + 1) if k % 2 == 1])
        never = sum(1 for r in records if not r["constrained_lengths"])
        return {"every_length": every, "odd_lengths_only": odd_only, "never": never,
                "other_patterns": len(records) - every - odd_only - never}

    p3_holds = all((len(r["constrained_lengths"]) == len(RING_LENGTHS[r["n"]])) == r["all_permutations"] == r["parity_knot"]
                   for r in ring_rows)
    result = {
        "schema_version": 1,
        "experiment_id": "KNOT-LOOPS-20261019-001A-E001",
        "ticket": "KNOT-LOOPS-20261019-001A",
        "evidence_stage": "exploratory",
        "raw_rows": str((OUT / "raw_rows.jsonl").relative_to(ROOT)),
        "knots": {"three_variables": len(knots(3)), "four_variables": len(knots(4))},
        "placements": {"three_variables": len(three), "four_variables": len(four)},
        "rings_classified": summary["rings"],
        "P1_no_other_or_contradiction": summary["P1_violations"] == 0,
        "P2_excluded_sets_match": summary["P2_mismatches"] == 0,
        "P3_every_length_iff_all_permutations_iff_parity": p3_holds,
        "P4_three_variable_split": split(three, 8),
        "four_variable_split": split(four, 6),
        "memory_profiles": memory_profile,
        "P5_chain_classes": chain_classes,
        "mixed_rings": mixed,
        "brute_vs_composition_mismatches": summary["brute_vs_composition_mismatches"],
        "controls": {"non_knot_link_gives_other": control_other == "other",
                     "contradiction_reachable": control_contradiction == "contradiction",
                     "even_prediction_fails": even_prediction_fails},
        "wall_seconds": round(time.time() - started, 1),
        "peak_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
    }
    p4 = result["P4_three_variable_split"]
    result["status"] = "passed" if (
        result["P1_no_other_or_contradiction"] and result["P2_excluded_sets_match"] and p3_holds
        and (p4["every_length"], p4["odd_lengths_only"], p4["never"], p4["other_patterns"]) == (12, 36, 156, 0)
        and set(chain_classes) <= {"knot", "free"} and mixed["P1_violations"] == 0 and mixed["P2_mismatches"] == 0
        and result["brute_vs_composition_mismatches"] == 0 and all(result["controls"].values())) else "signal_failed"
    (OUT / "result.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({k: result[k] for k in ("status", "P1_no_other_or_contradiction", "P2_excluded_sets_match",
                                              "P3_every_length_iff_all_permutations_iff_parity", "P4_three_variable_split",
                                              "four_variable_split", "P5_chain_classes", "mixed_rings", "controls",
                                              "wall_seconds")}, indent=1))
    return 0 if result["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
