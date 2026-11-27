"""tally.py: Part 1's scores by stratum (README.md); joins each score (order.py core, one line a grown row, in the grown
file's order) to its start's stratum (strata.txt) by the start's stars."""
import json, collections, sys, gzip
strata = {}
for l in open('strata.txt'):
    if not l.startswith('{'): continue
    x = json.loads(l); strata[(x['file'], x['line'])] = x
src = {}
for f in ('cyc6_uniform', 'cyc7_treeplus', 'cyc7_grow'):
    for i, l in enumerate(open(f + '.jsonl')):
        src[json.dumps(json.loads(l)['stars'])] = (f + '.jsonl', i + 1)
rows = []
for f in ('cyc6_uniform', 'cyc7_treeplus', 'cyc7_grow'):
    for law in ('nae', 'parity'):
        G = [json.loads(l) for l in gzip.open('grown_%s_%s.jsonl.gz' % (f, law), 'rt')]
        N = [json.loads(l) for l in open('nodes_%s_%s.jsonl' % (f, law))]
        assert len(G) == len(N)
        for g, n in zip(G, N):
            key = src[json.dumps(g['stars'])]; s = strata[key]
            cyc = [p for p in s['pieces'] if p['cycle by count']]
            core = ' / '.join(sorted({p['core'] for p in cyc}))
            ch = any(p['chains'] for p in cyc)
            if g.get('end') == 'not run (time limit)': verdict = 'growth not run'
            elif 'error' in n: verdict = 'not predicted: ' + n['error'][:40]
            elif isinstance(n['node reading'], str): verdict = n['node reading']
            elif n['node reading'] is None: verdict = 'agrees'
            else: verdict = 'differs from round %d' % n['node reading']
            rows.append({'file': key[0], 'line': key[1], 'draw': g.get('draw', g.get('index')), 'law': law, 'core': core,
                         'chains on it': ch, 'twins': s['twins'], 'rounds read': n.get('rounds read'), 'verdict': verdict})
with open('scores.jsonl', 'w') as f:
    for r in rows: f.write(json.dumps(r) + '\n')
c = collections.Counter((r['core'], r['chains on it'], r['twins'], r['verdict'].split(' from')[0] if r['verdict'].startswith('differs') else r['verdict']) for r in rows)
for k, v in sorted(c.items(), key=str): print(v, k)
print('misses:')
for r in rows:
    if r['verdict'].startswith('differs'): print(json.dumps(r))
