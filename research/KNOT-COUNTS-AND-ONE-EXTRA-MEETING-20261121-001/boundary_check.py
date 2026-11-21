"""Check whether the entire source can still close, before simulating any births.

A simple one-cycle founder is a cyclically ordered list of rooted trees.
Only holders of degree at least three can change whether they are live when
the one extra loose distinction is added. For each such choice we grant
every other live knot the largest budget permitted in the study.
"""
from collections import Counter
from functools import cache
from itertools import combinations
import sys
from pathlib import Path


@cache
def rooted(size):
    if size == 1:
        return ((),)
    options = [(n, t) for n in range(1, size) for t in rooted(n)]

    def children(left, first):
        if left == 0:
            yield ()
            return
        for j in range(first, len(options)):
            weight, shape = options[j]
            if weight > left:
                break
            for more in children(left-weight, j):
                yield (shape, *more)

    return tuple(children(size-1, 0))


def cycle_patterns(size, length):
    def sequences(left, slots):
        if slots == 0:
            if left == 0:
                yield ()
            return
        for weight in range(1, left-slots+2):
            for tail in sequences(left-weight, slots-1):
                for shape in rooted(weight):
                    yield (shape, *tail)
    for seq in sequences(size, length):
        backwards = seq[::-1]
        if all(seq <= side[j:]+side[:j] for side in (seq,backwards) for j in range(length)):
            yield seq


def holding(sequence):
    nodes = [[] for _ in sequence]
    def meet(a, b):
        nodes[a].append(b)
        nodes[b].append(a)
    def attach(parent, branches):
        for branch in branches:
            kid = len(nodes)
            nodes.append([])
            meet(parent,kid)
            attach(kid,branch)
    for v,trees in enumerate(sequence):
        meet(v,(v+1)%len(sequence))
        attach(v,trees)
    return tuple(sum(1 << j for j in nb) for nb in nodes)


def positions(mask):
    while mask:
        bit = mask & -mask
        yield bit.bit_length()-1
        mask ^= bit


def connected_and_funded(neighbors, live, length):
    witnesses = tuple(nb & live for nb in neighbors)
    adjacent = [0]*len(neighbors)
    for w in witnesses:
        for v in positions(w):
            adjacent[v] |= w ^ (1<<v)
    reached = todo = live & -live
    while todo:
        bit = todo & -todo
        v = bit.bit_length()-1
        new = adjacent[v] & ~reached
        todo = (todo ^ bit) | new
        reached |= new
    if reached != live:
        return False
    calls = [nb.bit_count() for nb in adjacent]
    # A set of three mutually related live knots without one witness is a
    # six-cycle in the bipartite incidence of live knots and witness copies.
    # A simple one-cycle founder gives each connected incidence component
    # at most one cycle. Therefore the three pairs of this triple are
    # replaced by one three-parent group, with no possible fourth member.
    if length in (3,6):
        for a,b,c in combinations(positions(live),3):
            triple=(1<<a)|(1<<b)|(1<<c)
            if (adjacent[a] & (1<<b) and adjacent[a] & (1<<c)
                    and adjacent[b] & (1<<c) and not any(w & triple == triple for w in witnesses)):
                for v in (a,b,c):
                    calls[v]-=1
    return all(calls[v] <= max(3-neighbors[v].bit_count(),0)+1 for v in positions(live))


def scan(size):
    counts=Counter()
    survivors=[]
    for length in range(3,size+1):
        for seq in cycle_patterns(size,length):
            counts['holdings']+=1
            nbs=holding(seq)
            forced=sum(1<<v for v,nb in enumerate(nbs) if nb.bit_count()<3)
            optional=((1<<size)-1) ^ forced
            mask=optional
            while True:
                live=mask | forced
                counts['live_choices']+=1
                if connected_and_funded(nbs, live, length):
                    survivors.append((length, seq, tuple(positions(live))))
                if not mask:
                    break
                mask=(mask-1)&optional
    return counts,survivors



def funded_threshold_fixture():
    """Give the two tree leaves one loose name above the minimum.

    The sixth funded parity birth closes the five-knot founder. Check the
    actual names, stage sizes, sign reversal and both full ordinary laws.
    """
    root=Path(__file__).resolve().parents[2]
    prior='STATE-DISTANCE-AND-REACHED-GROWTH-20261120-001B'
    sys.path.insert(0,str(root/'experiments'/prior/(prior+'-E001_pair_growth')))
    sys.path.insert(0,str(root/'research'/'ERASURE-AND-CLOSING-SIGNS-20261121-001'))
    from explosive_stages import advance
    from independent_checks import closed_components
    # First three knots meet pairwise; the last two each meet one spent knot.
    rows=((0,2,5,6),(0,1,3),(1,2,4),(3,7,8,9),(4,10,11,12))
    for law in ('parity','nae'):
        stage=rows
        cohorts=[]
        for cut in range(1,7):
            state,stage,births=advance(stage,law)
            assert state=='births'
            cohorts.append((len(births),sum(f for _,f in births)))
            closings=closed_components(stage)
            if cut<6 or law=='nae':
                assert not closings
        assert cohorts[:5]==[(6,14),(7,14),(6,14),(6,12),(4,4)]
        assert cohorts[5]==(1,0 if law=='parity' else 1)
        width=len(set.union(*(set(r) for r in stage)))
        print(law,'five founding knots',cohorts,'complete size',len(stage),width,'odd test at ordinary closures',list(closings.values()))
        if law=='parity':
            assert set(closings)=={frozenset(range(len(stage)))}
            assert closings[frozenset(range(len(stage)))]
            def row_mask(row):
                return sum(1<<name for name in row)
            total=0
            for row in stage[:-1]:
                total^=row_mask(row)
            assert total==row_mask(stage[-1])


def check():
    # This is an independent stress check past the registered maximum of 8.
    # Counts are counts of physical shapes and live subsets, not weighted rates.
    for n in range(4,14):
        cnt,keep=scan(n)
        print(n,'shapes',cnt['holdings'],'live subsets',cnt['live_choices'],'fundable connected live subsets',len(keep))
        if n>=6:
            assert len(keep)==n%2
            if keep:
                length,trees,live=keep[0]
                assert length==n and not any(trees) and len(live)==n
        elif n in (4,5):
            assert len(keep)==2
    funded_threshold_fixture()


if __name__=='__main__':
    check()
