"""What the arrangement of the count's rows holds: readings of a grown split base's disagreement-count table, all invariant under
renaming its distinctions, from the sorted rows (COUNT-BALLS-20261118-001's reading (a)) up to the full table.

Every reading is a multiset over the starts x of a view of x:
- a:   the sorted row of counts from x (x's ball growth);
- N1:  x's row with the rows of its nearest distinctions (those at the least count from x);
- W2:  x's row with every other row, each tagged by its count from x (one round of colour refinement);
- WL:  1-WL colour refinement on the count-weighted complete table, run 2n rounds (no new split of the starts after that);
- B_r: the table restricted to the distinctions within count r of x, with x marked, up to renaming (purely local; no rows).
Colours and views are named by a SHA-256 digest of their full description (24 hex digits), so equal names mean equal views
across bases and across processes."""
import hashlib
import itertools
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "experiments/STATE-RULES-20261117-001B/STATE-RULES-20261117-001B-E001_rules"))
sys.path.insert(0, str(ROOT / "experiments/COUNT-BALLS-20261118-001B/COUNT-BALLS-20261118-001B-E001_outlines"))
import rules as R  # noqa: E402
import census as CB  # noqa: E402  (reachable populations, chromatic number; frozen in COUNT-BALLS-20261118-001B)

pc = int.bit_count


def intern(t):
    return hashlib.sha256(repr(t).encode()).hexdigest()[:24]


def table(states, n):
    Z, O = R.columns(list(states), n)
    return [[pc(Z[u] & O[v]) + pc(O[u] & Z[v]) for v in range(n)] for u in range(n)]


def rows(D):
    n = len(D)
    return [tuple(sorted(D[x][y] for y in range(n) if y != x)) for x in range(n)]


def read_a(D):
    return tuple(sorted(rows(D)))


def read_N1(D):
    n = len(D)
    rw = rows(D)
    out = []
    for x in range(n):
        m = min(D[x][y] for y in range(n) if y != x)
        out.append((rw[x], tuple(sorted(rw[y] for y in range(n) if y != x and D[x][y] == m))))
    return tuple(sorted(out))


def wl_colours(D, rounds, start=None):
    n = len(D)
    c = list(start) if start is not None else [""] * n
    for _ in range(rounds):
        c = [intern((c[x], tuple(sorted((D[x][y], c[y]) for y in range(n) if y != x)))) for x in range(n)]
    return c


def read_W2(D):
    return tuple(sorted(wl_colours(D, 2)))


def read_WL(D):
    return tuple(sorted(wl_colours(D, 2 * len(D))))


def _refine(M, col):
    """Colour refinement inside a view until the number of classes stops growing."""
    m = len(M)
    while True:
        new = [intern((col[v], tuple(sorted((M[v][u], col[u]) for u in range(m) if u != v)))) for v in range(m)]
        if len(set(new)) == len(set(col)):
            return new
        col = new


def canon_view(M):
    """Canonical form of a small count table M with node 0 marked, by individualization and refinement: refine, and while a
    colour class has several members, individualize each member of the first such class in turn and keep the least result."""
    m = len(M)

    def search(col):
        col = _refine(M, col)
        classes = {}
        for v in range(m):
            classes.setdefault(col[v], []).append(v)
        multi = [c for c in sorted(classes) if len(classes[c]) > 1]
        if not multi:
            order = sorted(range(m), key=lambda v: col[v])
            return (tuple(col[v] for v in order),
                    tuple(M[order[i]][order[j]] for i in range(m) for j in range(i + 1, m)))
        best = None
        for v in classes[multi[0]]:
            c2 = list(col)
            c2[v] = intern(("individualized", col[v]))
            cand = search(c2)
            if best is None or cand < best:
                best = cand
        return best

    return intern(search(["x"] + [""] * (m - 1)))


def read_B(D, r):
    n = len(D)
    out = []
    for x in range(n):
        ball = [x] + [y for y in range(n) if y != x and D[x][y] <= r]
        out.append(canon_view([[D[u][v] for v in ball] for u in ball]))
    return tuple(sorted(out))


def read_BW(D, r):
    """1-WL on the full table started from each start's view within count r (stronger than both B_r and WL)."""
    n = len(D)
    start = []
    for x in range(n):
        ball = [x] + [y for y in range(n) if y != x and D[x][y] <= r]
        start.append(canon_view([[D[u][v] for v in ball] for u in ball]))
    return tuple(sorted(wl_colours(D, 2 * n, start=start)))


def diagnostics(D):
    rw = rows(D)
    return {"rows_distinct": len(set(rw)) == len(rw), "least_row_max": min(max(r) for r in rw)}


READINGS = {"a": read_a, "N1": read_N1, "W2": read_W2, "WL": read_WL, "BW4": lambda D: read_BW(D, 4)}


def targets(states, n):
    full = (1 << n) - 1
    sp = R.splits(list(states), n)
    return CB.chromatic(sp, full), R.lattice_dimension(sp, full)


def assess(bases, radii):
    """bases: list of (states, n, class id). For each reading, groups of classes with equal readings and how many mix k or lam."""
    info = []
    for st, n, cid in bases:
        D = table(st, n)
        k, lam = targets(st, n)
        rd = {name: f(D) for name, f in READINGS.items()}
        for r in radii:
            rd[f"B{r}"] = read_B(D, r)
        info.append((cid, k, lam, len(st), rd))
    out = {}
    for name in list(READINGS) + [f"B{r}" for r in radii]:
        groups = {}
        for cid, k, lam, N, rd in info:
            groups.setdefault(rd[name], []).append((cid, k, lam, N))
        multi = [g for g in groups.values() if len(g) > 1]
        out[name] = {"groups": len(groups), "multi": len(multi),
                     "mix_k": sum(len({k for _, k, _, _ in g}) > 1 for g in multi),
                     "mix_lam": sum(len({l for _, _, l, _ in g}) > 1 for g in multi),
                     "mix_N": sum(len({N for _, _, _, N in g}) > 1 for g in multi),
                     "first_mix_k": next(([c for c, *_ in g] for g in multi if len({k for _, k, _, _ in g}) > 1), None)}
    return out, info
