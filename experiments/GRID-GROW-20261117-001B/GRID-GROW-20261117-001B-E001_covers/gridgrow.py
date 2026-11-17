"""GRID-GROW-20261117-001B-E001: growing the two-way grid's cut system with knots, one distinction at a time.

A shape is a Young diagram S (cells (x, y), x, y >= 0, closed downward and leftward).  Its cut system is the base whose states are
the column cuts {x >= k}, the row cuts {y >= k}, their flips and the two constants.  A step adds one outer corner p.  Starting from
the cut system of S, the states with p free form the ambient set; the target is the cut system of S + p; the bad states are the
ambient ones not in the target.  A candidate is any of the 34 three-place knots on an ordered triple of cells containing p that
allows every target state; it excludes some bad states.  A step's minimal covers are the smallest sets of candidates excluding
every bad state.  The single four-place parity on p's unit square is also tried.
"""
import itertools

BTW = frozenset({(0, 1, 0), (1, 0, 1)})


def is_betweenness(ex):
    """A betweenness knot in some place order: excludes one complementary pair {s, s-bar} with s not constant
    (robust to the order in which the places were listed)."""
    ex = list(ex)
    if len(ex) != 2 or tuple(1 - v for v in ex[0]) != ex[1]:
        return False
    return len(set(ex[0])) == 2


def knots34():
    states = list(itertools.product((0, 1), repeat=3))
    out = []
    for k in range(1, 5):
        for ex in itertools.combinations(states, k):
            if all(sum(a != b for a, b in zip(x, y)) != 1 for x, y in itertools.combinations(ex, 2)):
                out.append(frozenset(ex))
    return out


KNOTS = knots34()


def young_diagrams(R, C):
    """All nonempty Young diagrams inside R columns x C rows, as frozensets of cells."""
    out = []
    for parts in itertools.product(range(R + 1), repeat=C):          # parts[y] = row length, nonincreasing
        if all(parts[i] >= parts[i + 1] for i in range(C - 1)) and parts[0] > 0:
            out.append(frozenset((x, y) for y in range(C) for x in range(parts[y])))
    return out


def outer_corners(S, R, C):
    out = []
    for x in range(R):
        for y in range(C):
            if (x, y) in S:
                continue
            if (x == 0 or (x - 1, y) in S) and (y == 0 or (x, y - 1) in S):
                out.append((x, y))
    return out


def cut_states(cells):
    """Cut system of a shape on the ordered cells (bit i = cells[i])."""
    n = len(cells)
    full = (1 << n) - 1
    out = {0, full}
    xs = sorted({c[0] for c in cells}); ys = sorted({c[1] for c in cells})
    for k in xs[1:]:
        m = sum(1 << i for i, c in enumerate(cells) if c[0] >= k)
        out |= {m, full ^ m}
    for k in ys[1:]:
        m = sum(1 << i for i, c in enumerate(cells) if c[1] >= k)
        out |= {m, full ^ m}
    return out


def box_base_equals_cuts(cells):
    n = len(cells)
    inbox = lambda a, b, c: min(a[0], c[0]) <= b[0] <= max(a[0], c[0]) and min(a[1], c[1]) <= b[1] <= max(a[1], c[1])
    trip = [(i, j, k) for i, j, k in itertools.permutations(range(n), 3) if inbox(cells[i], cells[j], cells[k])]
    sts = {s for s in range(1 << n) if all(not (((s >> i) & 1) == ((s >> k) & 1) != ((s >> j) & 1)) for i, j, k in trip)}
    return sts == cut_states(cells)


