"""The frozen census of FAR-BOUND-20261112-001A-E001 (contract.json beside this file): are the bounded bonds of
TRAVEL-READ-20261112-001A-E001 real, and do they stay bounded far away?

Samples: the 66 rank-1 bases of TRAVEL-READ's cross.jsonl (the travelling bases of COMMON-FOLD's census with one travelling
direction found), and for part "rings" the 103 rank-2 bases; frames, strips and targets as in TRAVEL-READ's census (imported).

Tests (all certificates sound):
  - refuted: some pattern has no state on the frame window (along a0 - 12 .. a0 + alpha + 12, across -28 .. 28, twice TRAVEL-READ's);
  - carried: a pattern is carried by a doubly periodic state on a frame-aligned torus (as TRAVEL-READ), or by an eventually periodic
    strip: periodic across with period Q (frame-aligned), and along repeating with period P left of X0 and right of X1, the SAT window
    holding two copies of each tail block constrained equal plus the transient, with P >= the largest along-span of the base's kinds
    (Q from the part's across-extent + 3 to + 10; P from that span to twice it + 2).
  - A candidate S u {x} (S holding the origin cell) is a certified bond when it is refuted and every proper part is carried in every
    pattern; a non-bond when a proper part is refuted; else window-only.
Part "recheck": for every one-cross-section target of TRAVEL-READ (alpha = 10: y = +-2 .. +-6; alpha = 14: y = +-3), b_cert = least
|S| + 1 (|S| <= 5, the same strip) with a certified bond, b_win = least with a bond or window-only. Classes on b_cert, frozen numbers:
"bounded across": b_cert defined at 10 along for some sign at both |y| = 2 and 6, b_cert(10, +-6) - b_cert(10, +-2) <= 1 wherever both
are defined, and every defined b_cert at 10 along with |y| <= 6 at most 5; "growing across": the difference >= 2 in some direction;
"unresolved": anything else (no certified bond within the cap is not counted as unbounded).
Part "far" (bases bounded across after the recheck): targets alpha in {7, 10, 15} and y in +-{7, 11, 13, 14, 15, 19, 20, 23}, the strip
of the target's across-range +- 2 in the one cross-section, |S| <= 5; candidates first the bonds found near the origin, then all sets
by increasing size; b_cert and b_win as above.
Part "rings" (rank-2 bases): the least certified and window-only bonds (|S| <= 4 in the 3 x 3 cells around the origin) to the targets
on the rings max(|m|, |n|) = 10 and 15 of the two travelling directions.

Each base in its own process, written as it finishes, capped (default 1,800 s) and recorded as dropped beyond it.

    .venv/bin/python -B experiments/FAR-BOUND-20261112-001A/FAR-BOUND-20261112-001A-E001_bounded_far/census.py --part control | recheck | far | rings [--workers 6] [--cap 1800]
Output: artifacts/FAR-BOUND-20261112-001A/FAR-BOUND-20261112-001A-E001_bounded_far/.
"""
from __future__ import annotations

import importlib.util
import itertools
import json
import multiprocessing as mp
import os
import sys
import time

from pysat.solvers import Minisat22

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
OUT = os.path.join(ROOT, "artifacts", "FAR-BOUND-20261112-001A", "FAR-BOUND-20261112-001A-E001_bounded_far")
TR = os.path.join(ROOT, "experiments", "TRAVEL-READ-20261112-001A", "TRAVEL-READ-20261112-001A-E001_law_reading", "census.py")
TR_OUT = os.path.join(ROOT, "artifacts", "TRAVEL-READ-20261112-001A", "TRAVEL-READ-20261112-001A-E001_law_reading")
spec = importlib.util.spec_from_file_location("trcensus", TR)
T = importlib.util.module_from_spec(spec)
spec.loader.exec_module(T)
C = T.C
NEAR = [(10, y) for y in (-6, -5, -4, -3, -2, 2, 3, 4, 5, 6)] + [(14, -3), (14, 3)]
FAR = [(a, s * y) for a in (7, 10, 15) for y in (7, 11, 13, 14, 15, 19, 20, 23) for s in (1, -1)]


def along_span(fr):
    return max(max(fr.co(c)[0] for c in k) - min(fr.co(c)[0] for c in k) for k in fr.kinds)


class Eventual:
    """Eventually periodic strips for one frame: periodic across with period Q, tails of period P left of X0 and right of X1."""

    def __init__(self, fr, X0, X1, Q, P):
        self.fr, self.Q = fr, Q
        A0, A1 = X0 - 2 * P, X1 + 2 * P
        cells = [(a, b) for a in range(A0, A1) for b in range(Q)]
        self.idx = {c: i + 1 for i, c in enumerate(cells)}
        cl = []
        for a, b in cells:
            z = fr.cell(a, b)
            for k in fr.kinds:
                pts = [self.rep((z[0] + dx, z[1] + dy)) for dx, dy in k]
                if all(p in self.idx for p in pts):
                    v = [self.idx[p] for p in pts]
                    cl += [v, [-w for w in v]]
        for lo in (X0 - 2 * P, X1):
            for a in range(lo, lo + P):
                for b in range(Q):
                    x, y = self.idx[(a, b)], self.idx[(a + P, b)]
                    cl += [[x, -y], [-x, y]]
        self.s = Minisat22(bootstrap_with=cl)
        self.ok = self.s.solve()

    def rep(self, z):
        a, b = self.fr.co(z)
        return (a, b % self.Q)

    def carries(self, cells, p):
        try:
            lits = [self.idx[self.rep(c)] * (1 if v else -1) for c, v in zip(cells, p)]
        except KeyError:
            return False
        if any(-l in lits for l in lits):
            return False
        return self.s.solve(assumptions=lits)

    def close(self):
        self.s.delete()


