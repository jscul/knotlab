"""tally_again.py RUNS: the sent-again table (AGAIN.md)."""
import sys, json, gzip, collections
def load(p): return [json.loads(l) for l in (gzip.open(p, 'rt') if p.endswith('.gz') else open(p))]
rows = load(sys.argv[1]); runs = [r for r in rows if 'again' in r]; lost = [r for r in rows if 'not run' in r]
print('| law | pairs | first change heard (round) | second change set (round) | its sharings from the receiver | second heard | third heard |')
print('|---|---|---|---|---|---|---|')
for law in ('ONE-FEWER', 'REC-ONE-FEWER', 'JOIN-FEWER', 'CAP-3'):
    rs = [r for r in runs if r['law'][0] == law]
    if not rs: continue
    h1 = collections.Counter(r['h1'] for r in rs)
    sets = collections.Counter(a[0]['set after round'] for r in rs for a in r['again'][:1] if a)
    dist = [t['sharings from A'] for r in rs for a in r['again'][:1] for t in a if t['sharings from A'] is not None]
    second = sum(1 for r in rs if r['again'] and any(t['heard'] is not None for t in r['again'][0]))
    third = sum(1 for r in rs if len(r['again']) > 1 and any(t['heard'] is not None for t in r['again'][1]))
    print('| %s | %d | %s | %s | %s to %s (median %s) | %d | %d |' % (law, len(rs), dict(sorted(h1.items(), key=lambda kv: (kv[0] is None, kv[0] or 0))),
          dict(sorted(sets.items())), min(dist) if dist else '-', max(dist) if dist else '-', sorted(dist)[len(dist) // 2] if dist else '-', second, third))
print('\nruns read', len(runs), 'not run', len(lost))
