#!/usr/bin/env python3
"""One size past for PATH-HYBRID-20261108-001 (research-next-steps, "Stress-Test Published Claims"), with a canonical check of the
smallest uniform native path. 16 worker processes, about five minutes.

    .venv/bin/python3 -B research/PATH-HYBRID-20261108-001/stress_test.py   writes stress_test.json
- Canonical check: the smallest native path of ticket A (one rule per ring): knots of its last contact's two-time law at lags L..L+5
  by GROWTH-LAW-20261107-001A's generic enumerator, and knotlab check on the parity of its eventual support.
- Transport of ticket A's construction: shift end rings (170 or 240 each), rule 150 on both middle rings, c1 and c3 reading both
  neighbours on both rings and c2 any one-sided law (one neighbour on each middle ring), with the end rings at 3 to 5 cells and the
  middle rings at 5 to 7, every position with the contacts at least two apart, 3/5/5/3 itself excluded.
- One ring longer: five-ring paths, shift / 150 / 150 / 150 / shift on 3/5/5/5/3 cells, contacts two or three apart, c1 and c4
  reading both neighbours, c2 and c3 any one-sided law.
Every verdict is exact by the row-sequence reduction (NATIVE-PATH-20261108-001A); a row sequence that does not repeat within
200,000 lags is counted as undecided. Each path that is not native records which verdict fails and its contacts' row periods."""
import itertools
import json
import subprocess
import sys
import time
from collections import Counter
from multiprocessing import Pool
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "proofs/NATIVE-PATH-20261108-001A/NATIVE-PATH-20261108-001A-P001_paths_reduce_to_row_sequences"))
sys.path.insert(0, str(ROOT / "proofs/GROWTH-LAW-20261107-001A/GROWTH-LAW-20261107-001A-P001_a_beginning_is_a_knot"))
import path_lib as PL  # noqa: E402
import growth_law_lib as G  # noqa: E402

W = PL.W
CAP = 200000
A_PATHS = ROOT / "artifacts/PATH-HYBRID-20261108-001A/PATH-HYBRID-20261108-001A-E001_broad_sweep/run/paths.json"
BOTH = ("self-blind", 6, 6)
ONE_SIDED = [("self-blind", x, y) for x in (0b1100, 0b1010) for y in (0b1100, 0b1010)]


def verdict(rules, sizes, ks, laws):
    a = PL.analyze(rules, sizes, ks, laws, cap=CAP)
    if a is None:
        return "undecided", None
    if a["all persist"] and a["ends at the last contact"]:
        return "native", a["periods"]
    if not a["all persist"]:
        return "contacts " + "".join("1" if p else "0" for p in a["persists"]) + " persist", a["periods"]
    return "all persist, ends not bound", a["periods"]


def canonical_lag(args):
    rules, sizes, ks, laws, T = args
    nxt, N, blocks = PL.mixed_state_map(rules, sizes, ks, laws)
    masks = [PL.mask(blocks, f"R{i}") for i in range(len(sizes))]
    cur = np.arange(len(nxt), dtype=np.int64)
    for _ in range(T):
        cur = nxt[cur]
    F = ((cur >> (len(sizes) - 2)) & 1).astype(np.uint8)
    R = G.Rel([f"v{j}" for j in range(N)] + ["c"], [u | (int(F[u]) << N) for u in range(1 << N)])
    kn = [S for S in G.knots(R) if S >> N & 1]
    return {"T": T, "knots through the last contact": len(kn), "places": sorted(bin(S).count("1") for S in kn),
            "each meets all four rings": bool(kn) and all(all(S & m for m in masks) for S in kn)}


def knotlab_check(rules, sizes, ks, laws):
    rows, N, blocks = PL.linear_matrix(rules, sizes, ks, laws)
    s, T1, p = W.row_orbit(rows, 1 << (len(sizes) - 2))
    support = [j for j in range(N) if s[-1] >> j & 1]
    masks = [PL.mask(blocks, f"R{i}") for i in range(len(sizes))]
    names = [f"x{j}" for j in support]
    cnf = [" ".join((f"~{n}" if v else n) for n, v in zip(names + ["c"], vals))
           for vals in itertools.product((0, 1), repeat=len(names) + 1) if sum(vals) % 2 == 1]
    env = {"PYTHONPATH": str(ROOT / "tools"), "PATH": "/usr/bin:/bin"}
    kl = json.loads(subprocess.run([sys.executable, "-B", "-m", "knotlab", "check", "--cnf", ";".join(cnf), "--loops", *names, "--contact",
                                    "c", "--json"], capture_output=True, text=True, env=env, cwd=ROOT, check=True).stdout)
    return {"eventual support per ring": [sum(1 for j in support if masks[i] >> j & 1) for i in range(len(sizes))],
            "knotlab check": {k: kl[k] for k in ("is_knot", "binding", "loss_on_erasure", "invisible_in_parts")}}


