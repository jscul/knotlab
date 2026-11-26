"""tally_b.py RUNS: the shortage table (README.md, "What was found: B")."""
import sys, json, gzip, collections
def load(p): return [json.loads(l) for l in (gzip.open(p, 'rt') if p.endswith('.gz') else open(p))]
rows = load(sys.argv[1]); runs = [r for r in rows if 'law' in r]; lost = [r for r in rows if 'not run' in r]
name = lambda l: l[0] + ('' if l[1] is None else ' + ' + l[1] + ('' if l[2] is None else '(%s)' % l[2]))
print('| law | pairs | ended by the guard / the knot bound / the rounds | pairs with a short knot made after the start | linked after round 3 / 8 | far changes heard, linked (of) | not linked (of) | latest first hearing |')
print('|---|---|---|---|---|---|---|---|')
order = []
for r in runs:
    k = name(r['law'])
    if k not in order: order.append(k)
for k in order:
    rs = [r for r in runs if name(r['law']) == k]
    e = collections.Counter(r['ended'] for r in rs)
    sh = sum(1 for r in rs if any(r['made short']))
    at = lambda i: sum(1 for r in rs if len(r['linked']) >= i and r['linked'][i - 1])
    ly = [c for r in rs for c in r['changes'] if c['linked']]; ln = [c for r in rs for c in r['changes'] if not c['linked']]
    hy = [c for c in ly if c['heard']]; hn = [c for c in ln if c['heard']]
    print('| %s | %d | %d / %d / %d | %d | %d / %d | %d of %d | %d of %d | %s |' % (k, len(rs), e['guard'], e['knots'], e['rounds'], sh, at(3), at(8),
          len(hy), len(ly), len(hn), len(ln), max((c['heard'] for c in hy + hn), default='-')))
print('\nnot run', len(lost), lost[:3])
