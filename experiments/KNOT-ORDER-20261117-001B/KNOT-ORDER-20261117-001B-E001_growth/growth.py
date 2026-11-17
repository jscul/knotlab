"""Read-out for KNOT-ORDER-20261117-001B-E001 (frozen before running).

B(a, b, c) is the knot excluding 010 and 101 on (a, b, c): b lies between a and c.  A line on positions 0..n-1 is the base whose
states are the thresholds (values change at most once along the positions).

R1 counts: consecutive triples and all triples at n = 4, 5; B(0,1,2) with B(0,2,3).
R2 growth from the single knot B(0, 1, 2) to n = 14 under four rules (one knot per step, new distinction n):
   start      B(start, end, new)                       start and end are the line's two ends as the rule tracks them
   neighbour  B(prev, end, new)                        prev = the distinction added before the end
   random     B(x, end, new), x uniform among the earlier distinctions other than the end (seed sha256 KO:random)
   states     find the ends from the allowed states alone (the distinctions strictly between no two others in the
              disagreement count), choose a side at random (seed sha256 KO:states), add B(other end, chosen end, new)
   spiral     B(x_(t-2), new, x_(t-1)): the new distinction between the last two added (inward growth, no hub)
   At each n: number of states, whether every state is a threshold along the rule's own order, and for states, whether the
   ends were found uniquely (exactly two distinctions between no two others).
R3 exhaustive single-knot check, m = 3..8: starting from the line on 0..m-1, every one of the 34 three-place knots on every
   ordered triple containing the new distinction m: which keep the base a line (thresholds along some order of 0..m)?  Counted
   as distinct constraints (the set of joint states of 0..m each excludes), with their kind.
R4 static two-way test: B(a, b, c) for every b in the box of a and c (coordinatewise between) on the 3 x 3 and 3 x 4 grids:
   number of states, whether d = 2 L1 for every pair, and whether the strict betweenness triples are exactly the box triples.
    python3 -B growth.py      (writes artifacts/.../results.json)
"""
import hashlib
import itertools
import json
import os
import random
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
OUT = os.path.join(ROOT, "artifacts", "KNOT-ORDER-20261117-001B", "KNOT-ORDER-20261117-001B-E001_growth")
BTW = frozenset({(0, 1, 0), (1, 0, 1)})


def allowed(n, knots):
    """knots: list of (places, excluded set)."""
    out = []
    for s in range(1 << n):
        if all(tuple((s >> p) & 1 for p in pl) not in ex for pl, ex in knots):
            out.append(s)
    return out


def is_threshold_line(n, sts, order):
    """Every state changes value at most once along order, and every threshold along order is present."""
    want = set()
    for k in range(n + 1):
        a = sum(1 << order[i] for i in range(k, n))
        want.add(a)
        want.add(((1 << n) - 1) ^ a)
    return set(sts) == want


def counts(n, sts):
    return [[sum(((s >> u) ^ (s >> v)) & 1 for s in sts) for v in range(n)] for u in range(n)]


def ends_from_states(n, sts):
    D = counts(n, sts)
    def between_some(w):
        return any(D[u][v] == D[u][w] + D[w][v] and D[u][w] > 0 and D[w][v] > 0
                   for u in range(n) for v in range(n) if u != v and w not in (u, v))
    return [w for w in range(n) if not between_some(w)]


def order_of(n, sts):
    """Recover an order along which the states are thresholds, from the counts: sort by count from one end."""
    ends = ends_from_states(n, sts)
    if len(ends) != 2:
        return None
    D = counts(n, sts)
    return sorted(range(n), key=lambda v: D[ends[0]][v])


def grow(rule, nmax=14):
    rng = random.Random(int.from_bytes(hashlib.sha256(f"KO:{rule}".encode()).digest()[:8], "little"))
    knots = [((0, 1, 2), BTW)]
    order = [0, 1, 2]                     # the rule's own order (ends: order[0], order[-1])
    spiral = [1, 2]                       # for the spiral: the last two placed, adjacent in the line 0, 1, 2
    rows = []
    for n in range(3, nmax + 1):
        sts = allowed(n, knots)
        row = {"n": n, "states": len(sts), "line_along_rule_order": is_threshold_line(n, sts, order)}
        if rule == "states":
            ends = ends_from_states(n, sts)
            row["ends_found"] = sorted(ends)
            row["ends_unique"] = len(ends) == 2
        rows.append(row)
        if n == nmax:
            break
        new = n
        if rule == "start":
            knots.append(((order[0], order[-1], new), BTW)); order = order + [new]
        elif rule == "neighbour":
            knots.append(((order[-2], order[-1], new), BTW)); order = order + [new]
        elif rule == "random":
            x = rng.choice(order[:-1])
            knots.append(((x, order[-1], new), BTW)); order = order + [new]
        elif rule == "spiral":
            knots.append(((spiral[-2], new, spiral[-1]), BTW))
            spiral.append(new)
            i = order.index(spiral[-3]); j = order.index(spiral[-2])
            lo, hi = sorted((i, j))
            order = order[:lo + 1] + [new] + order[lo + 1:]
        elif rule == "states":
            ends = ends_from_states(n, sts)
            if len(ends) != 2:
                row["stopped"] = "ends not unique"
                break
            near = rng.choice(ends)
            far = ends[1] if near == ends[0] else ends[0]
            knots.append(((far, near, new), BTW))
            ordr = order_of(n, sts)
            order = (ordr if ordr[-1] == near else ordr[::-1]) + [new]
    return rows


