"""Trace the two-base obstruction and distinguish maximality from an uncovered pair."""
import argparse
from collections import Counter
from itertools import combinations
import json
import time

from rebuild import Core, alike, check_growth, draw, families


def two_base_start():
    pairs = [(0,1),(0,2),(1,2),(0,3),(1,3),(0,4),(1,5)]
    openings = [3,3,1,1,2,2]
    stars = [[] for _ in range(13)]
    def join(a,b):
        name = sum(map(len,stars))
        stars[a].append(name)
        stars[b].append(name)
    for i,(a,b) in enumerate(pairs):
        joint = 6+i
        join(a,joint)
        join(b,joint)
        join(joint,6+(i+1)%7)
    for i,n in enumerate(openings):
        for _ in range(n):
            stars[i].append(sum(map(len,stars)))
    return stars


def display(core):
    name = {}
    for rank,row in enumerate(core.level):
        for i,v in enumerate(row):
            name[v] = f'{rank}.{i+1}'
    return name


def two_base_trace(horizon):
    stars = two_base_start()
    core = Core(stars)
    name = display(core)
    records = []
    overlaps = []
    for rank,row in enumerate(core.level[1:],1):
        for a,b in combinations(row,2):
            common = core.parent[a] & core.parent[b]
            if len(common) < 2:
                continue
            conflicts = [name[k] for p,q in combinations(common,2)
                         for k in core.parent[p] & core.parent[q] if core.bases[k]]
            overlaps.append([name[a],name[b],sorted(name[k] for k in common),conflicts])
        for child in row:
            for p,q in combinations(core.parent[child],2):
                both = core.bases[p] & core.bases[q]
                grandparents = core.parent[p] & core.parent[q]
                if both and not any(both <= core.bases[k] for k in grandparents):
                    records.append(dict(child=name[child],parents=[name[p],name[q]],
                                        required=sorted(both),
                                        common={name[k]:sorted(core.bases[k]) for k in grandparents}))
    _, levels = core.predictions(stars,'nae',horizon)
    missing = []
    extra = []
    def encode(x):
        v,vec = x
        return [name[v],list(vec)]
    for r in range(2,horizon+1):
        expected = Counter(frozenset(ps) for ps,_ in levels[r].values() if len(ps)>=2)
        actual = Counter(families({k:v[0] for k,v in levels[r-1].items()}))
        if actual != expected:
            missing = [[encode(x) for x in sorted(g)] for g in (expected-actual)]
            extra = [[encode(x) for x in sorted(g)] for g in (actual-expected)]
            break
    views = {}
    for law in ('nae','parity'):
        observed = alike.grow(stars,horizon,knot_law=law)
        comparison = check_growth(stars,core,law,horizon)
        first = comparison[1] if comparison[0]=='views' else None
        detail = {}
        if first:
            _, pred = core.predictions(stars,law,horizon)
            predict = Counter((len(ps),f) for ps,f in pred[first].values())
            ordinary = Counter({(s[1],s[2]):n for s,n in observed['rows'][first-1]['sig0']})
            detail = {'predicted_only': sorted((*k,n) for k,n in (predict-ordinary).items()),
                      'ordinary_only':sorted((*k,n) for k,n in (ordinary-predict).items())}
        views[law] = {'comparison':comparison,'counts':[t['n'] for t in observed['rows']],
                      'sig0_difference_at_first':detail}
    pairs = [(0,1),(0,2),(1,2),(0,3),(1,3),(0,4),(1,5),(5,6)]
    control = draw(7,pairs,{4:1})
    reduced = Core(control)
    return dict(stars=stars, core_status=core.failures(), rank_sizes=list(map(len,core.level)),
                labelled_ranks=[{name[v]:{'parents':sorted(name[p] for p in core.parent[v]),
                                           'points':sorted(core.points[v])} for v in row} for row in core.level],
                multiple_parent_overlaps=overlaps,failed_lifts=records,
                order_first_difference=r if missing or extra else None,
                proposed_parent_families_only=missing, round_rule_families_only=extra,
                ordinary=views, one_base_control={'status':reduced.failures(),
                'rank_sizes':list(map(len,reduced.level)), 'comparisons':{
                law:check_growth(control,reduced,law,horizon) for law in ('nae','parity')}})


def uncovered_trace():
    stars = draw(4,[(0,1),(0,2),(0,3)],{1:1,2:1})
    c = Core(stars)
    _, levels = c.predictions(stars,'nae',7)
    for r in range(2,8):
        for y,(ps,_) in levels[r].items():
            if len(ps)!=2 or len(y[1])!=2 or len(set(y[1]))!=2:
                continue
            if any(p[0]!=y[0] for p in ps):
                continue
            for w,(pws,_) in levels[r-1].items():
                if w in ps or w[1] or not all(levels[r-1][p][0] & pws for p in ps):
                    continue
                return {'stars':stars,'status':c.failures(),'round_of_y':r,
                        'core_points':sorted(c.points[y[0]]),'extra_core_points':sorted(c.points[w[0]]),
                        'shortenings':[list(p[1]) for p in ps], 'extra_vector':list(w[1]),
                        'pair_is_uncovered':frozenset(ps) in families({x:v[0] for x,v in levels[r-1].items()}),
                        'ordinary':{law:check_growth(stars,c,law,7) for law in ('nae','parity')}}
    raise AssertionError('missing lower-total example')


if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--rounds',type=int,default=10)
    args=p.parse_args()
    start=time.perf_counter()
    out={'two_bases':two_base_trace(args.rounds),'pair':uncovered_trace()}
    print(json.dumps(dict(out,seconds=round(time.perf_counter()-start,3)),indent=2))
