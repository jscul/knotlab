#!/usr/bin/env python3
"""Referee SHORT-DESC-R1, with the referee's own code (no import of dlang.py, census.py or fates.py):
  regen   one worker per variant regenerated from the census's seed (sha256 of "SD:variant:worker", first 16 hex digits) by the
          referee's own sampler of the frozen language (the draw order of the pre-registration's code: Elias gamma by fair coins,
          a uniform callee, a uniform ordered tuple of distinct arguments), expander and port evaluator; every pattern's bits, n, m and
          life (the referee's SAT and its port evaluation) and every family's fate, first death, limit and limit kinds compared with
          the record; then, for the nested families: how many SELF definitions have F(knot) containing the knot (life forever is then
          settled in one step), how many free limits are free at the first step from the top (F(TOP) = TOP), and how many SELF
          definitions call only SELF;
  chains  for 300 regenerated patterns with 7+ knots on <= 400 distinctions (worker 0 of main): the uniform baseline by the
          replace-one-knot chain at 30, 60 and 240 steps per knot and, where n <= 30 and m <= 14, by rejection sampling (uniform
          distinct triples, accepted when every distinction is in a knot); the degree baseline by the switch chain at 20, 40 and
          160 steps per knot; the dead shares.

    python3 -B ref_sd.py regen|chains|chainsbig     (chainsbig: the same chain test on 400 patterns of 25+ knots, workers 0 to 3)"""
import hashlib
import itertools
import json
import gzip
import math
import random
import sys
import time
from collections import Counter
from pathlib import Path

import numpy as np
from pysat.solvers import Solver

HERE = Path(__file__).resolve().parent
ART = HERE.parents[2] / "artifacts" / "SHORT-DESC-20261112-001A" / "SHORT-DESC-20261112-001A-E001_description_census"
CAPS = dict(defs=6, locals=6, calls=12, depth=6, knots=3000)
KEEP_N, KEEP_MIN = 300, 7
VAR = {"main": (6, True), "wide": (8, True), "noself": (6, False)}
NAE = np.array([s not in (0, 7) for s in range(8)])
TOP = np.ones(8, bool)


def seed_of(*parts):
    return int(hashlib.sha256(":".join(map(str, parts)).encode()).hexdigest()[:16], 16)


def gamma(rng):
    z = 0
    while rng.random() < 0.5:
        z += 1
    n = 1
    for _ in range(z):
        n = 2 * n + (rng.random() < 0.5)
    return n, 2 * z + 1


def sample(rng, arity_cap, self_ok):
    bits = 0.0
    r, b = gamma(rng)
    bits += b
    if r > CAPS["defs"]:
        return None, bits, None
    defs = []
    for i in range(r):
        x, b = gamma(rng)
        bits += b
        k = x + 2
        if k > arity_cap:
            return None, bits, None
        x, b = gamma(rng)
        bits += b
        l = x - 1
        if l > CAPS["locals"]:
            return None, bits, None
        c, b = gamma(rng)
        bits += b
        if c > CAPS["calls"]:
            return None, bits, None
        V = k + l
        opts = ["K"] + list(range(i)) + (["SELF"] if self_ok and k == 3 else [])
        calls = []
        for _ in range(c):
            ce = opts[rng.randrange(len(opts))]
            bits += math.log2(len(opts))
            ar = 3 if ce in ("K", "SELF") else defs[ce][0]
            if ar > V:
                return None, bits, None
            calls.append((ce, tuple(rng.sample(range(V), ar))))
            bits += math.log2(math.perm(V, ar))
        defs.append((k, l, calls))
    if not any(ce == "SELF" for d in defs for ce, _ in d[2]):
        return defs, bits, None
    t, b = gamma(rng)
    return defs, bits + b, t          # t may exceed the cap (family kept, pattern rejected)


def expand(defs, t):
    knots, nv = set(), [defs[-1][0]]

    def go(i, actual, depth):
        k, l, calls = defs[i]
        env = list(actual) + list(range(nv[0], nv[0] + l))
        nv[0] += l
        for ce, args in calls:
            a = [env[x] for x in args]
            if ce == "K" or (ce == "SELF" and depth <= 1):
                knots.add(tuple(sorted(a)))
                if len(knots) > CAPS["knots"]:
                    raise OverflowError
            elif ce == "SELF":
                go(i, a, depth - 1)
            else:
                go(ce, a, depth)
    try:
        go(len(defs) - 1, list(range(defs[-1][0])), t or 1)
    except OverflowError:
        return None
    used = sorted({v for e in knots for v in e})
    ix = {v: j for j, v in enumerate(used)}
    return len(used), sorted(tuple(sorted(ix[v] for v in e)) for e in knots)


