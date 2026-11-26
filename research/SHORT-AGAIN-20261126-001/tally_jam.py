"""tally_jam.py RUNS: the jam table (JAM.md)."""
import sys, json, gzip, collections
def load(p): return [json.loads(l) for l in (gzip.open(p, 'rt') if p.endswith('.gz') else open(p))]
rows = load(sys.argv[1]); cases = [r for r in rows if 'changes' in r]; lost = [r for r in rows if 'not run' in r]
LAWS = [('JOIN-FEWER', 'CANCEL-WAIT'), ('ONE-FEWER', 'CANCEL-WAIT'), ('REC-ONE-FEWER', 'CANCEL-WAIT'), ('CAP-3', 'CANCEL-WAIT'),
        ('FLOOR1', 'CANCEL-WAIT'), ('ORD', 'CANCEL-WAIT'), ('JOIN-FEWER', 'CANCEL-RETIRE')]
MULT = {'ring', 'copier'}
def jam_rounds(r): return [i + 1 for i, (m, s) in enumerate(zip(r['A members'], r['A short'])) if i > 0 and m and m == s]
print('| law | short knot | cases | receiver jammed in some round after round 1 | in two rounds running | changes heard from 2 steps or more (of) | from 3 or more | exceptions to the rule | ends a jam / starts one / both jammed | exceptions to the weaker rule (a waiting own knot) | ends the waiting / starts it / both wait | jammed receivers that hear from 2 or more | the ring and the two-knot part as receivers: jammed, heard from 2+ | latest first hearing |')
print('|---|---|---|---|---|---|---|---|---|---|---|---|---|---|')
far_sets = {}; exc_list = []; wexc_list = []
for law in LAWS:
    cs = [r for r in cases if r['law'] == list(law)]
    if not cs: continue
    jam = [r for r in cs if jam_rounds(r)]; jam2 = [r for r in cs if any(b == a + 1 for a, b in zip(jam_rounds(r), jam_rounds(r)[1:]))]
    far = [(r, c) for r in cs for c in r['changes'] if c['heard'] is not None and c['distance'] >= 2]
    tot2 = sum(1 for r in cs for c in r['changes'] if c['distance'] >= 2)
    far3 = [x for x in far if x[1]['distance'] >= 3]; tot3 = sum(1 for r in cs for c in r['changes'] if c['distance'] >= 3)
    exc = [(r, c) for r, c in far if not (c['jammed without'] or c['jammed with'])]
    exc_list += [(law, r['A'], r['B'], c['at'], c['distance'], c['heard']) for r, c in exc]
    kinds = collections.Counter(('ends' if c['jammed without'] and not c['jammed with'] else 'starts' if c['jammed with'] and not c['jammed without'] else 'both' if c['jammed with'] else 'neither') for r, c in far)
    wexc = [(r, c) for r, c in far if not (c['waiting own without'] or c['waiting own with'])]
    wexc_list += [(law, r['A'], r['B'], c['at'], c['distance'], c['heard']) for r, c in wexc]
    wk = collections.Counter(('ends' if c['waiting own without'] and not c['waiting own with'] else 'starts' if c['waiting own with'] and not c['waiting own without'] else 'both' if c['waiting own with'] else 'neither') for r, c in far)
    hearers = {(r['A'], r['B']) for r, c in far}
    jh = sum(1 for r in jam if (r['A'], r['B']) in hearers)
    mult = [r for r in cs if r['A'] in MULT]; mj = sum(1 for r in mult if jam_rounds(r)); mh = sum(1 for r in mult if (r['A'], r['B']) in hearers)
    latest = max((c['heard'] for r, c in far), default=None)
    far_sets[law] = {(r['A'], r['B'], c['at']) for r, c in far}
    print('| %s | %s | %d | %d | %d | %d of %d | %d of %d | %d | %d / %d / %d | %d | %d / %d / %d | %d of %d | %d, %d of %d | %s |' % (law[0], law[1][7:].lower(), len(cs), len(jam), len(jam2), len(far), tot2, len(far3), tot3, len(exc),
          kinds['ends'], kinds['starts'], kinds['both'], len(wexc), wk['ends'], wk['starts'], wk['both'], jh, len(jam), mj, mh, len(mult), latest))
print('\nexceptions to the rule:', len(exc_list)); [print('  ', e) for e in exc_list[:5]]
print('exceptions to the weaker rule:', len(wexc_list)); [print('  ', e) for e in wexc_list[:30]]
a, b = far_sets.get(('ONE-FEWER', 'CANCEL-WAIT'), set()), far_sets.get(('REC-ONE-FEWER', 'CANCEL-WAIT'), set())
print('ONE-FEWER vs the record\'s: same far hearings:', a == b, 'only made:', len(a - b), 'only record:', len(b - a))
# hearing round by distance, JOIN-FEWER with waiting
by = collections.defaultdict(collections.Counter)
for r in cases:
    if r['law'] == ['JOIN-FEWER', 'CANCEL-WAIT']:
        for c in r['changes']:
            if c['heard'] is not None and c['distance'] >= 2: by[c['distance']][c['heard'] - c['distance']] += 1
print('JOIN-FEWER, waiting: first hearing minus distance, by distance:', {k: dict(sorted(v.items())) for k, v in sorted(by.items())})
print('cases read', len(cases), 'not run', len(lost), lost[:3])
