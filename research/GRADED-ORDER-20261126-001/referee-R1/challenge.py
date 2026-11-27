"""Stress the two flags on connected, bare realizations of live-neighbour families.

Enumerate a connected graph and mark its maximal cliques as kept blocks or group
cells. Each uncovered pair has an inactive witness. The anchor construction is
the special case with a kept block and one private live knot per marked subset.
Use every core rank, and check suspect rosters by growing the realized stars.
"""
import argparse
from collections import Counter, defaultdict
from itertools import combinations
import json
from pathlib import Path
import random
import resource
import sys
import time

import networkx as nx

RESEARCH = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(RESEARCH / 'LATE-VIEWS-20261126-001'),
                str(RESEARCH / 'LOOK-ALIKE-20261126-001')]
import late
import alike


def bits(mask):
    while mask:
        bit = mask & -mask
        yield bit
        mask -= bit


def vertices(mask):
    return [b.bit_length() - 1 for b in bits(mask)]


def mask_of(items):
    return sum(1 << i for i in items)


def subsets(mask):
    sub = mask
    while sub:
        yield sub
        sub = (sub - 1) & mask


def sub(a, b):
    return a & b == a


def adjacency(n, cliques):
    adj = [0] * n
    for c in cliques:
        for a in vertices(c):
            adj[a] |= c ^ (1 << a)
    return adj


def connected(s, adj):
    left = s
    todo = s & -s
    while todo:
        a = todo & -todo
        left ^= a
        todo = (todo ^ a) | (adj[a.bit_length()-1] & left)
    return not left


def general_valid(n, cliques, groups):
    adj = adjacency(n, cliques)
    valid = {}
    for s in range(1, 1 << n):
        if any((s & g).bit_count() > 1 and not sub(g, s) for g in groups):
            continue
        if connected(s, adj):
            valid[s] = s.bit_count() - 1 - sum(g.bit_count()-2 for g in groups if sub(g, s))
    return valid


def anchored(n, links):
    """Every valid non-singleton contains an anchor; a private knot then enters exactly with all its anchors."""
    full = (1 << n) - 1
    groups = [a | (1 << (n+i)) for i, a in enumerate(links)]
    valid = {1 << (n+i): 0 for i in range(len(links))}
    for s in subsets(full):
        if any((s & a).bit_count() > 1 and not sub(a, s) for a in links):
            continue
        t = s | sum((1 << (n+i)) for i, a in enumerate(links) if sub(a, s))
        valid[t] = s.bit_count()-1-sum(a.bit_count()-2 for a in links if sub(a, s))
    return n+len(groups), [full]+groups, groups, valid


def information(valid):
    ranks = defaultdict(list)
    for s, r in valid.items():
        ranks[r].append(s)
    parents = {s: frozenset(t for t in ranks[r-1] if sub(t,s)) for s,r in valid.items()}
    split = any(not (parents[a] & parents[b]) for s, r in valid.items() if r >= 2
                for a,b in combinations(parents[s], 2))
    graded = True
    for s, r in valid.items():
        below = [t for t in valid if t != s and sub(t,s)]
        if any(not any(sub(t,p) for p in parents[s]) for t in below):
            graded = False
            break
        if any(any(t != p and sub(p,t) for t in below) for p in parents[s]):
            graded = False
            break
    # Bare elements require at least two parents at positive rank. A rank-zero set
    # with multiple members shadows a starting knot; even singleton type can then
    # be wrong. The concrete growth decides whether the two readings differ.
    bad_rank = any(r < 0 or (r==0) != (s.bit_count()==1) for s, r in valid.items())
    suspect = bad_rank
    for r in sorted(ranks):
        if r <= 0:
            continue
        curr = ranks[r]
        if len(curr) <= 1 and not ranks[r+1]:
            continue
        g = nx.Graph()
        g.add_nodes_from(curr)
        pp = {tuple(sorted((a,b))) for a,b in combinations(curr,2) if parents[a] & parents[b]}
        g.add_edges_from(pp)
        big = [frozenset(c) for c in nx.find_cliques(g) if len(c)>=3 and not
               set.intersection(*(set(parents[a]) for a in c))]
        actual = Counter(big)
        actual.update(frozenset(p) for p in pp if not any(set(p)<=b for b in big))
        predicted = Counter(parents[s] for s in ranks[r+1])
        if actual != predicted:
            suspect = True
            break
    return split, graded, suspect


def realize(n, cliques, groups):
    kept = [b for b in cliques if b not in groups]
    pairs = {a|b for g in groups for a,b in combinations(bits(g),2)
             if not any(sub(a|b,k) for k in kept)}
    family = sorted(kept + list(pairs))
    big_pair = {a|b for b0 in kept for a,b in combinations(bits(b0),2)
                if not any(sub(a|b,g) for g in groups)}
    roster = groups + list(big_pair)
    stars = [[] for _ in range(n+len(family))]
    key = 0
    def share(x,y):
        nonlocal key
        stars[x].append(key)
        stars[y].append(key)
        key += 1
    for i,b in enumerate(family):
        for j in vertices(b):
            share(j,n+i)
    for j in range(n):
        d = sum(bool((1 << j) & g) for g in roster)
        assert d >= 1
        for _ in range(d):
            stars[j].append(key)
            key += 1
        while len(stars[j]) < 3:
            i = next(i for i,b in enumerate(family) if (1<<j)&b)
            share(j,n+i)
    if len(family)==1 and len(stars[n]) < 3:
        share(0,n)
    for i in range(len(family)):
        while len(stars[n+i]) < 3:
            share(n+i,n+((i+1) % len(family)))
    assert min(map(len,stars)) >= 3
    return stars


