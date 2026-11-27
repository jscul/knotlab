"""tally2.py: Part 2's scores (README.md): each kept start's node-reading score (order.py core --groups, one line a grown
row) joined to its twin bucket (from the draw) and, for chained twins, the least rank of its chained twins (twins.py);
T1-T3 by weighting."""
import sys, os, json, collections, gzip
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'GRADED-ORDER-20261126-001'))
import twins
rows = []
for w, f in (('W1 tree+ nine knots', 'twin9'), ('W2 tree+s50 eight knots', 'twin8')):
    src = {json.dumps(json.loads(l)['stars']): json.loads(l) for l in open(f + '_draw.jsonl')}
    for law in ('nae', 'parity'):
        G = [json.loads(l) for l in gzip.open('grown_%s_%s.jsonl.gz' % (f, law), 'rt')]
        N = [json.loads(l) for l in open('nodes_%s_%s.jsonl' % (f, law))]
        assert len(G) == len(N)
        for g, n in zip(G, N):
            x = src[json.dumps(g['stars'])]
            if g.get('end') == 'not run (time limit)': v = 'growth not run'
            elif 'error' in n: v = 'not predicted: ' + n['error'][:40]
            elif isinstance(n['node reading'], str): v = n['node reading']
            elif n['node reading'] is None: v = 'agrees'
            else: v = n['node reading']
            r = {'weighting': w, 'draw': x['draw'], 'law': law, 'bucket': x['twins'], 'rounds read': n.get('rounds read'),
                 'first differing round': v if isinstance(v, int) else None, 'verdict': 'differs' if isinstance(v, int) else v}
            if x['twins'] == 'twins, chained':
                try: r['least rank of chained twins'] = min(t['rank'] for t in twins.twins(x['stars']) if t['chained'])
                except RuntimeError: r['least rank of chained twins'] = None    # core over the cap at scoring
            rows.append(r)
with open('scores2.jsonl', 'w') as f:
    for r in rows: f.write(json.dumps(r) + '\n')
c = collections.Counter((r['weighting'], r['bucket'], r['law'], r['verdict']) for r in rows)
for k, v in sorted(c.items()): print(v, k)
by = collections.defaultdict(dict)
for r in rows: by[(r['weighting'], r['draw'])][r['law']] = r
print('T1 (no chained twins: every start agrees under both laws):')
for w in ('W1 tree+ nine knots', 'W2 tree+s50 eight knots'):
    s = [d for (ww, _), d in by.items() if ww == w and next(iter(d.values()))['bucket'] != 'twins, chained']
    ok = sum(all(r['verdict'] == 'agrees' for r in d.values()) for d in s)
    bad = [next(iter(d.values()))['draw'] for d in s if any(r['verdict'] == 'differs' for r in d.values())]
    print(' ', w, '%d of %d agree under both laws; differing: %s; other: %d' % (ok, len(s), bad, len(s) - ok - len(bad)))
print('T2 / T3 (chained twins):')
for w in ('W1 tree+ nine knots', 'W2 tree+s50 eight knots'):
    s = [d for (ww, _), d in by.items() if ww == w and next(iter(d.values()))['bucket'] == 'twins, chained']
    differ = [d for d in s if any(r['verdict'] == 'differs' for r in d.values())]
    t3 = [d for d in differ if all(r['first differing round'] == r['least rank of chained twins'] for r in d.values()
                                    if r['verdict'] == 'differs')]
    agree = [next(iter(d.values()))['draw'] for d in s if all(r['verdict'] == 'agrees' for r in d.values())]
    print(' ', w, '%d of %d differ under at least one law; agree under both: %s; T3 holds on %d of %d' % (
        len(differ), len(s), agree, len(t3), len(differ)))
    for d in differ:
        if d not in t3: print('   T3 miss', json.dumps(list(d.values())))
