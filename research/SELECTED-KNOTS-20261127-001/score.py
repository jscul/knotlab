"""score.py: SK1 to SK4 of README.md "Frozen" on the frozen runs; writes score.json."""
import json, collections
from pathlib import Path
HERE = Path(__file__).resolve().parent
out = {}
for s in ('census', 'heldout', 'sampled', 'built'):
    c = collections.Counter(); bad = collections.defaultdict(list); short = collections.Counter()
    for l in open(HERE / ('frozen_%s.jsonl' % s)):
        r = json.loads(l); c['starts'] += 1
        if 'note' in r: c['fewer than two families'] += 1; continue
        c['starts with two or more families'] += 1
        if 'SK4' in r:
            c['SK4 read'] += 1
            v = r['SK4'].get('layer-three facts read by no single second-layer knot (dimension)')
            if v is None: c['SK4 too many places'] += 1
            elif v: bad['SK4'].append((r['start'], v))
            if r['SK4'].get('layer-three dimension'): c['SK4 starts with layer-three facts'] += 1
        for x in r['rounds']:
            if 'end' in x: continue
            c['rounds read'] += 1
            if x['SK1 failures']: bad['SK1'].append((r['start'], x['round'], x['SK1 failures'][:2]))
            if x['SK2 failures']: bad['SK2'].append((r['start'], x['round'], x['SK2 failures'][:2]))
            for k in (8, 12):
                y = x.get('SK3 k=%d' % k)
                if y is None: continue
                c['SK3 rows k=%d' % k] += 1
                if y['dimension'] != y['predicted']: bad['SK3 k=%d' % k].append((r['start'], x['round'], y))
            if 'shortest reading: kept sums' in x: short[(x['round'], x['shortest reading: kept sums'] > 0)] += 1
    out[s] = {'counts': dict(c), 'failure counts': {k: len(v) for k, v in bad.items()}, 'failures': {k: v[:10] for k, v in bad.items()},
              'shortest reading (round, any family sum kept): rows': {'%d %s' % k: v for k, v in sorted(short.items())}}
json.dump(out, open(HERE / 'score.json', 'w'), indent=1)
for s, v in out.items(): print(s, json.dumps(v['counts']), 'FAIL', json.dumps(v['failure counts']))
