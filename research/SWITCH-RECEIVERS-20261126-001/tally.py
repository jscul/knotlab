"""tally.py RUNS: the receiver census (README.md, "What was found")."""
import sys, json, gzip, collections
def load(p): return [json.loads(l) for l in (gzip.open(p, 'rt') if p.endswith('.gz') else open(p))]
rows = load(sys.argv[1]); runs = [r for r in rows if 'classes' in r]; lost = [r for r in rows if 'not run' in r]
def band(r):
    f, d = r['first differs'], r['d']
    if f is None: return 'none'
    return 'before d' if f < d else 'd to 2d' if f <= 2 * d else 'after 2d'
def alternate_after(r, B):
    """own knots short in alternate rounds after the first difference, with sender B"""
    s = r['by sender'][B]['A short'][r['first differs'] - 1:]
    return len(s) >= 3 and all(bool(s[i]) != bool(s[i + 1]) for i in range(len(s) - 1))
def switches(r):
    return band(r) == 'after 2d' and r['own short before'] is False
print('| law | d | receivers read | read the far end: before d / d to 2d / after 2d / never | after 2d with no own knot short before (switch) | first rounds of the switches |')
print('|---|---|---|---|---|---|')
sw = collections.defaultdict(list)
for law in ('CAP-3', 'CAP-4', 'CAP-5', 'REC-ONE-FEWER', 'ORD'):
    for d in (2, 3, 4, 5):
        rs = [r for r in runs if r['law'] == law and r['d'] == d]
        if not rs: continue
        b = collections.Counter(band(r) for r in rs)
        s = [r for r in rs if switches(r)]; sw[(law, d)] = s
        print('| %s | %d | %d | %d / %d / %d / %d | %d | %s |' % (law, d, len(rs), b['before d'], b['d to 2d'], b['after 2d'], b['none'], len(s),
              dict(sorted(collections.Counter(r['first differs'] for r in s).items()))))
print()
for (law, d), s in sorted(sw.items()):
    if s and d == 3:
        print('%s, d = 3: %d switching receivers' % (law, len(s)))
        for r in s:
            cl = ' | '.join(','.join(c) for c in r['classes'])
            alt = [B for B in r['by sender'] if alternate_after(r, B)]
            print('   %-18s first %s  classes: %s  alternate-short after with: %s' % (r['A'], r['first differs'], cl, alt))
print('\nreceivers read', len(runs) // 20 if runs else 0, 'lines', len(runs), 'not run', len(lost), lost[:3])