class Tester:
    def __init__(self, fr, a0, alpha, ylo, yhi, X0, X1):
        self.fr = fr
        self.win = T.BondTester(fr, a0 - 12, a0 + alpha + 12, -28 + min(0, ylo), 28 + max(0, yhi),
                                [(P, Q) for P in range(alpha + 2, alpha + 8) for Q in range(yhi - ylo + 3, yhi - ylo + 9)])
        s = along_span(fr)
        self.ev = [e for e in (Eventual(fr, X0, X1, Q, P) for Q in range(yhi - ylo + 3, yhi - ylo + 11) for P in range(max(1, s), 2 * s + 3)) if e.ok]

    def carried(self, cells, p):
        for e in self.ev:
            if e.carries(cells, p):
                return True
        for s, rep, idx in self.win.tori:
            imgs = [idx[rep(c)] for c in cells]
            lits = [w * (1 if v else -1) for w, v in zip(imgs, p)]
            if not any(-l in lits for l in lits) and s.solve(assumptions=lits):
                return True
        return False

    def free_cert(self, cells):
        return all(self.carried(cells, (0,) + q) for q in itertools.product((0, 1), repeat=len(cells) - 1))

    def classify(self, S, x):
        w = self.win
        cells = list(S) + [x]
        if not w.constrained(cells):
            return "not constrained"
        parts = [list(S)] + [[c for c in S if c != s] + [x] for s in S]
        if any(w.constrained(P_) for P_ in parts):
            return "non-bond"
        return "bond" if all(self.free_cert(P_) for P_ in parts) else "window-only"

    def close(self):
        self.win.close()
        for e in self.ev:
            e.close()


def least(tester, strip, origin, x, smax, first=()):
    out = {"b_cert": None, "b_win": None}
    tried = set()
    for S in first:
        S = [tuple(c) for c in S]
        if origin not in S or len(S) > smax:
            continue
        tried.add(frozenset(S))
        v = tester.classify(S, x)
        if v == "bond":
            out["b_cert"] = out["b_cert"] or len(S) + 1
        if v in ("bond", "window-only"):
            out["b_win"] = min(out["b_win"] or 99, len(S) + 1)
    others = [c for c in strip if c != origin and c != x]
    for size in range(1, smax + 1):
        if out["b_cert"] is not None and out["b_cert"] <= size:
            break
        for extra in itertools.combinations(others, size - 1):
            S = [origin] + list(extra)
            if frozenset(S) in tried:
                continue
            v = tester.classify(S, x)
            if v == "window-only" and out["b_win"] is None:
                out["b_win"] = size + 1
                out["window-only set"] = [list(c) for c in S]
            if v == "bond":
                out["b_cert"] = size + 1
                out["b_win"] = min(out["b_win"] or 99, size + 1)
                out["set"] = [list(c) for c in S]
                return out
    return out


def profile(sm, targets, first_sets=None):
    kinds, tr = sm["kinds"], sm["travels"]
    tp, g, u = T.frame(tuple(tr["t"]))
    fr = T.Frame(kinds, tp, u)
    a0 = min(fr.co(tuple(c))[0] for c in tr["A"])
    origin = fr.cell(a0, 0)
    res = {}
    for alpha, y in targets:
        lo, hi = min(0, y) - 2, max(0, y) + 2
        tester = Tester(fr, a0, alpha, lo, hi, a0 - 2, a0 + alpha + 3)
        strip = [fr.cell(a0, b) for b in range(lo, hi + 1)]
        res[f"{alpha},{y}"] = least(tester, strip, origin, fr.cell(a0 + alpha, y), 5, first_sets or ())
        tester.close()
    return res


def classify_profile(prof):
    b = {k: v["b_cert"] for k, v in prof.items()}
    diffs, defined_pair = [], False
    for sgn in (1, -1):
        b6, b2 = b.get(f"10,{6 * sgn}"), b.get(f"10,{2 * sgn}")
        if b6 is not None and b2 is not None:
            defined_pair = True
            diffs.append(b6 - b2)
    near = [v for k, v in b.items() if k.startswith("10,") and v is not None]
    if any(d >= 2 for d in diffs):
        return "growing across"
    if defined_pair and all(d <= 1 for d in diffs) and near and max(near) <= 5:
        return "bounded across"
    return "unresolved"


