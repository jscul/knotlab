"""checks45.py: Y4 and Y5 (README.md): the first-coded reading on the advisor's three starts, and the least rank of the
chained twins on the starts that have them."""
import sys, os, json, gzip
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'GRADED-ORDER-20261126-001'))
import order, twins, graded
late, score = order.late, graded.score
def rows(f): return [json.loads(l) for l in open(f)]
def grown(f, law, key, val):
    return next(x for x in [json.loads(l) for l in gzip.open('grown_%s_%s.jsonl.gz' % (f, law), 'rt')] if x.get(key) == val)
for f, key, val, R in (('cyc7_treeplus', 'draw', 335, 24), ('cyc6_uniform', 'index', 13560, 24), ('cyc7_treeplus', 'draw', 109, 9)):
    for law in ('nae', 'parity'):
        g = grown(f, law, key, val)
        for fc in (True, False):
            try:
                P, why = order.predict_nodes(g['stars'], R, law, True, True, fc)
                v = score.compare(P, dict(g, rows=g['rows'][:R])) if P is not None else 'not predicted: ' + why
            except RuntimeError as e: v = 'not predicted: ' + str(e)
            print(json.dumps({'start': '%s %s %s' % (f, key, val), 'law': law, 'rounds': R,
                              'reading': 'first-coded' if fc else 'as frozen', 'first differing round': v}))
for l in open('scores.jsonl'):
    r = json.loads(l)
    if r['twins'] == 'twins, chained' and r['law'] == 'nae':
        x = rows(r['file'])[r['line'] - 1]
        T = twins.twins(x['stars'], cycles=True)
        print(json.dumps({'start': r['draw'], 'least rank of chained twins': min(t['rank'] for t in T if t['chained']),
                          'first difference': r['verdict']}))
