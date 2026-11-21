"""Literal local-state replay and actual growth retaining a large repeated part."""
from collections import Counter
from fractions import Fraction
from functools import reduce
from itertools import combinations
import json
from math import prod
import networkx as nx

from local_parts import (OUT, archive, count_pairs, decode, load_catalogue, member, nae_separator,
                         physical_parts, profile, width)
from multiple_meetings import classify_stage, read_groups
from disconnected import advance, naelib, rows_of


def replay_library():
    checks=Counter()
    aliases=[]
    for ns,data in archive().items():
        n=int(ns)
        disagreements={(i,j):sum(1<<w for w in range(1<<n) if (w>>i ^ w>>j)&1)
                       for i,j in combinations(range(n),2)}
        for state in data['nae']:
            rows=tuple(map(tuple,state['presentations'][0]['supports']))
            key,total,counts=profile(rows)
            allowed=int(state['state_words_hex'],16)
            assert total==allowed.bit_count()
            if any(counts[p] != (m&allowed).bit_count() for p,m in disagreements.items()):
                # The state catalogue stores an orbit representative and a
                # presentation in its own naming. Transfer by its actual words.
                masks=[sum(1<<x for x in h) for h in rows]
                allowed=sum(1<<w for w in range(1<<n) if all(w&m not in (0,m) for m in masks))
            assert all(counts[p]==(m&allowed).bit_count() for p,m in disagreements.items())
            checks['state_orbits']+=1
            checks['literal_pair_comparisons']+=len(disagreements)
            if key.automorphisms>state['state_automorphisms']:
                aliases.append({'width':n,'rows':rows,'state_symmetries':state['state_automorphisms'],
                                'table_symmetries':key.automorphisms,'physical_status':state['presentations'][0]['status']})
    assert len(aliases)==3 and all(d['physical_status']=='closed' for d in aliases)
    return {'checks':checks,'named_state_aliases':aliases}


def correlations_on_parts(rows):
    pieces=physical_parts(rows)
    g=nx.Graph()
    local=[]
    totals=[]
    for index,(names,part) in enumerate(pieces):
        g.add_node(('h',index))
        for x in names:g.add_edge(('h',index),('x',x))
        total,counts=count_pairs(part,'nae')
        totals.append(total)
        local.append({tuple(sorted((names[a],names[b]))):Fraction(total-2*d,total)
                      for (a,b),d in counts.items()})
    assert nx.is_tree(g)
    divisor=1<<(len(pieces)-1)
    assert prod(totals)%divisor==0
    den=prod(totals)//divisor
    counts={}
    for i,j in combinations(range(width(rows)),2):
        path=nx.shortest_path(g,('x',i),('x',j))
        corr=prod(local[path[k][1]][tuple(sorted((path[k-1][1],path[k+1][1])))] for k in range(1,len(path),2))
        v=den*(1-corr)/2
        assert v.denominator==1
        counts[i,j]=int(v)
    return den,counts


def growing_example():
    # Three wider holders, two consecutive double meetings, three otherwise
    # private ports at each holder. The growing attachment uses just one port.
    rows=[(0,1,4,5,6),(0,1,2,3,7,8,9),(2,3,10,11,12)]
    new=13
    def close_port(x):
        nonlocal new
        a,b,c,d=range(new,new+4);new+=4
        rows.extend(((x,a,b),(a,c,d),(b,c,d)))
    for x in range(5,13):close_port(x)
    other=new;loose=new+1;new+=2
    rows.append((4,other,loose));close_port(other)
    stage=naelib.S.from_junctions(rows)
    library=load_catalogue()
    out=[]
    for age in (0,1,2):
        physical=rows_of(stage)
        total,counts=correlations_on_parts(physical)
        observed=decode(width(physical),total,counts,library,read_groups)
        assert nae_separator(observed,physical) is None and nae_separator(physical,observed) is None
        flags=classify_stage(physical,library,'nae')
        assert flags['extended_analytic'] and not flags['library']
        status,births=advance(stage,'nae')
        assert status=='births'
        out.append({'age':age,'width':width(physical),'word_count':total,'holders':len(physical),
                    'next_birth_count':len(births),'part_coverage':flags,'exact_global_word_recovery':True})
    return {'initial_rows':rows,'cuts':out}


def main():
    replay=replay_library()
    replay['attained_beyond_primary']=growing_example()
    (OUT/'recovery_verification.json').write_text(json.dumps(replay,indent=2)+'\n')
    print(replay['checks'],[(r['age'],r['width'],r['next_birth_count']) for r in replay['attained_beyond_primary']['cuts']])


if __name__=='__main__':
    main()
