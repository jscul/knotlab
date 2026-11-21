"""Exact matched receiver inputs, literal first cuts and full one-element outputs."""
from collections import Counter
from functools import lru_cache
from itertools import pairwise
from pathlib import Path
import gzip
import hashlib
import json
import random
import sys

import networkx as nx

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUT = ROOT / 'artifacts' / HERE.parent.name / HERE.name
OLD = next((ROOT / 'experiments/FREEDOM-CLOCKS-AND-BIRTHS-20261120-001B').iterdir())
sys.path.insert(0, str(OLD))
import clocks

fix, end, LAWS = clocks.fix, clocks.end, clocks.LAWS


def write(name, obj):
    raw = (json.dumps(obj, sort_keys=True, separators=(',', ':')) + '\n').encode()
    path = OUT / name
    path.write_bytes(gzip.compress(raw, compresslevel=6, mtime=0) if name.endswith('.gz') else raw)


def frame(length, priced):
    neutral, exits = clocks.cycle_words(length)
    g = nx.Graph()
    for zone in 'ALR':
        for circuit in [neutral, exits[0], exits[2]] + ([exits[1]] if zone == 'A' else []):
            sequence = [zone + x for x in circuit]
            g.add_edges_from(pairwise(sequence + sequence[:1]))
        g.add_edge(zone + 'b2', 'q')
    g.add_edges_from([('Ls', 'c'), ('c', 'Rt'), ('Rs', 'ds'), ('Lt', 'dt')])
    if priced:
        for d in ('ds', 'dt'):
            g.add_edges_from(pairwise([d, d+'1', d+'2', d+'3', d]))
    else:
        g.add_edge('ds', 'dt')
    assert nx.is_connected(g) and min(dict(g.degree).values()) >= 2 and not any(nx.triangles(g).values())
    return g