def port_relations(defs, selfrel):
    rels = []
    for i, (k, l, calls) in enumerate(defs):
        V = k + l
        A = (np.arange(2 ** V)[:, None] >> np.arange(V)) & 1
        ok = np.ones(2 ** V, bool)
        for ce, args in calls:
            R = NAE if ce == "K" else (selfrel[i] if ce == "SELF" else rels[ce])
            ok &= R[(A[:, list(args)] << np.arange(len(args))).sum(1)]
        rel = np.zeros(2 ** k, bool)
        rel[np.nonzero(ok)[0] & (2 ** k - 1)] = True
        rels.append(rel)
    return rels


def iterate(defs, start):
    selfs = [i for i, d in enumerate(defs) if any(ce == "SELF" for ce, _ in d[2])]
    prev = {i: start for i in selfs}
    seen, alive, first = {}, [], None
    while True:
        rels = port_relations(defs, prev)
        if first is None:
            first = {i: rels[i].copy() for i in selfs}
        alive.append(bool(rels[-1].any()))
        key = tuple(rels[i].tobytes() for i in selfs)
        if key in seen:
            return alive, seen[key], {i: rels[i] for i in selfs}, first
        seen[key] = len(alive) - 1
        prev = {i: rels[i] for i in selfs}


def alive_at_depth(defs, t):
    if t is None:
        return bool(port_relations(defs, {})[-1].any())
    prev = {i: NAE for i, d in enumerate(defs) if any(ce == "SELF" for ce, _ in d[2])}
    for _ in range(t):
        rels = port_relations(defs, prev)
        prev = {i: rels[i] for i in prev}
    return bool(rels[-1].any())


