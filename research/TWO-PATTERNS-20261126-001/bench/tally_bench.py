"""tally_bench.py RUNS [TAKE-MARKS-RUNS] [OUT.json]: the bench's table, from drive_bench.py's cases.  A READING is
one pattern in one case (each case has two).  Printed: the readings by join, ration and treatment with nothing
taken; what the takes change; the same table for the one take that took, from its pass with the marks; and the
cases that meet the stop, in its two readings."""
import sys, json, gzip, collections
def load(p): return [json.loads(l) for l in (gzip.open(p, 'rt') if p.endswith('.gz') else open(p))]
args = [a for a in sys.argv[1:] if not a.endswith('.json')]; outs = [a for a in sys.argv[1:] if a.endswith('.json')]
rows = load(args[0])
done = [r for r in rows if 'reads' in r]; lost = [r for r in rows if 'reads' not in r]
key = lambda r: (r['join'], r['A'], r['B'], r['steps'], r['law'][0], r['law'][1])
none = {key(r): r for r in done if r['law'][2] is None}
RN = {'CAP-3': 'cap of three', 'FLOOR1': 'just enough for three', 'ORD': 'ordinary count'}
TN = {'CANCEL-WAIT': 'waits', 'CANCEL-RETIRE': 'retires', 'CANCEL-OFFSHOOT': 'offshoots'}

def last(xs):                       # the last round (from 1) with a positive entry, 0 if none
    return max((i + 1 for i, x in enumerate(xs) if x), default=0)

summary = []
def table(cases, title):
  print(); print('**' + title + '**'); print()
  print('| join | ration | short knot | readings | cases with a short knot | joined at the last round read | last kept join, latest | differs from with a stub | other retired after round 8 changes own births | marks heard by own knots (latest first round) | marks heard by the joint descent (latest first round) |')
  print('|---|---|---|---|---|---|---|---|---|---|---|')
  for jn in ('meeting', 'share'):
    for ra in ('ORD', 'CAP-3', 'FLOOR1'):
        for tr in ('CANCEL-WAIT', 'CANCEL-RETIRE', 'CANCEL-OFFSHOOT'):
            cs = [r for k, r in cases.items() if k[0] == jn and k[4] == ra and k[5] == tr]
            rd = [(r, X) for r in cs for X in 'AB']
            if not rd: continue
            still = sum(1 for r, X in rd if r['reads'][X]['joined by round'][-1] > 0)
            lk = max(last(r['reads'][X]['kept by round']) for r, X in rd)
            stub = [r['reads'][X]['own making differs from with a stub, first round'] for r, X in rd]
            ret8 = [(r['reads'][X]['other retired after round'].get('8') or {}).get('own making first differs') for r, X in rd if '8' in r['reads'][X]['other retired after round']]
            marks = [m for r, X in rd for m in r['reads'][X].get('mark at a start knot of the other', {}).values()]
            own = [m['own making first differs'] for m in marks if m['own making first differs']]
            jd = [m['joint descent first differs'] for m in marks if m['joint descent first differs']]
            s = {'table': title, 'join': jn, 'ration': ra, 'treatment': tr, 'cases': len(cs), 'readings': len(rd),
                 'cases with a short knot': sum(1 for r in cs if any(r['short members by round'])),
                 'still joined at the last round read': still, 'latest kept join': lk,
                 'differs from with a stub': sum(1 for x in stub if x), 'retired after 8: tested': len(ret8), 'retired after 8: own births differ': sum(1 for x in ret8 if x),
                 'marks': len(marks), 'marks heard by own knots': len(own), 'latest first round, own': max(own, default=None),
                 'marks heard by the joint descent': len(jd), 'latest first round, joint': max(jd, default=None)}
            summary.append(s)
            print('| %s | %s | %s | %d | %s | %d | %d | %d | %d of %d | %d of %d (%s) | %d of %d (%s) |' % (
                'a meeting' if jn == 'meeting' else 'a shared distinction', RN[ra], TN[tr], len(rd), '%d of %d' % (s['cases with a short knot'], len(cs)), still, lk, s['differs from with a stub'],
                s['retired after 8: own births differ'], len(ret8), len(own), len(marks), s['latest first round, own'], len(jd), len(marks), s['latest first round, joint']))

table(none, 'Nothing taken')
takem = {}
if len(args) > 1:
    tm = load(args[1]); takem = {key(r): r for r in tm if 'reads' in r}
    table(takem, 'A birth may take a sole candidate from a knot its parent meets (%d cases read, %d not run)' % (len(takem), len(tm) - len(takem)))

# the takes
print()
tk = collections.defaultdict(lambda: [0, 0, 0])
for r in done:
    t = r['law'][2]
    if t is None: continue
    base = none.get(key(r)); tk[t][0] += 1; tk[t][1] += r['births that took'] > 0
    if base is not None:
        same = all(r['reads'][X][f] == base['reads'][X][f] for X in 'AB' for f in ('own births by round', 'joined by round', 'kept by round', 'own making differs from with a stub, first round'))
        tk[t][2] += (not same)
for t, (n, took, dif) in tk.items(): print('take %s: %d cases, a birth took in %d, readings differ from nothing taken in %d' % (t, n, took, dif))

# the stop, weaker reading: the other retired after round 8 still changes the own births, under two rations
weak = collections.defaultdict(set)
for src, tag in ((none, 'nothing taken'), (takem, 'sole take')):
    for k, r in src.items():
        for X in 'AB':
            v = r['reads'][X]['other retired after round'].get('8')
            if v and v['own making first differs']: weak[(tag, k[0], k[1], k[2], k[3], k[5], r['reads'][X]['pattern'])].add(k[4])
print(); print('the other retired after round 8 still changes the own births:', len(weak), 'readings;', sum(1 for v in weak.values() if len(v) >= 2), 'under two rations or more:')
for k, v in sorted(weak.items()):
    if len(v) >= 2: print('   ', k, sorted(v))
# the stop, stronger reading: a mark heard by a pattern's own knots after round 6, under two rations
late = collections.defaultdict(set); late_joint = collections.defaultdict(set)
for k, r in list(none.items()) + list(takem.items()):
    for X in 'AB':
        for i, m in r['reads'][X].get('mark at a start knot of the other', {}).items():
            if (m['own making first differs'] or 0) > 6: late[(k[0], k[1], k[2], k[3], k[5], X)].add(k[4])
            if (m['joint descent first differs'] or 0) > 6: late_joint[(k[0], k[1], k[2], k[3], k[5], X)].add(k[4])
print(); print('a mark first heard by own knots after round 6:', len(late), 'readings;', sum(1 for v in late.values() if len(v) >= 2), 'under two rations or more')
for k, v in sorted(late.items())[:12]: print('   ', k, sorted(v))
print('a mark first heard by the joint descent after round 6:', len(late_joint), 'readings;', sum(1 for v in late_joint.values() if len(v) >= 2), 'under two rations or more')
print(); print('cases:', len(rows), '; read:', len(done), '; not run:', len(lost), dict(collections.Counter(r.get('not run') for r in lost)))
print('ended by:', dict(collections.Counter(r['ended by'] for r in done)), '; rounds read:', dict(sorted(collections.Counter(r['rounds read'] for r in done).items())))
if outs: json.dump({'table': summary}, open(outs[0], 'w'), indent=1)
