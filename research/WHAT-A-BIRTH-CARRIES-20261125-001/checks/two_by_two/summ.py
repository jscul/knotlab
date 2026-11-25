import json, sys, collections
rows = [json.loads(l) for l in open(sys.argv[1])]
tab = collections.defaultdict(collections.Counter)
err = 0
for d in rows:
    if 'error' in d: err += 1; print('ERROR', d['spec'], d['error'][-200:]); continue
    sp = d['spec']
    key = (sp['take'], sp['ration'], sp['treatment'], sp['knot_law'], sp['start'])
    if not d['triples']: tab[key]['(no part with two partners)'] += 1
    for t in d['triples']:
        m = t.get('m') or {}
        tab[key][(t['kind'], tuple(t['classes']), t.get('renaming exchanging Y1 and Y2 fixing X'), m.get('verdict'), str(m.get('m')))] += 1
for k in sorted(tab): print(k, dict(tab[k]))
print('errors', err)
