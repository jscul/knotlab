"""The frozen census of TRAVEL-READ-20261112-001A-E001 (contract.json beside this file): what the not-all-equal law reads on the
travelling bases of COMMON-FOLD-20261112-001A-E001.

Samples: every base classed "travels" at r = 3, 4, 5, 6 in that census's main.json (sha256 pinned in the contract), with its kinds
and its certified travelling pattern (A, p, t, sigma). Control: base 16.

Part "dirs" (per base): for each of the census's ten shifts, whether some pattern on 2 to 4 cells of the box [0,1] x [0,2] holding
(0, 0) travels along it, certified as in the census (window SAT forcing; doubly periodic states carrying it; A free). The shifts are
reduced to primitive directions; "rank" is the rank of the travelling directions (1: one direction found, labelled rank >= 1; 2: two
independent). "common": one certified (A, p) travels along two independent shifts (then, by translation and complement symmetry,
p on A forces +-p on A + m t1 + n t2 for all m, n >= 0: bond distance bounded on that cone and its mirror).

Part "cross" (rank-1 bases): in the frame (t', u), t' = t / gcd, det(t', u) = 1, u shortest, a distinction has an along-count and an
across-count; a0 is the least along-count of A. For a target x at along-count a0 + alpha and across-count y: b = least |S| + 1 over S
holding the cell (a0, 0) (the origin when a0 = 0), within along-counts {a0} ("one cross-section", |S| <= 5; targets alpha = 10, y in
+-2 .. +-6, and alpha = 14, y = +-3) or {a0, a0 + 1} ("two cross-sections", |S| <= 4; alpha = 10, y in +-2 .. +-4), across-counts in
[min(0,y)-2, max(0,y)+2], such that S u {x} is a window bond: some pattern refuted in the frame window (along a0-6 .. a0+alpha+6,
across -14 .. 14), no pattern of any proper part refuted there. A window bond is certified ("bond") when every proper part is also
carried in every pattern by a state on a frame-aligned torus (periods P t', Q u, P in alpha+2 .. alpha+7, Q in span+3 .. span+8).
Window refutations are sound; "no refutation in the window" is not a certificate, and doubly periodic states cannot carry every
pattern a travelling set allows (on base 16 they miss two patterns of a heddle part), so a window bond is a bond up to the window.

Part "rings" (rank-2 bases, exploratory): for targets x = m t1' + n t2' on the rings max(|m|, |n|) = 3 and 6 of the first two
independent travelling directions, the least |S| + 1 over S in the 3 x 3 box of frame cells around the origin, |S| <= 4, with S u {x}
a window bond (as above).

Each base is run in its own process, written to <part>.jsonl as it finishes, and stopped at the cap (default 1,200 s), recorded as
dropped. Seeds: none (the samples are the census's).

    .venv/bin/python -B experiments/TRAVEL-READ-20261112-001A/TRAVEL-READ-20261112-001A-E001_law_reading/census.py --part control | dirs | cross | rings [--workers 6] [--cap 1200]
Output: artifacts/TRAVEL-READ-20261112-001A/TRAVEL-READ-20261112-001A-E001_law_reading/.
"""
from __future__ import annotations

import importlib.util
import itertools
import json
import math
import multiprocessing as mp
import os
import sys
import time

from pysat.solvers import Minisat22

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
OUT = os.path.join(ROOT, "artifacts", "TRAVEL-READ-20261112-001A", "TRAVEL-READ-20261112-001A-E001_law_reading")
CF = os.path.join(ROOT, "experiments", "COMMON-FOLD-20261112-001A", "COMMON-FOLD-20261112-001A-E001_periodic_influence", "census.py")
CF_MAIN = os.path.join(ROOT, "artifacts", "COMMON-FOLD-20261112-001A", "COMMON-FOLD-20261112-001A-E001_periodic_influence", "main.json")
spec = importlib.util.spec_from_file_location("cfcensus", CF)
C = importlib.util.module_from_spec(spec)
spec.loader.exec_module(C)
RS = (3, 4, 5, 6)
ALPHAS, YS, SMAX = (8, 12), (-6, -4, -2, 2, 4, 6), 5


def samples():
    rows = json.load(open(CF_MAIN))["rows"]
    out = []
    for row in rows:
        for r in RS:
            rb = row["by r"][str(r)]
            if C.classify(rb) == "travels":
                out.append({"sample": row["sample"], "r": r, "kinds": [tuple(map(tuple, k)) for k in rb["kinds"]], "travels": rb["travels"]})
    return out


