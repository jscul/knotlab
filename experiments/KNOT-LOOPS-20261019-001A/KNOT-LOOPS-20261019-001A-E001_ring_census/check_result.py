#!/usr/bin/env python3
"""Independent check of KNOT-LOOPS-20261019-001A-E001; imports no producer code.

- Enumerates knots again with bitmask code: 34 on three variables and 742 on
  four, the nonempty independent sets of the 3- and 4-cube.
- Recomputes ring composites by brute force over witness assignments (the
  producer composes transfer tables) for every three-variable placement up to
  k = 6 and every four-variable placement up to k = 3, and compares the
  excluded sets with the raw rows.
- Confirms every 'knot' verdict on at most six variables with knotlab's
  check_knot, and the shape of a sample of composites with knotlab's homology.
- Evaluates the frozen predictions as the contract states them (P3 included),
  and, labelled post hoc, the corrected memory statements.
"""

from __future__ import annotations

import json
import sys
from collections import Counter
from itertools import combinations, product
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from knotlab.knots import check_knot  # noqa: E402
from knotlab.relations import Relation  # noqa: E402
from knotlab.space import homology  # noqa: E402

ARTIFACT = ROOT / "artifacts" / "KNOT-LOOPS-20261019-001A" / HERE.name


def knots_by_mask(n: int) -> list[int]:
    size = 1 << n
    neighbours = [sum(1 << (s ^ (1 << b)) for b in range(n)) for s in range(size)]
    out = []
    for mask in range(1, 1 << size):
        if all(not (mask >> s & 1) or not (mask & neighbours[s]) for s in range(size)):
            out.append(mask)
    return out


def state_index(bits: tuple) -> int:
    return sum(b << i for i, b in enumerate(reversed(bits)))


def ring_excluded(mask: int, n: int, win: int, wout: int, k: int) -> set:
    middle = [i for i in range(n) if i not in (win, wout)]
    out = set()
    for pattern in product((0, 1), repeat=k * len(middle)):
        def ok(w):
            for i in range(k):
                state = [0] * n
                state[win], state[wout] = w[i], w[(i + 1) % k]
                for pos, v in zip(middle, pattern[i * len(middle):(i + 1) * len(middle)]):
                    state[pos] = v
                if mask >> state_index(tuple(state)) & 1:
                    return False
            return True
        if not any(ok(w) for w in product((0, 1), repeat=k)):
            out.add(pattern)
    return out


def main() -> int:
    result = json.loads((ARTIFACT / "result.json").read_text())
    rows = [json.loads(line) for line in (ARTIFACT / "raw_rows.jsonl").read_text().splitlines()]
    rings = [r for r in rows if r["part"] == "ring"]
    failures: list[str] = []

    def expect(condition: bool, message: str) -> None:
        if not condition:
            failures.append(message)

    k3, k4 = knots_by_mask(3), knots_by_mask(4)
    expect((len(k3), len(k4)) == (34, 742), f"own knot counts {len(k3)}, {len(k4)}")
    expect(result["knots"] == {"three_variables": 34, "four_variables": 742}, "producer knot counts")
    expect(len([r for r in rings if r["n"] == 3]) == 204 and len([r for r in rings if r["n"] == 4]) == 8904,
           "placement counts")

    # brute-force recomputation and knotlab confirmation
    recomputed = knot_checks = 0
    for r in rings:
        n = r["n"]
        mask = sum(1 << state_index(tuple(s)) for s in r["excluded"])
        for k in range(1, (6 if n == 3 else 3) + 1):
            ex = ring_excluded(mask, n, r["win"], r["wout"], k)
            entry = r["by_length"][str(k)]
            expect(len(ex) == entry["excluded"], f"n={n} {r['excluded']} {r['win']}{r['wout']} k={k}: excluded size")
            recomputed += 1
            n_vars = k * (n - 2)
            if entry["class"] == "knot" and n_vars <= 6:
                names = [f"m{i}" for i in range(n_vars)]
                allowed = frozenset(p for p in product((False, True), repeat=n_vars)
                                    if tuple(int(b) for b in p) not in ex)
                report = check_knot(Relation(tuple(names), allowed), names[:-1], names[-1])
                expect(report.is_knot, f"knotlab rejects knot verdict n={n} k={k}")
                knot_checks += 1
                if knot_checks <= 200:
                    faces = [frozenset(S) for size in range(n_vars + 1) for S in combinations(names, size)
                             if len({tuple(p[names.index(v)] for v in S) for p in allowed}) == 2 ** size]
                    expect(homology(faces) == {n_vars - 2: 1}, f"shape of a knot composite is not a hollow simplex")

    # frozen predictions as stated
    p3_as_frozen = all((len(r["constrained_lengths"]) == (8 if r["n"] == 3 else 6)) == r["all_permutations"]
                       == r["parity_knot"] for r in rings)
    expect(result["P3_every_length_iff_all_permutations_iff_parity"] == p3_as_frozen, "P3 misreported")
    expect(result["status"] == ("passed" if p3_as_frozen and result["P1_no_other_or_contradiction"]
                                and result["P2_excluded_sets_match"] else "signal_failed"), "status misreported")
    expect(result["P1_no_other_or_contradiction"] and result["P2_excluded_sets_match"], "P1 or P2 failed")
    expect(result["P4_three_variable_split"] == {"every_length": 12, "odd_lengths_only": 36, "never": 156,
                                                 "other_patterns": 0}, "P4")
    expect(set(result["P5_chain_classes"]) <= {"knot", "free"}, "P5")
    expect(result["mixed_rings"]["P1_violations"] == 0 and result["mixed_rings"]["P2_mismatches"] == 0, "mixed rings")
    expect(all(result["controls"].values()), "controls")

    # post hoc: corrected memory statements, on the same data
    identity, swap = 9, 6
    post_hoc = Counter()
    for r in rings:
        tables = list(r["transfers"].values())
        s, i = tables.count(swap), tables.count(identity)
        max_k = 8 if r["n"] == 3 else 6
        lengths = r["constrained_lengths"]
        expected = list(range(1, max_k + 1)) if s and i else ([k for k in range(1, max_k + 1) if k % 2] if s else [])
        post_hoc["lengths_match"] += lengths == expected
        post_hoc["counts_match"] += all(e["excluded"] == ((s + i) ** int(k) - (i - s) ** int(k)) // 2
                                        for k, e in r["by_length"].items())
        post_hoc["permutations_iff_parity"] += r["all_permutations"] == r["parity_knot"]
        post_hoc["half_iff_parity"] += all(e["excluded"] * 2 == 2 ** (int(k) * (r["n"] - 2))
                                           for k, e in r["by_length"].items()) == r["parity_knot"]
    expect(all(v == len(rings) for v in post_hoc.values()), f"post hoc statements: {dict(post_hoc)}")

    print(json.dumps({"recomputed_rings": recomputed, "knotlab_knot_confirmations": knot_checks,
                      "P3_as_frozen": p3_as_frozen, "post_hoc": dict(post_hoc), "rings": len(rings)}, indent=1))
    print(f"{'passed' if not failures else 'FAILED'}: the result is reported correctly "
          f"(frozen signal {'held' if p3_as_frozen else 'failed at P3'}; V1 recomputation, no theorem authority)")
    for failure in failures[:20]:
        print("  failed:", failure)
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
