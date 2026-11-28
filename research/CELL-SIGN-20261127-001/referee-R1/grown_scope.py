"""Test how far the claim about all grown closures extends within the source census."""
import argparse
from collections import Counter
import json
import sys
from time import monotonic

from scope_check import can_orient, HERE, INPUT, RESEARCH, strict_words

PRIOR = RESEARCH / 'ENCODED-READERS-20261127-001/referee-R1'
sys.path.insert(0, str(PRIOR))
from birth_inputs import columns, history


def run(probe):
    roster = json.loads((RESEARCH / 'FORBID-EDITS-20261126-001/starts.json').read_text())
    previous = {r['key']:r for r in map(json.loads, INPUT.read_text().splitlines()) if r['population']=='birth'}
    count, scopes, even_sizes = Counter(), Counter(), Counter()
    witnesses, rows = [], []
    for key in (range(50) if probe else range(len(roster))):
        outcome, stages = history(roster[key])
        scopes[outcome] += 1
        if outcome != 'grown closed':
            continue
        allowed, odd = columns(stages)
        assert odd == (key in previous)
        source = dict(supports=stages[-1],pairs=allowed)
        if odd:
            assert allowed == previous[key]['pairs']
        totals = Counter()
        for cycles,pairs,minimal in strict_words(source,minimal_only=False):
            sign = sum((min(a,b)<c<max(a,b)) != (min(a,b)<d<max(a,b)) for a,c,b,d in cycles) % 2
            oriented = can_orient(cycles)
            assert not (sign and oriented)
            label = ', '.join(('minimal' if minimal else 'nonminimal', 'odd' if sign else 'even',
                               'orientable' if oriented else 'nonorientable'))
            totals[label] += 1
            if not sign and minimal:
                even_sizes[len(cycles)] += 1
            if not sign and not oriented:
                odd_parts = []
                for mask in range(1, (1 << len(cycles)) - 1):
                    chosen = [i for i in range(len(cycles)) if mask >> i & 1]
                    ordered = [cycles[i] for i in chosen]
                    checks = Counter(tuple(sorted((a,b))) for walk in ordered for a,b in zip(walk,walk[1:]+walk[:1]))
                    sub_sign = sum((min(a,b)<c<max(a,b)) != (min(a,b)<d<max(a,b)) for a,c,b,d in ordered) % 2
                    if sub_sign and all(k % 2 == 0 for k in checks.values()):
                        odd_parts.append(chosen)
                witnesses.append(dict(start=key,cycle_lists=cycles,failing_pairs=pairs,minimal=minimal,
                                      strict_odd_subcollections_by_index=odd_parts))
        rows.append(dict(start=key,rounds=len(stages)-1,birth_choices_attain_odd=odd,counts=dict(totals)))
        count.update(totals)
    out = dict(population="Every positive-round closure of ordinary parity growth through four rounds and forty knots from the 7,075 archived starts; labelled nonempty strict birth choices at every size.",
               weighting="One per labelled choice per census start; the same grown holding can occur at several starts.",
               independent_input="Growth history and birth-pair eligibility from the encoded-readers referee, using the archived ordinary growth engine. Exhaustive strict-word enumeration and orientation by reversal masks in scope_check.py.",
               outcomes=dict(scopes),counts=dict(count),minimal_even_by_size=dict(sorted(even_sizes.items())),even_nonorientable_choices=witnesses,rows=rows)
    if not probe:
        (HERE/'grown_scope.json').write_text(json.dumps(out,indent=1)+'\n')
    print(dict(scopes),dict(count),len(witnesses))

if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--probe',action='store_true')
    started=monotonic()
    run(parser.parse_args().probe)
    print(f'{monotonic()-started:.3f} s')
