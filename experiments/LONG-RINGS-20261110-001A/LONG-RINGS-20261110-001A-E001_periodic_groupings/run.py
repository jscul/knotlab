"""LONG-RINGS-20261110-001A-E001: periodic groupings of the square torus's automaton (exploratory; see contract.json).

    .venv/bin/python3 -B run.py    writes artifacts/LONG-RINGS-20261110-001A/LONG-RINGS-20261110-001A-E001_periodic_groupings/run/result.json

A grouping is a re-routing of the n x n square torus (REROUTE-20261109-001B's reroute_lib), the same law-(12, 12) automaton with its
cells grouped into other rings. It is periodic under a sublattice L = <(a, 0), (b, c)> (Hermite normal form, 0 <= b < a) containing
n Z^2 when whether H(p) and V(p) are re-routed depends only on p mod L: 4^(ac) patterns per lattice. Every pattern that is a network is
read for the plain first need of every ring at every target of one fundamental domain (translations by L act on the grouping), and, when
on time, for its rings' homology classes (the total displacement of a ring, in units of n) and its ring graph's balls."""
import collections
import json
import math
import sys
import time
from multiprocessing import Pool
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "proofs/REROUTE-20261109-001B/REROUTE-20261109-001B-P001_rerouting_keeps_persistence"))
import reroute_lib as RR  # noqa: E402

OUT = ROOT / "artifacts" / "LONG-RINGS-20261110-001A" / "LONG-RINGS-20261110-001A-E001_periodic_groupings" / "run"
ROSTER = {24: 8, 16: 8, 12: 6}
BALL_RADIUS = 10


def hnf(k):
    for a in range(1, k + 1):
        if k % a == 0:
            for b in range(a):
                yield a, b, k // a


def compatible(n, a, b, c):
    return n % a == 0 and n % c == 0 and (b * (n // c)) % a == 0


def coset(x, y, a, b, c):
    return ((x - b * (y // c)) % a) * c + y % c


TORI = {}


def torus(n):
    if n not in TORI:
        sig, rot, edges, B = RR.lattice("square", n)
        TORI[n] = (sig, rot)
    return TORI[n]


def homology(n, s, rot):
    pos = {}
    for (x, y), lst in rot.items():
        pos[lst[0]] = (x + 0.5, y)
        pos[lst[1]] = (x, y + 0.5)
    out = []
    for cy in RR.cycles(s):
        tot = [0.0, 0.0]
        for i, d in enumerate(cy):
            p0, p1 = pos[d >> 1], pos[cy[(i + 1) % len(cy)] >> 1]
            for j in range(2):
                tot[j] += (p1[j] - p0[j] + n / 2) % n - n / 2
        out.append((round(tot[0] / n), round(tot[1] / n)))
    return out


def job(args):
    n, a, b, c, lo, hi = args
    sig0, rot = torus(n)
    H = {v: rot[v][0] for v in rot}
    V = {v: rot[v][1] for v in rot}
    cls = {v: coset(v[0], v[1], a, b, c) for v in rot}
    reps = {}
    for v in sorted(rot):
        reps.setdefault(cls[v], v)
    targets = [H[q] for q in reps.values()] + [V[q] for q in reps.values()]
    networks, on_time = 0, []
    for pat in range(lo, hi):
        S = {H[v] for v in rot if pat >> (2 * cls[v]) & 1} | {V[v] for v in rot if pat >> (2 * cls[v] + 1) & 1}
        s = RR.reroute(sig0, S)
        if not RR.is_network(s):
            continue
        networks += 1
        if RR.late_pairs(s, targets=targets):
            continue
        hom = homology(n, s, rot)
        prim = set()
        for h in hom:
            g = math.gcd(abs(h[0]), abs(h[1]))
            prim.add((h[0] // g, h[1] // g) if g else (0, 0))
        classes = {p if p > (0, 0) else (-p[0], -p[1]) for p in prim}
        rs = RR.rings(s)
        balls = RR.ring_graph_balls(s, BALL_RADIUS, roots=[0])[0]
        on_time.append({"lattice": [a, b, c], "pattern": pat, "rings": len(rs), "ring sizes": sorted(set(map(len, rs))),
                        "homology classes": sorted(collections.Counter(hom).items()), "classes up to sign": sorted(classes),
                        "every ring non-contractible": (0, 0) not in prim,
                        "ring balls": balls, "cycle": balls == [min(2 * r + 1, len(rs)) for r in range(BALL_RADIUS + 1)]})
    return n, (a, b, c), hi - lo, networks, on_time


def main():
    t0 = time.time()
    jobs = []
    for n, K in ROSTER.items():
        for k in range(1, K + 1):
            for a, b, c in hnf(k):
                if not compatible(n, a, b, c):
                    continue
                tot = 4 ** k
                step = max(1, tot // 64)
                jobs += [(n, a, b, c, lo, min(tot, lo + step)) for lo in range(0, tot, step)]
    summary = collections.defaultdict(lambda: {"patterns": 0, "networks": 0, "on time": 0})
    on = []
    with Pool(6) as pool:
        for n, lat, npat, nnet, ot in pool.imap_unordered(job, jobs, chunksize=1):
            key = "n = %d, lattice <(%d, 0), (%d, %d)>" % ((n,) + lat)
            summary[key]["patterns"] += npat
            summary[key]["networks"] += nnet
            summary[key]["on time"] += len(ot)
            on += [dict(r, n=n) for r in ot]
    h1 = all(r["every ring non-contractible"] and len(r["classes up to sign"]) == 1 for r in on)
    h2 = all(r["cycle"] for r in on)
    shapes = collections.Counter((r["n"], tuple(r["classes up to sign"][0]) if len(r["classes up to sign"]) == 1 else "mixed", r["rings"]) for r in on)
    result = {"experiment": "LONG-RINGS-20261110-001A-E001",
              "H1 every on-time grouping read is a family of parallel lines: every ring non-contractible, one homology class up to sign": h1,
              "H2 every on-time grouping read has a cyclic ring graph": h2,
              "patterns": sum(v["patterns"] for v in summary.values()), "networks": sum(v["networks"] for v in summary.values()),
              "on time": len(on),
              "on-time groupings by torus, line class and ring count": {"%s" % (k,): v for k, v in sorted(shapes.items(), key=str)},
              "by lattice": dict(sorted(summary.items())), "on-time groupings": on, "seconds": round(time.time() - t0, 1)}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "result.json").write_text(json.dumps(result, indent=1) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k not in ("by lattice", "on-time groupings")}, indent=1))


if __name__ == "__main__":
    main()