def kind_of(rel):
    S = [s for s in range(8) if rel[s]]
    if S and len(S) < 8 and all(len({tuple((s >> j) & 1 for j in range(3) if j != d) for s in S}) == 4 for d in range(3)):
        return "knot"
    return {0: "none", 1: "three tied", 2: "two tied", 4: "free"}.get(len(S) // 2, "other")


def fate(defs):
    alive, c0, _, first = iterate(defs, NAE)
    fd = next((j + 1 for j, a in enumerate(alive) if not a), None)
    f = "forever" if fd is None else ("at once" if fd == 1 else "a while")
    la, _, lim, first_top = iterate(defs, TOP)
    selfs = sorted(lim)
    return {"fate": f, "first_dead": fd, "limit_alive": la[-1], "limit_kinds": [kind_of(lim[i]) for i in selfs],
            "revives": bool(fd) and any(alive[fd:]),
            "monotone at the knot": all(bool(np.all(first[i][NAE])) for i in selfs),       # F(knot) contains the knot
            "free at the first step": [bool(first_top[i].all()) for i in selfs],
            "self-only bodies": [all(ce == "SELF" for ce, _ in defs[i][2]) for i in selfs],
            "K calls in the SELF definitions": [sum(ce == "K" for ce, _ in defs[i][2]) for i in selfs]}


def sat(K):
    with Solver(name="cadical153", bootstrap_with=[c for t in K for c in ([a + 1 for a in t], [-(a + 1) for a in t])]) as s:
        return s.solve()


def regen(variant, worker, tries=150000):
    arity, self_ok = VAR[variant]
    rng = random.Random(seed_of("SD", variant, worker))
    recs = [json.loads(l) for l in gzip.open(ART / f"runs_{variant}_{worker}.jsonl.gz", "rt")]
    pats = {r["try_"]: r for r in recs if r["kind"] == "pattern"}
    fams = {r["try_"]: r for r in recs if r["kind"] == "family"}
    tally = Counter()
    extra = Counter()
    keep = []
    for k in range(tries):
        defs, bits, t = sample(rng, arity, self_ok)
        if defs is not None and t is not None:
            f = fate(defs)
            rec = fams.get(k)
            tally["families"] += 1
            tally["family matches"] += bool(rec) and all(rec[x] == f[x] for x in ("fate", "first_dead", "limit_alive", "limit_kinds", "revives"))
            extra["monotone at the knot"] += f["monotone at the knot"]
            extra["monotone at the knot, forever"] += f["monotone at the knot"] and f["fate"] == "forever"
            extra["forever"] += f["fate"] == "forever"
            for kd, fr, so, kc in zip(f["limit_kinds"], f["free at the first step"], f["self-only bodies"], f["K calls in the SELF definitions"]):
                extra["SELF definitions"] += 1
                if kd == "free":
                    extra["free limits"] += 1
                    extra["free limits, free at the first step"] += fr
                    extra["free limits, self-only body"] += so
                    extra["free limits, no K call in the body"] += kc == 0
            if f["fate"] != "forever" and f["limit_alive"]:
                extra["die at a finite depth, limit lives"] += 1
            if t > CAPS["depth"]:
                continue
        if defs is None:
            continue
        e = expand(defs, t)
        if e is None:
            continue
        n, K = e
        rec = pats.get(k)
        tally["patterns"] += 1
        if rec is None:
            tally["pattern missing"] += 1
            continue
        same = abs(rec["bits"] - bits) < 1e-9 and (rec["n"], rec["m"], rec["t"]) == (n, len(K), t)
        tally["pattern matches"] += same
        if len(K) >= 7:
            a = sat(K)
            ports = alive_at_depth(defs, t)
            tally["7+ knots"] += 1
            tally["life matches (SAT)"] += a == rec["alive"]
            tally["port evaluation equals SAT"] += a == ports
            if n <= 400 and len(keep) < KEEP_N and len(K) >= KEEP_MIN:
                keep.append({"n": n, "K": K, "alive": a, "nested": t is not None})
    return dict(tally), dict(extra), keep


def uniform_chain(n, K, rng, per):
    E, S = list(K), set(K)
    cnt = Counter(v for e in E for v in e)
    for _ in range(per * len(E)):
        i = rng.randrange(len(E))
        new = tuple(sorted(rng.sample(range(n), 3)))
        if new in S:
            continue
        old = E[i]
        if any(cnt[v] == 1 and v not in new for v in old):
            continue
        for v in old:
            cnt[v] -= 1
        for v in new:
            cnt[v] += 1
        S.discard(old)
        S.add(new)
        E[i] = new
    return E


def rejection(n, m, rng, tries=20000):
    allt = None
    for _ in range(tries):
        S = set()
        while len(S) < m:
            S.add(tuple(sorted(rng.sample(range(n), 3))))
        if len({v for e in S for v in e}) == n:
            return list(S)
    return None


def degree_chain(K, rng, per):
    E, S = [tuple(sorted(t)) for t in K], set(K)
    for _ in range(per * len(E)):
        i, j = rng.randrange(len(E)), rng.randrange(len(E))
        if i == j:
            continue
        a, b = E[i], E[j]
        u, v = a[rng.randrange(3)], b[rng.randrange(3)]
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


def chains(keep):
    rng = random.Random(77)
    out = Counter()
    for p in keep:
        n, K = p["n"], p["K"]
        out["patterns"] += 1
        out["patterns dead"] += not p["alive"]
        for per in (30, 60, 240):
            out[f"uniform {per}: dead"] += not sat(uniform_chain(n, K, rng, per))
        for per in (20, 40, 160):
            out[f"degree {per}: dead"] += not sat(degree_chain(K, rng, per))
        if n <= 30 and len(K) <= 14:
            R = rejection(n, len(K), rng)
            if R is not None:
                out["rejection-sampled"] += 1
                out["rejection: dead"] += not sat(R)
                out["uniform 30 on the same patterns: dead"] += not sat(uniform_chain(n, K, rng, 30))
    return dict(out)


def main():
    part = sys.argv[1]
    t0 = time.time()
    if part == "regen":
        res = {}
        for variant in ("main", "wide", "noself"):
            tally, extra, keep = regen(variant, 0)
            res[variant] = {"tally": tally, "families": extra}
            if variant == "main":
                (HERE / "keep_main0.json").write_text(json.dumps(keep) + "\n")
            print(variant, tally, extra, round(time.time() - t0), "s", flush=True)
        (HERE / "result_regen.json").write_text(json.dumps(res, indent=1) + "\n")
    elif part == "chainsbig":
        global KEEP_N, KEEP_MIN
        KEEP_N, KEEP_MIN = 400, 25
        keep = []
        for w in range(4):
            keep += regen("main", w)[2]
        res = chains(keep[:400])
        res["patterns with 25+ knots from main workers 0 to 3"] = len(keep)
        (HERE / "result_chains_big.json").write_text(json.dumps(res, indent=1) + "\n")
        print(json.dumps(res, indent=1), round(time.time() - t0), "s")
    else:
        keep = json.loads((HERE / "keep_main0.json").read_text())
        for p in keep:
            p["K"] = [tuple(t) for t in p["K"]]
        res = chains(keep)
        (HERE / "result_chains.json").write_text(json.dumps(res, indent=1) + "\n")
        print(json.dumps(res, indent=1), round(time.time() - t0), "s")


if __name__ == "__main__":
    main()
