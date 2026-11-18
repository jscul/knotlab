"""COUNT-BALLS-20261118-001B-E001: the frozen run.  python3 -B run.py --part <name> writes parts/<name>.json under the
artifact directory; python3 -B run.py --score merges them into results.json and scores the frozen predictions."""
import argparse
import itertools
import json
import math
import sys
import time
from pathlib import Path

import mpmath as mp
import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
ART = ROOT / "artifacts/COUNT-BALLS-20261118-001B/COUNT-BALLS-20261118-001B-E001_outlines"
sys.path.insert(0, str(HERE))
import census as G  # noqa: E402
import chain as C  # noqa: E402
import outline as O  # noqa: E402
import weave as W  # noqa: E402

mp.mp.dps = 40
U_LEVELS = [0.30, 0.27, 0.24, 0.21, 0.19, 0.17, 0.16, 0.15]
TAU_LEVELS = [2.0, 3.0, 4.0, 5.0, 6.0, 7.0]


def weave_rays():
    out = {}
    kmax = {"row (0 deg)": 20, "(4,1) (10.9 deg)": 13, "(5,2) (16.1 deg)": 9, "(1,1) (30 deg)": 35}
    for name, (vec, steps) in W.RAYS.items():
        pts = []
        for k in range(1, kmax[name] + 1):
            target = (vec[0] * k, vec[1] * k)
            c = W.corr(W.walk(steps * k))
            pts.append({"k": k, "target": target, "class": W.cls(target), "r": W.euclid(target), "C": mp.nstr(c, 30)})
        out[name] = pts
    cross = []
    for x in range(1, 60):
        if x % 3:
            c = W.corr(W.walk([W.E] * x))
            cross.append({"target": (x, 0), "class": x % 3, "r": float(x), "C": mp.nstr(c, 30)})
    out["row, other classes"] = cross
    return out


def weave_scan(R=22.0):
    sites = []
    span = int(R * 1.2) + 2
    for a in range(-span, span + 1):
        for b in range(-span, span + 1):
            if (a, b) != (0, 0) and W.euclid((a, b)) <= R:
                sites.append((a, b))
    rows = []
    for t in sites:
        rows.append({"site": t, "class": W.cls(t), "r": W.euclid(t), "C": W.corr_float(W.walk(W.steps_to(*t)))})
    return {"R": R, "sites": rows}


def chain_rays():
    out = {}
    for l in (1, 2, 3):
        t = 3.0 ** -l
        w = (1 - t) / (1 + t)
        Rt, Rd = C.Resolvent(t), C.Resolvent(w)
        A = O.A_of(t)
        rays = {}
        for name, (vec, steps) in C.RAYS.items():
            norm = math.hypot(*vec)
            pts = []
            for k in range(1, int(40 / norm) + 1):
                p = C.path(steps * k)
                a, b = C.corr_reweight(Rt, t, p), C.corr_dual(Rd, p)
                agree = abs(a - b) / abs(b) if b != 0 else float("inf")
                pts.append({"k": k, "r": k * norm, "C_reweight": a, "C_dual": b, "rel_agree": agree})
                if agree > 1e-6:
                    break
            rays[name] = {"vec": vec, "rate_closed_form": O.rate(math.atan2(vec[1], vec[0]), A), "points": pts}
        out[f"l={l}"] = rays
    return out


def chain_scan(R=22.0):
    t = 1 / 3
    Rt = C.Resolvent(t)
    rows = []
    span = int(R) + 1
    for a in range(0, span + 1):
        for b in range(0, a + 1):             # one eighth; the law has the square's eight symmetries
            if (a, b) != (0, 0) and math.hypot(a, b) <= R:
                p = C.path([(1, 0)] * a + [(0, 1)] * b)
                rows.append({"site": (a, b), "C": C.corr_reweight(Rt, t, p)})
    return {"R": R, "l": 1, "sites": rows}


