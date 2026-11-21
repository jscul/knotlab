"""Sample initial holdings once per vote, retaining each paired law and unknown."""
from itertools import combinations,product
import gzip
import json
import random
import sys

import networkx as nx

from receivers import OUT,LAWS,clocks,fix,end,write


def sparse_rows():
    rng=random.Random(20261120522)
    for draw in range(64):
        n=rng.randint(9,12);prufer=[rng.randrange(n) for _ in range(n-2)]
        graph=nx.from_prufer_sequence(prufer)
        candidates=[p for p in combinations(range(n),2) if not graph.has_edge(*p)]
        additions=rng.sample(candidates,3);graph.add_edges_from(additions)
        coins=[int(rng.randrange(4)==0) for _ in range(n)]
        data={'n':n,'draw':draw,'word':prufer,'coins':coins,'extra':3,'extra_meetings':additions,
              'edges':sorted(tuple(sorted(e)) for e in graph.edges),'size_group':'9-12','supply':'original'}
        row=clocks.previous.source(data)
        obs={}
        for law in LAWS:
            scored=clocks.general_events(row,law)
            obs[law]={'legal':scored['legal'],'funded':scored['funded'],'source_certificate':scored['proved'],
                      'source_possible':scored['possible'],'seen_twice':scored['two_by32'],
                      'direct':False,'direct_possible':scored['possible'],'paid':False,
                      'paid_possible':scored['possible']}
        yield {'weighting':'tree_plus_three','draw':draw,'data':row,'observations':obs}


def explosive_rows():
    rng=random.Random(20261120523)
    pairs=[p for p in combinations(range(6),2) if p[0]//2!=p[1]//2]
    first=set(product((0,1),(2,3),(4,5)))
    for draw in range(64):
        incidence=[];flags=[rng.randrange(2) for _ in pairs]
        for j,((v,w),flag) in enumerate(zip(pairs,flags),6):
            if flag:v,w=w,v
            incidence.extend([(v,j),(w,j),(w,j)])
        stars=fix.source_from(incidence,[4]*6+[0]*12);obs={};actual={}
        for law in LAWS:
            fix.certify_source(stars,law)
            _,layers=fix.trajectory(stars,law,2)
            born={b.knot:b for b in layers[0][0]}
            assert {b.parents for b in born.values()}==first
            seconds=layers[1][0]
            assert all(set.union(*(set(born[v].parents) for v in b.parents))==set(range(6)) for b in seconds)
            actual[law]=[[(b.knot,b.parents,len(b.fresh)) for b in group] for group,_ in layers]
            obs[law]={'legal':True,'funded':True,'source_certificate':False,'source_possible':False,
                      'seen_twice':False,'direct':False,'direct_possible':False,'paid':False,'paid_possible':False}
        yield {'draw':draw,'weighting':'three_partner_pairs','input':stars,'orientations':flags,
               'two_actual_cuts':actual,'observations':obs}


def matched_rows():
    for r in json.loads(gzip.decompress((OUT/'matched_draws.json.gz').read_bytes())):
        passed=all(all(o['eligible_in_first_eight']) for o in r['emissions'].values())
        changed=all(all(o['total_differences']) for o in r['emissions'].values())
        assert passed==r['addressed'] and changed==r['degree_three']
        ob={'legal':True,'funded':True,'source_certificate':True,'source_possible':True,
            'seen_twice':True,'direct':passed,'direct_possible':passed,'paid':bool(changed),'paid_possible':bool(changed)}
        yield {'draw':r['draw'],'weighting':'connected_receiver','observations':dict.fromkeys(LAWS,ob)}


def main():
    sparse=list(sparse_rows()); write('sparse_draws.json.gz',sparse)
    large=list(explosive_rows());write('explosive_draws.json.gz',large)
    rows=sparse+large+list(matched_rows());best=[]
    for group in sorted({r['weighting'] for r in rows}):
        for law in LAWS:
            for den in ('all','legal','funded'):
                items=[r['observations'][law] for r in rows if r['weighting']==group and (den=='all' or r['observations'][law][den])]
                n=len(items);out={}
                for event,upper in [('legal','legal'),('funded','funded'),('source_certificate','source_possible'),
                                    ('seen_twice','seen_twice'),('direct','direct_possible'),('paid','paid_possible')]:
                    a=sum(bool(z[event]) for z in items);u=sum(bool(z[upper]) for z in items)
                    out[event]={'detected':a,'exact95':clocks.exact(a,n),'unresolved':u-a,'excluded':n-u,
                                'possible_count':[a,u],'outer95':None if not n else [clocks.exact(a,n)[0],clocks.exact(u,n)[1]]}
                best.append({'weighting':group,'law':law,'denominator':den,'n':n,'outcomes':out})
    write('rates.json',best)


if __name__=='__main__':
    main()
