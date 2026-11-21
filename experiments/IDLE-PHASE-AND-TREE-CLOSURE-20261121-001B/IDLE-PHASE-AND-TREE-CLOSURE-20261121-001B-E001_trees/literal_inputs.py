"""Replay all raw labelled tree/mask pairs at four and five, and the previous named draws."""

from argparse import ArgumentParser
from collections import Counter, defaultdict
from itertools import product
import gzip
import json
import sys
import time
import networkx as nx

from multiplicities import ROOT, adjacency, colored_code, prufer_edges, save

REPLAY = 'CALIBRATIONS-CLOCKS-AND-WIDER-KNOTS-20261120-001C'
sys.path.insert(0, str(ROOT/'experiments'/REPLAY/(REPLAY+'-E001_wider_meetings')))
from census_verify_wider import native, replay_allocation

OLDER = 'ERASURE-AND-CLOSING-SIGNS-20261121-001B'


def founder(n, edges, flags):
    rows = [[] for i in range(n)]
    for name,(a,b) in enumerate(edges):
        rows[a].append(name)
        rows[b].append(name)
    name = len(edges)
    for h,row in enumerate(rows):
        additional = max(0,3-len(row))+flags[h]
        row.extend(range(name,name+additional))
        name += additional
    return tuple(map(tuple,rows))


def local_data(births):
    counts = Counter((len(parents),fresh) for parents,fresh in births)
    return [[arity,fresh,m] for (arity,fresh),m in sorted(counts.items())]


def terminal_verdict(rows):
    owners = defaultdict(list)
    for h,row in enumerate(rows):
        for x in row:
            owners[x].append(h)
    assert all(len(p)==2 for p in owners.values())
    graph = nx.Graph(tuple(v) for v in owners.values())
    assert nx.is_connected(graph)
    planar,_=nx.check_planarity(graph)
    return not planar


def physical(rows,law):
    history=[]
    result={'history':history,'termination':'open','age':0,'arity':None,'positive':None}
    for age in range(1,5):
        status, after, births = native(rows,law)
        if status=='stall':
            result['termination']='stalled'
            break
        assert status=='births'
        width=len({name for row in after for name in row})
        history.append([len(after),width,local_data(births)])
        result['age']=age
        if any(fresh==0 for parents,fresh in births):
            assert len(births)==1 and law=='parity'
            result.update(termination='closed',arity=len(births[0][0]),positive=terminal_verdict(after))
            break
        rows=after
    return result


def count_literal(n):
    outputs = {}
    signatures = {}
    count=0
    for word in product(range(n),repeat=n-2):
        edges=tuple(prufer_edges(word,n))
        neighbors=adjacency(n,edges)
        for flags in product((0,1),repeat=n):
            rows=founder(n,edges,flags)
            code,symmetry=colored_code(neighbors,flags)
            outcome={law:physical(rows,law) for law in ('parity','nae')}
            assert signatures.setdefault(code,outcome)==outcome
            outputs[code]=outputs.get(code,0)+1
            count+=1
    assert count==n**(n-2)*2**n
    return {'n':n,'raw_labelled_inputs':count,'labelled_multiplicity':outputs,'class_histories':signatures}


def archived():
    path=ROOT/'artifacts'/OLDER/(OLDER+'-E001_closures')/'panels_histories.json.gz'
    with gzip.open(path,'rt') as f:
        draws=[x for x in json.load(f) if x['panel']=='T']
    entries=[]
    literal_cuts=0
    for draw in draws:
        rows=tuple(map(tuple,draw['source_rows']))
        n=len(rows)
        edges=[(u,v) for u,v,m in draw['original_meetings']]
        assert all(m==1 for u,v,m in draw['original_meetings'])
        code,symmetry=colored_code(adjacency(n,edges),draw['extra_private'])
        outcome={}
        for law,d in draw['laws'].items():
            before=rows
            for cut in d['cuts']:
                status,after,births=native(before,law)
                assert status=='births'
                wanted=tuple(map(tuple,cut['after_rows']))
                roster=[(tuple(b['parents']),b['fresh']) for b in cut['births']]
                assert Counter(births)==Counter(roster)
                replay_allocation(before,wanted,after,roster,births)
                literal_cuts+=1
                before=wanted
            term={'closed':'closed','stall':'stalled','still_open':'open'}[d['termination']]
            report=physical(rows,law)
            assert term==report['termination'] and d['last_complete_age']==report['age']
            if term=='closed':
                closed,=d['cuts'][-1]['new_closing_components']
                assert report['positive']==closed['operator_positive'] and report['arity']==closed['closing_arity']
            outcome[law]=report
        entries.append({'draw':draw['draw'],'n':n,'decoration_code':code,'laws':outcome})
    assert len(entries)==256
    return {'founders':entries,'matched_named_funded_cuts':literal_cuts}


def main():
    parser=ArgumentParser()
    parser.add_argument('--sizes',nargs='*',type=int,default=[])
    parser.add_argument('--sample',action='store_true')
    args=parser.parse_args()
    for n in args.sizes:
        start=time.monotonic()
        z=count_literal(n)
        save(f'literal_inputs_{n}.json.gz',z)
        print(n,z['raw_labelled_inputs'],len(z['class_histories']),round(time.monotonic()-start,3),flush=True)
    if args.sample:
        z=archived()
        save('archived_tree_replay.json.gz',z)
        print('previous named trees:',len(z['founders']),z['matched_named_funded_cuts'],flush=True)


if __name__=='__main__':
    main()
