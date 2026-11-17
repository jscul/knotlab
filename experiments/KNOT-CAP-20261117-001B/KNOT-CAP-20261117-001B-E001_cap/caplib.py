"""Library for KNOT-CAP-20261117-001B-E001: growth with a cap on how many knots a distinction may join.

It builds on STATE-RULES-20261117-001B-E001's rules.py (closed; imported from its folder, sha256 pinned in the contract). A base
is (states, knots). A move adds the new distinction n with an irredundant set of 1 to 3 betweenness knots, each on n and two old
distinctions, admitted as in A99 (every old state extends; n constrained and not a copy).

The cap c: a move is allowed only if afterwards every distinction lies in at most c knots. A distinction already over the cap
takes no more. The pair cap m: a move is allowed only if afterwards every pair of distinctions lies together in at most m knots
(the advisor's parameter-free variant at m = 2). With knot-locality, each new knot's two old distinctions must already share a
knot.

Erasure (the owner's question, passed on from Codex): grow with a knot-reading rule to n0, forget the knots, and continue with
the states-only fewest-states rule of STATE-RULES (rules.step, extensions counted one by one).

The weighting is fewest states, ties uniform over knot sets. The rule reads the states and the knots, renamed at random before
each read."""
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


def degrees(knots, n):
    d = [0] * n
    for k in knots:
        for x in k:
            d[x] += 1
    return d


def pair_counts(knots):
    return collections.Counter((min(a, b), max(a, b)) for k in knots for a, b in itertools.combinations(k, 2))


def cap_moves(states, n, knots, c, local=None, pair=None):
    """Moves of R.knot_moves (up to three knots; local None or "knot") that keep every distinction within c knots and, when pair
    is given, every pair of distinctions within pair knots."""
    deg = degrees(knots, n)
    pcount = pair_counts(knots) if pair is not None else None
    out = []
    for a0, a1, ks in R.knot_moves(states, n, knots, 3, local):
        if len(ks) > c:
            continue
        add = collections.Counter(x for k in ks for x in k if x != n)
        if not all(deg[x] + m <= c for x, m in add.items()):
            continue
        if pair is not None:
            new = pair_counts(ks)
            if any(pcount.get(q, 0) + m > pair for q, m in new.items()):
                continue
        out.append((a0, a1, ks))
    return out


def cap_step(states, n, knots, c, rng, local=None, canon=None, pair=None):
    perm = list(range(n))
    rng.shuffle(perm)
    blind, bknots = R.relabel(states, n, perm), R.relabel_knots(knots, perm)
    moves = cap_moves(blind, n, bknots, c, local, pair)
    if not moves:
        return None, None, None, {"options": 0}
    sizes = [pc(a0) + pc(a1) for a0, a1, _ in moves]
    low = min(sizes)
    top = [mv for mv, s in zip(moves, sizes) if s == low]
    rec = {"options": len(moves), "top_options": len(top), "N": len(blind), "excess": low - len(blind)}
    if canon is not None:
        rec["top_classes"] = len({canon.cid(R.apply(blind, n, a0, a1), n + 1, bknots + list(ks)) for a0, a1, ks in top})
    a0, a1, ks = rng.choice(top)
    return R.apply(blind, n, a0, a1), bknots + list(ks), ks, rec


def cap_grow(start, nmax, seed_value, c, local=None, canon=None, pair=None, erase_at=None):
    rng = random.Random(seed_value)
    n, knots = R.SEEDS[start][0], list(R.SEEDS[start][1])
    states = R.base_from_knots(n, knots)
    trace = [{"n": n, **R.measure(states, n), "max_degree": max(degrees(knots, n))}]
    while n < nmax:
        if erase_at is not None and n >= erase_at:
            new, ks, rec = R.step(states, n, "fewest", 3, rng)          # the knots are forgotten: states only
            if new is None:
                trace.append({"n": n + 1, "stopped": "no admitted extension"})
                break
            states, n = new, n + 1
            trace.append({"n": n, "knots": len(ks), "erased": True, **rec, **R.measure(states, n), "state_class": None})
            continue
        new, nk, ks, rec = cap_step(states, n, knots, c, rng, local, canon, pair)
        if new is None:
            trace.append({"n": n + 1, "stopped": "no allowed move"})
            break
        states, knots, n = new, nk, n + 1
        trace.append({"n": n, "knots": len(ks), **rec, **R.measure(states, n), "max_degree": max(degrees(knots, n))})
    return states, knots, n, trace


def cap_exact(start, nmax, c, local=None, canon=None, pair=None):
    """Exact distribution over classes of (states, knots), fewest states, ties uniform over knot sets; the mass that stalls."""
    canon = canon or R.Canon()
    n, knots = R.SEEDS[start][0], list(R.SEEDS[start][1])
    states = R.base_from_knots(n, knots)
    dist = {canon.cid(states, n, knots): 1.0}
    levels = []
    stalled = 0.0
    while True:
        rows = []
        for cl, p in sorted(dist.items()):
            st, nn, kk = canon.reps[cl]
            rows.append((cl, p, {**R.measure(list(st), nn), "max_degree": max(degrees(kk, nn))}))
        levels.append({"n": n, "classes": len(dist), "dist": rows, "stalled_before": stalled})
        if n >= nmax or not dist:
            break
        new, determined = {}, 0.0
        for cl, p in dist.items():
            st, nn, kk = canon.reps[cl]
            moves = cap_moves(list(st), nn, list(kk), c, local, pair)
            if not moves:
                stalled += p
                continue
            sizes = [pc(a0) + pc(a1) for a0, a1, _ in moves]
            low = min(sizes)
            top = [mv for mv, s in zip(moves, sizes) if s == low]
            tops = set()
            for a0, a1, ks in top:
                d = canon.cid(R.apply(list(st), nn, a0, a1), nn + 1, list(kk) + list(ks))
                new[d] = new.get(d, 0.0) + p / len(top)
                tops.add(d)
            if len(tops) == 1:
                determined += p
        levels[-1]["determined_next"] = determined
        dist = new
        n += 1
    return levels, canon


def states_mixture(levels, canon, state_canon):
    """The distribution over classes of states alone (knots forgotten) at the last level of cap_exact."""
    out = collections.Counter()
    for cl, p, _ in levels[-1]["dist"]:
        st, nn, kk = canon.reps[cl]
        out[state_canon.cid(list(st), nn)] += p
    return dict(out)


def states_exact_from(mix, state_canon, nmax):
    """Exact states-only fewest-states continuation (rules.options, three knots, extensions counted one by one) of a mixture of
    classes of states, to nmax.  Returns [(n, {class: p})]."""
    out = []
    dist = dict(mix)
    n = state_canon.reps[next(iter(dist))][1]
    out.append((n, dict(dist)))
    while n < nmax:
        new = collections.Counter()
        for cl, p in dist.items():
            st, nn, _ = state_canon.reps[cl]
            for w, o, _ in R.options(list(st), nn, "fewest", 3):
                new[state_canon.cid(o, nn + 1)] += p * w
        dist = dict(new)
        n += 1
        out.append((n, dict(dist)))
    return out


def tv(p, q):
    keys = set(p) | set(q)
    return 0.5 * sum(abs(p.get(k, 0.0) - q.get(k, 0.0)) for k in keys)


def feature_key(m):
    return {"N": m["N"], "splits": m["splits"], "crossings": m["crossings"], "lam": m["lam"], "k": m["k"]}