def prim(t):
    g = math.gcd(abs(t[0]), abs(t[1]))
    return (t[0] // g, t[1] // g), g


def frame(t):
    tp, g = prim(t)
    best = None
    for c in range(-3, 4):
        for d in range(-3, 4):
            if tp[0] * d - tp[1] * c == 1 and (best is None or c * c + d * d < best[0] ** 2 + best[1] ** 2):
                best = (c, d)
    return tp, g, best


class Frame:
    def __init__(self, kinds, e1, e2):
        self.kinds, self.e1, self.e2 = kinds, e1, e2
        self.det = e1[0] * e2[1] - e1[1] * e2[0]
        assert abs(self.det) == 1

    def cell(self, a, b):
        return (a * self.e1[0] + b * self.e2[0], a * self.e1[1] + b * self.e2[1])

    def co(self, z):
        return ((z[0] * self.e2[1] - z[1] * self.e2[0]) * self.det, (self.e1[0] * z[1] - self.e1[1] * z[0]) * self.det)

    def window(self, A0, A1, B0, B1):
        cells = [self.cell(a, b) for a in range(A0, A1 + 1) for b in range(B0, B1 + 1)]
        idx = {c: i + 1 for i, c in enumerate(cells)}
        cl = []
        for (x, y) in cells:
            for k in self.kinds:
                pts = [(x + a, y + b) for a, b in k]
                if all(p in idx for p in pts):
                    v = [idx[p] for p in pts]
                    cl += [v, [-w for w in v]]
        return idx, cl

    def torus_solver(self, P, Q):
        """States invariant under P e1 and Q e2 (frame-aligned periods)."""
        def rep(z):
            a, b = self.co(z)
            return (a % P, b % Q)
        cells = [(a, b) for a in range(P) for b in range(Q)]
        idx = {c: i + 1 for i, c in enumerate(cells)}
        cl = []
        for a, b in cells:
            z = self.cell(a, b)
            for k in self.kinds:
                v = [idx[rep((z[0] + dx, z[1] + dy))] for dx, dy in k]
                cl += [v, [-w for w in v]]
        s = Minisat22(bootstrap_with=cl)
        return (s, rep, idx) if s.solve() else (s.delete() or None)


class BondTester:
    def __init__(self, fr, A0, A1, B0, B1, tori):
        self.fr = fr
        self.idx, cl = fr.window(A0, A1, B0, B1)
        self.s = Minisat22(bootstrap_with=cl)
        self.tori = [t for t in (fr.torus_solver(P, Q) for P, Q in tori) if t]

    def lit(self, c, v):
        return self.idx[c] * (1 if v else -1)

    def refuted(self, cells, p):
        return not self.s.solve(assumptions=[self.lit(c, v) for c, v in zip(cells, p)])

    def constrained(self, cells):
        n = len(cells)
        return any(self.refuted(cells, (0,) + q) for q in itertools.product((0, 1), repeat=n - 1))

    def free_cert(self, cells):
        for q in itertools.product((0, 1), repeat=len(cells) - 1):
            p = (0,) + q
            ok = False
            for s, rep, idx in self.tori:
                imgs = [idx[rep(c)] for c in cells]
                lits = [w * (1 if v else -1) for w, v in zip(imgs, p)]
                if any(-l in lits for l in lits):
                    continue
                if s.solve(assumptions=lits):
                    ok = True
                    break
            if not ok:
                return False
        return True

    def classify(self, S, x):
        """'not constrained' (no pattern refuted), 'non-bond' (a proper part refuted), else a window bond: every proper part has
        every pattern consistent in the window; 'bond' when every proper part is also certified free by a torus state."""
        cells = list(S) + [x]
        if not self.constrained(cells):
            return "not constrained"
        parts = [list(S)] + [[c for c in S if c != s] + [x] for s in S]
        if any(self.constrained(P_) for P_ in parts):
            return "non-bond"
        return "bond" if all(self.free_cert(P_) for P_ in parts) else "window bond"

    def close(self):
        self.s.delete()
        for s, _, _ in self.tori:
            s.delete()


def travels_cert(kinds, s, idx, A, p, t):
    assum = [idx[c] * (1 if v else -1) for c, v in zip(A, p)]
    if not s.solve(assumptions=assum):
        return None
    for fl in (0, 1):
        if all(not s.solve(assumptions=assum + [idx[(c[0] + t[0], c[1] + t[1])] * (-1 if (v ^ fl) else 1)]) for c, v in zip(A, p)):
            fix = list(zip(A, p)) + [((c[0] + t[0], c[1] + t[1]), v ^ fl) for c, v in zip(A, p)]
            if C.carried(kinds, fix) and all(C.carried(kinds, list(zip(A, (0,) + q))) for q in itertools.product((0, 1), repeat=len(A) - 1)):
                return fl
    return None


def part_dirs(sm):
    kinds = sm["kinds"]
    idx, cl = C.window(kinds, C.WIN)
    s = Minisat22(bootstrap_with=cl)
    found, by_pattern = {}, {}
    for size in range(2, 5):
        for A in itertools.combinations(C.BOX, size):
            if (0, 0) not in A:
                continue
            for tail in itertools.product((0, 1), repeat=size - 1):
                p = (0,) + tail
                for t in C.SHIFTS:
                    if t in found and by_pattern:
                        pass
                    fl = travels_cert(kinds, s, idx, A, p, t)
                    if fl is not None:
                        found.setdefault(t, {"A": [list(c) for c in A], "p": list(p), "sigma": fl})
                        by_pattern.setdefault((A, p), set()).add(t)
    s.delete()
    dirs = sorted({prim(t)[0] for t in found})
    rank = 2 if any(a[0] * b[1] - a[1] * b[0] for a, b in itertools.combinations(dirs, 2)) else (1 if dirs else 0)
    common = any(any(a[0] * b[1] - a[1] * b[0] for a, b in itertools.combinations(sorted({prim(t)[0] for t in ts}), 2))
                 for ts in by_pattern.values())
    return {"shifts": [list(t) for t in sorted(found)], "directions": [list(d) for d in dirs], "rank": rank, "common pattern": common}


def least_bond(bt, strip_cells, origin, x, smax):
    """Least |S| + 1 with S u {x} a window bond (certified or not), S within strip_cells holding origin."""
    others = [c for c in strip_cells if c != origin and c != x]
    for size in range(1, smax + 1):
        for extra in itertools.combinations(others, size - 1):
            S = [origin] + list(extra)
            v = bt.classify(S, x)
            if v in ("bond", "window bond"):
                return {"b": size + 1, "certified": v == "bond", "set": [list(c) for c in S]}
    return {"b": None}


TARGETS1 = [(10, y) for y in (-6, -5, -4, -3, -2, 2, 3, 4, 5, 6)] + [(14, -3), (14, 3)]
TARGETS2 = [(10, y) for y in (-4, -3, -2, 2, 3, 4)]


def cross_profile(kinds, tr):
    tp, g, u = frame(tuple(tr["t"]))
    fr = Frame(kinds, tp, u)
    a0 = min(fr.co(tuple(c))[0] for c in tr["A"])
    res = {"t": tr["t"], "frame": [list(tp), g, list(u)], "one cross-section": {}, "two cross-sections": {}}
    for label, targets, cols, smax in (("one cross-section", TARGETS1, (a0,), 5), ("two cross-sections", TARGETS2, (a0, a0 + 1), 4)):
        for alpha, y in targets:
            lo, hi = min(0, y) - 2, max(0, y) + 2
            tori = [(P, Q) for P in range(alpha + 2, alpha + 8) for Q in range(hi - lo + 3, hi - lo + 9)]
            bt = BondTester(fr, a0 - 6, a0 + alpha + 6, -14, 14, tori)
            strip = [fr.cell(a, b) for a in cols for b in range(lo, hi + 1)]
            res[label][f"{alpha},{y}"] = least_bond(bt, strip, fr.cell(a0, 0) if a0 else (0, 0), fr.cell(a0 + alpha, y), smax)
            bt.close()
    return res


def part_cross(sm):
    return cross_profile(sm["kinds"], sm["travels"])


def part_rings(sm, dirs_row):
    kinds = sm["kinds"]
    ds = [tuple(d) for d in dirs_row["directions"]]
    pair = next((a, b) for a, b in itertools.combinations(ds, 2) if a[0] * b[1] - a[1] * b[0])
    det = pair[0][0] * pair[1][1] - pair[0][1] * pair[1][0]
    tp, g, u = frame(pair[0])
    fr = Frame(kinds, tp, u)
    box = [fr.cell(a, b) for a in (-1, 0, 1) for b in (-1, 0, 1)]
    res = {"directions": [list(pair[0]), list(pair[1])], "lattice index": abs(det), "rings": {}}
    for R in (3, 6):
        targets = sorted({(m * pair[0][0] + n * pair[1][0], m * pair[0][1] + n * pair[1][1])
                          for m in range(-R, R + 1) for n in range(-R, R + 1) if max(abs(m), abs(n)) == R})
        cos = [fr.co(z) for z in targets]
        A0, A1 = min(a for a, _ in cos) - 4, max(a for a, _ in cos) + 4
        B0, B1 = min(b for _, b in cos) - 4, max(b for _, b in cos) + 4
        span_a, span_b = A1 - A0 - 8, B1 - B0 - 8
        tori = [(P, Q) for P in range(span_a + 2, span_a + 6) for Q in range(span_b + 2, span_b + 6)]
        bt = BondTester(fr, A0, A1, B0, B1, tori)
        out = []
        for z in targets:
            r_ = least_bond(bt, box, (0, 0), z, 4)
            out.append({"target": list(z), **r_})
        bt.close()
        res["rings"][R] = out
    return res


def run_one(part, sm, extra, q):
    if part == "dirs":
        q.put(part_dirs(sm))
    elif part == "cross":
        q.put(part_cross(sm))
    else:
        q.put(part_rings(sm, extra))


def log(*a):
    msg = " ".join(str(x) for x in a)
    print(msg, flush=True)
    with open(os.path.join(OUT, "log.txt"), "a") as f:
        f.write(msg + "\n")


def control():
    sm = {"sample": "base16", "r": 2, "kinds": C.BASE16, "travels": C.read_base(C.BASE16)["travels"]}
    d = part_dirs(sm)
    cp = cross_profile(sm["kinds"], sm["travels"])
    one = {k: v["b"] for k, v in cp["one cross-section"].items()}
    two = {k: v["b"] for k, v in cp["two cross-sections"].items()}
    # base 16 (ACROSS-FOLD-20261112-001): one cross-section b = floor((y+1)/2) + 3 for y >= 2 and none for y <= -3; with two,
    # the referee's bonds of 5 reach y = -3 and -4
    exp_one = {f"10,{y}": (y + 1) // 2 + 3 for y in (2, 3, 4, 5, 6)} | {f"10,{y}": None for y in (-3, -4, -5, -6)} | {"14,3": 5, "14,-3": None}
    ok = d["rank"] == 1 and all(one[k] == v for k, v in exp_one.items()) and two["10,-3"] == 5 and two["10,-4"] == 5
    return {"dirs": d, "profile": cp, "expected one cross-section": exp_one, "expected two": {"10,-3": 5, "10,-4": 5}, "holds": ok}


def main():
    part = sys.argv[sys.argv.index("--part") + 1]
    workers = int(sys.argv[sys.argv.index("--workers") + 1]) if "--workers" in sys.argv else 6
    cap = int(sys.argv[sys.argv.index("--cap") + 1]) if "--cap" in sys.argv else 1200
    os.makedirs(OUT, exist_ok=True)
    if part == "control":
        res = control()
        json.dump(res, open(os.path.join(OUT, "control.json"), "w"), indent=1)
        log("control", json.dumps(res))
        return
    sms = samples()
    extra = {}
    if part in ("cross", "rings"):
        dirs = {(r["sample"], r["r"]): r for r in map(json.loads, open(os.path.join(OUT, "dirs.jsonl")))}
        want = 1 if part == "cross" else 2
        sms = [sm for sm in sms if dirs.get((sm["sample"], sm["r"]), {}).get("rank") == want]
        extra = dirs
    path = os.path.join(OUT, f"{part}.jsonl")
    done = set()
    if os.path.exists(path):
        done = {(r["sample"], r["r"]) for r in map(json.loads, open(path))}
    pending = [sm for sm in sms if (sm["sample"], sm["r"]) not in done]
    live, t0 = [], time.time()
    log(part, "start", len(pending), "bases")
    while pending or live:
        while pending and len(live) < workers:
            sm = pending.pop(0)
            q = mp.Queue()
            p = mp.Process(target=run_one, args=(part, sm, extra.get((sm["sample"], sm["r"])), q))
            p.start()
            live.append((sm, p, q, time.time()))
        time.sleep(0.5)
        for entry in list(live):
            sm, p, q, start = entry
            if not q.empty():
                res = q.get()
                p.join()
                with open(path, "a") as f:
                    f.write(json.dumps({"sample": sm["sample"], "r": sm["r"], **res}) + "\n")
                live.remove(entry)
            elif time.time() - start > cap:
                p.terminate()
                p.join()
                with open(path, "a") as f:
                    f.write(json.dumps({"sample": sm["sample"], "r": sm["r"], "dropped at the cap": cap}) + "\n")
                live.remove(entry)
                log(part, "dropped", sm["sample"], sm["r"])
    log(part, "finished", round(time.time() - t0, 1), "s")


if __name__ == "__main__":
    main()
