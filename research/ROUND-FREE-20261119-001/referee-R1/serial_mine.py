"""Referee R1 for ROUND-FREE-20261119-001: the present-state serial law re-implemented on the referee's own data structures
(JOIN-GROWTH-R1's lean engine for the groups), to see the order effects for the two touching three-place knots and the lone
four-place knot.  The law, as the study states it: one join at a time, chosen uniformly among the moves the current presentation
allows; a move is a group (a maximal valid set or an uncovered candidate pair) among the junctions that still hold loose
distinctions, not already joined by one junction, or a one-parent offshoot of a junction holding more loose distinctions than its
groups use; the new junction gets the fewest fresh distinctions max(d, 3 - p, 1), d its groups in the present state, or 0 when
it takes every loose distinction and d = 0 (its parity is then implied).

  ../../../.venv/bin/python -B serial_mine.py > referee_free_serial.json      (from this directory)
"""
import json
import random
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "research/JOIN-GROWTH-20261118-001/referee-R1"))
sys.path.insert(0, str(ROOT / "research/TOUCH-CENSUS-20261118-001/referee-R1"))
import lean as L  # noqa: E402
import referee_touch as RT  # noqa: E402


def serial(sizes, M, seed, maxj=400):
    G = L.Lean(RT.stars(sizes, M))
    rng = random.Random(seed)
    children = defaultdict(set)
    while len(G.bits) <= maxj:
        live = [j for j in range(len(G.bits)) if G.loose(j)]
        gs = [tuple(sorted(g)) for g in G.groups(live)]
        ok = [g for g in gs if not set.intersection(*[children[j] for j in g])]
        use = Counter(j for g in ok for j in g)
        off = [(j,) for j in live if len(G.loose(j)) > use[j]]
        pool = ok + off
        if not pool:
            return "closed", len(G.bits)
        g = rng.choice(pool)
        all_loose = sorted(b for j in live for b in G.loose(j))
        bits = [G.loose(j)[0] for j in g]
        jid = len(G.bits)
        G.bits.append(tuple(bits))
        G.nbr.append(set())
        G.parents.append(set())
        for b in bits:
            for o in G.owner[b]:
                G.nbr[o].add(jid)
                G.nbr[jid].add(o)
                G.parents[jid].add(o)
            G.owner[b].append(jid)
        G.round.append(0)
        G.fresh.append(0)
        for j in g:
            children[j].add(jid)
        live2 = [j for j in range(len(G.bits)) if G.loose(j) or j == jid]
        d = sum(1 for h in G.groups(live2) if jid in h)
        p = len(bits)
        k = 0 if (sorted(bits) == all_loose and d == 0) else max(d, 3 - p, 1)
        fresh = tuple(range(G.nb, G.nb + k))
        G.nb += k
        G.bits[jid] = G.bits[jid] + fresh
        for b in fresh:
            G.owner[b] = [jid]
        G.fresh[jid] = k
    return "passed 400", len(G.bits)


if __name__ == "__main__":
    out = {}
    for name, sizes, M in (("two touching three-place knots", [3, 3], [[0, 1], [1, 0]]), ("lone four-place knot", [4], [[0]])):
        res = [serial(sizes, M, s) for s in range(40)]
        out[name] = {"orders": len(res), "outcomes": dict(Counter(r[0] for r in res)),
                     "junctions when closed": sorted(r[1] for r in res if r[0] == "closed")}
    print(json.dumps(out, indent=1))