def transport_job(args):
    e0, e3, m0, m3 = args
    out = []
    for m1 in (5, 6, 7):
        for m2 in (5, 6, 7):
            if (m0, m1, m2, m3) == (3, 5, 5, 3):
                continue
            for k1 in range(2, m1 - 1):
                for k2 in range(2, m2 - 1):
                    for law in ONE_SIDED:
                        v, per = verdict((e0, 150, 150, e3), (m0, m1, m2, m3), [k1, k2], (BOTH, law, BOTH))
                        out.append([[e0, e3], [m0, m1, m2, m3], [k1, k2], list(law), v, per])
    return out


def five_job(args):
    e0, e4, ks = args
    out = []
    for l2, l3 in itertools.product(ONE_SIDED, repeat=2):
        v, per = verdict((e0, 150, 150, 150, e4), (3, 5, 5, 5, 3), list(ks), (BOTH, l2, l3, BOTH))
        out.append([[e0, e4], list(ks), [list(l2), list(l3)], v, per])
    return out


def main():
    t0 = time.time()
    rows = json.loads(A_PATHS.read_text())["rows"]
    nat = sorted([r for r in rows if r[4]], key=lambda r: (sum(r[1]), r[1], r[2], r[0]))
    x = nat[0]
    rules, sizes, ks, laws = tuple(x[0]), tuple(x[1]), x[2], tuple(tuple(l) for l in x[3])
    L = PL.light_cone(sizes, ks)
    with Pool(16) as pool:
        lag_res = pool.map_async(canonical_lag, [(rules, sizes, ks, laws, T) for T in range(L, L + 6)])
        tr = pool.map_async(transport_job, [(e0, e3, m0, m3) for e0 in (170, 240) for e3 in (170, 240) for m0 in (3, 4, 5) for m3 in (3, 4, 5)])
        fv = pool.map_async(five_job, [(e0, e4, k) for e0 in (170, 240) for e4 in (170, 240) for k in itertools.product((2, 3), repeat=3)])
        lags, trans, five = lag_res.get(), [r for chunk in tr.get() for r in chunk], [r for chunk in fv.get() for r in chunk]
    canon = {"path": x[:4], "light cone": L, "generic enumerator": lags, **knotlab_check(rules, sizes, ks, laws)}
    per_count = lambda rs, i: Counter(max(r[i]) if r[i] else None for r in rs)
    out = {
        "canonical check of the smallest uniform native path": canon,
        "transport of the construction": {
            "paths": len(trans), "verdicts": dict(Counter(r[4] for r in trans)),
            "native": [r for r in trans if r[4] == "native"],
            "longest row period among decided paths (count by period, top 12)":
                [[k, v] for k, v in Counter(max(r[5]) for r in trans if r[5]).most_common(12)],
            "share of decided paths with every row period at most 12": round(sum(1 for r in trans if r[5] and max(r[5]) <= 12) /
                                                                         max(1, sum(1 for r in trans if r[5])), 4)},
        "five-ring paths": {"paths": len(five), "verdicts": dict(Counter(r[3] for r in five)),
                            "native": [r for r in five if r[3] == "native"],
                            "longest row period (count by period, top 8)": [[k, v] for k, v in per_count(five, 4).most_common(8)]},
        "seconds": round(time.time() - t0, 1)}
    (HERE / "stress_test.json").write_text(json.dumps(out, indent=1) + "\n")
    show = {"canonical": {k: v for k, v in canon.items() if k != "path"},
            "transport": {k: v for k, v in out["transport of the construction"].items() if k != "native"},
            "transport native": out["transport of the construction"]["native"][:6],
            "five": {k: v for k, v in out["five-ring paths"].items() if k != "native"}, "five native": out["five-ring paths"]["native"][:6],
            "seconds": out["seconds"]}
    print(json.dumps(show, indent=1)[:6000])


if __name__ == "__main__":
    main()
