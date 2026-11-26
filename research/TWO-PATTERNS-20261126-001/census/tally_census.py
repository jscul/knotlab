"""tally_census.py RUNS [OUT.json]: the census's table.  A READING is one start in one case (two a case).  The
growth of the joint descent is sorted by the knots of both made in each of the last four rounds read:
    none        none made in the last round
    constant    the same number in each of the four
    fixed step  more each round, by the same step
    faster      more each round, by a growing step
    other       anything else"""
import sys, json, gzip, collections
def load(p): return [json.loads(l) for l in (gzip.open(p, 'rt') if p.endswith('.gz') else open(p))]
rows = load(sys.argv[1]); cases = [r for r in rows if 'reads' in r]; lost = [r for r in rows if 'not run' in r]
RN = {'ORD': 'ordinary count', 'CAP-3': 'cap of three', 'FLOOR1': 'just enough for three'}
TN = {'CANCEL-WAIT': 'waits', 'CANCEL-RETIRE': 'retires', 'CANCEL-OFFSHOOT': 'offshoots'}
def growth(j):
    if not j or j[-1] == 0: return 'none'
    if len(j) < 4: return 'other'
    d = [j[-3] - j[-4], j[-2] - j[-3], j[-1] - j[-2]]
    if d == [0, 0, 0]: return 'constant'
    if d[0] > 0 and d[0] == d[1] == d[2]: return 'fixed step'
    if 0 < d[0] <= d[1] <= d[2] and d[0] < d[2]: return 'faster'
    return 'other'
def slow(r): return growth(r['joint']) in ('constant', 'fixed step') and any(r['reads'][X]['last kept'] == r['rounds'] for X in 'AB')
out = []
print('| join | ration | short knot | cases | a knot short | own births differ from with a stub (readings) | marks heard by own knots (latest first round) | marks heard by the joint descent (latest) | a join kept in the last round (readings) | joint growth: none / constant / fixed step / faster / other | slow cases |')
print('|---|---|---|---|---|---|---|---|---|---|---|')
for jn in ('meeting', 'share'):
    for ra in ('ORD', 'CAP-3', 'FLOOR1'):
        for tr in ('CANCEL-WAIT', 'CANCEL-RETIRE', 'CANCEL-OFFSHOOT'):
            cs = [r for r in cases if r['join'] == jn and r['law'] == [ra, tr]]
            rd = [(r, X) for r in cs for X in 'AB']
            marks = [m for r, X in rd for m in r['reads'][X]['marks']]
            own = [m[0] for m in marks if m[0]]; jd = [m[1] for m in marks if m[1]]
            g = collections.Counter(growth(r['joint']) for r in cs)
            s = {'join': jn, 'ration': ra, 'treatment': tr, 'cases': len(cs), 'a knot short': sum(1 for r in cs if any(r['short'])),
                 'readings': len(rd), 'differ from with a stub': sum(1 for r, X in rd if r['reads'][X]['stub']),
                 'marks': len(marks), 'heard by own': len(own), 'latest own': max(own, default=None), 'heard by joint': len(jd), 'latest joint': max(jd, default=None),
                 'kept in the last round': sum(1 for r, X in rd if r['reads'][X]['last kept'] == r['rounds']),
                 'growth': dict(g), 'slow': sum(1 for r in cs if slow(r))}
            out.append(s)
            print('| %s | %s | %s | %d | %d | %d of %d | %d of %d (%s) | %d of %d (%s) | %d | %s | %d |' % (
                'a meeting' if jn == 'meeting' else 'a shared distinction', RN[ra], TN[tr], len(cs), s['a knot short'], s['differ from with a stub'], len(rd),
                len(own), len(marks), s['latest own'], len(jd), len(marks), s['latest joint'], s['kept in the last round'],
                ' / '.join(str(g[k]) for k in ('none', 'constant', 'fixed step', 'faster', 'other')), s['slow']))
print()
# 1. marks first heard late
late = [(r['A'], r['B'], r['join'], r['law'], X, m[0]) for r in cases for X in 'AB' for m in r['reads'][X]['marks'] if (m[0] or 0) > 6]
latej = [(r['A'], r['B'], r['join'], r['law'], X, m[1]) for r in cases for X in 'AB' for m in r['reads'][X]['marks'] if (m[1] or 0) > 6]
print('1. marks first heard by own knots after round 6:', len(late), late[:6])
print('   by the joint descent after round 6:', len(latej), '; cases read to round 7 or further:', sum(1 for r in cases if r['rounds'] >= 7), 'of', len(cases))
# 2. meeting, ordinary count: pairs in which either start's own births differ from with a stub
pairs = collections.defaultdict(bool); allp = set()
for r in cases:
    if r['join'] == 'meeting' and r['law'][0] == 'ORD':
        allp.add((r['i'], r['j'])); pairs[(r['i'], r['j'])] |= any(r['reads'][X]['stub'] for X in 'AB')
print('2. a meeting under the ordinary count: pairs in which own births differ from with a stub:', sum(pairs.values()), 'of', len(allp))
sh = collections.defaultdict(bool)
for r in cases:
    if r['join'] == 'meeting' and r['law'][0] == 'ORD': sh[(r['i'], r['j'])] |= any(r['short'])
print('   pairs with a knot short there:', sum(sh.values()), '; pairs that differ without a short knot:', sum(1 for k in pairs if pairs[k] and not sh[k]))
# 3. slow joint growth, by pair
sl = collections.defaultdict(set)
for r in cases:
    if slow(r): sl[(r['join'], r['law'][0])].add((r['i'], r['j']))
print('3. pairs with a slow case, by join and ration:', {('%s, %s' % k): len(v) for k, v in sorted(sl.items())})
names = {}
for r in cases: names[r['i']] = r['A']; names[r['j']] = r['B']
so = sorted(sl.get(('share', 'ORD'), set()))
print('   shared distinction, ordinary count:', [(names[i], names[j]) for i, j in so][:40])
steps = collections.Counter()
for r in cases:
    if slow(r) and r['join'] == 'share' and r['law'][0] == 'ORD': steps[(growth(r['joint']), r['joint'][-1] - r['joint'][-2])] += 1
print('   their growth and step:', dict(steps))
# 4. just enough for three: the latest kept join
f = [max(r['reads'][X]['last kept'] for X in 'AB') for r in cases if r['law'][0] == 'FLOOR1']
print('4. just enough for three: cases by the last round with a kept join:', dict(sorted(collections.Counter(f).items())))
print(); print('cases read:', len(cases), 'of', 990 * 18, '; not run:', sum(r['not run'] for r in lost), 'in', len(lost), 'pairs', dict(collections.Counter(r['why'] for r in lost)))
print('rounds read:', dict(sorted(collections.Counter(r['rounds'] for r in cases).items())), '; ended by:', dict(collections.Counter(r['ended'] for r in cases)))
if len(sys.argv) > 2: json.dump({'table': out}, open(sys.argv[2], 'w'), indent=1)
