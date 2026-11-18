"""Library for LOCAL-ROOM-20261118-001B-E001: the cheapest rule with a reach limit read from the states.

The moves are A99's (one new distinction with up to three betweenness knots, every old state kept, not a copy). The reach limit r:
every knot's two old distinctions u, v must be within r splits of each other, that is d(u, v) <= 2r in the disagreement count, read
from the states alone. The rule takes the fewest states, ties uniform over distinct extensions. It builds on STATE-RULES's
rules.py (closed; pinned in the contract)."""
import collections
import itertools
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.append(os.path.join(ROOT, "experiments", "STATE-RULES-20261117-001B", "STATE-RULES-20261117-001B-E001_rules"))
import rules as R  # noqa: E402

pc = R.pc


def local_extensions(states, n, K, r):
    """Admitted extensions with up to K knots whose old pairs lie within r splits: {(A0, A1): knots}."""
    masks, Z, O = R.knot_masks(states, n)
    dist = lambda u, v: pc(Z[u] & O[v]) + pc(O[u] & Z[v])
    masks = [m for m in masks if dist(*[x for x in m[0] if x != n]) <= 2 * r]
    N = len(states)
    full = (1 << N) - 1
    ties = {(Z[u], O[u]) for u in range(n)}
    found = {}

    def offer(a0, a1, ks):
        if (a0, a1) in found or (a0, a1) in ties or pc(a0) + pc(a1) >= 2 * N:
            return
        found[(a0, a1)] = ks
    m = len(masks)
    for i in range(m):
        ki, a0, a1 = masks[i]
        offer(a0, a1, (ki,))
        if K < 2:
            continue
        for j in range(i + 1, m):
            kj, b0, b1 = masks[j]
            c0, c1 = a0 & b0, a1 & b1
            if (c0 | c1) != full:
                continue
            offer(c0, c1, (ki, kj))
            if K < 3:
                continue
            for l in range(j + 1, m):
                kl, d0, d1 = masks[l]
                e0, e1 = c0 & d0, c1 & d1
                if (e0 | e1) == full:
                    offer(e0, e1, (ki, kj, kl))
    return found


def options(states, n, K, r):
    ext = local_extensions(states, n, K, r)
    if not ext:
        return []
    items = list(ext.items())
    sizes = [pc(a0) + pc(a1) for (a0, a1), _ in items]
    low = min(sizes)
    top = [kv for kv, s in zip(items, sizes) if s == low]
    return [(1.0 / len(top), R.apply(states, n, a0, a1), ks) for (a0, a1), ks in top]


def exact(start, nmax, K, r, canon=None):
    canon = canon or R.Canon()
    n, states = R.seed(start)
    dist = {canon.cid(states, n): 1.0}
    levels, stalled = [], 0.0
    while True:
        rows = []
        for c, p in sorted(dist.items()):
            st, nn, _ = canon.reps[c]
            rows.append((c, p, R.measure(list(st), nn)))
        levels.append({"n": n, "classes": len(dist), "dist": rows, "stalled_before": stalled})
        if n >= nmax or not dist:
            break
        new = collections.Counter()
        for c, p in dist.items():
            st, nn, _ = canon.reps[c]
            opts = options(list(st), nn, K, r)
            if not opts:
                stalled += p
                continue
            for w, o, _ in opts:
                new[canon.cid(o, nn + 1)] += p * w
        dist = dict(new)
        n += 1
    return levels, canon


def grow(start, nmax, seed_value, K, r):
    rng = random.Random(seed_value)
    n, states = R.seed(start)
    trace = [{"n": n, **R.measure(states, n)}]
    while n < nmax:
        perm = list(range(n))
        rng.shuffle(perm)
        blind = R.relabel(states, n, perm)
        opts = options(blind, n, K, r)
        if not opts:
            trace.append({"n": n + 1, "stopped": "no admitted move"})
            break
        _, states, ks = rng.choice(opts)
        n += 1
        trace.append({"n": n, "excess": len(states) - len(blind), **R.measure(states, n)})
    return states, n, trace


