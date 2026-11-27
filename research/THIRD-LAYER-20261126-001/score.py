"""score.py: T1 to T4 of README.md "Frozen" on the frozen runs; writes score.json."""
import json, collections
from pathlib import Path
HERE = Path(__file__).resolve().parent
out = {}
base_m = {}
for s in ('census', 'heldout', 'sampled', 'built', 'merge'):
    rows = [json.loads(l) for l in open(HERE / ('frozen_%s.jsonl' % s))]
    c = collections.Counter(); bad = collections.defaultdict(list)
    for r in rows:
        c['starts'] += 1; c['families %d' % min(r['families'], 9)] += 1
        if r['T1 births across families']: bad['T1'].append(r['start'])
        m = r['families']
        if m and not r.get('T2 one rule, every proper subfamily free'): bad['T2'].append((r['start'], m, r.get('T2 tuples')))
        if s == 'built': base_m[r['start']] = m
        if s == 'merge' and base_m.get(r['start'].split(' + ')[0]) is not None and base_m[r['start'].split(' + ')[0]] - m != 1:
            bad['T2 merge'].append((r['start'], m))
        reads = [x for x in r['rounds'] if 'least flips' in x]
        if reads:
            L0 = reads[0]['least flips']
            for x in reads[1:]:
                for a, (b0, bt) in enumerate(zip(L0, x['least flips'])):
                    if b0 is None or bt is None: continue
                    if isinstance(bt, str): continue               # more than 40: at least the bound
                    if isinstance(b0, str) or bt < b0 + 2 * x['round']: bad['T3'].append((r['start'], a, b0, x['round'], bt))
            c['rounds read'] += len(reads)
        r34 = {x['round']: x for x in reads if 'UPTO5 class facts' in x}
        if 3 in r34 and 4 in r34:
            c['starts with rounds 3 and 4'] += 1
            if r34[3]['UPTO5 class facts'] != r34[4]['UPTO5 class facts']: bad['T4 dimension'].append((r['start'], r34[3]['UPTO5 class facts'], r34[4]['UPTO5 class facts']))
        for x in r34.values():
            if x.get('every l_A a class fact') is False: bad['T4 facts'].append((r['start'], x['round']))
        ends = [x['end'] for x in r['rounds'] if 'end' in x]
        c['end: ' + (ends[0] if ends else 'read to round 4')] += 1
    out[s] = {'counts': dict(c), 'failures': {k: v[:12] for k, v in bad.items()}, 'failure counts': {k: len(v) for k, v in bad.items()}}
json.dump(out, open(HERE / 'score.json', 'w'), indent=1)
for s, v in out.items(): print(s, json.dumps(v['counts']), 'FAIL', json.dumps(v['failure counts']))