def l1(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def step_covers(S, p):
    old = sorted(S)
    cells = old + [p]
    n = len(cells)
    P = n - 1
    old_states = cut_states(old)
    ambient = {s | (b << P) for s in old_states for b in (0, 1)}
    target = cut_states(cells)
    assert target <= ambient
    bad = sorted(ambient - target)
    bidx = {s: i for i, s in enumerate(bad)}
    cands = {}
    for trip in itertools.permutations(range(n), 3):
        if P not in trip:
            continue
        for ex in KNOTS:
            proj = lambda s: tuple((s >> t) & 1 for t in trip)
            if any(proj(s) in ex for s in target):
                continue
            hit = frozenset(bidx[s] for s in bad if proj(s) in ex)
            if not hit:
                continue
            key = (frozenset(trip), hit)
            if key not in cands:
                cands[key] = (trip, ex, hit)
    items = list(cands.values())
    nb = len(bad)
    fullmask = (1 << nb) - 1
    def min_cover(pool):
        """Fewest candidates covering every bad state (breadth-first over covered sets); and one such cover."""
        masks = [(sum(1 << b for b in c[2]), c) for c in pool]
        dist = {0: (0, None, None)}
        frontier = [0]
        while frontier and fullmask not in dist:
            nxt = []
            for m in frontier:
                for mk, c in masks:
                    m2 = m | mk
                    if m2 not in dist:
                        dist[m2] = (dist[m][0] + 1, m, c)
                        nxt.append(m2)
            frontier = nxt
        if fullmask not in dist:
            return None, None
        combo, m = [], fullmask
        while m:
            _, prev, c = dist[m]
            combo.append(c)
            m = prev
        return dist[fullmask][0], combo
    size, combo = min_cover(items)
    by_radius = {}
    for r in range(1, 2 * (max(c[0] for c in cells) + max(c[1] for c in cells)) + 2):
        pool = [c for c in items if all(l1(cells[t], p) <= r for t in c[0])]
        k, _ = min_cover(pool)
        by_radius[r] = k
    def describe(combo):
        pts = sorted({cells[t] for c in combo for t in c[0] if t != P})
        return {"knots": [{"cells": [cells[t] for t in c[0]], "betweenness": is_betweenness(c[1])} for c in combo],
                "knots_full": [{"cells": [cells[t] for t in c[0]], "excluded": c[1]} for c in combo],
                "max_l1_from_p": max(l1(q, p) for q in pts)}
    smallest_r = min((r for r, k in by_radius.items() if k == size), default=None)
    local_combo = None
    if smallest_r is not None:
        _, local_combo = min_cover([c for c in items if all(l1(cells[t], p) <= smallest_r for t in c[0])])
    # four-place parity on the unit square
    sq = [(p[0] - 1, p[1] - 1), (p[0] - 1, p[1]), (p[0], p[1] - 1)]
    parity_cover = None
    if all(q in S for q in sq):
        idxs = [cells.index(q) for q in sq] + [P]
        parity_cover = all(sum((s >> t) & 1 for t in idxs) % 2 == 0 for s in target) and \
            all(sum((s >> t) & 1 for t in idxs) % 2 == 1 for s in bad)
    kind = "corner" if (p[0] > 0 and p[1] > 0) else "new line"
    single = [c for c in items if len(c[2]) == nb] if nb else []
    single_desc = [{"cells": [cells[t] for t in c[0]], "betweenness": is_betweenness(c[1])} for c in single]
    singles_distinct = len({frozenset(c[0]) for c in single})
    local = [c for c in items if all(l1(cells[t], p) <= 2 for t in c[0])]
    local3 = [combo for combo in itertools.combinations(local, 3) if frozenset().union(*[c[2] for c in combo]) == frozenset(range(nb))] if nb else []
    local3_distinct = {frozenset((frozenset(c[0]), c[1]) for c in combo) for combo in local3}
    return {"single_knot_covers": singles_distinct, "single_knot_cover_cells": single_desc[:2],
            "local_three_covers_distinct": len(local3_distinct),
            "local_three_covers_all_betweenness": all(is_betweenness(c[1]) for combo in local3 for c in combo) if local3 else None,
            "shape": sorted(S), "p": p, "kind": kind, "bad": len(bad), "candidates": len(items),
            "min_knots": size, "min_knots_within_l1": by_radius,
            "smallest_radius_for_min": smallest_r,
            "example_cover": describe(local_combo) if local_combo else None,
            "unit_square_parity_covers": parity_cover}
