"""Complete start census by holder multiplicities, followed by exact six-mark scores."""
from collections import Counter
from functools import cache
from fractions import Fraction
from itertools import combinations, permutations, product
from math import gcd
import sys

import networkx as nx
import numpy as np

from observables import CONTEXTS, SIGNS, WORDS, measure

TRIPLE_ORDERS = list(permutations(range(3)))
ORDERS = [(l, r) for l in TRIPLE_ORDERS for r in TRIPLE_ORDERS]
WORD_INDEX = {word:i for i,word in enumerate(WORDS)}
REORDER = np.array([[WORD_INDEX[tuple(np.array(word)[np.argsort(tuple(l) + tuple(3 + i for i in r))])]
                     for word in WORDS] for l,r in ORDERS])
SIGNS_ARRAY = np.array(SIGNS)
BITS = np.asarray(WORDS)
S, T = BITS[:,2], BITS[:,5]
SEL = np.asarray([(S==s)&(T==t) for s,t in CONTEXTS], dtype=np.int64)
PAIR_BITS = (2*BITS[:,0]+BITS[:,1], 2*BITS[:,3]+BITS[:,4])
LOCAL = np.asarray([SEL[st]*(p==v) for p in PAIR_BITS for st in range(4) for v in range(4)])
COND, COMMON, BOTH_FLIP = [], [], []
for s,t in CONTEXTS:
    i = BITS[:,s] ^ BITS[:,3+t]
    ii = ((BITS[:,0]==s)&(BITS[:,1]==s)) ^ ((BITS[:,3]==t)&(BITS[:,4]==t))
    for output in (i,ii):
        signs = 1 - 2 * output
        COMMON.append(signs)
        COND.append(SEL[2*s+t]*signs)
    BOTH_FLIP.append(SEL[2*s+t] * (BITS[:,s]!=s) * (BITS[:,3+t]!=t))
COND, COMMON, BOTH_FLIP = map(np.asarray,(COND,COMMON,BOTH_FLIP))


def splits(total, places):
    if places == 0:
        if total == 0:
            yield ()
    elif places == 1:
        yield (total,)
    else:
        for first in range(total+1):
            for tail in splits(total-first,places-1):
                yield (first,)+tail


@cache
def graph_templates(k):
    out = []
    for g in nx.graph_atlas_g():
        if len(g) != k or len(g.edges)>10:
            continue
        pairs = tuple(sorted(tuple(sorted(p)) for p in g.edges))
        seq = tuple((i,) for i in g) + pairs
        pos = {v:i for i,v in enumerate(seq)}
        actions = [tuple(pos[tuple(sorted(a[j] for j in group))] for group in seq)
                   for a in nx.isomorphism.GraphMatcher(g,g).isomorphisms_iter()]
        out.append((pairs,seq,actions))
    return out


def presentations(n,k):
    # Every distinction is identified up to renaming by its one or two holders.
    # The simple sharing pattern is fixed first. Its automorphisms then act on
    # all positive meeting multiplicities and all nonnegative loose counts.
    for pairs, seq, actions in graph_templates(k):
        if len(pairs)>n:
            continue
        for doubles in range(max(len(pairs),3*k-n),n+1):
            for extra in splits(doubles-len(pairs),len(pairs)):
                counts = tuple(v+1 for v in extra)
                held = [0]*k
                for (a,b),v in zip(pairs,counts):
                    held[a] += v
                    held[b] += v
                least = [max(0,3-total) for total in held]
                spare = n-doubles-sum(least)
                if spare < 0:
                    continue
                for add in splits(spare,k):
                    weights = tuple(a+b for a,b in zip(add,least))+counts
                    if any(tuple(weights[j] for j in action)<weights for action in actions):
                        continue
                    rows = [[] for _ in range(k)]
                    label = 0
                    for holders, value in zip(seq,weights):
                        for h in holders:
                            rows[h].extend(range(label,label+value))
                        label += value
                    assert label==n
                    yield tuple(map(tuple,rows)), bool(extra and max(extra)>0)


@cache
def law_mask(n, v, law):
    vals = np.arange(1<<n,dtype=np.uint16)
    held = vals & v
    return ((np.bitwise_count(held)%2)==0) if law=="parity" else ((held!=0)&(held!=v))


@cache
def codes(n, marks):
    vals = np.arange(1<<n,dtype=np.uint16)
    packed = np.zeros(1<<n,dtype=np.uint16)
    for m in marks:
        packed = 2*packed + ((vals>>m)&1)
    return packed


def states_and_gate(n, rows,law):
    ok = np.ones(1<<n,dtype=bool)
    for row in rows:
        ok &= law_mask(n, sum(1<<bit for bit in row),law)
    for row in rows:
        proj = np.bincount(codes(n,row)[ok],minlength=1<<len(row))>0
        if not np.array_equal(proj,law_mask(len(row),(1<<len(row))-1,law)):
            return None
    return ok


def triples(rows):
    together = {}
    for row in rows:
        for bit in row:
            together.setdefault(bit,set()).update(row)
    # Breadth-first support-step distances are computed once for each distinction.
    steps={}
    for start in together:
        seen={start:0}
        todo=[start]
        for b in todo:
            for c in together[b]:
                if c not in seen:
                    seen[c]=seen[b]+1
                    todo.append(c)
        steps[start]=seen
    for i,j in combinations(range(len(rows)),2):
        for lhs in combinations(rows[i],3):
            forbidden = set.union(*(together[b] for b in lhs))
            for rhs in combinations([b for b in rows[j] if b not in forbidden],3):
                d=min((steps[a][b] for a in lhs for b in rhs if b in steps[a]),default=None)
                yield i,j,lhs,rhs,("no_chain" if d is None else "2" if d==2 else "finite_3_or_more")


