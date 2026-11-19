"""Read minimum bonds at a distinction and check against the full parity span."""
from itertools import combinations
from pathlib import Path
import json
import sys

import networkx as nx

ROOT = Path(__file__).resolve().parents[3]
FAMILY = "GROWN-END-READING-20261119-001"
sys.path.insert(0, str(ROOT/"experiments"/FAMILY/(FAMILY+"-E001_readings")))
from named import bond_readings, named_cases
from verify import Arrangement


def recover(labels, pairs, triples):
    """Uses just the lower-order distances. All recorded distances are size minus one."""
    result = {}
    for x in labels:
        pair = {y:pairs[tuple(sorted((x,y)))] for y in labels if y != x}
        minimum = min(value for value in pair.values() if value is not None)
        links = nx.Graph()
        links.add_nodes_from(y for y in pair if pair[y] == minimum)
        links.add_edges_from((a,b) for a,b in combinations(list(links),2)
                             if triples[tuple(sorted((x,a,b)))] == minimum)
        masks = {sum(1 << z for z in [x,*clique]) for clique in nx.find_cliques(links)}
        assert all(mask.bit_count()==minimum+1 for mask in masks)
        result[x] = masks
    return result


def rank(words):
    basis = {}
    for v in words:
        while v:
            top = v.bit_length()-1
            if top not in basis:
                basis[top] = v
                break
            v ^= basis[top]
    return len(basis)


def audit(rows):
    stage = Arrangement.parse(rows)
    (_,pairs,triples), bonds, span = bond_readings(stage)
    assert tuple(stage.labels) == tuple(range(len(stage.labels)))
    visible = recover(stage.labels,pairs,triples)
    for x, recovered in visible.items():
        containing = [b for b in bonds if b & (1 << x)]
        m = min(b.bit_count() for b in containing)
        assert recovered == {b for b in containing if b.bit_count()==m}
    all_minima = set.union(*visible.values())
    equations = list(all_minima) + [stage.masks[i] for i in stage.live]
    pair_envelopes = set()
    for (x,y), reading in pairs.items():
        if reading is None:
            continue
        names = {x,y} | {z for z in stage.labels if z not in (x,y)
                         and triples[tuple(sorted((x,y,z)))]==reading}
        if len(names)==reading+1:
            word = sum(1 << u for u in names)
            assert word in bonds
            pair_envelopes.add(word)
    return {'junctions':len(rows),'distinctions':len(stage.labels),
            'size_of_recovered_bond_family':len(all_minima),
            'rank_of_minimum_bonds':rank(all_minima),'rank_including_live_rows':rank(equations),
            'rank_including_unique_pair_minimizers':rank(equations+list(pair_envelopes)),
            'actual_rank':rank(stage.masks),'true_bonds':len(bonds),'equation_space_size':len(span)}


def complete_bipartite(size):
    # One of the three high-degree sites serves as exterior.
    # Each y is the far endpoint of one distinction from each of the three sites.
    all_rows = [[i*size+j for j in range(size)] for i in range(3)]
    all_rows += [[i*size+j for i in range(3)] for j in range(size)]
    return all_rows[1:]


def reached_parallel_paths(size):
    # Two distinctions at each ordinary meeting on each two-step A--B path.
    from named import lineage
    law_dir=ROOT/"experiments/EXTEND-ROUND-20261119-001A/EXTEND-ROUND-20261119-001A-E001_extend"
    sys.path.insert(0,str(law_dir))
    from extend import C
    rows=[[],[]]+[[] for _ in range(size)]+[[],[]]
    for i in range(size):
        for j in range(4):
            rows[int(j>=2)].append(4*i+j)
            rows[2+i].append(4*i+j)
    for pole in range(2):
        x=4*size+3*pole
        rows[pole].append(x)
        rows[-2+pole].extend((x,x+1,x+2))
    grown=C.S.from_junctions(rows)
    stages=[]
    for _ in range(2):
        step=grown.step(C.S.gf2(C.F.fewest),None)
        assert step and step['new']>0
        stages.append([sorted(row) for row in grown.bits_of])
    lineage({'start':rows,'current':stages[0],'next':stages[1]})
    return stages[0]


def main():
    records = {name:audit(case['current']) for name,_,case,_ in named_cases()}
    for n in (4,5,6):
        r=audit(complete_bipartite(n))
        assert r['rank_of_minimum_bonds']==n and r['actual_rank']==n+2
        records[f'locally_shortest_static_K3_{n}']=r
    for n in (3,4,5):
        r=audit(reached_parallel_paths(n))
        assert r['rank_including_unique_pair_minimizers'] < r['actual_rank']
        records[f'reached_parallel_paths_{n}']=r
    print(json.dumps(records,indent=2))


if __name__=='__main__':
    main()