# ---------- the class law: one remembered bit per split ----------

def splits_of(states, n):
    full = (1 << n) - 1
    return sorted({min(s, full ^ s) for s in states if s not in (0, full)})


def norm(m, n):
    full = (1 << n) - 1
    return min(m, full ^ m)


def class_extensions(states, n, classes):
    """Admitted extensions with up to three knots such that every knot's old pair is separated by splits of pairwise different
    classes, and no step makes a split whose restriction to the old distinctions is constant (no pendants).  classes maps each
    split (normalised mask over the old distinctions) to its class."""
    masks, Z, O = R.knot_masks(states, n)
    full_old = (1 << n) - 1
    sp = splits_of(states, n)

    def separating(u, v):
        return [m for m in sp if ((m >> u) & 1) != ((m >> v) & 1)]

    ok_pair = {}
    for (k, a0, a1) in masks:
        u, v = [x for x in k if x != n]
        key = (min(u, v), max(u, v))
        if key not in ok_pair:
            cl = [classes[m] for m in separating(u, v)]
            ok_pair[key] = len(cl) == len(set(cl))
    masks = [m for m in masks if ok_pair[tuple(sorted(x for x in m[0] if x != n))]]
    N = len(states)
    full = (1 << N) - 1
    ties = {(Z[u], O[u]) for u in range(n)}
    found = {}

    def offer(a0, a1, ks):
        if (a0, a1) in found or (a0, a1) in ties or R.pc(a0) + R.pc(a1) >= 2 * N:
            return
        new = R.apply(states, n, a0, a1)
        for s in new:                                    # no split that is constant on the old distinctions (a pendant)
            if s not in (0, (1 << (n + 1)) - 1) and (s & full_old) in (0, full_old):
                return
        found[(a0, a1)] = ks
    m = len(masks)
    for i in range(m):
        ki, a0, a1 = masks[i]
        offer(a0, a1, (ki,))
        for j in range(i + 1, m):
            kj, b0, b1 = masks[j]
            c0, c1 = a0 & b0, a1 & b1
            if (c0 | c1) != full:
                continue
            offer(c0, c1, (ki, kj))
            for l in range(j + 1, m):
                kl, d0, d1 = masks[l]
                e0, e1 = c0 & d0, c1 & d1
                if (e0 | e1) == full:
                    offer(e0, e1, (ki, kj, kl))
    return found


def carry_classes(new_states, n, classes):
    """Each split of the new base inherits the class of its restriction to the old distinctions."""
    out = {}
    for m in splits_of(new_states, n + 1):
        out[m] = classes[norm(m & ((1 << n) - 1), n)]
    return out


def class_grow(nmax, seed_value):
    """From the 2 x 2 pattern with its two splits in two classes."""
    rng = random.Random(seed_value)
    n, states = R.seed("2x2")
    sp = splits_of(states, n)
    classes = {sp[0]: 0, sp[1]: 1}
    trace = [{"n": n, **R.measure(states, n)}]
    while n < nmax:
        ext = class_extensions(states, n, classes)
        if not ext:
            trace.append({"n": n + 1, "stopped": "no admitted move"})
            break
        items = list(ext.items())
        low = min(R.pc(a0) + R.pc(a1) for (a0, a1), _ in items)
        (a0, a1), ks = rng.choice([kv for kv in items if R.pc(kv[0][0]) + R.pc(kv[0][1]) == low])
        new = R.apply(states, n, a0, a1)
        classes = carry_classes(new, n, classes)
        excess = len(new) - len(states)
        states, n = new, n + 1
        counts = collections.Counter(classes.values())
        full_grid = (counts[0] + 1) * (counts[1] + 1) == n
        trace.append({"n": n, "excess": excess, **R.measure(states, n),
                      "class_splits": [counts[0], counts[1]], "full_grid": full_grid})
    return states, n, trace