def all_knots34():
    states = list(itertools.product((0, 1), repeat=3))
    out = []
    for k in range(1, 5):
        for ex in itertools.combinations(states, k):
            if all(sum(a != b for a, b in zip(x, y)) != 1 for x, y in itertools.combinations(ex, 2)):
                out.append(frozenset(ex))
    return out


def single_knot_check(m):
    base = [((i, j, k), BTW) for i, j, k in itertools.combinations(range(m), 3)]
    keep = {}
    for ex in all_knots34():
        for pl in itertools.permutations(range(m + 1), 3):
            if m not in pl:
                continue
            mask = frozenset(s for s in range(1 << (m + 1)) if tuple((s >> p) & 1 for p in pl) in ex)
            if mask in keep:
                continue
            sts = allowed(m + 1, base + [(pl, ex)])
            o = order_of(m + 1, sts)
            if o is not None and is_threshold_line(m + 1, sts, o):
                keep[mask] = {"places": pl, "excluded": sorted(ex), "betweenness": ex == BTW, "new_in_middle": pl[1] == m}
    return {"distinct_line_keeping_knots": len(keep), "knots": list(keep.values())}


def grid_test(nr, nc):
    pts = [(i, j) for i in range(nr) for j in range(nc)]
    idx = {p: k for k, p in enumerate(pts)}
    inbox = lambda a, b, c: min(a[0], c[0]) <= b[0] <= max(a[0], c[0]) and min(a[1], c[1]) <= b[1] <= max(a[1], c[1])
    knots = [((idx[a], idx[b], idx[c]), BTW) for a, b, c in itertools.permutations(pts, 3) if inbox(a, b, c)]
    n = len(pts)
    sts = allowed(n, knots)
    D = counts(n, sts)
    l1 = all(D[idx[a]][idx[b]] == 2 * (abs(a[0] - b[0]) + abs(a[1] - b[1])) for a in pts for b in pts)
    btw = {(u, w, v) for u in range(n) for v in range(u + 1, n) for w in range(n)
           if w not in (u, v) and D[u][w] > 0 and D[w][v] > 0 and D[u][v] == D[u][w] + D[w][v]}
    box = {(idx[a], idx[b], idx[c]) for a, b, c in itertools.permutations(pts, 3) if idx[a] < idx[c] and inbox(a, b, c)}
    return {"grid": f"{nr}x{nc}", "states": len(sts), "predicted_states": 2 * (nr + nc) - 2, "d_is_2L1": l1,
            "betweenness_is_box": btw == box}


def main():
    os.makedirs(OUT, exist_ok=True)
    res = {"started": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    c = {}
    for n in (4, 5):
        cons = allowed(n, [((i, i + 1, i + 2), BTW) for i in range(n - 2)])
        allt = allowed(n, [((i, j, k), BTW) for i, j, k in itertools.combinations(range(n), 3)])
        c[n] = {"consecutive": len(cons), "all_triples": len(allt),
                "extra": [format(s, f"0{n}b")[::-1] for s in cons if s not in allt]}
    c["B(0,1,2)+B(0,2,3)"] = len(allowed(4, [((0, 1, 2), BTW), ((0, 2, 3), BTW)]))
    res["R1"] = c
    res["R2"] = {rule: grow(rule) for rule in ("start", "neighbour", "random", "states", "spiral")}
    res["R3"] = {m: single_knot_check(m) for m in range(3, 9)}
    res["R4"] = [grid_test(3, 3), grid_test(3, 4)]
    res["finished"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    with open(os.path.join(OUT, "results.json"), "w") as f:
        json.dump(res, f, indent=1, default=str)
    print("wrote", os.path.join(OUT, "results.json"), res["started"], res["finished"])


if __name__ == "__main__":
    main()
