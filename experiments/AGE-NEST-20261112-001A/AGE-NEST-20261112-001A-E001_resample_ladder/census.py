"""The frozen census of AGE-NEST-20261112-001A-E001 (contract.json beside this file): which structure beyond degrees carries the end
of growth with closings anywhere?

Endings: OLD-CORE-20261112-001A-E001's X(0.25), X(0.3) and X(0.35) endings, regenerated exactly from its seeds (its census.py and
fates.py imported by path, hashes pinned), except the pilot's endings (X(0.3) runs 0, 1, 4, 10, 11, 12; X(0.35) runs 0 to 5). For
each, the dying core C (the knots among the oldest k* distinctions) and 20 resamples on each rung, all with k* distinctions and |C|
knots, simple (no knot twice):
  SW   degrees kept: a switch chain (pick two knots and one member of each uniformly; swap them if both results are new simple
       knots; a rejected proposal counts as a step), 20|C| steps from C. Symmetric, so uniform on its component.
  R2   degrees and each knot's youngest distinction kept: the same chain, members chosen among the two older ones, a swap allowed
       only if each moved distinction stays older than its new knot's youngest; so every count of knots among the oldest j
       distinctions is kept. Symmetric, so uniform on its component.
  R2p  each knot's youngest distinction kept, the other two redrawn uniformly among older distinctions (knots redrawn in time order,
       simple).
  FULL the core redrawn under the growth's own rule in time order: a birth knot keeps its new distinction and redraws its pair
       among older ones; a closing redraws three among the core's distinctions that existed at its time.
For each rung: the share of resamples allowing no state, and the share identical in pair counts to C (forced by the pair-count
lemma). Control Q0: where C contains a Pasch configuration, apply one trade (its four knots replaced by the complementary four) and
check that no state is allowed (the pair-count lemma). Fairness: for each degree sequence in FAIR_SEQS, every simple pattern with it is
enumerated and the exact transition matrices of SW and R2 (R2 with the vertex order as age) are checked for symmetry and connectivity.

Run from the repository root:
    .venv/bin/python -B experiments/AGE-NEST-20261112-001A/AGE-NEST-20261112-001A-E001_resample_ladder/census.py [--workers 8]
    .venv/bin/python -B experiments/AGE-NEST-20261112-001A/AGE-NEST-20261112-001A-E001_resample_ladder/census.py --summary
Output: artifacts/AGE-NEST-20261112-001A/AGE-NEST-20261112-001A-E001_resample_ladder/{runs.jsonl, fairness.json, summary.json}.
"""

from __future__ import annotations

import hashlib
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
import importlib.util  # noqa: E402
_spec = importlib.util.spec_from_file_location(
    "old_core_census", os.path.join(ROOT, "experiments", "OLD-CORE-20261112-001A", "OLD-CORE-20261112-001A-E001_old_core", "census.py"))
OC = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(OC)
F = OC.F

OUT = os.path.join(ROOT, "artifacts", "AGE-NEST-20261112-001A", "AGE-NEST-20261112-001A-E001_resample_ladder")
OC_RUNS = os.path.join(ROOT, "artifacts", "OLD-CORE-20261112-001A", "OLD-CORE-20261112-001A-E001_old_core", "runs.jsonl")
LABELS = ("X0.25", "X0.3", "X0.35")
PILOT = {("X0.3", r) for r in (0, 1, 4, 10, 11, 12)} | {("X0.35", r) for r in range(6)}
R = 20
STEPS_PER_KNOT = 20
FAIR_SEQS = [[3, 3, 3, 3, 3, 3], [4, 3, 3, 2, 2, 1], [5, 4, 3, 2, 2, 1, 1], [6, 3, 3, 2, 2, 1, 1], [4, 4, 3, 3, 2, 2, 2, 1]]


def seed_of(*parts):
    return int(hashlib.sha256(":".join(map(str, parts)).encode()).hexdigest()[:12], 16)


def pair_counts(K):
    c = Counter()
    for t in K:
        for p in itertools.combinations(t, 2):
            c[p] += 1
    return c


def chain(core, steps, rng, keep_youngest):
    E = [tuple(sorted(t)) for t in core]
    S = set(E)
    m = len(E)
    for _ in range(steps):
        i, j = rng.randrange(m), rng.randrange(m)
        if i == j:
            continue
        a, b = E[i], E[j]
        if keep_youngest:
            u, v = rng.choice(a[:2]), rng.choice(b[:2])
            if v >= a[2] or u >= b[2]:
                continue
        else:
            u, v = rng.choice(a), rng.choice(b)
        if u in b or v in a:
            continue
        na = tuple(sorted([x for x in a if x != u] + [v]))
        nb = tuple(sorted([x for x in b if x != v] + [u]))
        if na in S or nb in S:
            continue
        S.discard(a)
        S.discard(b)
        S.add(na)
        S.add(nb)
        E[i], E[j] = na, nb
    return E


