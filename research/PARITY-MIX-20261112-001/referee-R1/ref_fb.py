#!/usr/bin/env python3
"""Referee PARITY-MIX-R1, flip-blind triples against stitch triples beyond the census: for every kind set of 1 to 3 kinds of span 2 to 9
that is a harmony (every presentation, every period), and for the not-all-equal laws that are not harmonies of LINE-LOCK-R1's chain
test (1 to 3 kinds of span at most 5, periods 4 to 10, all periodic states), count the flip-blind triples (u xor v xor w constant) and
those that are also one-order stitch triples R(u, v, w). FB is symmetric in its three entries, so one slot order suffices.

    python3 -B ref_fb.py      (writes result_fb.json)"""
import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "BASES-WITHIN-20261112-001" / "referee-R1"))
import ref_lib as RL  # noqa: E402


def stitch(u, v, w, kinds, P):
    b = lambda x, i: (x >> (i % P)) & 1
    return all(len({b(u, i), b(v, i + a), b(w, i + bb)}) == 2 for a, bb in kinds for i in range(P))


def fb(W, P, kinds):
    full = (1 << P) - 1
    Ws = set(W)
    n = both = 0
    ex = None
    for u in W:
        for v in W:
            for w in (u ^ v, u ^ v ^ full):
                if w in Ws:
                    n += 1
                    if stitch(u, v, w, kinds, P):
                        both += 1
                        ex = ex or [format(x, f"0{P}b")[::-1] for x in (u, v, w)]
    return n, both, ex


def main():
    rows = []
    for span in range(2, 10):
        for S in RL.kind_sets(span):
            cyc = RL.window_cycles(S)
            if cyc is None:
                continue
            key = tuple(sorted(set(RL.canon(c) for c in cyc)))
            P = 1
            for w in key:
                P = P * len(w) // math.gcd(P, len(w))
            if P > 300:
                continue
            h = {"orbits": ["".join(map(str, w)) for w in key], "P": P}
            W = sorted(sum(b << i for i, b in enumerate(w)) for w in RL.states(h))
            n, both, ex = fb(W, P, [tuple(k) for k in S])
            rows.append({"harmony": " + ".join(h["orbits"]), "P": P, "kinds": [list(k) for k in S], "flip-blind": n, "in the stitch": both, "example": ex})
        print("span", span, len(rows), flush=True)
    harm = {}
    for r in rows:
        harm.setdefault(r["harmony"], []).append(r)
    laws = {"laws and periods": 0, "with a flip-blind triple": 0, "with one in the stitch": 0, "examples": []}
    for span in range(2, 6):
        for S in RL.kind_sets(span, 3):
            kinds = [tuple(k) for k in S]
            for P in range(4, 11):
                W = [w for w in range(1 << P) if all(len({(w >> (i % P)) & 1, (w >> ((i + a) % P)) & 1, (w >> ((i + b) % P)) & 1}) == 2
                                                     for a, b in kinds for i in range(P))]
                if len(W) < 2 or len(W) > 200:
                    continue
                n, both, ex = fb(W, P, kinds)
                laws["laws and periods"] += 1
                laws["with a flip-blind triple"] += n > 0
                laws["with one in the stitch"] += both > 0
                if both and len(laws["examples"]) < 5:
                    laws["examples"].append({"kinds": kinds, "P": P, "triple": ex, "periodic states": len(W)})
    summ = {"presentations (kind sets that are harmonies, span 2 to 9, period at most 300)": len(rows), "harmonies": len(harm),
            "harmonies with a flip-blind triple": sum(1 for v in harm.values() if v[0]["flip-blind"]),
            "presentations with a flip-blind stitch triple": sum(1 for r in rows if r["in the stitch"]),
            "laws that are not harmonies": laws}
    (HERE / "result_fb.json").write_text(json.dumps({"summary": summ, "rows": rows}, indent=1) + "\n")
    print(json.dumps(summ, indent=1))


if __name__ == "__main__":
    main()
