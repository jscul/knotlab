"""Exhaust all bond cuts on a built eight-input proposal and its continuing twin."""
from collections import Counter
from itertools import combinations
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[3]
EPIC = "BOND-CLOSURE-20261120-001A"
OUT = ROOT / "artifacts" / EPIC / (EPIC + "-E001_proposals") / "eight_inputs.json"


def fixture(extra):
    # Parents of each missing-hub type, then A, B, C, the far knot and two intervening knots.
    labels = [f"parent-{i}" for i in range(8)] + ["A", "B", "C", "X", "WA", "WB", "exterior"]
    A, B, C, X, WA, WB, exterior = range(8, 15)
    edges = [(i, exterior) for i in range(8)]
    missing = [A]*3 + [B]*3 + [C]*2
    for i, absent in enumerate(missing):
        edges.extend((i, hub) for hub in (A,B,C) if hub != absent)
    for hub, middle in [(A,WA),(B,WB)]:
        edges.extend([(hub,middle),(middle,X),(middle,X)])
    if extra:
        edges.append((X,exterior))
    return labels, edges, missing


def adjacent(num, edges):
    rows = [0]*num
    for u,v in edges:
        rows[u] |= 1 << v
        rows[v] |= 1 << u
    return rows


def connected(mask, rows):
    if not mask:
        return False
    seen = todo = mask & -mask
    while todo:
        one = todo & -todo
        todo ^= one
        nxt = rows[one.bit_length()-1] & mask & ~seen
        seen |= nxt
        todo |= nxt
    return seen == mask


def examine(extra):
    labels, edges, missing = fixture(extra)
    p, outside = 8, len(labels)-1
    full = (1 << len(labels))-1
    adjacency = adjacent(len(labels), edges)
    ordinary = full ^ (1 << outside)
    assert connected(ordinary,adjacency)
    # The physical star at every ordinary holder is a bond in the wired presentation.
    degrees = Counter(v for e in edges for v in e)
    assert all(degrees[j] >= 3 and connected(full ^ (1<<j),adjacency) for j in range(outside))
    # At most one group: all core holders form one unheld clique. The extra holder has no partner.
    core = (1 << p)-1
    assert all(adjacency[i]&adjacency[j]&ordinary for i,j in combinations(range(p),2))
    assert all(adjacency[v]&core != core for v in range(outside))
    if extra:
        assert all(not (adjacency[i]&adjacency[11]&ordinary) for i in range(p))

    infinity = len(edges)+1
    costs = [infinity] * (1<<p)
    parent_marks = list(range(24))
    pairs = list(combinations(parent_marks,2))
    parent_costs = {pair:infinity for pair in pairs}
    num_bonds = 0
    for shore in range(1,ordinary+1):
        if not connected(shore, adjacency) or not connected(full ^ shore, adjacency):
            continue
        num_bonds += 1
        crossing = [i for i,(u,v) in enumerate(edges) if ((shore>>u)^(shore>>v))&1]
        size = len(crossing)
        use = shore & core
        costs[use] = min(costs[use],size)
        for a,b in combinations((i for i in crossing if i<24),2):
            parent_costs[a,b] = min(parent_costs[a,b],size)
    # A containing bond may contain other marked loose distinctions.
    for j in range(p):
        for mask in range(1,1<<p):
            if not mask & (1<<j):
                costs[mask] = min(costs[mask], costs[mask | (1<<j)])
    return (costs,parent_costs),dict(
        knots=outside,distinctions=len(edges),all_physical_stars_are_bonds=True,
        loose_count=p+extra,parent_group=list(range(p)),source_is_funded=True,
        fresh_at_common_join=int(extra),total_bonds_enumerated=num_bonds,
        labels=labels,edges=edges,missing_hubs=missing)


def main():
    (base,p0),left = examine(False)
    (added,p1),right = examine(True)
    rows=[]
    for k in range(1,9):
        masks=[s for s in range(1,256) if s.bit_count()==k]
        classes=Counter((base[s],added[s]) for s in masks)
        rows.append(dict(order=k,queries=len(masks),different=sum(base[s] != added[s] for s in masks),
                         minima_by_count=[[a,b,n] for (a,b),n in sorted(classes.items())]))
    assert rows[0]['different']==rows[1]['different']==0
    assert rows[-1]['minima_by_count']==[[8,9,1]]
    assert max(base[s] for s in range(1,256) if s.bit_count()==2)<=8
    # Sentinel is arm-specific. Normalize failure to find any joint support.
    def value(c,arm):
        return c if c<=arm['distinctions'] else None
    diffs = [[a,b,value(p0[a,b],left),value(p1[a,b],right)] for a,b in p0
             if value(p0[a,b],left)!=value(p1[a,b],right)]
    record=dict(design="Post-freeze analytic eight-input example with two loose-count preparations; all listed queries exhausted.",
                closing=left,continuing=right,subset_deck=rows,
                first_distinguishing_loose_order=next(row['order'] for row in rows if row['different']),
                parent_support_pair_queries=len(p0),parent_support_pair_differences=diffs)
    OUT.write_text(json.dumps(record,indent=2)+"\n")
    print([(r['order'],r['different'],r['queries']) for r in rows],
          len(diffs),"differences on pairs within complete parent supports")


if __name__=='__main__':
    main()
