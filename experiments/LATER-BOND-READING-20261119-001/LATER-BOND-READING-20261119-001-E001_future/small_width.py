"""Enumerate small simple wired supports and arbitrary positive shared multiplicities."""
import argparse
from itertools import combinations
import json
import os
from pathlib import Path
import subprocess
import tempfile

import networkx as nx

def residual_groups(rows):
    import sys
    here=Path(__file__).resolve().parent
    law="GROWN-END-MEET-ONCE-20261119-001"
    sys.path.insert(0,str(here.parents[2]/"experiments"/law/(law+"-E001_rounds")))
    from readings import all_mappings, bond_readings
    from verify import Arrangement
    results=[]
    for row in rows:
        outside,n,e,*links=row
        stars=[[] for _ in range(n)]
        label=0
        for i in range(e):
            u,v,w=links[3*i:3*i+3]
            for _ in range(w):
                stars[u].append(label);stars[v].append(label);label+=1
        stage=Arrangement.parse([sorted(s) for j,s in enumerate(stars) if j!=outside])
        (_,pairs,triples),_,equations=bond_readings(stage)
        fixed=set().union(*(stage.stars[j] for j in stage.live))
        groups=[0,0,0]
        for phi in all_mappings(stage.labels,pairs,fixed):
            groups[0]+=1
            if any(value!=triples[tuple(sorted(phi[x] for x in X))] for X,value in triples.items()):
                continue
            groups[1]+=1
            if all(sum(stage.label_bits[phi[x]] for x in s) in equations for s in stage.stars):
                groups[2]+=1
        results.append({'width':label,'fixed':len(fixed),'pair_group':groups[0],
                        'triple_subgroup':groups[1],'equation_preservers_in_subgroup':groups[2]})
    return results


def run(bound, geng):
    nmax=(2*bound+1)//3
    counts=[]
    residual=[]
    here=Path(__file__).resolve().parent
    with tempfile.TemporaryDirectory() as temp:
        exe=Path(temp)/'scan'
        subprocess.run(['c++','-O3','-std=c++20',str(here/'small_width.cpp'),'-o',str(exe)],check=True)
        for n in range(2,nmax+1):
            if n<=7:
                graphs=(g for g in nx.graph_atlas_g() if len(g)==n and g.number_of_edges()<=bound
                        and nx.is_biconnected(g))
            else:
                if not geng: raise RuntimeError('geng required at this width')
                out=subprocess.check_output([geng,'-Cq',str(n),f'0:{bound}'])
                graphs=(nx.from_graph6_bytes(row) for row in out.splitlines())
            inputs=[]
            for g in graphs:
                es=list(g.edges())
                inputs.append(' '.join(map(str,[n,len(es),*(x for pair in es for x in pair)])))
            row=subprocess.run([str(exe),str(bound)],input='\n'.join(inputs)+'\n',text=True,check=True,capture_output=True)
            for line in row.stdout.splitlines():
                tag,*nums=line.split()
                if tag=='R':
                    residual.append([int(s) for s in nums])
                else:
                    assert tag=='C'
                    counts.append([n,len(inputs),*[int(s) for s in nums]])
    return {'maximum_distinctions':bound,'maximum_wired_vertices':nmax,
            'population':'Every positive open stage is included in this larger collection of biconnected wired graphs. Every connected simple wired support is represented once, every positive link multiplicity allocation through the width bound is tested, and every possible exterior with admissible degree and pairwise nonmeeting live holders is tested. Rooted allocations need not be non-isomorphic.',
            'columns':['wired_vertices','simple_supports','eligible_allocations','eligible_rooted_allocations','rank_full_from_single_minima_or_small_bonds','add_unique_pair_minima','add_growing_end','unresolved_by_rank'],
            'tiers':counts,'residual':residual,'exact_residual_groups':residual_groups(residual)}

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--bound',type=int,default=14)
    parser.add_argument('--geng',default=os.getenv('NAUTY_GENG'))
    args=parser.parse_args()
    out=run(args.bound,args.geng)
    here=Path(__file__).resolve().parent
    where=here.parents[2]/'artifacts'/here.parent.name/here.name/f'small_width_{args.bound}.json'
    where.write_text(json.dumps(out,indent=2)+'\n')
    print(out['tiers'],len(out['residual']))
