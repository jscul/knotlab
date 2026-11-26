"""tally_made.py BENCH CENSUS: the made rations on the bench's three patterns and on the census's 990 pairs.  A
reading is one pattern in one case."""
import sys, json, gzip, collections
def load(p): return [json.loads(l) for l in (gzip.open(p, 'rt') if p.endswith('.gz') else open(p))]
TN = {'CANCEL-WAIT': 'waits', 'CANCEL-RETIRE': 'retires', 'CANCEL-OFFSHOOT': 'offshoots'}
last = lambda xs: max((i + 1 for i, x in enumerate(xs) if x), default=0)
def table(cases, get, title):
    print('**' + title + '**'); print()
    print('| ration | join | short knot | cases | short knots in half the rounds or more | readings with a kept join in the last round | marks heard by own knots | latest first round | first heard after round 6 | heard by the joint descent |')
    print('|---|---|---|---|---|---|---|---|---|---|')
    keys = sorted({(r['law'][0], r['join'], r['law'][1]) for r in cases}, key=lambda k: (['ODD-FEWER', 'BUSY-FEWER', 'ONE-FEWER', 'JOIN-FEWER', 'THIRD-FEWER'].index(k[0]), k[1], k[2]))
    late_all = []
    for ra, jn, tr in keys:
        cs = [r for r in cases if (r['law'][0], r['join'], r['law'][1]) == (ra, jn, tr)]
        often = sum(1 for r in cs if 2 * sum(1 for x in get(r, 'short') if x) >= len(get(r, 'short')))
        kept = own = tot = jd = 0; latest = 0; late = 0
        for r in cs:
            for X in 'AB':
                lk, marks = get(r, 'read')(X)
                kept += (lk == get(r, 'rounds'))
                for o, j in marks:
                    tot += 1; own += bool(o); jd += bool(j); latest = max(latest, o or 0)
                    if (o or 0) > 6: late += 1; late_all.append((ra, jn, TN[tr], r['A'], r['B'], o))
        print('| %s | %s | %s | %d | %d | %d of %d | %d of %d | %s | %d | %d |' % (ra, 'a meeting' if jn == 'meeting' else 'a shared distinction', TN[tr], len(cs), often, kept, 2 * len(cs), own, tot, latest or 'none', late, jd))
    print(); print('first heard after round 6:', len(late_all), sorted(late_all, key=lambda x: -x[5])[:10]); print()
B = load(sys.argv[1]); bc = [r for r in B if 'reads' in r]
def getb(r, what):
    if what == 'short': return r['short members by round']
    if what == 'rounds': return r['rounds read']
    return lambda X: (last(r['reads'][X]['kept by round']), [(m['own making first differs'], m['joint descent first differs']) for m in r['reads'][X]['mark at a start knot of the other'].values()])
table(bc, getb, 'The bench\'s three patterns, one to three steps apart (%d of %d cases read)' % (len(bc), len(B)))
C = load(sys.argv[2]); cc = [r for r in C if 'reads' in r]
def getc(r, what):
    if what == 'short': return r['short']
    if what == 'rounds': return r['rounds']
    return lambda X: (r['reads'][X]['last kept'], r['reads'][X]['marks'])
table(cc, getc, 'The census\'s 990 pairs of small starts, one step apart (%d cases read of %d; %d not run)' % (len(cc), 990 * 12, sum(r.get('not run', 0) for r in C)))
print('rounds read, bench:', dict(sorted(collections.Counter(r['rounds read'] for r in bc).items())), '; census:', dict(sorted(collections.Counter(r['rounds'] for r in cc).items())))
