"""Referee R1 for ROUND-FREE-20261119-001 (own code; parts.py, animals.py and covermodel.py are not imported).

  ../../../.venv/bin/python -B referee_free.py <part> > referee_free_<part>.json      (from this directory)

Parts:
  partc     the part shares by size, by the referee's own brute force on the cover (Redelmeier enumeration of connected vertex
            sets in the cover built lazily as non-backtracking walks of the vertex-block incidence graph; RING-PAIR-R1's
            construction), each cluster labelled by the parts its points lie over; orbits counted as sum over root points of the
            clusters containing that root, divided by size.  For the two frozen joins in RING-PAIR's scope (5-7 by a distinction;
            5-5 through a path of one knot), sizes 1 to 13; and the totals against the referee's own exact orbit count.
  closure   the order-free closure law, run: on the clusters of the cover up to size 9 (as rooted cluster sets per orbit),
            20 random orders of making a cluster once all its parents (the cluster less one point, still connected) exist; the
            sets made, and the counts by size, against the referee's growth counts by round.
"""
import json
import random
import sys
from collections import defaultdict
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "research/RING-PAIR-20261119-001/referee-R1"))
import referee_pair as RP  # noqa: E402


def cover(nv, B):
    at = defaultdict(list)
    for i, blk in enumerate(B):
        for z in blk:
            at[z].append(i)
    base, entry, parent, cache = {}, {}, {}, {}

    def nbrs(v):
        if v in cache:
            return cache[v]
        x = base[v]
        out = []
        for j in at[x]:
            if entry[v] == j:
                p = parent[v]
                for w in B[j]:
                    if w == base[p]:
                        out.append(p)
                    elif w != x:
                        u = (p, j, w)
                        base.setdefault(u, w)
                        entry.setdefault(u, j)
                        parent.setdefault(u, p)
                        out.append(u)
            else:
                for w in B[j]:
                    if w != x:
                        u = (v, j, w)
                        base.setdefault(u, w)
                        entry.setdefault(u, j)
                        parent.setdefault(u, v)
                        out.append(u)
        cache[v] = out
        return out

    def root(x):
        r = ("r", x)
        base[r], entry[r], parent[r] = x, None, None
        return r
    return nbrs, root, base


def shares(nv, B, part_of, N):
    nbrs, root, base = cover(nv, B)
    out = defaultdict(lambda: defaultdict(Fraction))
    for x in range(nv):
        r = root(x)

        def rec(cur, untried, seen, size):
            parts = frozenset(part_of[base[v]] for v in cur)
            out[size][parts] += Fraction(1, size)
            if size == N:
                return
            untried = list(untried)
            while untried:
                v = untried.pop()
                new = [u for u in nbrs(v) if u not in seen]
                rec(cur | {v}, untried + new, seen | set(new), size + 1)
        rec(frozenset([r]), list(nbrs(r)), {r} | set(nbrs(r)), 1)
    return out


def part_partc(N=13):
    out = {}
    joins = {"5-7 by a distinction": (12, RP.ring(5) + RP.ring(7, 5) + [(0, 5)], lambda k: "ring5" if k < 5 else "ring7"),
             "5-5 through a path of one": (11, RP.ring(5) + RP.ring(5, 5) + [(0, 10), (10, 5)],
                                            lambda k: "ringA" if k < 5 else ("ringB" if k < 10 else "path"))}
    study = json.load(open(ROOT / "artifacts/ROUND-FREE-20261119-001B/ROUND-FREE-20261119-001B-E001_serial/partc.json"))["joins"]
    for name, (n, edges, lab) in joins.items():
        nv, B = RP.blocks(n, edges, {})
        s = shares(nv, B, {k: lab(k) for k in range(nv)}, N)
        rooted, _, _, _, _ = RP.orbit_counts(n, edges, {}, N + 1)
        rows = {}
        for k in range(1, N + 1):
            tot = sum(s[k].values())
            multi = sum(v for p, v in s[k].items() if len(p) >= 2)
            rows[k] = {"total": int(tot), "single-part counts": {"+".join(sorted(p)): int(v) for p, v in s[k].items() if len(p) == 1},
                       "share spanning two or more parts": round(float(multi / tot), 6),
                       "total equals the exact orbit count": int(tot) == int(rooted[k - 1]),
                       "equals the study's split": {"+".join(sorted(p)): int(v) for p, v in s[k].items()} ==
                                                   {"+".join(sorted(q.split("+"))): v for q, v in study[name][str(k)]["parts"].items()}}
        out[name] = rows
    return out


def part_closure(N=9, orders=20):
    """Clusters per orbit are represented by rooted sets at a fixed lift of their least base point, using all rooted sets."""
    out = {}
    for name, (n, edges) in {"ring 4,4,4,4,5": (5, RP.ring(5)), "5-7 by a distinction": (12, RP.ring(5) + RP.ring(7, 5) + [(0, 5)])}.items():
        surplus = {0: 1} if name.startswith("ring") else {}
        nv, B = RP.blocks(n, edges, surplus)
        nbrs, root, base = cover(nv, B)
        # every connected set of size <= N containing a root lift (rooted sets); parents: remove one point, keep connected
        sets = set()
        for x in range(nv):
            r = root(x)

            def rec(cur, untried, seen, size):
                sets.add(cur)
                if size == N:
                    return
                untried = list(untried)
                while untried:
                    v = untried.pop()
                    new = [u for u in nbrs(v) if u not in seen]
                    rec(cur | {v}, untried + new, seen | set(new), size + 1)
            rec(frozenset([r]), list(nbrs(r)), {r} | set(nbrs(r)), 1)

        def connected(S):
            S = set(S)
            if not S:
                return False
            st = [next(iter(S))]
            seen = {st[0]}
            while st:
                v = st.pop()
                for u in nbrs(v):
                    if u in S and u not in seen:
                        seen.add(u)
                        st.append(u)
            return seen == S
        parents = {}
        for S in sets:
            ps = [S - {v} for v in S if len(S) > 1 and connected(S - {v})]
            parents[S] = [p for p in ps if p in sets]
        children = defaultdict(list)
        for S, ps in parents.items():
            for q in ps:
                children[q].append(S)
        made_sets = []
        rng = random.Random(7)
        for _ in range(orders):
            missing = {S: len(parents[S]) for S in sets}
            made = {S for S in sets if len(S) == 1}
            enabled = []
            for S in made:
                for T in children[S]:
                    missing[T] -= 1
            enabled = [T for T in sets if T not in made and missing[T] == 0 and parents[T]]
            while enabled:
                S = enabled.pop(rng.randrange(len(enabled)))
                made.add(S)
                for T in children[S]:
                    missing[T] -= 1
                    if missing[T] == 0 and T not in made:
                        enabled.append(T)
            made_sets.append(frozenset(made))
        same = all(m == made_sets[0] for m in made_sets)
        by_size = defaultdict(Fraction)
        for S in made_sets[0]:
            by_size[len(S)] += Fraction(1, len(S))
        rooted, _, _, _, _ = RP.orbit_counts(n, edges, surplus, N + 1)
        out[name] = {"rooted clusters up to size N": len(sets), "orders": orders, "every order made the same set": same,
                     "every cluster made": made_sets[0] == frozenset(sets),
                     "orbits by size (closure law)": [str(by_size[k]) for k in range(1, N + 1)],
                     "the exact orbit count (= the growth's junctions by round, RING-PAIR-R1)": [int(x) for x in rooted[:N]]}
    return out


if __name__ == "__main__":
    print(json.dumps({"partc": part_partc, "closure": part_closure}[sys.argv[1]](), indent=1, default=str))