def redraw_youngest(core, rng):
    out = set()
    for t in sorted(core, key=lambda t: t[2]):
        y = t[2]
        for _ in range(1000):
            a, b = rng.sample(range(y), 2)
            nt = tuple(sorted((a, b, y)))
            if nt not in out:
                break
        out.add(nt)
    return list(out)


def redraw_full(K, ks, rng):
    seen = set()
    sched = []
    for t in K:
        new = [v for v in t if v not in seen]
        seen |= set(t)
        if t[2] < ks:
            sched.append(("birth", t[2]) if new else ("closing", max(seen) + 1))
    out = set()
    for kind, x in sched:
        for _ in range(1000):
            if kind == "birth":
                if x < 2:
                    nt = (0, 1, 2)
                else:
                    a, b = rng.sample(range(x), 2)
                    nt = tuple(sorted((a, b, x)))
            else:
                nt = tuple(sorted(rng.sample(range(min(ks, x)), 3)))
            if nt not in out:
                break
        out.add(nt)
    return list(out)


def find_pasch(core):
    S = set(core)
    byv = {}
    for t in core:
        for v in t:
            byv.setdefault(v, []).append(t)
    for t in core:
        a, b, c = t
        for t2 in byv.get(a, []):
            if len(set(t2) & set(t)) != 1:
                continue
            y, z = [w for w in t2 if w != a]
            for yy, zz in ((y, z), (z, y)):
                for t3 in byv.get(b, []):
                    if zz in t3 and len(set(t3) & set(t)) == 1 and a not in t3:
                        x = [w for w in t3 if w not in (b, zz)][0]
                        if x in (a, c, yy):
                            continue
                        t4 = tuple(sorted((x, yy, c)))
                        if t4 in S:
                            old = [t, t2, t3, t4]
                            new = [tuple(sorted(q)) for q in ((x, yy, zz), (x, b, c), (a, yy, c), (a, b, zz))]
                            if len(set(new)) == 4 and not (set(new) & (S - set(old))):
                                return old, new
    return None


def task(spec):
    label, run, ks = spec
    t0 = time.time()
    rng = random.Random(OC.seed_of("OC", label, run))
    knots, dead = F.grow(OC.make_gen(label, rng), dict(OC.SETTINGS)[label])
    K = [tuple(sorted(t)) for t in knots]
    core = [t for t in K if t[2] < ks]
    pc = pair_counts(core)
    rr = random.Random(seed_of("AN", label, run))
    rec = {"label": label, "run": run, "kstar": ks, "m": len(core), "core_unsat": not OC.sat(core)}
    for name, fn in (("SW", lambda: chain(core, STEPS_PER_KNOT * len(core), rr, False)),
                     ("R2", lambda: chain(core, STEPS_PER_KNOT * len(core), rr, True)),
                     ("R2p", lambda: redraw_youngest(core, rr)),
                     ("FULL", lambda: redraw_full(K, ks, rr))):
        ends = same = 0
        for _ in range(R):
            Q = fn()
            ends += not OC.sat(Q)
            same += pair_counts(Q) == pc
        rec[f"P_{name}"] = ends / R
        rec[f"same_{name}"] = same / R
    tr = find_pasch(core)
    if tr:
        old, new = tr
        Q = [t for t in core if t not in old] + new
        rec["pasch_trade_unsat"] = not OC.sat(Q)
        rec["pasch_trade_same_pairs"] = pair_counts(Q) == pc
    rec["seconds"] = round(time.time() - t0, 1)
    return rec


def enumerate_patterns(deg):
    n = len(deg)
    m = sum(deg) // 3
    triples = list(itertools.combinations(range(n), 3))
    out = []

    def rec(start, chosen, d):
        if len(chosen) == m:
            if d == list(deg):
                out.append(tuple(chosen))
            return
        for i in range(start, len(triples)):
            t = triples[i]
            if all(d[v] < deg[v] for v in t):
                for v in t:
                    d[v] += 1
                rec(i + 1, chosen + [t], d)
                for v in t:
                    d[v] -= 1
    rec(0, [], [0] * n)
    return out


def transitions(state, keep_youngest):
    """All proposals from `state` with their probabilities; rejected ones stay."""
    E = list(state)
    m = len(E)
    S = set(E)
    res = Counter()
    for i in range(m):
        for j in range(m):
            pij = 1 / (m * m)
            if i == j:
                res[state] += pij
                continue
            a, b = E[i], E[j]
            ua = a[:2] if keep_youngest else a
            vb = b[:2] if keep_youngest else b
            for u in ua:
                for v in vb:
                    p = pij / (len(ua) * len(vb))
                    ok = u not in b and v not in a and (not keep_youngest or (v < a[2] and u < b[2]))
                    if ok:
                        na = tuple(sorted([x for x in a if x != u] + [v]))
                        nb = tuple(sorted([x for x in b if x != v] + [u]))
                        ok = na not in S and nb not in S
                    if ok:
                        new = list(E)
                        new[i], new[j] = na, nb
                        res[tuple(sorted(new))] += p
                    else:
                        res[state] += p
    return res


