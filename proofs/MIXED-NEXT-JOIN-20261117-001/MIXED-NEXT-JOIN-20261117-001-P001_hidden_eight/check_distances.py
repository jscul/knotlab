"""Measure the two scalar bond distances directly and check one shortest witness per pair."""

import json
import os
import subprocess
import sys
from functools import lru_cache
from itertools import combinations, product
from pathlib import Path

from check_witness import base_model, enumerate_rows

TOOLS = Path(__file__).resolve().parents[3] / "tools"
PAIRS = (("z101", "x101"), ("z101", "y011"))


def canonical_knot(labels, rows, support):
    positions = [labels.index(name) for name in support]
    observed = {tuple((row >> i) & 1 for i in positions) for row in rows}
    missing = set(product((0, 1), repeat=len(support))) - observed
    clauses = [" ".join(("~" if bit else "") + name for name, bit in zip(support, row))
               for row in sorted(missing)]
    cnf = "; ".join(clauses) or f"{support[0]} ~{support[0]}"
    run = subprocess.run(
        [sys.executable, "-B", "-m", "knotlab", "check", "--cnf", cnf, "--loops",
         *support[:-1], "--contact", support[-1], "--json"],
        check=True, capture_output=True, text=True, env={**os.environ, "PYTHONPATH": str(TOOLS)},
    )
    report = json.loads(run.stdout)
    assert set(report["allowed"]) == {"".join(map(str, row)) for row in observed}
    return report["is_knot"]


def main():
    base, marks, cuts = base_model()
    labels, rows, _ = enumerate_rows(base, marks, cuts)
    ordered = sorted(rows)
    columns = {name: sum(1 << j for j, row in enumerate(ordered) if row >> i & 1)
               for i, name in enumerate(labels)}

    @lru_cache(None)
    def fibers(support):
        if not support:
            return ((1 << len(ordered)) - 1,)
        column = columns[support[-1]]
        return tuple(t for f in fibers(support[:-1]) for t in (f & column, f & ~column) if t)

    def full(support):
        return len(fibers(support)) == 1 << len(support)

    out = []
    for pair in PAIRS:
        others = [bit for bit in labels if bit not in pair]
        for size in (3, 4, 5):
            hits = []
            for rest in combinations(others, size - 2):
                support = tuple(sorted((*pair, *rest)))
                if not full(support) and all(full(support[:i] + support[i+1:]) for i in range(size)):
                    hits.append(support)
            if hits:
                assert canonical_knot(labels, rows, hits[0])
                assert not canonical_knot(labels, rows, hits[0][:-1])
                out.append({"pair": pair, "bond_distance": size - 1, "shortest_supports": len(hits),
                            "one_shortest_support": hits[0]})
                break
        else:
            raise AssertionError(f"No witness of size at most five for {pair}")
    assert [r["bond_distance"] for r in out] == [4, 4]

    # A pure-parity assignment can violate the diagonal identity. Fix k001=1,
    # all the other marked bits zero, and enumerate the admissible completions.
    pure_word = 1 << marks.index("z001")
    assert pure_word not in cuts
    pure_names, pure_rows, _ = enumerate_rows(base, marks, (pure_word,))
    mask = sum(1 << pure_names.index(bit) for bit in ("z001", "z111", "z101", "z011"))
    assert all((row & mask).bit_count() % 2 for row in pure_rows)
    return {"minimum_distances": out, "single_mark_pure_control_completions": len(pure_rows)}


if __name__ == "__main__":
    print(json.dumps(main(), indent=2, sort_keys=True))
