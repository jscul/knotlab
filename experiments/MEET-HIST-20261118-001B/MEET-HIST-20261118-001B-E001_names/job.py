"""MEET-HIST-20261118-001B frozen run, for the shared runner (docs/tooling/shared-runner.md).

melib.py is MEET-ORDERS-20261118-001B's engine, copied unchanged (same sha256).

Case H|n0|d|i: labelled KF3 from bracketing i of the line of n0 (every bracketing, so the prior needs no mirror weights), to
n0 + d. At every level, the law of the grown states read four ways, each up to the renamings it allows and up to the line's
reversal:
  U   unnamed: every distinction anonymous (the state class; by DISTANCE-ORDER 3(a) the disagreement table's class);
  NL  the line's distinctions named by place, the new ones anonymous;
  NO  the new ones named by order of growth, the line's anonymous;
  N   all named.
and the joint laws of (U, NO), (U, NL) and (NL, N), for the conditional entropies of the order of growth and of the line's names
given U, and of the order of growth given the named line. NO equals N by construction (the line's distinctions, known as a set,
are a chain of nested cuts, which the states order up to reversal), so NO is a sanity check.
"""
import hashlib
import itertools
import sys
from collections import Counter, defaultdict
from fractions import Fraction
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import melib as M

CASES = [(5, 4), (6, 4), (7, 4), (8, 3)]


def cases():
    for n0, d in CASES:
        for i, T in enumerate(M.bracketings(0, n0 - 1)):
            yield f"H|{n0}|{d}|{i}", {"n0": n0, "depth": d, "knots": T}


def relabel(S, perm):
    return tuple(sorted(sum(1 << perm[u] for u in range(len(perm)) if (s >> u) & 1) for s in S))


def colored_canon(S, n, colors):
    """Canonical form of the state set S under renamings that keep each distinction's colour (individualisation-refinement on
    the disagreement counts, exhaustive over the search tree)."""
    D = M.dmat(S, n)

    def refine(col):
        while True:
            sig = [(col[u], tuple(sorted((D[u][v], col[v]) for v in range(n) if v != u))) for u in range(n)]
            keys = sorted(set(sig))
            new = [keys.index(x) for x in sig]
            if len(set(new)) == len(set(col)):
                return new
            col = new

    best = [None]

    def search(col):
        col = refine(col)
        if len(set(col)) == n:
            order = sorted(range(n), key=lambda u: col[u])
            pos = {u: i for i, u in enumerate(order)}
            cert = relabel(S, [pos[u] for u in range(n)])
            if best[0] is None or cert < best[0]:
                best[0] = cert
            return
        cnt = Counter(col)
        target = min((cnt[c], c) for c in cnt if cnt[c] > 1)[1]
        for u in range(n):
            if col[u] == target:
                c2 = [2 * x for x in col]
                c2[u] = 2 * target - 1
                search(c2)

    keys = sorted(set(colors))
    search([keys.index(c) for c in colors])
    return best[0]


def key(x):
    return hashlib.sha256(repr(x).encode()).hexdigest()[:20]


def readings(S, n, n0):
    m = n0 - 1
    mirror = [m - u if u < n0 else u for u in range(n)]
    S_m = relabel(S, mirror)
    out = {}
    out["U"] = key(colored_canon(S, n, [0] * n))
    # line named by place (up to reversal), new anonymous
    out["NL"] = key(min(colored_canon(X, n, [("line", u) if u < n0 else ("new",) for u in range(n)]) for X in (S, S_m)))
    # new named by order, line anonymous (reversal is a renaming of the line, so nothing more to take)
    out["NO"] = key(colored_canon(S, n, [("line",) if u < n0 else ("new", u) for u in range(n)]))
    out["N"] = key(min(S, S_m))
    return out


def run(case_id, p):
    n0, d, T = p["n0"], p["depth"], [tuple(k) for k in p["knots"]]
    lv = M.exact(n0, T, n0 + d, use_canon=False)
    levels = []
    for L in lv:
        laws = {r: defaultdict(Fraction) for r in ("U", "NL", "NO", "N", "U|NO", "U|NL", "NL|N")}
        cache = {}
        for (S, G), q in L["dist"].items():
            if S not in cache:
                cache[S] = readings(S, L["n"], n0)
            rd = cache[S]
            for r in ("U", "NL", "NO", "N"):
                laws[r][rd[r]] += q
            laws["U|NO"][rd["U"] + ":" + rd["NO"]] += q
            laws["U|NL"][rd["U"] + ":" + rd["NL"]] += q
            laws["NL|N"][rd["NL"] + ":" + rd["N"]] += q
        levels.append({"n": L["n"], "laws": {r: {k: str(v) for k, v in sorted(w.items())} for r, w in laws.items()},
                       "labelled_states": len(cache)})
    return {"n0": n0, "depth": d, "knots": T, "bare": M.nesting(T, 0, n0 - 1), "levels": levels}


if __name__ == "__main__":
    print(sum(1 for _ in cases()), "cases")
