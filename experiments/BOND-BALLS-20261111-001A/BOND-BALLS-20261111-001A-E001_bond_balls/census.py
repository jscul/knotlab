"""The frozen census of BOND-BALLS-20261111-001A-E001 (contract.json beside this file): bond balls on infinite overlapping bases.

On each of the 134 two-shift periodic knot patterns that PERIODIC-READ-20261111-001A-E001 found read faithfully by NAE (its
census.json), around the origin distinction:
  - the step shells: how many distinctions lie 1, 2, 3, 4 steps away (steps apart: the shortest row of co-knotted pairs, the
    shared-distinction distance; the control, which the two shifts dictate);
  - for every distinction w three steps away: a bond of four containing the origin and w (a shortcut), else a bond of five (bond
    distance 4 = steps + 1), else none, among the distinctions within three steps of both (the lens);
  - for every distinction w four steps away: a bond of four containing the origin and w, among the lens (a shortcut by two).
A bond is a constrained set whose every part with one distinction fewer is free. A candidate counts as constrained when the window of
radius 10 refutes one of its value patterns (settled); its parts' freeness uses PERIODIC-READ's bounds (finite repeats and one-shift
repeats show a pattern extends), with 300 sampled periodic states first. "None in the lens" means no candidate was shown constrained
with settled-free parts: an absence relative to the window, not a proof.

Run from the repository root:
    .venv/bin/python -B experiments/BOND-BALLS-20261111-001A/BOND-BALLS-20261111-001A-E001_bond_balls/census.py
Output: artifacts/BOND-BALLS-20261111-001A/BOND-BALLS-20261111-001A-E001_bond_balls/census.json and census_log.txt.
"""

from __future__ import annotations

import hashlib
import importlib.util
import itertools
import json
import os
import random
import sys
import time
from collections import Counter
from multiprocessing import Pool

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
PR = os.path.join(ROOT, "experiments", "PERIODIC-READ-20261111-001A", "PERIODIC-READ-20261111-001A-E001_periodic_census")
PR_SHA = "8722986805e2b60b639fc2b24215a684bc623a1545c6fc55b5cbea5e684d6765"
PR_OUT = os.path.join(ROOT, "artifacts", "PERIODIC-READ-20261111-001A", "PERIODIC-READ-20261111-001A-E001_periodic_census", "census.json")
OUT = os.path.join(ROOT, "artifacts", "BOND-BALLS-20261111-001A", "BOND-BALLS-20261111-001A-E001_bond_balls")

R, SAMPLES, SEED, WORKERS = 10, 300, 20261121, 8   # window radius 10 holds every distinction within four steps (at most two shifts a step)


