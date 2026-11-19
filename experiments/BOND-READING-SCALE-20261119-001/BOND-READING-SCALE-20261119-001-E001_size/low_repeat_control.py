"""Independently reconstruct the small weighted prefix and the exact width-21 hit."""

from argparse import ArgumentParser
from collections import Counter
from itertools import combinations
import json
from pathlib import Path

from low_delayed import production_law, verifier


def compositions(slots,budget,minimum):
    if slots == 0:
        yield ()
        return
    for first in range(minimum,budget-minimum*(slots-1)+1):
        for rest in compositions(slots-1,budget-first,minimum):
            yield (first,*rest)


def independent_prefix(width_case):
    reference = verifier()
    law = production_law()
    graphs = ((1,()),(2,((0,1),)),(3,((0,1),(0,2))),(3,((0,1),(0,2),(1,2))))
    counts = Counter()
    attempted = 0
    for n,edges in graphs:
        for weights in compositions(len(edges),11,1):
            length = sum(weights)
            core = [[] for _ in range(n)]
            label = 0
            for (a,b),weight in zip(edges,weights,strict=True):
                core[a].extend(range(label,label+weight))
                core[b].extend(range(label,label+weight))
                label += weight
            for loose in compositions(n,11-length,0):
                if sum(loose)<3 or any(len(row)+free<3 for row,free in zip(core,loose,strict=True)):
                    continue
                seed = []
                name = label
                for row,free in zip(core,loose,strict=True):
                    seed.append(row + list(range(name,name+free)))
                    name += free
                if not reference.start_audit(reference.Arrangement.parse(seed))['census_open_legal']:
                    continue
                grown = law.from_junctions(seed)
                attempted += 1
                new = grown.step(law.gf2(law.F.fewest),None)['new']
                assert grown.implied_mismatch == 0
                if new<3 or len(grown.bits_of)>6:
                    continue
                here = reference.Arrangement.parse([sorted(row) for row in grown.bits_of])
                if len(here.labels)<=14:
                    counts[len(here.stars),len(here.labels)] += 1
    expected = {(row['junctions'],row['width']):row['histories'] for row in width_case['joint_tiers']
                if row['junctions']<=6 and row['width']<=14}
    assert dict(counts)==expected
    return {'maximum_width':14,'maximum_current_junctions':6,'literal_growth_attempts':attempted,
            'counts':[[j,w,n] for (j,w),n in sorted(counts.items())]}


def verify_failure(failure):
    reference = verifier()
    law = production_law()
    stages = [reference.Arrangement.parse(failure[key]) for key in ('start','current','next')]
    assert all(reference.start_audit(stage)['census_open_legal'] for stage in stages)
    literal = law.from_junctions(failure['start'])
    for before,after in zip(stages,stages[1:]):
        reference.round_replay(before,after)
        assert literal.step(law.gf2(law.F.fewest),None)['new']
        assert sorted(tuple(sorted(row)) for row in literal.bits_of)==sorted(tuple(sorted(row)) for row in after.stars)
    prefix = failure['old_movable_permutation']
    present = stages[1]
    image = prefix + list(range(len(prefix),len(present.labels)))
    assert all(image[x] == x for i in present.live for x in present.stars[i])
    old,_,_ = reference.exact_table(present,1<<18)
    assert all(old[tuple(sorted(image[x] for x in q))] == price for q,price in old.items())
    p = tuple(failure['old_pair'])
    q = tuple(sorted(image[x] for x in p))
    later,shores,_ = reference.exact_table(stages[2],1<<18)
    values = [later[p],later[q]]
    assert [value+1 for value in values] == failure['successor_K']
    assert values[0] != values[1]
    return {'current_full_pairs':len(old),'successor_full_pairs':len(later),'old_pair':p,'image':q,
            'now_K':[old[p]+1,old[q]+1], 'next_K':failure['successor_K'],
            'minimizers':[reference.cut_certificate(stages[2],key,later[key],shores[key]) for key in (p,q)]}


def main():
    p = ArgumentParser(description=__doc__)
    p.add_argument('negative',type=Path)
    p.add_argument('joint',type=Path)
    a = p.parse_args()
    j = json.loads(a.joint.read_bytes())
    print(json.dumps({'prefix':independent_prefix(json.loads(a.negative.read_bytes())),
                      'joint_failures':[verify_failure(failure) for failure in j['failures']]},indent=2))


if __name__ == '__main__':
    main()
