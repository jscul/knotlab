"""tally_reach.py RUNS: the reach table.  A change's DISTANCE is the number of steps from A's site to the knot that
was changed: k for the k-th link knot, d for B's site, d + 1 or d + 2 for B's other knots."""
import sys, json, gzip, collections
import rations
def load(p): return [json.loads(l) for l in (gzip.open(p, 'rt') if p.endswith('.gz') else open(p))]
rows = load(sys.argv[1]); cases = [r for r in rows if 'changes' in r]; lost = [r for r in rows if 'not run' in r]
RN = ['ORD', 'ODD-FEWER', 'BUSY-FEWER', 'ONE-FEWER', 'JOIN-FEWER', 'THIRD-FEWER']
TN = {'CANCEL-WAIT': 'waits', 'CANCEL-RETIRE': 'retires', 'CANCEL-OFFSHOOT': 'offshoots'}
DEPTH = {'g7:112@0': [0, 1, 1], 'g6:133@0': [0, 1, 1], 'g6:123@0': [0, 1, 1], 'g6:122@0': [0, 1, 1]}
def dist(r, ch):
    if ch[0] == 'L': return int(ch[1:])
    if ch[0] == 'B': return r['d'] + DEPTH[r['B']][int(ch[1:])]
    return r['d']
last = lambda xs: max((i + 1 for i, x in enumerate(xs) if x), default=0)
print('| ration | short knot | cases | own knots still joining others in the last round | rounds with a short knot (median) | receiver alone still making | changes heard by own knots, by distance 1 / 2 / 3 / 4 and more | latest first round heard | heard by the joint descent |')
print('|---|---|---|---|---|---|---|---|---|')
summary = {}
for ra in RN:
    for tr in ('CANCEL-WAIT', 'CANCEL-RETIRE', 'CANCEL-OFFSHOOT'):
        cs = [r for r in cases if r['law'] == [ra, tr]]
        if not cs: continue
        joined = sum(1 for r in cs if r['kept'][-1] > 0)
        sr = sorted(sum(1 for x in r['short'] if x) for r in cs); med = sr[len(sr) // 2]
        alone = sum(1 for r in cs if r['alone']['own births, last round'] > 0)
        by = collections.defaultdict(lambda: [0, 0]); latest = 0; jd = [0, 0]; order_bad = 0
        for r in cs:
            for ch, v in r['changes'].items():
                k = min(dist(r, ch), 4); by[k][1] += 1; jd[1] += 1
                if v['own']: by[k][0] += 1; latest = max(latest, v['own'])
                if v['joint']: jd[0] += 1
                if v['own'] and (v['groups'] is None or v['groups'] > v['own']): order_bad += 1
        summary[(ra, tr)] = {'cases': len(cs), 'joined': joined, 'by': {k: v for k, v in by.items()}, 'latest': latest, 'order_bad': order_bad}
        print('| %s | %s | %d | %d | %d | %d | %s | %s | %d of %d |' % ('the ordinary count' if ra == 'ORD' else ra, TN[tr], len(cs), joined, med, alone,
              ' / '.join('%d of %d' % tuple(by[k]) for k in (1, 2, 3, 4)), latest or 'none', jd[0], jd[1]))
print()
# heard at two steps or more: the list
far = [(r['A'], r['B'], r['d'], r['law'][0], TN[r['law'][1]], ch, dist(r, ch), v['own'], v['joint']) for r in cases for ch, v in r['changes'].items() if v['own'] and dist(r, ch) >= 2]
print('changes two or more steps from A\'s site that A\'s own knots hear:', len(far))
c = collections.Counter((x[3], x[4], x[6]) for x in far)
for k, v in sorted(c.items()): print('   %s, %s, distance %d: %d' % (k + (v,)))
for x in sorted(far, key=lambda x: (-x[6], x[7]))[:12]: print('   ', x)
late = [x for x in far if x[7] > 6]
print('first heard after round 6:', len(late), sorted(late, key=lambda x: -x[7])[:8])
print('the second reading (cancelled groups) comes after the first, or not at all, where own knots hear:', sum(s['order_bad'] for s in summary.values()))
# the demand table under the ordinary count, and what each ration would leave short
dem = collections.Counter()
for r in cases:
    for k, v in r.get('demand', []): dem[tuple(k)] += v
tot = collections.Counter(); sh = collections.defaultdict(collections.Counter)
for (cls, kind, p, D), v in dem.items():
    tot[cls] += v
    for name, rule in rations.RULES.items():
        floor = max(3 - p, 1); q = max(D, floor); f = max(rule(kind, p, D, None, q), floor)
        if D > f: sh[name][cls] += v
print(); print('under the ordinary count, new knots by whose they are:', dict(tot))
for name in rations.RULES: print('   %s would leave short: %s' % (name, {c: '%d (%.0f%%)' % (sh[name][c], 100 * sh[name][c] / tot[c]) for c in tot}))
print(); print('cases read:', len(cases), 'of', 128 * 18, '; not run:', sum(r['not run'] for r in lost), 'in', len(lost), 'runs', dict(collections.Counter(r['why'] for r in lost)))
print('rounds read:', dict(sorted(collections.Counter(r['rounds'] for r in cases).items())))
