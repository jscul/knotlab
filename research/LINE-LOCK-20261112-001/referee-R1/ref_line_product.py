#!/usr/bin/env python3
"""Referee LINE-LOCK-R1, the product lemma (the referee's sharpening of the proof's first two steps): in any not-all-equal stitch, lagged
or not, a Latin square S1 x S2 -> S3 inside R puts the whole product S1 x S2 x S3 inside R. (At every kind and place at most one of the
three role fibres varies and the other two are constant and opposite, or all three are constant and not all equal; either way every
triple of the product satisfies that knot.) So a not-all-equal stitch never holds a permutive law exactly; it holds one only inside a free
product. Checked here: (1) every Latin 2-set triple of the 64 harmonies with at most 64 states (any three ranges), (2) every permutive set
of order 2 and 3 on one set, and every order-2 Latin 2-set triple with three ranges, in the not-all-equal laws that are not harmonies
of the chain test (1 to 3 kinds of span at most 5, periods 4 to 10, at most 30 states for the three-range part).

    python3 -B ref_line_product.py      (writes result_product.json)"""
import itertools
import json
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1] / "BASES-WITHIN-20261112-001" / "referee-R1"))
import ref_lib as RL  # noqa: E402
import ref_line as L  # noqa: E402
import ref_line_checks as C  # noqa: E402
import ref_line_ranges as G  # noqa: E402
import ref_line_sites as St  # noqa: E402


def main():
    out = {}
    hist = Counter()
    for h in L.span8_harmonies() + [L.odd_harmony(n, S) for n, S in L.ODD_SETS]:
        if len(h["W"]) > 64:
            continue
        T = St.latin_triples(G.relation(h))
        hist.update(held for lst in T.values() for _, _, held in lst)
    out["harmonies: Latin 2-set triples by triples held (of 8)"] = dict(hist)
    one, three = Counter(), Counter()
    for span in range(2, 6):
        for S in RL.kind_sets(span, 3):
            kinds = [tuple(k) for k in S]
            for P in range(4, 11):
                W = [w for w in range(1 << P) if all(len({(w >> (i % P)) & 1, (w >> ((i + a) % P)) & 1, (w >> ((i + b) % P)) & 1}) == 2
                                                     for a, b in kinds for i in range(P))]
                if len(W) < 2 or len(W) > 60:
                    continue
                h = {"P": P, "kinds": kinds, "W": W, "name": "law"}
                ok = G.relation(h)
                n = len(W)
                for m, squares in ((2, C.LATIN2), (3, C.LATIN3)):
                    for Sset in itertools.combinations(range(n), m):
                        if any(all(ok[Sset[i], Sset[j], Sset[sq[i][j]]] for i in range(m) for j in range(m)) for sq in squares):
                            one[f"order {m}: {int(sum(ok[x, y, z] for x in Sset for y in Sset for z in Sset))} of {m ** 3}"] += 1
                if n <= 30:
                    T = St.latin_triples(ok)
                    three.update(f"{held} of 8" for lst in T.values() for _, _, held in lst)
    out["laws that are not harmonies: permutive sets on one set, by triples held"] = dict(one)
    out["laws that are not harmonies: Latin 2-set triples with three ranges, by triples held"] = dict(three)
    (HERE / "result_product.json").write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