def grouped_orders(hist,law):
    """The 36 re-orderings in one batch. Integer products use the census bound."""
    normalized = np.asarray(hist,dtype=np.int64)
    assert sum(hist)<=1024
    raw = normalized[REORDER]
    weights = raw @ SEL.T
    complete = (weights!=0).all(axis=1)
    local = (raw @ LOCAL.T).reshape(36,2,4,4)
    hide = complete.copy()
    for side,tests in enumerate((((0,1),(2,3)),((0,2),(1,3)))):
        for a,b in tests:
            hide &= (local[:,side,a]*weights[:,b,None]==local[:,side,b]*weights[:,a,None]).all(axis=1)
    if law=="nae":
        assert np.array_equal(raw, raw[:,::-1])
        assert (raw @ BOTH_FLIP.T > 0).all()  # Every stipulated pin pattern extends.
        assert complete.all()
    cond = (raw @ COND.T).reshape(36,4,2)
    common = (raw @ COMMON.T).reshape(36,4,2)
    den = np.prod(weights,axis=1)
    safe = np.where(weights==0,1,weights)
    values = cond * (den[:,None]//safe)[:,:,None]
    ranked, ext = [], []
    for reading in range(2):
        ranked.append((values[:,:,reading] @ SIGNS_ARRAY.T).max(axis=1))
        ext.append((common[:,:,reading] @ SIGNS_ARRAY.T).max(axis=1))
        assert (ext[-1]<=2*sum(hist)).all()
    if law=="nae":
        assert (ranked[0] < 4*den).all() and (ranked[1]<=2*den).all()
    return complete,hide,den,ranked,ext


def count_case(n,k):
    detail = {"n":n,"holders":k,"presentations":0,"multiple_meetings":0,"duplicate_displays":0}
    laws = {}
    for law in ("nae","parity"):
        laws[law] = {"lawful":0,"lawful_with_eligible_readers":0,"eligible_orders":0,
                     "complete_cells":0,"hidden":0,"strict_I_excesses_with_hidden_pair":0,
                     "strict_II_excesses_with_hidden_pair":0,"raw":{},"bands":{}}
    for rows,repeated in presentations(n,k):
        detail["presentations"] += 1
        detail["multiple_meetings"] += int(repeated)
        detail["duplicate_displays"] += int(len(set(rows))<len(rows))
        placements = list(triples(rows))
        for law, entry in laws.items():
            ok = states_and_gate(n,rows,law)
            if ok is None:
                continue
            entry["lawful"] += 1
            entry["lawful_with_eligible_readers"] += bool(placements)
            for ai,bi,l,r,band in placements:
                hist = tuple(np.bincount(codes(n,l+r)[ok],minlength=64).tolist())
                cache_key = ",".join(map(str,hist))
                if cache_key not in entry["raw"]:
                    entry["raw"][cache_key] = {"triples":0, "supports":rows,"holders":[ai,bi],"marks":l+r,"bands":{}}
                record=entry["raw"][cache_key]
                record["triples"]+=1
                bands=record["bands"]
                bands[band]=bands.get(band,0)+1
    for law, entry in laws.items():
        peak = {}
        for hist_key, row in entry["raw"].items():
            hist = tuple(map(int,hist_key.split(",")))
            comp,hide,den,ranked,ext = grouped_orders(hist,law)
            copies = row["triples"]
            entry["eligible_orders"] += 36*copies
            entry["complete_cells"] += int(comp.sum())*copies
            entry["hidden"] += int(hide.sum())*copies
            for band,quantity in row["bands"].items():
                br=entry["bands"].setdefault(band,{"orders":0,"hidden":0,"complete":0,"peaks":{}})
                br["orders"]+=36*quantity
                br["hidden"]+=int(hide.sum())*quantity
                br["complete"]+=int(comp.sum())*quantity
                for read,nums in zip(("I","II"),ranked):
                    for category,mask in (("hidden",hide),("all",comp)):
                        if not mask.any(): continue
                        best=max(Fraction(int(nums[ix]),int(den[ix])) for ix in np.flatnonzero(mask))
                        label=category+"_"+read
                        if label not in br["peaks"] or best>Fraction(br["peaks"][label]):
                            br["peaks"][label]=str(best)
            for p,name in enumerate(("I","II")):
                entry["strict_"+name+"_excesses_with_hidden_pair"] += int(((ranked[p]>2*den)&hide).sum())*copies
                for group,mask,numer,denom in (("hidden",hide,ranked[p],den),("all",comp,ranked[p],den),
                                                ("external",np.ones(36,dtype=bool),ext[p],np.full(36,sum(hist)))):
                    key = group+"_"+name
                    for a in np.flatnonzero(mask):
                        f = Fraction(int(numer[a]),int(denom[a]))
                        if key not in peak or f>peak[key][0]:
                            peak[key]=(f,{"histogram":hist_key,"orders":ORDERS[a],"score":str(f),"tied_orders":copies})
                        elif f==peak[key][0]:
                            peak[key][1]["tied_orders"] += copies
        entry["peaks"]={key:val[1] for key,val in peak.items()}
    return {**detail,"laws":laws}
