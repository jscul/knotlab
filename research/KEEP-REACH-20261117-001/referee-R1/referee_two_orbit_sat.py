"""Referee R1 for KEEP-REACH-20261117-001: two-orbit bonds and actual-value forgetting at finite depth, by SAT, with the referee's
own orbits, joints and bond search.

  .venv/bin/python -B referee_two_orbit_sat.py > referee_two_orbit_sat.json

The pattern P_N is the census's `pattern(key, N)` (the object under study). Everything else is the referee's:
- orbits at level n: the components of the level's addresses under the placement's used words (the census's `addr.action` gives
  each word's image of every level-n address);
- the joint of two orbits: every assignment of their addresses tested for extension by CaDiCaL (pysat), so the joint is the exact
  projection of all states of P_N;
- the least two-orbit bond: the least set inside the two orbits meeting both that is constrained in the joint with every proper
  subset free.
Checks:
1. b_N(3, s) = least two-orbit bond over all orbit pairs at levels 3 and 3 + s, against two_orbit.every_depth_cross's value for
   remaining depth r = N - 3 - s, for the four census patterns, mutant 8db5da810c00-73 and its parent, and the 12 "hidden" and 13
   "products" third-class patterns (s = 1 .. N - 3).
2. Actual-value forgetting at every remaining depth: for the 14 "forget on actual values" patterns, with r their reported length
   from level 3, every joint of an orbit at level j >= 3 and an orbit r levels below inside its subtree is a product, at depth N,
   for every j with j + r <= N (so remaining depths N - j - r down to 0 are included).
"""
from __future__ import annotations

import itertools
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CODEX = ROOT / "experiments/LEVEL-REACH-20261114-001A/LEVEL-REACH-20261114-001A-E001_level_reach/codex"
sys.path.insert(0, str(CODEX))
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(ROOT / "research/DIRECT-REACH-20261115-001/exploratory"))
from pattern import addr, pattern  # noqa: E402  (the census's address maps and pattern: the object under study)
from pysat.solvers import Cadical195  # noqa: E402


def vid(n, y):
    return y + (1 << n) - 1


def orbits(key, n):
    s, sw, d0, d1, pls = key
    W = addr.words(s)
    aut = tuple(tuple(r) for r in (sw, d0, d1))
    used = sorted({t // 3 for p in pls for t in p})
    par = list(range(1 << n))

    def find(a):
        while par[a] != a:
            par[a] = par[par[a]]
            a = par[a]
        return a
    for wi in used:
        img = addr.action(aut, W[wi], n)
        for y in range(1 << n):
            a, b = find(y), find(int(img[y]))
            if a != b:
                par[a] = b
    comp = {}
    for y in range(1 << n):
        comp.setdefault(find(y), []).append(y)
    return [sorted(c) for c in comp.values()]


def clauses(K):
    out = []
    for a, b, c in K.tolist():
        out.append([a + 1, b + 1, c + 1])
        out.append([-(a + 1), -(b + 1), -(c + 1)])
    return out


def joint(solver, U, V):
    allv = U + V
    J = set()
    for bits in itertools.product((0, 1), repeat=len(allv)):
        if solver.solve(assumptions=[v + 1 if b else -(v + 1) for v, b in zip(allv, bits)]):
            J.add(bits)
    return J


def least_cross(J, mu):
    if not J:
        return None
    n = len(next(iter(J)))
    free = {}

    def isfree(S):
        if S not in free:
            free[S] = len({tuple(r[i] for i in S) for r in J}) == 1 << len(S)
        return free[S]
    for size in range(2, n + 1):
        for S in itertools.combinations(range(n), size):
            if S[0] < mu <= S[-1] and not isfree(S) and all(isfree(S[:i] + S[i + 1:]) for i in range(size)):
                return size
    return None


def product(J, mu):
    A = {r[:mu] for r in J}
    B = {r[mu:] for r in J}
    return len(J) == len(A) * len(B)


def below(n0, U, r):
    """Descendant addresses r levels below a set of level-n0 addresses."""
    return {(u << r) | t for u in U for t in range(1 << r)}


def check_b(key, N, ks=3):
    K = pattern(key, N)
    with Cadical195(bootstrap_with=clauses(K)) as S:
        if not S.solve():
            return {"alive": False}
        top = orbits(key, ks)
        res = {}
        for s in range(1, N - ks + 1):
            low = orbits(key, ks + s)
            best = None
            for U in top:
                for V in low:
                    b = least_cross(joint(S, [vid(ks, u) for u in U], [vid(ks + s, v) for v in V]), len(U))
                    if b is not None and (best is None or b < best):
                        best = b
            res[s] = best
        return {"alive": True, "b": res}


def check_forget(key, N, r, ks=3):
    K = pattern(key, N)
    bad = []
    with Cadical195(bootstrap_with=clauses(K)) as S:
        if not S.solve():
            return {"alive": False}
        for j in range(ks, N - r + 1):
            for U in orbits(key, j):
                sub = below(j, U, r)
                for V in orbits(key, j + r):
                    if not set(V) <= sub:
                        continue
                    J = joint(S, [vid(j, u) for u in U], [vid(j + r, v) for v in V])
                    if J and not product(J, len(U)):
                        bad.append({"level": j, "remaining_depth": N - j - r})
    return {"alive": True, "checked_levels": list(range(ks, N - r + 1)), "non_product": bad[:10], "non_product_count": len(bad)}


def main():
    from two_orbit import every_depth_cross
    from window_tree import WindowTree
    third = json.load(open(HERE.parent / "third_class.json"))["third"]
    import gzip
    census = json.load(open(HERE.parent / "census_keep.json"))["rows"]
    four = [c for c, r in census.items() if r.get("r_all") is None and r.get("small_orbits")
            and r.get("two_orbit_tail_max") not in (2, 3)]
    recs = ROOT / "artifacts/LEVEL-REACH-20261114-001A/LEVEL-REACH-20261114-001A-E001_level_reach/records_slim.jsonl.gz"
    keys = {}
    for line in gzip.open(recs, "rt"):
        r = json.loads(line)
        if r["case"] in four:
            keys["census:" + r["case"][:12]] = r["key"]
    keys["8db5da810c00-73"] = third["8db5da810c00-73"]["key"]
    for idx, v in third.items():
        if v["kind"] != "forgets on actual values":
            keys[idx] = v["key"]
    N = 8
    out = {"b_check": {}, "forget_check": {}}
    for name, key in keys.items():
        tree = WindowTree(key)
        e = every_depth_cross(tree, 3)
        seqs = e["sequences"]
        r0 = e["r0"]
        routine = {}
        for s in range(1, N - 3 + 1):
            r = N - 3 - s
            tier = f"r={r}" if r < r0 else f"r>={r0}"
            routine[s] = seqs[tier][s - 1]
        mine = check_b(key, N)
        out["b_check"][name] = {"routine": routine, "sat": mine.get("b"), "alive": mine["alive"],
                                "agree": mine["alive"] and all(routine[s] == mine["b"][s] for s in routine),
                                "start": e["start"], "period": e["period"], "r0": r0,
                                "kind": third.get(name, {}).get("kind", "census")}
        print(name, out["b_check"][name]["agree"], routine, mine.get("b"), e["start"], e["period"], flush=True)
    for idx, v in third.items():
        if v["kind"] == "forgets on actual values":
            out["forget_check"][idx] = {"r": v["actual_forget_from_3"], **check_forget(v["key"], N, v["actual_forget_from_3"])}
            print(idx, out["forget_check"][idx]["non_product_count"], flush=True)
    print(json.dumps(out, indent=1, default=str))


if __name__ == "__main__":
    main()
