import json, sys, collections
tab = collections.Counter(); where = collections.defaultdict(set); err = 0
for fn in sys.argv[1:]:
    for l in open(fn):
        d = json.loads(l)
        if 'error' in d: err += 1; continue
        sp = d['spec']
        for r in d['rows']:
            c = r['classes']
            kind = 'no difference' if len(set(c)) == 1 else ('differs with which' if c[1] != c[2] else 'how many')
            start = any(x['start knot holds a linking distinction'] for x in r['links'])
            anc = all(x['ancestral'] for x in r['links'])
            k = (sp['take'], sp['ration'], sp['treatment'], r['why'], kind, str(c) if kind != 'no difference' else '', 'm=%s' % r['m'],
                 'a start knot holds a linking distinction' if start else 'no start knot holds one', 'ancestral' if anc else 'not ancestral')
            tab[k] += 1; where[k].add(sp['start'])
print('runs that failed', err)
for k, v in sorted(tab.items(), key=str): print(v, k, len(where[k]), 'starts', sorted(where[k])[:6])