def physical(g, rng, checks=True):
    names = sorted(g)
    idx = {v:i for i,v in enumerate(names)}
    codes = {v:2+2*i+rng.randrange(2) for i,v in enumerate(names)}
    bonds = sorted(tuple(sorted(e)) for e in g.edges)
    incidence = []
    for w,(p,q) in enumerate(bonds, len(names)):
        for v in (p,q):
            incidence.extend([(idx[v],w)]*codes[v])
    opens = [g.degree(v) for v in names]+[0]*len(bonds)
    stars = fix.source_from(incidence, opens)
    # Factored K1-K3 projection: distinct spent witnesses use disjoint bit sets;
    # each live original has two free positions. Exterior-connectivity after
    # deleting one old holder is the parity projection check for this scheme.
    owners, ordinary, loose = fix.incidence(stars)
    assert set(loose) == set(range(len(names)))
    assert all(len(bits) == opens[i] >= 2 for i,bits in loose.items())
    assert len(set(map(frozenset,stars))) == len(stars)
    weights = Counter(tuple(vs) for vs in owners.values() if len(vs)==2)
    inferred = {}
    for i in loose:
        counts = {weights[tuple(sorted((i,w)))] for w in ordinary[i]}
        assert len(counts)==1
        inferred[i] = names[(counts.pop()-2)//2]
    recovered = {frozenset(inferred[i] for i in ordinary[w]) for w in ordinary if w not in loose}
    assert recovered == set(map(frozenset,bonds))
    state = end.from_stars(stars)
    expected = {tuple(sorted((idx[v],idx[w]))) for v,w in bonds}
    assert set(end.proposals(state))==expected and set(state.opens)==set(loose)
    actual={}
    for law in LAWS:
        plan=end.step(state,law)
        assert plan.status=='extend' and set(plan.parents)==expected
        prices = {p:h for p,h in zip(plan.parents,plan.fresh)}
        for (a,b),f in prices.items():
            assert f == g.degree(names[a])+g.degree(names[b])-2
        actual[law]={'first_true_binary_groups':len(prices),'first_fresh':sum(prices.values())}
    if checks:
        for law in LAWS:
            frames,layers=fix.trajectory(stars,law,3)
            assert len(layers)==3
            raw=[]
            for births,_ in layers:
                raw.append({'births':len(births),'fresh':sum(len(b.fresh) for b in births),
                            'parent_counts':dict(Counter(len(b.parents) for b in births))})
            actual[law]['literal_cuts']=raw
            # Match physical windows by all and only actual parents at each layer.
            words = [centred(length_of(g),n,m,zone) for zone in ('A','T') for n in (1,2) for m in (4,)]
            expected_words={tuple(w[i:j]) for w in words for i in range(len(w)) for j in range(i+1,len(w)+1)}
            ids={(v,):idx[v] for v in names}
            for m,(births,_) in enumerate(layers,2):
                by={frozenset(b.parents):b for b in births if len(b.parents)==2}
                for w in expected_words:
                    if len(w)!=m: continue
                    b=by[frozenset((ids[w[1:]],ids[w[:-1]]))]
                    assert len(b.fresh)==sum(g.degree(v)-2 for v in w)+2
                    ids[w]=b.knot
            actual[law]['physical_words_matched']=len(ids)-len(names)
        perm=list(range(len(stars))); rng.shuffle(perm)
        bits=sorted(owners); shuffled=bits[:];rng.shuffle(shuffled); rename=dict(zip(bits,shuffled))
        reshaped=[None]*len(stars)
        for i,row in enumerate(stars): reshaped[perm[i]]=tuple(rename[b] for b in row)
        owners2,graph2,loose2=fix.incidence(reshaped)
        w2=Counter(tuple(sorted(vs)) for vs in owners2.values() if len(vs)==2)
        assert {perm[i] for i in loose}==set(loose2)
        for i in loose:
            assert {w2[tuple(sorted((perm[i],w)))] for w in graph2[perm[i]]}=={codes[inferred[i]]}
    return {'holder_codes':codes,'candidate_pairs':bonds,'physical_knots':len(stars),
            'physical_distinctions':len(owners),'laws':actual}


def length_of(g):
    return 1+sum(v.startswith('Ar') for v in g)


@lru_cache(maxsize=None)
def baseword(length,n):
    neutral,marked=clocks.cycle_words(length)
    period=neutral*n+marked[0]
    marker=period.index('b0')
    return period[marker:]+period[:marker]


def letter(length,n,k,zone,exception=True):
    w=baseword(length,n)
    v=w[k%len(w)]
    if k==0 and exception:
        return 'Ab1' if zone=='A' else 'c'
    side='A' if zone=='A' else ('L' if k<0 else 'R')
    return side+v


def centred(length,n,m,zone,exception=True,reverse=False):
    low=-(m//2) + int(reverse and m%2==0)
    return tuple(letter(length,n,k,zone,exception) for k in range(low,low+m))


def extensions(g,word):
    old=2+sum(g.degree(v)-2 for v in word)
    prices=Counter()
    for i,v in enumerate(word):
        internal=set()
        if i: internal.add(word[i-1])
        if i+1<len(word): internal.add(word[i+1])
        assert len(internal)==min(i,1)+min(len(word)-1-i,1) and internal<=set(g[v])
        for extra in set(g[v])-internal:
            prices[old+g.degree(extra)-2]+=1
    assert sum(prices.values())==old
    return old,prices


def word_on_clock(w,length,n,p):
    if not w or not all(x.startswith('A') for x in w):return False
    if 'Ab1' not in w:return False
    b=w.index('Ab1')
    return all(x==('Ab1' if (i-b)%p==0 else 'A'+baseword(length,n)[(i-b)%len(baseword(length,n))]) for i,x in enumerate(w))


def adjacent_outside_phases(g,w):
    # All children of the straight receiver are one-element extensions. If removing
    # some other point is to leave a straight donor, remove an endpoint of w
    # (unless the new child is itself w + an endpoint). Enumerate branches too.
    if len(w)<4:return
    # A donor containing the internal leaves of w must retain a length-m-1 endpoint
    # deletion of w. Check whether each such word can be completed as a donor, at
    # either end, including a fork at the old second site.
    for dropped,common in [('left',w[1:]),('right',w[:-1])]:
        for side in ('left','right'):
            site=common[0] if side=='left' else common[-1]
            oldneighbor=common[1] if side=='left' else common[-2]
            for add in sorted(set(g[site])-{oldneighbor}):
                if (dropped==side and add==(w[0] if side=='left' else w[-1])):continue
                candidate=((add,)+common) if side=='left' else (common+(add,))
                info={'drop':dropped,'new_end':side,'added':add,'parents_in_union':2 if dropped!=side else 3}
                yield candidate,info


def admission(g,w,length,n,p):
    return [info for candidate,info in adjacent_outside_phases(g,w)
            if word_on_clock(candidate,length,n,p) or word_on_clock(candidate[::-1],length,n,p)]


def receiver_read(g,w,mark):
    # Look only through physical co-parents of the receiver's own outputs.
    # Equality uses original identities within this preparation, including on
    # the two wings of the unaddressed receiver.
    if len(w)%2: return []
    half=len(w)//2
    return [info for v,info in adjacent_outside_phases(g,w)
            if v[:half]==v[half:] and v[:half].count(mark)==1 and any(x.endswith('b0') for x in v[:half])]


def clock_case(g,length,n,m,keep_words=False):
    s=n*length+4
    is_send=m%(2*s)==0 and m>=4*s
    p=m//2
    sides={}
    for zone in ('A','T'):
        w=centred(length,n,m,zone)
        before=centred(length,n,m-1,zone) if m>1 else ()
        assert m==1 or before in (w[1:],w[:-1])
        if m>1:assert w[1:]!=w[:-1] and len(set((w[1:],w[:-1])) )==2
        own,price=extensions(g,w)
        hits=admission(g,w,length,n,p) if is_send else []
        shift=admission(g,centred(length,n,m,zone,reverse=True),length,n,p) if is_send else []
        sham_word=tuple((('A' if zone=='A' else 'R')+baseword(length,n)[k%len(baseword(length,n))]) for k in range(-(m//2),m-m//2))
        sham=admission(g,sham_word,length,n,p) if is_send else []
        assert not sham
        intrinsic=receiver_read(g,w,'Ab1' if zone=='A' else 'c')
        assert intrinsic==hits
        if is_send:
            assert (len(hits),len(shift))==((2,2) if zone=='A' else (0,0))
            j=m//(2*s)
            assert own==2+4*j*(n+3)
            assert price[own+1]==(4+2*int(zone=='T' and g.degree('ds')==3))*j
        sides[zone]={'own_fresh':own,'true_parent_count':0 if m==1 else 2,
                     'child_price_multiset':dict(sorted(price.items())),'total_child_fresh':sum(v*k for v,k in price.items()),
                     'direct_on_own_output':hits,'intrinsic_new_doubled_parent':intrinsic,'reversed_eligible':len(shift),'all_neutral_sham':len(sham)}
        if keep_words and is_send:
            sides[zone]['receiver_word']=w
            sides[zone]['receiver_parents']=[w[:-1],w[1:]]
            if zone=='A':
                x=w[1:]+('Ab1',)
                assert word_on_clock(x,length,n,p)
                sides[zone]['child_and_exact_parents']=[w+('Ab1',),w,x]
                sides[zone]['fork_child']={'base':w[1:],'two_new_leaves_at_base_start':[w[0],'Ab1'],
                    'two_straight_parents':[w,('Ab1',)+w[1:]],
                    'third_parent':{'base':w[1:-1],'two_leaves_at_base_start':[w[0],'Ab1']}}
    assert sides['A']['own_fresh']==sides['T']['own_fresh']
    foreign=centred(length,n,m,'T')
    mismatch=foreign.count('Rs')+foreign.count('Lt')
    delta=sides['T']['total_child_fresh']-sides['A']['total_child_fresh']
    assert delta==(g.degree('ds')-2)*mismatch
    return {'size':m,'send':is_send,'period_parent_steps':2*s,'outside_slot_occurrences':mismatch,'total_difference':delta,'roles':sides}


def broad_receipt(g,length,n):
    neutral,marked=clocks.cycle_words(length)
    u,v=neutral*n+marked[0],neutral*n+marked[1]
    rows=[]
    for ell in range(1,9):
        period=u*ell+v;m=2*len(period)
        phases={tuple('A'+x for x in w) for w in clocks.windows(period,m)}
        examples=[]
        for w in sorted(phases):
            for z in ('Ab2','Rb2'):
                if z not in g[w[-1]]:continue
                assert z not in w
                child=w+(z,);old=child[1:]
                assert child[:-1]==w and z in old and old not in phases
                examples.append({'sender':w,'exact_receiver_parent':old,'new_mark':z})
        assert examples and {x['new_mark'] for x in examples}=={'Ab2'}
        rows.append({'ell':ell,'size':m,'examples':examples})
    return rows


def main():
    raw={}
    for priced in (False,True):
        g=frame(4,priced)
        raw[str(priced)]={'physical':physical(g,random.Random(238+priced)),
                          'broad_receivers':{str(n):broad_receipt(g,4,n) for n in (1,2)},
                          'sizes':{str(n):[clock_case(g,4,n,m,True) for m in range(1,129)] for n in (1,2)}}
    write('receiver_controls.json.gz',raw)
    rng=random.Random(20261120521);draws=[];memo={}
    for i in range(64):
        length=rng.randint(4,8);addressed=bool(rng.randrange(2));priced=bool(rng.randrange(2))
        g=frame(length,priced)
        record=physical(g,rng,False)
        key=length,priced
        if key not in memo:
            memo[key]={}
            for n in (1,2):
                s=n*length+4
                planned=sorted(set(range(1,129))|{2*s*(j+1) for j in range(1,9)})
                memo[key][n]=[clock_case(g,length,n,m) for m in planned]
        evidence={}
        for n,hist in memo[key].items():
            sends=[r for r in hist if r['send']]
            evidence[n]={'first_eight_sends':[r['size'] for r in sends[:8]],
                         'eligible_in_first_eight':[bool(r['roles']['A' if addressed else 'T']['direct_on_own_output']) for r in sends[:8]],
                         'total_differences':[r['total_difference'] for r in sends[:8]],
                         'first_difference':next((r['size'] for r in hist if r['total_difference']),None)}
        draws.append({'draw':i,'neutral_length':length,'addressed':addressed,'degree_three':priced,
                      'input':record,'emissions':evidence})
    write('matched_draws.json.gz',draws)
    write('matched_profiles.json.gz',{f'{k[0]}_{int(k[1])}':v for k,v in sorted(memo.items())})


if __name__=='__main__':
    main()
