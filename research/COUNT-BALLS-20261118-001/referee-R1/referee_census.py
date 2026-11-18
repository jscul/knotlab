"""Referee R1 for COUNT-BALLS-20261118-001, the census (own code; the study's census.py and STATE-RULES' rules.py are not imported).

  ../../../.venv/bin/python -B referee_census.py <population> <nmax> > referee_census_<population>_<nmax>.json    (this directory)

Populations from the line of three B(a, b, c), every class followed (classes up to renaming the distinctions):
  cheap      the admitted extensions (CUBE-DOUBLING-R1's closure of one to three betweenness knots on p and two old distinctions,
             every old state extends, p constrained, not a copy) with the fewest states, every tie;
  one-split  every admitted extension that adds at most two states (at most one new split).
Classes by the referee's canonical form: the n x s table of orientations (distinction u's side of each split) up to permuting the
distinctions, permuting the splits and swapping a split's sides, computed as the least, over the choice of a reference distinction
(whose sides fix the swaps) and over every order of the splits, of the sorted rows.
(The reference distinctions are restricted to those with the least sorted row of splits apart, a renaming-free choice.)
Readings, as the note defines them: (a) the multiset over distinctions of the sorted row of disagreement counts; (c) the multiset
over states of the sorted row of Hamming distances.  Targets k (the exact least number of colours of the crossing graph, by
backtracking) and lambda (Eppstein's, from the referee's KNOT-CAP-R1 `measure`).  Per n: classes, (k, lambda) table, and for (a) and (c) the groups, the groups holding several
classes, and those whose k (lambda) differ, with the first such group's splits.
"""
import itertools
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "research/CUBE-DOUBLING-20261118-001/referee-R1"))
sys.path.insert(0, str(ROOT / "research/KNOT-CAP-20261117-001/referee-R1"))
import referee_cube as RC  # noqa: E402
import referee_cap as KC  # noqa: E402

PERMS = {}


def perms(s):
    if s not in PERMS:
        PERMS[s] = np.array(list(itertools.permutations(range(s))), dtype=np.int64) if s else np.zeros((1, 0), dtype=np.int64)
    return PERMS[s]


def canon(st, n):
    sp, ori = RC.orientations(st, n)
    s = len(sp)
    M = np.array([[(o >> j) & 1 for j in range(s)] for o in ori], dtype=np.int64)          # n x s
    P = perms(s)
    w = (1 << np.arange(s)[::-1]).astype(np.int64)
    inv = [tuple(sorted(int(x) for x in (M[u] ^ M).sum(axis=1))) for u in range(n)]    # u's splits-apart row, renaming-free
    least = min(inv)
    best = None
    for r in (u for u in range(n) if inv[u] == least):
        F = M ^ M[r]                                                                         # reference distinction on side 0
        V = (F[:, P] * w).sum(axis=2)                                                        # n x |P|: row codes per split order
        R = np.sort(V.T, axis=1)                                                             # |P| x n
        cand = min(map(tuple, R.tolist()))
        if best is None or cand < best:
            best = cand
    return (s, best)


def chromatic(sp, full):
    """Exact least number of colours of the crossing graph (1 when nothing crosses), by backtracking."""
    s = len(sp)
    adj = [set() for _ in range(s)]
    for i, j in itertools.combinations(range(s), 2):
        a, b = sp[i], sp[j]
        if all(x for x in (a & b, a & (full ^ b), (full ^ a) & b, (full ^ a) & (full ^ b))):
            adj[i].add(j)
            adj[j].add(i)
    if not any(adj):
        return 1
    order = sorted(range(s), key=lambda v: -len(adj[v]))
    def ok(k):
        col = {}
        def rec(i):
            if i == s:
                return True
            v = order[i]
            used = {col[w] for w in adj[v] if w in col}
            for c in range(min(k, max(col.values(), default=-1) + 2)):
                if c not in used:
                    col[v] = c
                    if rec(i + 1):
                        return True
                    del col[v]
            return False
        return rec(0)
    k = 2
    while not ok(k):
        k += 1
    return k


def readings(st, n):
    O, Z, full = RC.cols(st, n)
    pc = RC.pc
    a = tuple(sorted(tuple(sorted(pc(Z[u] & O[v]) + pc(O[u] & Z[v]) for v in range(n) if v != u)) for u in range(n)))
    c = tuple(sorted(tuple(sorted(pc(x ^ y) for y in st if y != x)) for x in st))
    m = KC.measure(st, n)                                   # lambda by Eppstein; its k is capped at 3, so k is recomputed here
    return {"a": a, "c": c, "k": chromatic(RC.splits_of(st, n), (1 << n) - 1), "lam": m["lam"]}


def names(sp, n):
    full = (1 << n) - 1
    L = "abcdefghijklmnop"
    return ["".join(L[u] for u in range(n) if (x >> u) & 1) + "|" + "".join(L[u] for u in range(n) if not (x >> u) & 1)
            for x in sp]


def determination(level, n):
    rd = {key: readings(st, n) for key, st in level.items()}
    out = {"classes": len(level)}
    kl = defaultdict(int)
    for r in rd.values():
        kl[f"{r['k']},{r['lam']}"] += 1
    out["k_lam"] = dict(sorted(kl.items()))
    for x in ("a", "c"):
        groups = defaultdict(list)
        for key, r in rd.items():
            groups[r[x]].append(key)
        bad_k = [g for g in groups.values() if len({rd[c]["k"] for c in g}) > 1]
        bad_l = [g for g in groups.values() if len({rd[c]["lam"] for c in g}) > 1]
        ex = None
        for g in bad_k + bad_l:
            ex = [{"splits": names(RC.splits_of(level[c], n), n), "k": rd[c]["k"], "lam": rd[c]["lam"], "states": len(level[c])}
                  for c in g[:2]]
            break
        out[x] = {"groups": len(groups), "multi": sum(len(g) > 1 for g in groups.values()), "fail_k": len(bad_k),
                  "fail_lam": len(bad_l), "example": ex}
    return out


def main(pop, nmax):
    st = sorted(S for S in range(8) if RC.allowed(S, 3, [(0, 1, 2)]))
    n = 3
    level = {canon(st, n): st}
    out = {"population": pop, "levels": []}
    while True:
        d = determination(level, n)
        d["n"] = n
        out["levels"].append(d)
        print("level", n, json.dumps({k: v for k, v in d.items() if k not in ("a", "c")}),
              {x: {k: v for k, v in d[x].items() if k != "example"} for x in ("a", "c")}, file=sys.stderr, flush=True)
        if n >= nmax:
            break
        nxt = {}
        for key, S in level.items():
            ext, O, Z, full = RC.closure(S, n)
            N = len(S)
            adm = [(a0, a1) for a0, a1 in ext if RC.admitted(a0, a1, O, Z, full, N)]
            if not adm:
                continue
            if pop == "cheap":
                low = min(RC.pc(a0) + RC.pc(a1) for a0, a1 in adm)
                keep = [x for x in adm if RC.pc(x[0]) + RC.pc(x[1]) == low]
            else:
                keep = [x for x in adm if RC.pc(x[0]) + RC.pc(x[1]) <= N + 2]
            for e in {tuple(RC.apply(S, n, a0, a1)) for a0, a1 in keep}:
                kk = canon(list(e), n + 1)
                if kk not in nxt:
                    nxt[kk] = list(e)
        level = nxt
        n += 1
    return out


if __name__ == "__main__":
    print(json.dumps(main(sys.argv[1], int(sys.argv[2])), indent=1))
