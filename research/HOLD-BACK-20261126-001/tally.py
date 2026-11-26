"""tally.py RUNS: the hold-back tables (README.md): by law, pairs read, pairs with a knot made after the start short,
far changes heard (linked, not linked) by the round they were set, late hearings (after round 2d = 6) and whether both
growths go on making knots after a late hearing (the advisor's jam check)."""
import sys, json, gzip, collections
def load(p): return [json.loads(l) for l in (gzip.open(p, 'rt') if p.endswith('.gz') else open(p))]
rows = load(sys.argv[1]); runs = [r for r in rows if 'law' in r]; lost = [r for r in rows if 'not run' in r]
name = lambda l: ' + '.join(str(x) for x in l if x is not None)
print('| law | pairs read | with a short knot made after the start | changes after round 1 / 2 / 3 heard (of) | late (after round 6) | late with growth going on in both |')
print('|---|---|---|---|---|---|')
order = []
for r in runs:
    if name(r['law']) not in order: order.append(name(r['law']))
late_list = []
for k in order:
    rs = [r for r in runs if name(r['law']) == k]
    sh = sum(1 for r in rs if any(r['made short']))
    cell = []
    for t in sorted({c['t0'] for r in rs for c in r['changes']}):
        ch = [c for r in rs for c in r['changes'] if c['t0'] == t]
        cell.append('%d of %d' % (sum(1 for c in ch if c['heard']), len(ch)))
    late = [(r, c) for r in rs for c in r['changes'] if c['heard'] and c['heard'] > 6]
    goes = sum(1 for r, c in late if sum(r['births'][c['heard']:]) > 0 and c['births with'] and sum(c['births with'][c['heard']:]) > 0)
    late_list += [(k, r['A'], r['B'], c['t0'], c['sharings'], c['heard'], c['linked']) for r, c in late]
    print('| %s | %d | %d | %s | %d | %d |' % (k, len(rs), sh, ' / '.join(cell), len(late), goes))
print('\nlate hearings:', len(late_list)); [print('  ', x) for x in late_list[:30]]
print('receivers with a late hearing:', collections.Counter((x[0], x[1]) for x in late_list))
print('not run', len(lost), [(r['job'], r['not run'], r['lines read']) for r in lost])
