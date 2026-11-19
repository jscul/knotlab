"""Referee R1 for VARIABLE-OUTPUT-READER-20261118-001K: every member of the family to width 28, grown by the family's own moves
(seed; two unary three-fresh additions; one three-parent three-fresh addition at any later point; otherwise two- or
three-parent two-fresh), deduplicated up to isomorphism; for each member: its legal triples, whether every symmetry of its table
clipped through K = 6 (D = 5) keeps its junction supports, and whether every symmetry of its full table does.

  ../../../.venv/bin/python -B family_self.py > referee_k_family_self.json      (from this directory)

This is a self-symmetry test (one presentation, all renamings), one size past the exhaustive all-rival census of referee_k.py
(which stops at width 24): it reaches the study's width-26 sharp example and the width-28 pair.
"""
import itertools
import json
import sys
from collections import defaultdict
from multiprocessing import Pool
from pathlib import Path

import networkx as nx

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "research/VARIABLE-OUTPUT-READER-20261118-001F/referee-R1"))
import referee_f as F  # noqa: E402

WMAX = int(__import__("os").environ.get("WMAX", "28"))


def children(state):
    T, k, used = state
    out = []
    for P in F.moves(T):
        if k < 2:
            if len(P) == 1:
                out.append((F.add(T, P, 3), k + 1, used))
            continue
        if len(P) in (2, 3):
            out.append((F.add(T, P, 2), k + 1, used))
        if len(P) == 3 and not used:
            out.append((F.add(T, P, 3), k + 1, True))
    return [s for s in out if F.width(s[0]) <= WMAX]


def key(state):
    T, k, used = state
    return (F.wl(T), used, min(k, 2))


def dedup(bucket):
    reps = []
    for s in bucket:
        G = F.graph(s[0])
        if not any(nx.is_isomorphic(G, H, node_match=F.nm) for H, _ in reps):
            reps.append((G, s))
    return [s for _, s in reps]


def examine(state):
    T, k, used = state
    J, n = F.supports(T)
    K, _ = F.bond_table(J, n)
    stars = {frozenset(S) for S in J}
    lt = F.legal_triples(T, J)
    g6, _, c6, _ = F.generators(F.clip(K, 6))
    gf, _, cf, _ = F.generators(K)
    return {"width": n, "junctions": T[0], "used": used, "legal": len(lt), "clipped K<=6 keeps supports": F.keeps(g6, stars),
            "clipped K<=6 keeps triples": F.keeps(g6, lt) if lt else True, "full table keeps supports": F.keeps(gf, stars),
            "capped": c6 or cf}


def main():
    level = [(F.seed(), 0, False)]
    members = []
    with Pool(20) as pool:
        while level:
            kids = [c for s in level for c in children(s)]
            buckets = defaultdict(list)
            for c in kids:
                buckets[key(c)].append(c)
            level = [s for r in pool.map(dedup, list(buckets.values())) for s in r]
            members.extend(s for s in level if s[2])
            print(len(level), file=sys.stderr, flush=True)
        rows = pool.map(examine, [s for s in members if F.width(s[0]) >= 20], chunksize=4)
    out = {}
    for w in sorted({r["width"] for r in rows}):
        rs = [r for r in rows if r["width"] == w]
        live = [r for r in rs if r["legal"]]
        dead = [r for r in rs if not r["legal"]]
        out[f"width {w}"] = {"family members (third three-fresh join made)": len(rs), "with a legal triple": len(live),
                             "with a legal triple: a K<=6 table symmetry moves a junction support": sum(not r["clipped K<=6 keeps supports"] for r in live),
                             "with a legal triple: a K<=6 table symmetry moves a legal triple": sum(not r["clipped K<=6 keeps triples"] for r in live),
                             "with a legal triple: a full-table symmetry moves a support": sum(not r["full table keeps supports"] for r in live),
                             "empty menu: a K<=6 table symmetry moves a support": sum(not r["clipped K<=6 keeps supports"] for r in dead),
                             "empty menu: a full-table symmetry moves a support": sum(not r["full table keeps supports"] for r in dead),
                             "searches capped": sum(r["capped"] for r in rs)}
    return out


if __name__ == "__main__":
    print(json.dumps(main(), indent=1))
