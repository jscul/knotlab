"""Check G's obligations from the prospective first paid cohort.

The separate physical replay tests whether ordinary founders actually produce
this cohort. This checker uses only common payers and the registered input slots.
"""
from itertools import combinations
import json
from pathlib import Path


PAYER_ROSTERS = (
    ('W P1 D1', 'W P1 D1'),
    ('W P2', 'W P2'),
    ('W D2 P2', 'W D2'),
    ('P1 P2', 'P1 P2'),
    ('D1 D2', 'D1 D2'),
    ('W Z', 'W Z'),
    ('D2 D3', 'D2 D3'),
    ('Da Zs', 'Da Zs'),
    ('Da', 'Da P2'),
    ('D2', 'D2 P3'),
    ('Da P3', 'Da'),
)
ANCHORS = 'W P1 P2 D1 D2 Da P3'.split()
RELEASE = {'A':'P1 P2 W', 'B':'W Z', 'T':'Z', 'X':'D1 D2 W',
           'V1':'D1 P1'}
TARGET = 'G'


def maximal(sets):
    return {s for s in sets if not any(s < t for t in sets)}


def groups_at(center, blocks):
    """Every funded multiple-parent proposal containing the center."""
    local = [b for b in blocks if center in b]
    neighbors = set().union(*local) - {center}
    triples_or_more = set()
    for size in range(2, len(neighbors) + 1):
        for others in combinations(sorted(neighbors), size):
            g = frozenset((center, *others))
            if any(g <= b for b in blocks):
                continue
            if all(any(a in b and c in b for b in blocks)
                   for a, c in combinations(g, 2)):
                triples_or_more.add(g)
    large = maximal(triples_or_more)
    residual = {frozenset((center, n)) for n in neighbors
                if not any(n in g for g in large)}
    return sorted(large | residual, key=lambda g: tuple(sorted(g)))


def grant(parent_count, demand):
    # All compared cuts have several actual children.
    return max(1, 3 - parent_count, demand)


def flip_marked_pair(blocks, present):
    """Diagnostic on the restricted input only. The physical edits precede it."""
    pair = frozenset(('X', 'V2'))
    reduced = set(blocks)
    if present:
        reduced.add(pair)
    else:
        # Drop only joint witness of this pair; keep every other witnessed subset.
        for b in list(reduced):
            if pair <= b:
                reduced.remove(b)
                reduced.update((b - {'X'}, b - {'V2'}))
    return maximal(reduced)


def words(sets):
    return sorted(' '.join(sorted(s)) for s in sets)


def compare(divert, diagnostic):
    old = {f'p{i}':frozenset(row[divert].split()) for i,row in enumerate(PAYER_ROSTERS)}
    old.update({f'anchor_{s}':frozenset((s,)) for s in ANCHORS})
    children = set().union(*old.values())
    blocks = list(old.values())
    next_groups = set()
    unaries = {}
    first_bank = {}
    for u in sorted(children):
        gs = groups_at(u, blocks)
        bank = grant(sum(u in b for b in blocks), len(gs))
        first_bank[u] = bank
        unaries[u] = bank - len(gs)
        next_groups.update(gs)
    assert all(x <= 1 for x in unaries.values())
    next_groups.update(frozenset((u,)) for u,x in unaries.items() if x)
    release = dict(RELEASE, V2='P2 '+('Da' if divert else 'D2'))
    labels = {frozenset(v.split()):k for k,v in release.items()}
    assert set(labels) <= next_groups
    parents = {labels.get(g,'other('+','.join(sorted(g))+')'):g for g in next_groups}
    payment_blocks = [frozenset(u for u,gs in parents.items() if p in gs) for p in children]
    rnames = {'A','B','T'}
    neighborhood = set().union(*(b for b in payment_blocks if b & rnames))
    restricted = maximal({b & neighborhood for b in payment_blocks})
    native_pair = any({'X','V2'}<=b for b in restricted)
    read = flip_marked_pair(restricted, diagnostic) if diagnostic is not None else restricted
    around = {s:groups_at(s,read) for s in rnames}
    banks = {s:grant(len(parents[s]),len(gs)) for s,gs in around.items()}
    through_ab = set(around['A']) | set(around['B'])
    for s in ('A','B'):
        assert banks[s]==len(around[s]), 'An unpaired remainder needs explicit handling'
    assert frozenset(('A','B')) in through_ab
    # One child per distinct paid group.
    gnames = {g: (TARGET if g=={'A','B'} else '+'.join(sorted(g))) for g in through_ab}
    next_blocks = [frozenset(gnames[g] for g in through_ab if p in g)
                   for p in set().union(*through_ab)]
    local_groups = groups_at(TARGET,next_blocks)
    return dict(physical_pair=native_pair, diagnostic_pair=diagnostic,
                first_banks=first_bank, receiver_banks=banks, local_members=sorted(neighborhood),
                restricted_launch_witnesses=words(restricted), tested_launch_witnesses=words(read),
                obligations_at_launch={k:words(v) for k,v in sorted(around.items())},
                siblings_of_G={v:sorted(k) for k,v in sorted(gnames.items(),key=lambda kv:kv[1])},
                obligations_through_G=words(local_groups),
                grant_and_funded_children=grant(2,len(local_groups)))


if __name__=='__main__':
    cases={a:{'paid':compare(i,None),'with_joint_witness':compare(i,True),
              'without_joint_witness':compare(i,False)} for i,a in enumerate(('intact','diverted'))}
    intact = cases['intact']['paid']
    diverted = cases['diverted']['paid']
    assert intact['receiver_banks'] == diverted['receiver_banks']
    assert intact['local_members'] == diverted['local_members']
    intact_witnesses = set(intact['restricted_launch_witnesses'])
    diverted_witnesses = set(diverted['restricted_launch_witnesses'])
    assert intact_witnesses - diverted_witnesses == {'V2 X'}
    assert not diverted_witnesses - intact_witnesses
    for c in cases.values():
        for key in ('with_joint_witness', 'without_joint_witness'):
            assert c[key]['obligations_through_G'] == cases['intact'][key]['obligations_through_G']
    for name,c in cases.items():
        print(name,[(k,v['grant_and_funded_children']) for k,v in c.items()])
    (Path(__file__).parent/'local_check.json').write_text(json.dumps(cases,indent=2,sort_keys=True)+'\n')
