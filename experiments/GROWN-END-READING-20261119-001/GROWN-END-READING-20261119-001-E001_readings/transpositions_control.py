"""Check a small prefix using independent row growth and direct parity equations."""
from collections import Counter
from itertools import combinations, product
from pathlib import Path
import json
import subprocess
import sys

import networkx as nx

from named import bond_readings
from verify import Arrangement, start_audit

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
sys.path.insert(0,str(ROOT/"experiments/EXTEND-ROUND-20261119-001A/EXTEND-ROUND-20261119-001A-E001_extend"))
from extend import C


def sources(width=8):
    for graph in nx.graph_atlas_g():
        n=len(graph)
        if n<2 or n>4 or not nx.is_connected(graph):
            continue
        edges=sorted(graph.edges())
        for weights in product((1,2),repeat=len(edges)):
            if 2 not in weights or sum(weights)>width:
                continue
            base=[[] for _ in range(n)]
            x=0
            for (u,v),k in zip(edges,weights):
                for _ in range(k):
                    base[u].append(x)
                    base[v].append(x)
                    x+=1
            ranges=[range(max(0,3-len(row)),width-x+1) for row in base]
            for loose in product(*ranges):
                if sum(loose)+x>width:
                    continue
                rows=[row.copy() for row in base]
                y=x
                for u,k in enumerate(loose):
                    rows[u]+=list(range(y,y+k))
                    y+=k
                audit=start_audit(Arrangement.parse(rows))
                if not audit['non_outside_cut_holders'] and not audit['forced_distinctions']:
                    yield rows


def main():
    control=Counter()
    for rows in sources():
        control['allocations']+=1
        growth=C.S.from_junctions(rows)
        for age in range(1,10):
            step=growth.step(C.S.gf2(C.F.fewest),None)
            if not step or not step['new'] or len(growth.bits_of)>8:
                break
            current=[sorted(row) for row in growth.bits_of]
            probe=C.S.from_junctions(current)
            next_step=probe.step(C.S.gf2(C.F.fewest),None)
            if not next_step or not next_step['new']:
                break
            a=Arrangement.parse(current)
            control['open_stages']+=1
            (_,pairs,triples),_,space=bond_readings(a)
            fixed=set().union(*(a.stars[j] for j in a.live))
            for x,y in combinations(sorted(set(a.labels)-fixed),2):
                swap=dict(zip(a.labels,a.labels))
                swap[x],swap[y]=y,x
                if all(sum(1<<swap[q] for q in support) in space for support in a.stars):
                    continue
                control['non_span_swaps_tested']+=1
                def preserves(values):
                    return all(k==values[tuple(sorted(swap[q] for q in mark))] for mark,k in values.items())
                if not preserves(pairs):
                    continue
                control['pair_table']+=1
                flip={mark:a.owners[mark[0]]==a.owners[mark[1]] for mark in pairs}
                keeps_flip=preserves(flip)
                control['pair_and_flip']+=keeps_flip
                if preserves(triples):
                    control['pair_and_triples']+=1
                    control['pair_triples_flip']+=keeps_flip
    command=[sys.executable,'-B',str(HERE/'transpositions.py'),'--start-junctions','4','--width','8','--current','8']
    if sys.argv[1:]:
        command+=['--engine',sys.argv[1]]
    expected=json.loads(subprocess.check_output(command,text=True))['totals']
    assert {key:control[key] for key in expected}==expected,(control,expected)
    print(json.dumps(expected,indent=2))


if __name__=='__main__':
    main()
