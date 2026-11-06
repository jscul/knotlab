"""Scout (not a ticket check): the access lemma of PLANAR-COMPOSE-20261102-001A on grown plane knot spaces of 16, 18 and 20 points.
Run from the repository root with .venv/bin/python -B; output is recorded in access_lemma_scout.txt."""
import sys, itertools, collections, time
from pathlib import Path
import numpy as np
ROOT = Path("/home/jscul/p-vs-np-contact-first")
sys.path.insert(0, str(ROOT / "proofs/HANDLE-EMERGENCE-20261102-001A/HANDLE-EMERGENCE-20261102-001A-P001_a_planar_removed_side_creates_nothing"))
import planar_lib as PL
G = PL.G
def solutions(H, s, n, M):
    keep = [k for k in range(len(H)) if k != M]
    return G.states(n)[G.sat_matrix([H[k] for k in keep], [s[k] for k in keep], n).all(axis=1)]


def tied_to(A, h, n):
    return {p for p in range(n) if len({(int(r[h]), int(r[p])) for r in A}) == 2}


def odd_index(t, sigma):
    d = [i for i in range(3) if t[i] != sigma[i]]
    if len(d) == 1:
        return d[0]
    return next(i for i in range(3) if t[i] == sigma[i])


def classify_pinnings(H, s, n):
    """every pinning of the closing line's pattern by the hub and one near point, over all (closing line, removed line) pairs with six
    patterns: (i) hub tied to a non-odd port, (i') to the odd port, (ii) hub, non-odd ports form a knot excluding a pattern one step
    from the pinned one, (ii') two steps, (iv) neither"""
    out = collections.Counter()
    for mi, M in enumerate(H):
        A = solutions(H, s, n, mi)
        h = M[0]
        hub = tied_to(A, h, n)
        for li, L1 in enumerate(H):
            if li == mi:
                continue
            X = list(L1)
            I = {tuple(int(b) for b in r) for r in A[:, X]}
            if len(I) != 6:
                continue
            sigma = next(t for t in itertools.product((0, 1), repeat=3) if t not in I)
            tied = [i for i, y in enumerate(X) if y in hub]
            for a in sorted(set(range(n)) - set(L1) - hub):
                for hv, av in itertools.product((0, 1), repeat=2):
                    rows = A[(A[:, h] == hv) & (A[:, a] == av)]
                    pats = {tuple(int(b) for b in r) for r in rows[:, X]}
                    if len(pats) != 1:
                        continue
                    tau = next(iter(pats))
                    oi = odd_index(tau, sigma)
                    if tied:
                        out["(i) hub tied to a non-odd port" if tied[0] != oi else "(i') hub tied to the odd port"] += 1
                        continue
                    j, k = [i for i in range(3) if i != oi]
                    allowed = {(int(r[X[j]]), int(r[X[k]])) for r in A if int(r[h]) == hv}
                    excl = {(b1, b2) for b1 in (0, 1) for b2 in (0, 1)} - allowed
                    if not excl:
                        out["(iv) hub free of the two non-odd ports"] += 1
                    elif any((e[0] != tau[j]) + (e[1] != tau[k]) == 1 for e in excl):
                        out["(ii) two-port knot, excluded pattern one step from the pinned one"] += 1
                    else:
                        out["(ii') two-port knot, excluded pattern two steps from the pinned one"] += 1
    return out



T0 = time.time()
tot = collections.Counter()
for size, seeds in ((16, range(3)), (18, range(2)), (20, range(1))):
    for seed in seeds:
        g = PL.grow(size, 100 + seed)
        for swap in (False, True):
            H, s, n = PL.to_space(g, swap)
            assert PL.incidence_planar(H) and G.fails_globally(H, s, n)
            c = classify_pinnings(H, s, n)
            tot.update(c)
            print("grown %d seed %d%s: %s  %.0fs" % (size, 100 + seed, " dual" if swap else "", dict(c), time.time() - T0), flush=True)
print("TOTAL", dict(tot))
