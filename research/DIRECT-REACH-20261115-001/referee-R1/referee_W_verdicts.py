"""Referee R1, item (a): Corollary W's verdicts from MY every-depth block computation (referee_blocks.py) for every description
with orbits <= 4, tops k = 2 and 3, every s <= 60 and every remaining depth r (r = 0 .. r0 - 1 separately, r >= r0 together).
Writes referee_W_verdicts.json."""
import collections
import json
import sys

sys.path.insert(0, '/home/jscul/p-vs-np-contact-first/research/DIRECT-REACH-20261115-001/referee-R1')
from referee_pattern import load_population, HERE  # noqa: E402
from referee_blocks import Blocks  # noqa: E402

SMAX = 60


def classify(pred):
    vals = [tuple(v) for P in pred.values() for v in P]
    ties = {a for a, _ in vals}
    if ties == {1}:
        return 'tie at every s and r'
    if ties == {0}:
        b3_s = sorted({s + 1 for P in pred.values() for s, (_, b) in enumerate(P) if b})
        b3_not = sorted({s + 1 for P in pred.values() for s, (_, b) in enumerate(P) if not b})
        if not b3_not:
            return 'no tie; two-orbit 3-bond at every s and r'
        if b3_s == [1] and 1 not in b3_not:
            return 'no tie; two-orbit 3-bond only at s = 1'
        return 'no tie; two-orbit 3-bond at s in %s (s <= %d)' % (b3_s[:10], SMAX)
    return 'mixed: ' + str(sorted(set(vals)))


out, tally = {}, collections.Counter()
for d in load_population():
    try:
        B = Blocks(d['key'])
    except ValueError as e:
        tally[(d['profile'], 'orbits grow')] += 1
        continue
    row = dict(profile=d['profile'], types=len(B.types), orbit_sizes=sorted(set(B.m)))
    for k in (2, 3):
        ev = B.every_depth(k, SMAX)
        row['k%d' % k] = dict(r0=ev['r0'], start=ev['start'], period=ev['period'], alive_every_depth=ev['alive_every_depth'],
                              verdict=classify(ev['pred']),
                              first8={'r=%d' % r if r < ev['r0'] else 'r>=%d' % ev['r0']: P[:8] for r, P in ev['pred'].items()})
    out[d['case']] = row
    tally[(d['profile'], row['k3']['verdict'], row['k3']['alive_every_depth'])] += 1
    if row['k2']['verdict'] != row['k3']['verdict']:
        print('k2 differs from k3:', d['case'][:12], d['profile'], '| k2:', row['k2']['verdict'], row['k2']['first8'], '| k3:', row['k3']['verdict'])
json.dump(dict(smax=SMAX, tally={str(k): v for k, v in tally.items()}, cases=out), open(HERE / 'referee_W_verdicts.json', 'w'), indent=1)
for k, v in sorted(tally.items(), key=str):
    print(k, v)
print('types range', min(r['types'] for r in out.values()), max(r['types'] for r in out.values()),
      'orbit-size sets', collections.Counter(str(r['orbit_sizes']) for r in out.values()))
