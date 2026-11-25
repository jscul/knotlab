import json, sys, collections, itertools
rows = [json.loads(l) for l in open(sys.argv[1])]
ok = [d for d in rows if 'error' not in d]
print('studies', len(rows), 'failed or over time', len(rows) - len(ok))
bylaw = collections.defaultdict(dict)
for d in ok:
    sp = d['spec']; bylaw[(str(sp['take']), sp['ration'], sp['treatment'])][sp['first'][0]] = d
print('law | for each first seed A..E: classes by what it makes at round 1 > at the last round read by all (last round the count rose) | fates of the first seed\'s own line over forms: ends/steady/grows/other')
for law, D in bylaw.items():
    cells = []; F = collections.Counter(); tot = 0
    for f in sorted(D):
        d = D[f]; c = d['classes by round, by what it makes']; n = d['forms still read, by round']
        full = [i for i, x in enumerate(n) if x == n[0]]          # rounds read by every form
        cc = [c[i] for i in full]
        rose = max([i + 1 for i in range(1, len(cc)) if cc[i] > cc[i - 1]] or [1])
        cells.append('%s %d>%d(r%d of %d)' % (f, cc[0], cc[-1], rose, len(cc)))
        for v in d['fate'].values():
            k = 'ends' if v == 'ends' else 'steady' if v.startswith('steady') else 'grows' if v == 'grows' else 'other'
            F[k] += 1
    print('%-9s %-7s %-16s | %s | %d/%d/%d/%d' % (law + ('  '.join(cells), F['ends'], F['steady'], F['grows'], F['other'])))
