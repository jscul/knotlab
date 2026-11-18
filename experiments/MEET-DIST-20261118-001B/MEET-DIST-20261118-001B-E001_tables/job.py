"""MEET-DIST-20261118-001B frozen run, for the shared runner (docs/tooling/shared-runner.md).

melib.py is MEET-ORDERS-20261118-001B's engine, copied unchanged (same sha256).

Case D|n0|d|j: exact KF3 (classes up to renaming) from presentation j (one per mirror pair) of the line of n0, to n0 + d. At every
level, the law over classes of the grown base's disagreement table: the number of allowed states N with the table d(u, v) of
disagreement counts, up to renaming (canonical form by refinement on the counts and an exhaustive search), and, as a coarse
reading, the law of the number of orders; the ablation law of N with the sorted multiset of table entries; and the advisor's
bag-of-knots null (k distinct knots chosen uniformly and revealed as fills, no growth). Mirror images carry the same laws, so each
case reports its mirror weight.
"""
import hashlib
import itertools
import sys
from collections import Counter, defaultdict
from fractions import Fraction
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import melib as M

CASES = [(5, 4), (6, 4), (7, 4), (8, 3), (9, 3)]


def reps(n0):
    seen = set()
    out = []
    m = n0 - 1
    for T in M.bracketings(0, m):
        key = tuple(sorted(T))
        mk = tuple(M.mirror(T, m))
        if mk in seen or key in seen:
            continue
        seen.add(key)
        out.append((sorted(T), 1 if mk == key else 2))
    return out


def cases():
    for n0, d in CASES:
        for j, (T, w) in enumerate(reps(n0)):
            yield f"D|{n0}|{d}|{j}", {"n0": n0, "depth": d, "knots": T, "mirror_weight": w}


def table_class(S, n):
    """Canonical form of (N, disagreement table) under renaming."""
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
            cert = tuple(D[order[i]][order[j]] for i in range(n) for j in range(i + 1, n))
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

    search([0] * n)
    return hashlib.sha256(repr((len(S), best[0])).encode()).hexdigest()[:20]


def multiset_class(S, n):
    """The ablation: N with the sorted multiset of the table's entries, labels dropped."""
    D = M.dmat(S, n)
    return hashlib.sha256(repr((len(S), tuple(sorted(D[u][v] for u in range(n) for v in range(u + 1, n))))).encode()).hexdigest()[:20]


def fills_base(n0, T, chosen):
    """The line with the fill points (parities) of the chosen knots, as new distinctions n0, n0 + 1, ... (no state added)."""
    S0 = M.base(n0, T)
    out = []
    for s in S0:
        x = s
        for i, k in enumerate(chosen):
            par = sum((s >> v) & 1 for v in k) & 1
            x |= par << (n0 + i)
        out.append(x)
    return tuple(sorted(out))


def null_laws(n0, T, depth):
    """The bag-of-knots null (the advisor's): k distinct knots chosen uniformly and revealed as fills, k = 1 .. depth."""
    laws = []
    for k in range(1, depth + 1):
        if k > len(T):
            laws.append(None)
            continue
        subs = list(itertools.combinations(T, k))
        law = defaultdict(Fraction)
        for c in subs:
            law[table_class(fills_base(n0, T, c), n0 + k)] += Fraction(1, len(subs))
        laws.append({key: str(v) for key, v in sorted(law.items())})
    return laws


def run(case_id, p):
    n0, d, T = p["n0"], p["depth"], [tuple(k) for k in p["knots"]]
    lv = M.exact(n0, T, n0 + d)
    levels = []
    for L in lv:
        law = defaultdict(Fraction)
        mlaw = defaultdict(Fraction)
        for (S, G), q in L["dist"].items():
            law[table_class(S, L["n"])] += q
            mlaw[multiset_class(S, L["n"])] += q
        levels.append({"n": L["n"], "table_law": {k: str(v) for k, v in sorted(law.items())},
                       "multiset_law": {k: str(v) for k, v in sorted(mlaw.items())},
                       "table_classes": len(law), "lam": {str(k): str(v) for k, v in sorted(L["lam"].items())},
                       "two": str(L["two"])})
    nulls = null_laws(n0, T, d)
    for k, nl in enumerate(nulls, start=1):
        levels[k]["null_law"] = nl
    return {"n0": n0, "depth": d, "knots": T, "mirror_weight": p["mirror_weight"],
            "bare": M.nesting(T, 0, n0 - 1), "ordered": M.nesting(T, 0, n0 - 1, ordered=True), "levels": levels}


if __name__ == "__main__":
    print(sum(1 for _ in cases()), "cases")