def grow_check(n, cliques, groups, valid, split, graded, suspect):
    stars = realize(n, cliques, groups)
    m = late.Map(stars)
    assert m.cls == 'in' and all(tree for _,tree,_ in m.pieces)
    assert set(m.live)==set(range(n))
    assert set(groups)=={mask_of(g) for g in m.cells}
    assert not m.chains
    assert len(m.pieces) == 1
    args = (m.pieces[0][0], m.adj, m.chains, lambda v:v < m.n, None, lambda v:1, m.cells)
    p = late.GeneralPiece(*args)
    assert valid == {mask_of(s): r-1 for s,r in p.sizes_of.items()}
    flagged = split or any((a&b).bit_count() >= 2 for a,b in combinations(groups,2))
    res = {}
    for law in ('nae','parity'):
        target, why = late.predict(stars, 7, law, general=True)
        assert why=='predicted'
        g = alike.grow(stars, rounds=7, bound=1000, knot_law=law)
        observed = g['rows'].copy()
        if g['end'].startswith('closes'):
            observed.extend([{'sig0':[], 'sig1':[], 'n':0}] * (7-len(observed)))
        first = {}
        for kind in ('sig0','sig1'):
            for i,(p0,a) in enumerate(zip(target,observed),1):
                if p0[kind] != a[kind]:
                    first[kind] = dict(round=i,predicted=p0[kind],grown=a[kind])
                    break
        res[law] = {'first':first,'end':g['end'],'actual_rounds':len(g['rows']),
                    'rounds_compared':len(observed)}
    return {'knots':len(stars),'live':n,'cliques':[vertices(c) for c in cliques],
            'cells':[vertices(c) for c in groups], 'flagged':flagged,'split':split,
            'graded':graded,'suspect':suspect,'stars':stars, 'laws':res,
            'rank_counts':dict(Counter(valid.values()))}


def atlas(top):
    for g in nx.graph_atlas_g():
        n = len(g)
        if not 2 <= n <= top or not nx.is_connected(g):
            continue
        cl = [mask_of(c) for c in nx.find_cliques(g)]
        choices = [c for c in cl if c.bit_count() >= 3]
        for i in range(1<<len(choices)):
            groups = [c for j,c in enumerate(choices) if i&(1<<j)]
            blocks = [c for c in cl if c not in groups]
            count = sum(c.bit_count()-1 for c in cl)-n+1
            fill = sum(max((g&b).bit_count()-1,0) for b in blocks for g in groups)
            if count==fill:
                yield n, cl, groups, general_valid(n,cl,groups)


def anchors(draws, rng):
    # Includes three triples which meet successively. Add varied exact-size
    # families of triples and larger subsets, with at most one common anchor.
    yield anchored(6, [mask_of(x) for x in [(0,1,2),(2,3,4),(4,5,0)]])
    for _ in range(draws):
        n = rng.randint(5,10)
        all_sets = [mask_of(s) for k in range(3,min(n-2,5)+1) for s in combinations(range(n),k)]
        rng.shuffle(all_sets)
        links = []
        for a in all_sets:
            if all((a&b).bit_count()<2 for b in links):
                links.append(a)
                if rng.random()<.20:
                    break
        yield anchored(n,links)


def run(mode, limit, top):
    stamp = time.process_time()
    counts = Counter()
    seen = set()
    cases = atlas(top) if mode=='atlas' else anchors(limit,random.Random(715291))
    checks = 0
    best = 100
    for idx,(n,cl,gr,valid) in enumerate(cases):
        if idx>=limit:
            break
        if time.process_time()-stamp > 54:
            counts['cpu cut'] += 1
            break
        split, graded, suspect = information(valid)
        overlap = any((a&b).bit_count()>=2 for a,b in combinations(gr,2))
        flagged = bool(split or overlap)
        counts[f'{flagged=} {graded=} {suspect=}'] += 1
        # Prefer genuine grading; allow a smaller first counterexample with a
        # failed grading, and controls. A flagged suspect may mix differences
        # from several pieces; this search only handles connected bare cores.
        kind = (flagged,graded,suspect)
        if n > 14 or (flagged==suspect and (kind in seen or checks>=6)):
            continue
        if flagged!=suspect and not graded and n>=best:
            continue
        seen.add(kind)
        checks += 1
        row = grow_check(n,cl,gr,valid,split,graded,suspect)
        row['case'] = idx
        contradicted = all(bool(row['laws'][law]['first'])!=flagged for law in row['laws'])
        if contradicted:
            best = min(best,n)
        row['opposite_to_flag_both_laws'] = contradicted
        print(json.dumps(row),flush=True)
        if contradicted and graded:
            counts['decisive stop'] += 1
            break
    print(json.dumps(dict(counts),sort_keys=True),file=sys.stderr)
    print(f'{checks} stars grown under each law; {time.process_time()-stamp:.3f} CPU seconds; {resource.getrusage(resource.RUSAGE_SELF).ru_maxrss} KiB',file=sys.stderr)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('mode',choices=['atlas','anchors'])
    parser.add_argument('limit',type=int)
    parser.add_argument('top',type=int,nargs='?',default=7)
    args=parser.parse_args()
    resource.setrlimit(resource.RLIMIT_AS,(2<<30,2<<30))
    resource.setrlimit(resource.RLIMIT_CPU,(65,65))
    run(args.mode,args.limit,args.top)
