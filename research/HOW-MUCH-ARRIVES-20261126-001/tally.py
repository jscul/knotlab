"""tally.py RUNS.jsonl[.gz]: the tables of HOW-MUCH-ARRIVES-20261126-001 from drive.py's output."""
import sys, json, gzip, collections
path = sys.argv[1]
op = gzip.open if path.endswith('.gz') else open
rows = [json.loads(l) for l in op(path, 'rt')]
R3 = ('name', 'sig0', 'sig1')
bad = [r for r in rows if 'not run' in r]
print('# Jobs: %d read, %d not run' % (len(rows) - len(bad), len(bad)))
for r in bad: print('  not run:', r['job'], r['not run'])

def share(row, R):
    m = row['n'] + row["n'"]
    return sum(row[R]) / m if m else 0.0

print('\n## Setting A: verdicts by start, change and knot law (cases), in each reading')
tab = collections.defaultdict(lambda: {R: collections.Counter() for R in R3})
last_share = collections.defaultdict(list)
for r in rows:
    if r.get('setting') or 'not run' in r or r.get('change') == 'pair': continue
    key = (r['start'], r['change'] + ('' if r['change'] in ('mark', 'move') else ' %d' % r['round']), r['knot law'])
    cases = [r] if r['change'] in ('mark', 'move') else r['marks']
    for c in cases:
        for R in R3: tab[key][R][c['verdicts'][R]] += 1
        if c['rows']: last_share[key].append(share(c['rows'][-1], 'sig1'))
print('| start | change | knot law | cases | by name | sig0 | sig1 | sig1 share, last round (min to max) |')
print('|---|---|---|---|---|---|---|---|')
for key in sorted(tab):
    t = tab[key]; n = sum(t['name'].values())
    f = lambda C: ', '.join('%s %d' % (k, v) for k, v in sorted(C.items()))
    s = last_share[key]
    print('| %s | %s | %s | %d | %s | %s | %s | %.2f to %.2f |' % (key[0], key[1], key[2], n, f(t['name']), f(t['sig0']), f(t['sig1']),
                                                             min(s) if s else 0, max(s) if s else 0))

print('\n## Setting A: every case that weakens in an ancestry-free reading')
for r in rows:
    if r.get('setting') or 'not run' in r or r.get('change') == 'pair': continue
    cases = [r] if r['change'] in ('mark', 'move') else r['marks']
    for c in cases:
        if 'weakens' in (c['verdicts']['sig0'], c['verdicts']['sig1']):
            ser = [(x['round'], sum(x['sig1']), x['n'] + x["n'"]) for x in c['rows']]
            print('-', r['start'], r['change'], r.get('at', r.get('round')), 'knot', c.get('knot'), r['knot law'], c['verdicts'], 'sig1 damage/(n+n\') by round:', ser)

print('\n## Setting A: shells of made marks and pulses, last round read (sig1)')
wid = collections.defaultdict(collections.Counter)
for r in rows:
    if r.get('change') not in ('made', 'pulse') or 'not run' in r: continue
    for c in r['marks']:
        if not c['rows'] or 'shells' not in c['rows'][-1]: continue
        sh = c['rows'][-1]['shells']
        hit = sorted(int(k) for k, v in sh.items() if v[2] > 0)
        allsh = sorted(int(k) for k in sh)
        w = 0 if not hit else hit[-1] - hit[0] + 1
        wid[(r['start'], r['change'], r['round'], r['knot law'])]['width %s' % (w if w <= 4 else '5+')] += 1
        front = allsh[-1] if allsh else None
        wid[(r['start'], r['change'], r['round'], r['knot law'])]['damage at the last shell' if hit and hit[-1] == front else 'none at the last shell'] += 1
for key in sorted(wid): print('-', key, dict(sorted(wid[key].items())))

print('\n## Setting A: pairs of made marks in round 2, damage at the last round read: both against u + v')
for r in rows:
    if r.get('change') != 'pair' or 'not run' in r: continue
    for R in R3:
        C = collections.Counter()
        for p in r['pairs']:
            u, v, b = p['damage u, v, both'][R]
            C['less than either' if b < min(u, v) else 'less than the sum' if b < u + v else 'the sum' if b == u + v else 'more than the sum'] += 1
        print('-', r['start'], r['knot law'], R, len(r['pairs']), 'pairs:', dict(C))

print('\n## Setting B1: two seven-knot generators, a mark at each start knot of the far one')
print('| law | d | marks that show (by name) | first round, each | first-round sig1 share (mean) | last-round sig1 share (mean) |')
print('|---|---|---|---|---|---|')
for r in sorted((r for r in rows if r.get('setting') == 'B1'), key=lambda r: (r['law'], r['d'])):
    firsts = [m['first'] for m in r['marks'].values()]
    shown = [m for m in r['marks'].values() if m['first'] is not None]
    fs = [share(m['rows'][m['first'] - 1], 'sig1') for m in shown]
    ls = [share(m['rows'][-1], 'sig1') for m in shown]
    print('| %s | %d | %d of %d | %s | %s | %s |' % (r['law'], r['d'], len(shown), len(firsts), firsts,
          '%.2f' % (sum(fs) / len(fs)) if fs else '-', '%.2f' % (sum(ls) / len(ls)) if ls else '-'))

print('\n## Setting B2: the switch receiver, far site with two against three loose, and each against a stub')
print('| law | d | pair | first round | first-round sig1 share | last-round sig1 share | rounds |')
print('|---|---|---|---|---|---|---|')
for r in sorted((r for r in rows if r.get('setting') == 'B2'), key=lambda r: (r['law'], r['d'])):
    for nm, p in r['pairs'].items():
        f = p['first']
        print('| %s | %d | %s | %s | %s | %.2f | %d |' % (r['law'], r['d'], nm, f, '%.2f' % share(p['rows'][f - 1], 'sig1') if f else '-',
              share(p['rows'][-1], 'sig1') if p['rows'] else 0, p['rounds']))
