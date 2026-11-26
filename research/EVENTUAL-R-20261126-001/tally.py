"""tally.py: the counts of part B over the sampled starts (part_b_census.jsonl.gz), against preregistration.md."""
import json, collections, gzip
from pathlib import Path
HERE = Path(__file__).resolve().parent
rows = [json.loads(l) for l in gzip.open(HERE / 'part_b_census.jsonl.gz', 'rt')]
c = collections.Counter(r['end'] for r in rows)
print(json.dumps({'starts': len(rows), 'ends': dict(c)}))
grow = [r for r in rows if r['end'] == 'growing']
print(json.dumps({'1 growing starts': len(grow), 'with a settled failing pair by round 3':
                  sum(1 for r in grow if r['B1 first round with a settled failing pair'] is not None and r['B1 first round with a settled failing pair'] <= 3),
                  'first failing round': dict(collections.Counter(str(r['B1 first round with a settled failing pair']) for r in grow))}))
for end in ('closed', 'stalled'):
    S = [r for r in rows if r['end'] == end]
    print(json.dumps({end: len(S), 'every knot pair commuting at the end': sum(1 for r in S if r['B1 knot pairs at the end'].get('fail', 0) == 0 and r['B1 knot pairs at the end'].get('open', 0) == 0),
                      'first failing round': dict(collections.Counter(str(r['B1 first round with a settled failing pair']) for r in S))}))
closers = [r for r in rows if r['end'] == 'closed']
print(json.dumps({'2 closers': len(closers), 'knots commute (B4 run)': sum(1 for r in closers if isinstance(r.get('B4'), dict)),
                  'forced odd': sum(1 for r in closers if isinstance(r.get('B4'), dict) and r['B4']['forced sign'] == 'odd'),
                  'closer sizes (knots)': dict(collections.Counter(r['knots'] for r in closers))}))
f = collections.Counter()
for r in rows:
    for k, v in r['B2'].items(): f[k] += v
print(json.dumps({'3 flip formula': dict(f)}))
b3 = collections.Counter()
for r in rows:
    ff = r['B1 first round with a settled failing pair']
    for x in r['B3']:
        before = ff is None or x['round'] < ff
        key = 'before the first failing pair' if before else 'at or after it'
        b3[(key, 'rounds')] += 1; b3[(key, 'a choice exists')] += x['a choice exists']
        b3[(key, 'unique')] += x['unique']; b3[(key, 'next round realises one')] += x['next round realises one']
print(json.dumps({'4 demand for a state': {' / '.join(k): v for k, v in sorted(b3.items())}}))
b4 = [r['B4'] for r in closers if isinstance(r.get('B4'), dict)]
print(json.dumps({'5 closers with commuting knots': len(b4),
                  'odd: GF(2) reader contradicted somewhere': sum(1 for b in b4 if b['forced sign'] == 'odd' and b.get('GF(2) reader contradicted', 0) > 0),
                  'odd': sum(1 for b in b4 if b['forced sign'] == 'odd'),
                  'even: GF(2) reader contradicted somewhere': sum(1 for b in b4 if b['forced sign'] == 'even' and b.get('GF(2) reader contradicted', 0) > 0),
                  'even': sum(1 for b in b4 if b['forced sign'] == 'even'),
                  'closers with laws gained from later layers': sum(1 for b in b4 if b.get('laws gained from later layers', 0) > 0)}))
