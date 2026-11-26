"""tally.py RUNS [RUNS ...]: the self-read threshold tables (README.md): by law, pairs read, pairs with a knot made after
the start short, pairs still linked after round 3, far changes heard by the round they were set after, late hearings
(after round 6) with growth going on in both runs after them (the advisor's jam check); then, for each pair of laws, in
how many pairs the growth with no change makes the same births, and in how many the whole record (changes included)
is the same."""
import sys, json, gzip, collections
def load(p): return [json.loads(l) for l in (gzip.open(p, 'rt') if p.endswith('.gz') else open(p))]
runs = [r for p in sys.argv[1:] for r in load(p) if 'law' in r]
order = []
for r in runs:
    if r['law'] not in order: order.append(r['law'])
print('| law | pairs read | with a short knot made after the start | linked after round 3 | changes after round %s heard (of) | late (after round 6) | late with growth going on in both |'
      % ' / '.join(str(t) for t in sorted({c['t0'] for r in runs for c in r['changes']})))
print('|---|---|---|---|---|---|---|')
for k in order:
    rs = [r for r in runs if r['law'] == k]
    cell = []
    for t in sorted({c['t0'] for r in runs for c in r['changes']}):
        ch = [c for r in rs for c in r['changes'] if c['t0'] == t]
        cell.append('%d of %d' % (sum(1 for c in ch if c['heard']), len(ch)))
    late = [(r, c) for r in rs for c in r['changes'] if c['heard'] and c['heard'] > 6]
    goes = sum(1 for r, c in late if sum(r['births'][c['heard']:]) > 0 and c['births with'] and sum(c['births with'][c['heard']:]) > 0)
    print('| %s | %d | %d | %d | %s | %d | %d |' % (k, len(rs), sum(1 for r in rs if any(r['made short'])),
          sum(1 for r in rs if len(r['linked']) > 2 and r['linked'][2]), ' / '.join(cell), len(late), goes))
    if late: print('|  | receivers with a late hearing: %s; rounds %s |' % (sorted({(r['A'], r['B']) for r, c in late})[:6], dict(collections.Counter(c['heard'] for r, c in late))))
by = collections.defaultdict(dict)
for r in runs: by[(r['A'], r['B'])][r['law']] = r
strip = lambda r: {k: v for k, v in r.items() if k not in ('law', 'binds on the growth with no change')}
print('\n| laws | pairs with both | same births, no change | same whole record |\n|---|---|---|---|')
for i, a in enumerate(order):
    for b in order[i + 1:]:
        ks = [k for k, v in by.items() if a in v and b in v]
        print('| %s, %s | %d | %d | %d |' % (a, b, len(ks), sum(1 for k in ks if by[k][a]['births'] == by[k][b]['births']),
                                           sum(1 for k in ks if strip(by[k][a]) == strip(by[k][b]))))