def run_one(part, sm, extra, q):
    if part == "recheck":
        prof = profile(sm, NEAR)
        q.put({"profile": prof, "class": classify_profile(prof)})
    elif part == "far":
        firsts = [v["set"] for v in extra["profile"].values() if v.get("set")]
        firsts = [list(x) for x in {tuple(map(tuple, f)) for f in firsts}]
        q.put({"far": profile(sm, FAR, firsts)})
    else:
        q.put({"rings": rings(sm, extra)})


def rings(sm, dirs_row):
    kinds = sm["kinds"]
    ds = [tuple(d) for d in dirs_row["directions"]]
    pair = next((a, b) for a, b in itertools.combinations(ds, 2) if a[0] * b[1] - a[1] * b[0])
    tp, g, u = T.frame(pair[0])
    fr = T.Frame(kinds, tp, u)
    box = [fr.cell(a, b) for a in (-1, 0, 1) for b in (-1, 0, 1)]
    out = {}
    for R in (10, 15):
        targets = sorted({(m * pair[0][0] + n * pair[1][0], m * pair[0][1] + n * pair[1][1])
                          for m in range(-R, R + 1) for n in range(-R, R + 1) if max(abs(m), abs(n)) == R})
        cos = [fr.co(z) for z in targets]
        A0, A1 = min(a for a, _ in cos), max(a for a, _ in cos)
        B0, B1 = min(b for _, b in cos), max(b for _, b in cos)
        tester = Tester(fr, A0 - 2, A1 - A0 + 4, B0, B1, A0 - 3, A1 + 3)
        rows = []
        for z in targets:
            r_ = least(tester, box, (0, 0), z, 4)
            rows.append({"target": list(z), "b_cert": r_["b_cert"], "b_win": r_["b_win"]})
        tester.close()
        out[R] = rows
    return out


def log(*a):
    msg = " ".join(str(x) for x in a)
    print(msg, flush=True)
    with open(os.path.join(OUT, "log.txt"), "a") as f:
        f.write(msg + "\n")


def control():
    sm = {"sample": "base16", "r": 2, "kinds": C.BASE16, "travels": C.read_base(C.BASE16)["travels"]}
    prof = profile(sm, NEAR)
    b = {k: v["b_cert"] for k, v in prof.items()}
    exp = {f"10,{y}": (y + 1) // 2 + 3 for y in (2, 3, 4, 5, 6)} | {"14,3": 5}
    return {"profile": prof, "b_cert": b, "expected": exp, "class": classify_profile(prof),
            "holds": all(b[k] == v for k, v in exp.items()) and classify_profile(prof) == "growing across"}


def main():
    part = sys.argv[sys.argv.index("--part") + 1]
    workers = int(sys.argv[sys.argv.index("--workers") + 1]) if "--workers" in sys.argv else 6
    cap = int(sys.argv[sys.argv.index("--cap") + 1]) if "--cap" in sys.argv else 1800
    os.makedirs(OUT, exist_ok=True)
    if part == "control":
        res = control()
        json.dump(res, open(os.path.join(OUT, "control.json"), "w"), indent=1)
        log("control", res["class"], res["b_cert"], res["holds"])
        return
    sms = {(x["sample"], x["r"]): x for x in T.samples()}
    extra = {}
    if part == "recheck":
        keys = [(r["sample"], r["r"]) for r in map(json.loads, open(os.path.join(TR_OUT, "cross.jsonl")))]
    elif part == "far":
        rows = [json.loads(l) for l in open(os.path.join(OUT, "recheck.jsonl"))]
        keys = [(r["sample"], r["r"]) for r in rows if r.get("class") == "bounded across"]
        extra = {(r["sample"], r["r"]): r for r in rows}
    else:
        rows = [json.loads(l) for l in open(os.path.join(TR_OUT, "dirs.jsonl"))]
        keys = [(r["sample"], r["r"]) for r in rows if r["rank"] == 2]
        extra = {(r["sample"], r["r"]): r for r in rows}
    path = os.path.join(OUT, f"{part}.jsonl")
    done = set()
    if os.path.exists(path):
        done = {(r["sample"], r["r"]) for r in map(json.loads, open(path))}
    pending = [k for k in keys if k not in done]
    live, t0 = [], time.time()
    log(part, "start", len(pending), "bases")
    while pending or live:
        while pending and len(live) < workers:
            k = pending.pop(0)
            q = mp.Queue()
            p = mp.Process(target=run_one, args=(part, sms[k], extra.get(k), q))
            p.start()
            live.append((k, p, q, time.time()))
        time.sleep(0.5)
        for entry in list(live):
            k, p, q, start = entry
            if not q.empty():
                res = q.get()
                p.join()
                with open(path, "a") as f:
                    f.write(json.dumps({"sample": k[0], "r": k[1], "seconds": round(time.time() - start, 1), **res}) + "\n")
                live.remove(entry)
            elif time.time() - start > cap:
                p.terminate()
                p.join()
                with open(path, "a") as f:
                    f.write(json.dumps({"sample": k[0], "r": k[1], "dropped at the cap": cap}) + "\n")
                live.remove(entry)
                log(part, "dropped", k)
    log(part, "finished", round(time.time() - t0, 1), "s")


if __name__ == "__main__":
    main()
