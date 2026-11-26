"""tally.py RUNS: the second-switch tables (README.md, "What was found")."""
import sys, json, gzip, collections
def load(p): return [json.loads(l) for l in (gzip.open(p, 'rt') if p.endswith('.gz') else open(p))]
rows = load(sys.argv[1]); lost = [r for r in rows if 'not run' in r]
base = {(r['A'], r['B'], r['law']): r for r in rows if r.get('reading') == 'base'}
far = {(r['A'], r['B'], r['law']): r['by round'] for r in rows if r.get('reading') == 'far end distance'}
print('| receiver | cap | far end | rounds read | far end\'s distance at rounds 3, 6, 10, last | far-end changes heard (of) | earliest heard: t0, sharings, round | way after |')
print('|---|---|---|---|---|---|---|---|')
for key in sorted(base, key=lambda k: (k[2] == 'ORD', k[0], k[1])):
    b = base[key]; f = far.get(key, [])
    ch = [r for r in rows if r.get('reading') == 'change' and (r['A'], r['B'], r['law']) == key]
    hd = sorted([r for r in ch if r['heard'] is not None], key=lambda r: (r['t0'], r['heard']))
    pick = lambda i: (f[i - 1] if len(f) >= i else '-')
    def way(r):
        s = b['own births with a stub']; w = r['own births with']; n = min(len(s), len(w))
        return 'slow' if w[:n][-1:] == s[:n][-1:] else 'fast'
    print('| %s | %s | %s | %d | %s, %s, %s, %s | %d of %d | %s | %s |' % (key[0], key[2], key[1], b['rounds'], pick(3), pick(6), pick(10), f[-1] if f else '-',
          len(hd), len(ch), ('%d, %d, %d' % (hd[0]['t0'], hd[0]['sharings'], hd[0]['heard'])) if hd else '-', ', '.join(sorted({way(r) for r in hd})) or '-'))
print()
print('| receiver | cap | far end | after round | heard from sharing distances (of tried) |')
print('|---|---|---|---|---|')
for key in sorted(base, key=lambda k: (k[2] == 'ORD', k[0], k[1])):
    for t0 in (3, 6):
        hz = [r for r in rows if r.get('reading') == 'horizon' and (r['A'], r['B'], r['law']) == key and r['t0'] == t0]
        if not hz: continue
        by = collections.defaultdict(lambda: [0, 0])
        for r in hz: by[r['sharings']][1] += 1; by[r['sharings']][0] += r['heard'] is not None
        print('| %s | %s | %s | %d | %s |' % (key[0], key[2], key[1], t0, ', '.join('%d: %d/%d' % (s, v[0], v[1]) for s, v in sorted(by.items()))))
print('\nnot run', len(lost), lost[:3])
