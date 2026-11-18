"""The advisor's (v, S) model of the ring of n knots with one extra open distinction at knot 0 (FRESH model check)."""
from collections import Counter
from itertools import combinations
def lifts_below(a, b, n):
    # lifts p_k = (n k, -n k) with p_k <= (a, b)
    lo = -(b // n) if b >= 0 else -((b) // n)
    ks = [k for k in range(-(abs(b)//n)-2, a//n + 3) if n*k <= a and -n*k <= b]
    return ks
def junctions(n, T):
    """All (v, S) of round <= T, v = (a, b) with representative a in 0..n-1 (mod the shift (n, -n)); S a set of lift indices."""
    out = {}
    for h in range(0, T + 1):
        for a0 in range(n):
            a, b = a0, h - a0
            L = lifts_below(a, b, n)
            for s in range(0, len(L) + 1):
                if h + s > T: break
                for S in combinations(L, s):
                    out[((a, b), S)] = h + s
    return out
def canon(a, b, S, n):
    # shift so that a in 0..n-1
    q = a // n
    return ((a - n*q, b + n*q), tuple(k - q for k in S))
def parents(v, S, n):
    a, b = v; ps = []
    for k in S:
        ps.append(canon(a, b, tuple(x for x in S if x != k), n))
    for (a2, b2) in ((a - 1, b), (a, b - 1)):
        if a2 + b2 < 0: continue
        if all(n*k <= a2 and -n*k <= b2 for k in S):
            ps.append(canon(a2, b2, S, n))
    return ps
def demand(v, S, n):
    return 2 + len(lifts_below(*v, n)) - len(S)
if __name__ == '__main__':
    n = 5; T = 22
    J = junctions(n, T)
    hist = {}
    for (v, S), t in J.items():
        if t == 0: continue
        hist.setdefault(t, Counter())[(len(parents(v, S, n)), demand(v, S, n))] += 1
    for t in range(1, T + 1): print(t, sum(hist[t].values()), dict(sorted(hist[t].items())))