def load_pr():
    spec = importlib.util.spec_from_file_location("periodic_census", os.path.join(PR, "census.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


pr = load_pr()


def log(*a):
    msg = " ".join(str(x) for x in a)
    print(msg, flush=True)
    with open(os.path.join(OUT, "census_log.txt"), "a") as f:
        f.write(msg + "\n")


class Sampler:
    """Sampled periodic states (from the first 40 finite repeats with states), for a quick check before the bounds."""

    def __init__(self, rd, seed):
        rng = random.Random(seed)
        self.keys = sorted(rd.widx, key=lambda x: rd.widx[x])
        srcs = [(q[1], q[3], q[4]) for q in rd.quots[:40]]
        rows = []
        for _ in range(SAMPLES if srcs else 0):
            qidx, s, red = srcs[rng.randrange(len(srcs))]
            s.set_phases([(i if rng.random() < 0.5 else -i) for i in range(1, len(qidx) + 1)])
            s.solve()
            m = set(x for x in s.get_model() if x > 0)
            rows.append([1 if (qidx[(v, red(z))] + 1) in m else 0 for v, z in self.keys])
        self.S = np.array(rows, dtype=np.int64).reshape(len(rows), len(self.keys))
        self.col = {x: i for i, x in enumerate(self.keys)}

    def seen(self, S):
        if len(self.S) == 0:
            return set()
        code = np.zeros(len(self.S), dtype=np.int64)
        for i, x in enumerate(S):
            code |= self.S[:, self.col[x]] << i
        return set(np.unique(code).tolist())


def status(rd, smp, S, cache):
    S = tuple(sorted(S))
    if S in cache:
        return cache[S]
    seen = smp.seen(S)
    vals = []
    for p in range(1 << len(S)):
        if p in seen:
            vals.append(True)
            continue
        vals.append(rd.extends(list(S), tuple((p >> i) & 1 for i in range(len(S)))))
        if vals[-1] is False:
            break
    if any(v is False for v in vals):
        res = "constrained"
    elif all(v is True for v in vals) and len(vals) == 1 << len(S):
        res = "free"
    else:
        res = "unsettled"
    cache[S] = res
    return res


def refuted(rd, smp, S, cache):
    """Is some value pattern on S refuted by the window (S constrained, settled)? Patterns seen in a sampled state are skipped."""
    S = tuple(sorted(S))
    key = ("refuted", S)
    if key not in cache:
        seen = smp.seen(S)
        res = False
        for p in range(1 << len(S)):
            if p in seen:
                continue
            bits = tuple((p >> i) & 1 for i in range(len(S)))
            if not rd.ws.solve(assumptions=[(rd.widx[x] + 1) * (1 if b else -1) for x, b in zip(S, bits)]):
                res = True
                break
        cache[key] = res
    return cache[key]


def least_bond(rd, smp, cache, o, w, lens, sizes):
    """The least size in `sizes` of a bond containing o and w with the rest from `lens`: a set the window shows constrained whose
    every part with one distinction fewer is free (settled by PERIODIC-READ's bounds). Returns (size, 'found'), or (None, 'none') when
    no candidate is shown constrained with settled-free parts, (None, 'unsettled') when some candidate's parts are unsettled."""
    unsettled = False
    for k in sizes:
        for extra in itertools.combinations(lens, k - 2):
            S = tuple(sorted((o, w) + extra))
            if not refuted(rd, smp, S, cache):
                continue
            parts = [status(rd, smp, tuple(sorted(set(S) - {u})), cache) for u in S]
            if all(p == "free" for p in parts):
                return k, "found"
            if "unsettled" in parts and "constrained" not in parts:
                unsettled = True
    return None, ("unsettled" if unsettled else "none")


def read_base(item):
    i, knots = item
    P = pr.Pattern(2, 1, [tuple((v, tuple(s)) for v, s in kn) for kn in knots])
    rd = pr.Reader(P, R, pr.F2_LATTICES, window_exact=False, strips=pr.F2_STRIPS)
    smp = Sampler(rd, SEED + i)
    adj, _ = pr.adjacency(P, R)
    o = (0, (0, 0))
    dist = pr.ball(adj, [o], 4)
    shells = [sum(1 for v in dist.values() if v == k) for k in range(5)]
    cache = {}
    rows3, rows4 = Counter(), Counter()
    for w in sorted(x for x, v in dist.items() if v == 3):
        dw = pr.ball(adj, [w], 3)
        lens = sorted(x for x in dist if dist[x] <= 3 and dw.get(x, 99) <= 3 and x not in (o, w))
        k, how = least_bond(rd, smp, cache, o, w, lens, (4, 5))
        rows3[{4: "bond of four (shortcut)", 5: "bond of five"}.get(k, "none in the lens" if how == "none" else "unsettled")] += 1
    for w in sorted(x for x, v in dist.items() if v == 4):
        dw = pr.ball(adj, [w], 3)
        lens = sorted(x for x in dist if dist[x] <= 3 and dw.get(x, 99) <= 3 and x not in (o, w))
        k, how = least_bond(rd, smp, cache, o, w, lens, (4,))
        rows4[{4: "bond of four (shortcut)"}.get(k, "none in the lens" if how == "none" else "unsettled")] += 1
    rd.close()
    return {"index": i, "knots": knots, "step shells": shells, "three steps": dict(rows3), "four steps": dict(rows4),
            "sets read": len(cache)}


def main():
    os.makedirs(OUT, exist_ok=True)
    open(os.path.join(OUT, "census_log.txt"), "w").close()
    t0 = time.time()
    have = hashlib.sha256(open(os.path.join(PR, "census.py"), "rb").read()).hexdigest()
    log("PERIODIC-READ's census hash matches:", have == PR_SHA)
    if have != PR_SHA:
        raise SystemExit("PERIODIC-READ's census changed")
    src = json.load(open(PR_OUT))
    bases = [r for r in src["F2"] if r.get("faithful")]
    log("faithful two-shift bases:", len(bases), Counter(r["max knots per pair"] for r in bases))
    items = [(i, r["knots"]) for i, r in enumerate(bases)]
    with Pool(WORKERS) as pool:
        recs = pool.map(read_base, items, chunksize=1)
    for r, b in zip(recs, bases):
        r["max knots per pair"] = b["max knots per pair"]
    t3, t4 = Counter(), Counter()
    for r in recs:
        t3.update(r["three steps"])
        t4.update(r["four steps"])
    b1_fail = [r["index"] for r in recs if set(r["three steps"]) - {"bond of five"}]
    b1_bad = [r["index"] for r in recs if r["three steps"].get("bond of four (shortcut)") or r["three steps"].get("none in the lens")]
    b2_bad = [r["index"] for r in recs if r["four steps"].get("bond of four (shortcut)")]
    summary = {
        "bases": len(recs),
        "B1": {"three steps": dict(t3), "bases with a settled violation": b1_bad, "bases not all settled bonds of five": b1_fail,
               "holds": not b1_bad, "settled everywhere": not b1_fail},
        "B2": {"four steps": dict(t4), "bases with a shortcut": b2_bad, "holds": not b2_bad},
        "step shells (sum over bases)": [sum(r["step shells"][k] for r in recs) for k in range(5)],
        "step shells by most knots per pair": {m: [sum(r["step shells"][k] for r in recs if r["max knots per pair"] == m) for k in range(5)]
                                               for m in sorted({r["max knots per pair"] for r in recs})}}
    summary["failures"] = [k for k in ("B1", "B2") if not summary[k]["holds"]]
    log("summary:", json.dumps(summary, default=str)[:3000])
    json.dump({"bases": recs, "summary": summary}, open(os.path.join(OUT, "census.json"), "w"), indent=1, default=str)
    log("done", round(time.time() - t0, 1), "s")


if __name__ == "__main__":
    main()
