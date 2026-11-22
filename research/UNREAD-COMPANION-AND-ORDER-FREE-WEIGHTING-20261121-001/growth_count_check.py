"""Count the marked old event before and after a witnessed not-all-equal birth.

The engine replay in the scientific leaf identifies the actual new knot.
This independent transfer uses only its old and fresh names; it also enumerates
every word of the smallest roster explicitly.
"""
from collections import Counter
from fractions import Fraction
import gzip
from itertools import product
import json
from pathlib import Path

import numpy as np


PAIR = tuple(product((0, 1), repeat=2))


def permitted(bits):
    return len(set(bits)) > 1


def four_mark_row(loose=()):
    return np.array([[int(permitted(p + q + loose)) for q in PAIR] for p in PAIR],
                    dtype=object)


def transfer(m):
    # Old holders 0, ..., m+1 form a chain of double meetings. A further
    # spent witness meets each end in two names, closing the sequence below.
    bare = four_mark_row()
    half = np.linalg.matrix_power(bare, m//2)
    equal = np.diag(np.array([1, 0, 0, 1], dtype=object))
    ends = [(s, four_mark_row((s,))) for s in range(2)]
    original = [0, 0]
    grown = [0, 0]
    for (a, left), (b, right) in product(ends, repeat=2):
        ways = sum(permitted((a, b, new)) for new in range(2))
        counts = (int(np.trace(left @ half @ half @ right @ bare)),
                  int(np.trace(left @ half @ equal @ half @ right @ bare)))
        for i in range(2):
            original[i] += counts[i]
            grown[i] += ways * counts[i]
    return tuple(original), tuple(grown)


def direct(m):
    old = [0, 0]
    new = [0, 0]
    for links in product(PAIR, repeat=m+3):
        for a, b in product(range(2), repeat=2):
            rows = [links[i-1] + links[i] for i in range(m+3)]
            rows[0] += (a,)
            rows[m+1] += (b,)
            if not all(map(permitted, rows)):
                continue
            event = links[m//2][0] == links[m//2][1]
            copies = sum(permitted((a, b, fresh)) for fresh in range(2))
            old[0] += 1
            new[0] += copies
            if event:
                old[1] += 1
                new[1] += copies
    return tuple(old), tuple(new)


def archival_marginals():
    root = Path(__file__).resolve().parents[2]
    folder = root / "artifacts" / "ENTANGLEMENT-READ-20261120-001B"
    path, = folder.glob("*/exact_readings.json.gz")
    with gzip.open(path, "rt") as source:
        cases = json.load(source)["sources"]
    changed, totals = Counter(), Counter()
    max_tv = Fraction(0)
    for case in cases:
        for law, stages in case["laws"].items():
            stage = stages[1]
            assert stage["age"] == 1
            for family in ("external_pairs", "six_marks"):
                for slot in stage.get(family, {}).get("slots", []):
                    if "result" not in slot:
                        continue
                    result = slot["result"]
                    names = result["mark_order"]
                    old = [i for i, name in enumerate(names) if name < case["old_distinctions"]]
                    totals[law, family] += 1
                    for weighting in ("U", "L"):
                        data = result["weightings"][weighting]
                        before = data["old_mark_check"]["start_counts"]
                        after = [0] * (1 << len(old))
                        for word, count in enumerate(data["counts"]):
                            key = 0
                            for i in old:
                                key = 2*key + ((word >> (len(names)-1-i)) & 1)
                            after[key] += count
                        assert after == data["old_mark_check"]["grown_counts"]
                        tv = sum(abs(Fraction(a, sum(before)) - Fraction(b, sum(after)))
                                 for a, b in zip(before, after, strict=True)) / 2
                        if tv:
                            changed[law, weighting] += 1
                        max_tv = max(max_tv, tv)
    assert all(totals[law, "external_pairs"] == 126 and totals[law, "six_marks"] == 107
               for law in ("parity", "nae"))
    assert changed == {("nae", "U"): 221} and max_tv == Fraction(434, 2565)
    print("Historic 233 = 126 four-mark + 107 six-mark placements per law across 33 starts.")
    print("Present-uniform changed 221 NAE marginals and 0 parity; inherited changed 0 of either.")


def main():
    assert direct(2) == transfer(2)
    for m in (2, 4, 6):
        (n, count), (n_new, count_new) = transfer(m)
        p, q = Fraction(count, n), Fraction(count_new, n_new)
        assert p != q
        print(f"m={m}: {count}/{n} before; {count_new}/{n_new} after; difference {q-p}.")
    # The direct-meeting control gives two separate unary births. With one
    # old bit each, a lawful ternary has three fresh not-all-equal completions.
    assert all(sum(permitted((a, *t)) for t in PAIR) == 3 for a in range(2))
    print("Two unary births at the controls multiply every old word by nine.")
    archival_marginals()


if __name__ == "__main__":
    main()
