"""When are two forms first told apart?  From a run of form.py: for every pair of second seeds, the first round at
which what the first seed's descent makes differs; tallied by taking rule and by how short knots are treated."""
import json, sys, collections, itertools
rows = [json.loads(l) for l in open(sys.argv[1])]
tab = collections.defaultdict(collections.Counter)
for d in rows:
    if 'error' in d: continue
    sp = d['spec']; key = (str(sp['take']), sp['treatment'])
    P = d['classes by what it makes']
    forms = [f for f in P[0] if f != '(none)']
    for a, b in itertools.combinations(forms, 2):
        r = None
        for R, C in enumerate(P, 1):
            if a not in C or b not in C: r = 'not read further'; break
            if C[a] != C[b]: r = R; break
        tab[key][r if r is not None else 'never'] += 1
cols = [1, 2, 3, 4, 5, 6, 7, 8, 9, 'never', 'not read further']
print('%-28s' % 'taking rule, short knots' + ''.join('%9s' % str(c)[:8] for c in cols))
for key in sorted(tab): print('%-28s' % ('%s, %s' % key) + ''.join('%9d' % tab[key][c] for c in cols))