def outline_cf():
    out = {}
    for l in (1, 2, 3, 4, 6, 8, 12):
        t = 3.0 ** -l
        A = O.A_of(t)
        h = lambda th: O.rate(th, A)
        out[f"l={l}"] = {"t": t, "A": A, "axis_per_step_log3": h(0) / math.log(3),
                         "diagonal_per_step_log3": h(math.pi / 4) * math.sqrt(2) / math.log(3),
                         "anisotropy": O.anisotropy(h), "golab_pi": O.golab_pi(h, 8000)}
    return out


def census(nmax_cheap=12, nmax_split=8):
    out = {}
    for pop, nmax in (("cheap", nmax_cheap), ("one-split", nmax_split)):
        t0 = time.time()
        canon, levels = G.reachable(pop, nmax)
        out[pop] = {}
        for n, cl in levels.items():
            out[pop][str(n)] = G.determination(canon, cl, n)
            out[pop][str(n)]["seconds"] = round(time.time() - t0, 1)
            print(pop, n, len(cl), out[pop][str(n)]["seconds"], flush=True)
    return out


def state_side():
    """Descriptive: states within r disagreements of a state on a finite six-regular weave (L = 6) and on a full split box."""
    L = 6
    S = 1 << L
    rowok = {}
    for r in range(S):
        for s in range(S):
            ok = all(not ((r >> i & 1) == (r >> ((i + 1) % L) & 1) == (s >> i & 1)) and
                     not ((r >> ((i + 1) % L) & 1) == (s >> i & 1) == (s >> ((i + 1) % L) & 1)) for i in range(L))
            if ok:
                rowok.setdefault(r, []).append(s)
    states = []
    def extend(rows):
        if len(rows) == L:
            if rows[0] in rowok[rows[-1]]:
                states.append(sum(x << (L * i) for i, x in enumerate(rows)))
            return
        for s in rowok.get(rows[-1], []):
            extend(rows + [s])
    for r in range(S):
        if r in rowok:
            extend([r])
    arr = np.array(states, dtype=np.uint64)
    def pop64(x):
        x = x - ((x >> np.uint64(1)) & np.uint64(0x5555555555555555))
        x = (x & np.uint64(0x3333333333333333)) + ((x >> np.uint64(2)) & np.uint64(0x3333333333333333))
        x = (x + (x >> np.uint64(4))) & np.uint64(0x0F0F0F0F0F0F0F0F)
        return (x * np.uint64(0x0101010101010101)) >> np.uint64(56)
    single = None
    rng = np.random.default_rng(1)
    picks = list(rng.choice(len(arr), 400, replace=False))
    prof = []
    for i in picks:
        d = pop64(arr ^ arr[i]).astype(int)
        prof.append([int(np.sum(d <= r)) for r in range(0, 9)])
    prof.sort(key=lambda p: p[1])
    out = {"weave_L6": {"states": len(states), "profiles_low_high_median": [prof[0], prof[len(prof) // 2], prof[-1]],
                        "flip_counts_range": [prof[0][1] - 1, prof[-1][1] - 1]}}
    for sides in ((7, 7), (4, 4, 4)):
        pts, (st, n) = G.box(sides)
        a = np.array(st, dtype=np.uint64)
        d = pop64(a ^ a[0]).astype(int)          # from the all-0 state
        vals, cnt = np.unique(d, return_counts=True)
        out[f"box{sides}"] = {"states": len(st), "from_all_equal": {int(v): int(c) for v, c in zip(vals, cnt)}}
    return out


PARTS = {"weave_rays": weave_rays, "weave_scan": weave_scan, "chain_rays": chain_rays, "chain_scan": chain_scan,
         "outline_cf": outline_cf, "census": census, "state_side": state_side}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--part")
    ap.add_argument("--score", action="store_true")
    a = ap.parse_args()
    (ART / "parts").mkdir(parents=True, exist_ok=True)
    if a.part:
        t0 = time.time()
        res = PARTS[a.part]()
        json.dump({"part": a.part, "seconds": round(time.time() - t0, 1), "result": res},
                  open(ART / "parts" / f"{a.part}.json", "w"), indent=1, default=str)
        print(a.part, "done", round(time.time() - t0, 1), flush=True)
    if a.score:
        import score
        score.main(ART)


if __name__ == "__main__":
    main()
