"""Pair-reading counterexamples whose first mismatch occurs after two further rounds."""

import argparse
from collections import Counter
from itertools import combinations
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / 'experiments/GROWN-END-MEET-ONCE-20261119-001/GROWN-END-MEET-ONCE-20261119-001-E001_rounds'
sys.path.insert(0,str(SOURCE))
from census import production_law  # noqa: E402
from reach_bound import verifier  # noqa: E402

STARTS = {
    'parallel_allowed': [[0,1,4,5,6], [2,3,7,8], [0,1,2,3], [7,8,9,10]],
    'meet_once': [[0,1,8,9,10], [2,3,5,6], [0,2,4], [1,3,4], [5,7,11,12], [6,7,13]],
}


def study(kind):
    check = verifier()
    rule = production_law()
    rooted = rule.from_junctions(STARTS[kind])
    supports = [STARTS[kind]]
    for _ in range(3):
        assert rooted.step(rule.gf2(rule.F.fewest),None)['new']
        assert rooted.implied_mismatch == 0
        supports.append([sorted(row) for row in rooted.bits_of])
    presentations = [check.Arrangement.parse(phase) for phase in supports]
    assert all(check.start_audit(stage)['census_open_legal'] for stage in presentations)
    assert all(check.start_audit(stage)['meets_once'] == (kind == 'meet_once') for stage in presentations)
    rounds = [check.round_replay(a,b) for a,b in zip(presentations,presentations[1:])]

    pair = (0,1)
    image = (1,2)
    swap = {0:2,2:0}
    reports = []
    for age,stage in enumerate(presentations[1:],start=1):
        fixed = set().union(*(stage.stars[j] for j in stage.live))
        assert not (fixed & swap.keys())
        table, shores, seen = check.exact_table(stage,1 << 20)
        assert table is not None
        mismatches = [(mark,(table[mark],table[target]))
                      for mark in combinations(stage.labels,2)
                      if (target := tuple(sorted(swap.get(x,x) for x in mark))) != mark and table[mark] != table[target]]
        readings = [table[marks] for marks in (pair,image)]
        citations = [check.cut_certificate(stage,marks,table[marks],shores[marks]) for marks in (pair,image)]
        reports.append({'age':age,'junctions':len(stage.stars),'distinctions':len(stage.labels),
                        'loose':len(stage.loose),'fixed_live_count':len(fixed),
                        'whole_pairs_checked':len(table),'moved_pair_mismatches':len(mismatches),
                        'split_pair_distances':readings, 'minimizing_bonds':citations})
    assert [p['moved_pair_mismatches'] != 0 for p in reports] == [False,False,True]
    assert [p['split_pair_distances'] for p in reports] == [[3,3],[3,3],[2,3]]
    return {'meeting_convention':kind,'permutation':swap,'source_pair':pair,'image_pair':image,
            'start_and_round_rows':supports,
            'independent_rounds':[sorted(Counter((len(r['taken']),len(r['fresh'])) for r in moves).items()) for moves in rounds],
            'positive_stages':reports}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--convention',choices=STARTS,action='append')
    a = p.parse_args()
    print(json.dumps({key:study(key) for key in (a.convention or STARTS)},indent=2))


if __name__ == '__main__':
    main()