def fairness():
    out = []
    for deg in FAIR_SEQS:
        pats = [tuple(sorted(p)) for p in enumerate_patterns(deg)]
        idx = {p: i for i, p in enumerate(pats)}
        for keep in (False, True):
            # R2 moves only between patterns with the same youngest members per knot: group by that signature
            T = {}
            for p in pats:
                for q, pr in transitions(p, keep).items():
                    T[(idx[p], idx[q])] = T.get((idx[p], idx[q]), 0) + pr
            sym = all(abs(T.get((j, i), 0) - v) < 1e-12 for (i, j), v in T.items())
            # components
            parent = list(range(len(pats)))

            def find(x):
                while parent[x] != x:
                    parent[x] = parent[parent[x]]
                    x = parent[x]
                return x
            for (i, j), v in T.items():
                if v > 0 and i != j:
                    parent[find(i)] = find(j)
            comps = len({find(i) for i in range(len(pats))})
            if keep:
                sig = {tuple(sorted(t[2] for t in p)) for p in pats}
                classes = len(sig)
            else:
                classes = 1
            out.append({"degrees": deg, "chain": "R2" if keep else "SW", "patterns": len(pats), "symmetric": sym,
                        "components": comps, "classes_it_must_preserve": classes,
                        "connected_within_classes": comps == classes})
    return out


def run(workers):
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "fairness.json"), "w") as f:
        json.dump(fairness(), f, indent=1)
    oc = [json.loads(l) for l in open(OC_RUNS)]
    specs = [(r["label"], r["run"], r["kstar"]) for r in oc if r["label"] in LABELS and r["dead"] and (r["label"], r["run"]) not in PILOT]
    path = os.path.join(OUT, "runs.jsonl")
    done = set()
    if os.path.exists(path):
        done = {(json.loads(l)["label"], json.loads(l)["run"]) for l in open(path)}
    specs = [s for s in specs if (s[0], s[1]) not in done]
    with Pool(workers) as pool, open(path, "a") as f:
        for rec in pool.imap_unordered(task, specs, chunksize=1):
            f.write(json.dumps(rec) + "\n")
            f.flush()


def summarize():
    recs = [json.loads(l) for l in open(os.path.join(OUT, "runs.jsonl"))]
    fair = json.load(open(os.path.join(OUT, "fairness.json")))
    S = {"fairness": fair, "settings": {}}
    for lab in LABELS:
        rs = [r for r in recs if r["label"] == lab]
        e = {"cores": len(rs), "all_core_unsat": all(r["core_unsat"] for r in rs)}
        for k in ("SW", "R2", "R2p", "FULL"):
            e[f"P_{k}_median"] = float(np.median([r[f"P_{k}"] for r in rs])) if rs else None
            e[f"same_{k}_mean"] = float(np.mean([r[f"same_{k}"] for r in rs])) if rs else None
        diff = [r["P_R2"] - r["P_SW"] for r in rs if r["P_R2"] != r["P_SW"]]
        e["R2_above_SW_share"] = float(np.mean([d > 0 for d in diff])) if diff else None
        e["R2_vs_SW_untied"] = len(diff)
        tr = [r for r in rs if "pasch_trade_unsat" in r]
        e["pasch_cores"] = len(tr)
        e["pasch_trades_unsat"] = all(r["pasch_trade_unsat"] and r["pasch_trade_same_pairs"] for r in tr)
        S["settings"][lab] = e
    st = S["settings"]
    P = {"fair": all(x["symmetric"] and x["connected_within_classes"] for x in fair),
         "Q0_pair_count_lemma": all(st[l]["pasch_trades_unsat"] for l in LABELS),
         "N1_degrees_miss_it": {l: st[l]["P_SW_median"] for l in ("X0.3", "X0.35")},
         "N2_nesting_carries_it": {l: [st[l]["P_R2_median"], st[l]["R2_above_SW_share"]] for l in ("X0.3", "X0.35")}}
    P["N1_holds"] = all(st[l]["P_SW_median"] <= 0.1 for l in ("X0.3", "X0.35"))
    P["N2_holds"] = all(st[l]["P_R2_median"] >= 0.2 and (st[l]["R2_above_SW_share"] or 0) >= 0.7 for l in ("X0.3", "X0.35"))
    S["predictions"] = P
    with open(os.path.join(OUT, "summary.json"), "w") as f:
        json.dump(S, f, indent=1, sort_keys=True, default=lambda o: o.item())
    print(json.dumps(S, indent=1, sort_keys=True, default=lambda o: o.item()))


if __name__ == "__main__":
    if "--summary" in sys.argv:
        summarize()
    else:
        run(int(sys.argv[sys.argv.index("--workers") + 1]) if "--workers" in sys.argv else 8)
