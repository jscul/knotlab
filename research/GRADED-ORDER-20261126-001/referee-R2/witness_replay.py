"""Recheck the previous eight constructions with a finite horizon."""
import json
import sys
from reading import HERE, compare

for name in ('obstruction_nae', 'small_nae', 'challenge_anchor'):
    with (HERE.parent / 'referee-R1' / (name + '.jsonl')).open() as f:
        for r in map(json.loads, f):
            if 'stars' not in r:
                continue
            n = len(r['stars'])
            horizon = 4 if n == 30 else 6
            for law in ('nae','parity'):
                result = compare(r['stars'], law, horizon)
                print(json.dumps(dict(source=name, case=r.get('case'), knots=n, horizon=horizon, law=law,
                                      **result)),flush=True)
            if '--pilot' in sys.argv:
                sys.exit(0)
