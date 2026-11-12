#!/usr/bin/env python3
"""Referee PARITY-MIX-R1, every kind set: the not-all-equal stitch depends on the kind set that presents a harmony, and the census
used one per harmony. For every kind set of 1 to 3 kinds of span 2 to 8 presenting one of the 8 harmonies with a flip-blind triple
(96 kind sets), on 3 x 3, every placement: flip-blind stitch triples, survival, counts fixed but unreached, full fixing (1 <= k < 9).

    python3 -B ref_presentations.py      (writes result_presentations.json)"""
import json
import math
import sys
import time
from multiprocessing import Pool
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import ref_parity as RP  # noqa: E402
import ref_fb as FB  # noqa: E402

RL = RP.RL


def kind_sets_of(names):
    out = []
    for span in range(2, 9):
        for S in RL.kind_sets(span):
            cyc = RL.window_cycles(S)
            if cyc is None:
                continue
            key = tuple(sorted(set(RL.canon(c) for c in cyc)))
            name = " + ".join("".join(map(str, w)) for w in key)
            if name in names:
                P = 1
                for w in key:
                    P = P * len(w) // math.gcd(P, len(w))
                out.append({"orbits": ["".join(map(str, w)) for w in key], "P": P, "kinds": [list(k) for k in S]})
    return out


def job(h):
    st = RP.setup(h)
    func = RP.census(st)["functional slots"]
    _, both, _ = FB.fb(st["W"], st["P"], st["kinds"])
    surv = fbu = ff = 0
    one = None
    for mask in range(1, 511):
        K = frozenset(c for c in range(9) if (mask >> c) & 1)
        r = RP.analyse(st, 3, 3, K, func)
        if K == frozenset([0]):
            one = r["state"]
        if r["state"]:
            surv += 1
            fbu += r["fixed but unreached"] > 0
            ff += r["full fixing"]
    return {"harmony": st["name"], "kinds": h["kinds"], "flip-blind stitch triples": both, "functional slots": func,
            "one parity knot keeps a state": one, "survivors (1 <= k < 9)": surv, "with a count fixed but unreached": fbu, "full fixing": ff}


def main():
    t0 = time.time()
    census = json.loads((HERE / "result_census.json").read_text())["rows"]
    names = {r["harmony"] for r in census if r["flip-blind triples"]}
    hs = kind_sets_of(names)
    print(len(hs), "kind sets", flush=True)
    rows = []
    with Pool(2) as pool:
        for r in pool.imap_unordered(job, hs):
            rows.append(r)
            print(r["harmony"][:30], r["kinds"], r["flip-blind stitch triples"], r["one parity knot keeps a state"], r["survivors (1 <= k < 9)"],
                  r["with a count fixed but unreached"], r["full fixing"], round(time.time() - t0), "s", flush=True)
            (HERE / "result_presentations.json").write_text(json.dumps(rows, indent=1) + "\n")
    print("done", round(time.time() - t0, 1), "s")


if __name__ == "__main__":
    main()
