#!/usr/bin/env python3
"""Referee LINE-LOCK-R1, the converse: in a not-all-equal law, if a periodic state u has a free place i (every knot through i has its
other two members opposite) and the three members of every knot lie at distinct places modulo P, then u and u flipped at i (modulo P)
form a free pair (all 8 triples of S^3 in R), which holds both Latin squares of order 2. So, with the theorem's lemma, R holds a
permutive sub-stitch on one set exactly when some periodic state has a free place. Checked on the laws of ref_line_checks.py's chain test.

    python3 -B ref_line_converse.py      (writes result_converse.json)"""
import itertools
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1] / "BASES-WITHIN-20261112-001" / "referee-R1"))
import ref_lib as RL  # noqa: E402
import ref_line as L  # noqa: E402
import ref_line_checks as C  # noqa: E402


def main():
    tally = {"laws and periods": 0, "free place and permutive pair": 0, "free place, no permutive set": 0,
             "permutive set, no free place": 0, "neither": 0, "free-place flips that are free pairs": 0, "free-place flips tried": 0}
    for span in range(2, 6):
        for S in RL.kind_sets(span, 3):
            kinds = [tuple(k) for k in S]
            for P in range(4, 11):
                if any(a % P == 0 or b % P == 0 or (b - a) % P == 0 for a, b in kinds):
                    continue
                W = [w for w in range(1 << P) if all(len({(w >> (i % P)) & 1, (w >> ((i + a) % P)) & 1, (w >> ((i + b) % P)) & 1}) == 2
                                                     for a, b in kinds for i in range(P))]
                if len(W) < 2 or len(W) > 60:
                    continue
                tally["laws and periods"] += 1
                h = {"P": P, "kinds": kinds, "W": W}
                fs = L.free_site(h)
                free_flips = []
                for w in W:
                    for i in range(P):
                        if all(((w >> ((i + o[0]) % P)) & 1) != ((w >> ((i + o[1]) % P)) & 1)
                               for a, b in kinds for o in ((a, b), (-a, b - a), (-b, a - b))):
                            free_flips.append((w, w ^ (1 << i)))
                for x, y in free_flips:
                    tally["free-place flips tried"] += 1
                    tally["free-place flips that are free pairs"] += all(L.stitch(*t, kinds, P) for t in itertools.product((x, y), repeat=3))
                perm = False
                for x, y in itertools.combinations(W, 2):
                    for sq in C.LATIN2:
                        if all(L.stitch((x, y)[j], (x, y)[k], (x, y)[sq[j][k]], kinds, P) for j in range(2) for k in range(2)):
                            perm = True
                            break
                    if perm:
                        break
                key = {(True, True): "free place and permutive pair", (True, False): "free place, no permutive set",
                       (False, True): "permutive set, no free place", (False, False): "neither"}[(fs is not None, perm)]
                tally[key] += 1
    (HERE / "result_converse.json").write_text(json.dumps(tally, indent=1) + "\n")
    print(json.dumps(tally, indent=1))


if __name__ == "__main__":
    main()
