"""tally.py OUT.json: the census predictions read from out/census_*.jsonl (README.md, P3.7 and P4.1-P4.3).
RING-BOND-20261127-001."""
import sys, json, glob, collections
from pathlib import Path
HERE = Path(__file__).resolve().parent


def load(pat):
    rows = []
    for f in sorted(glob.glob(str(HERE / 'out' / pat))):
        rows += [json.loads(l) for l in open(f)]
    return rows


def tally(rows, law):
    t = collections.Counter(); shapes = collections.Counter(); hold = collections.Counter()
    for r in rows:
        t['starts read'] += 1
        r0 = r['round 0']; t['with a bond at round 0'] += r0['bonds'] > 0; t['bonds at round 0'] += r0['bonds']
        key = 'bound fails' if law == 'nae' else 'six-sum fails'
        for rr in (r0, r['round 1'] if isinstance(r['round 1'], dict) else None):
            if rr is None: continue
            t[key] += rr[key]; t['all agree missing'] += rr['all agree missing']
            shapes.update(rr['by shape and missing count']); hold.update(rr['holder sizes'])
            t['bonds missing more than one triple'] += sum(v for k, v in rr['missing counts'].items() if k != '1')
        if isinstance(r['round 1'], dict):
            t['funded'] += 1; r1 = r['round 1']
            t['bonds at round 1'] += r1['bonds']
            t['funded with a round-1 bond with a birth among the holders'] += r1['with a birth among the holders'] > 0
            t['round-1 bonds with a birth among the holders'] += r1['with a birth among the holders']
            t['funded with readings shared by two bonds at round 1'] += r1['readings in two or more bonds'] > 0
        else: t['not funded'] += 1
    return {'tally': dict(t), 'by shape and missing count': dict(sorted(shapes.items())), 'holder sizes': dict(hold)}


if __name__ == '__main__':
    out = {'nae, holders <= 4': tally(load('census_nae_[0-9].jsonl'), 'nae'),
           'parity, holders <= 4': tally(load('census_parity_[0-9].jsonl'), 'parity')}
    m5 = {r['start']: r for r in load('census_nae_m5.jsonl')}
    m4 = {r['start']: r for r in load('census_nae_[0-9].jsonl')}
    both = sorted(set(m5) & set(m4)); c = collections.Counter()
    for s in both:
        for rd in ('round 0', 'round 1'):
            a, b = m4[s][rd], m5[s][rd]
            if not isinstance(a, dict): continue
            c['stages compared'] += 1; c['bonds, holders <= 4'] += a['bonds']; c['bonds, holders <= 5'] += b['bonds']
            c['stages with a bond only at five'] += a['bonds'] == 0 and b['bonds'] > 0
    out['holder-cap swap, nae'] = {'starts': len(both), **dict(c)}
    json.dump(out, open(sys.argv[1], 'w'), indent=1); print(json.dumps(out, indent=1))
