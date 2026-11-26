"""tally_deep.py RUNS [OUT.json]: compare the starts of drive_deep.py pair by pair.

For one distance d, one ration and one treatment, the three starts m = 1, 2, 3 are compared two at a time on the
rounds both read.  For each pair:
    differs r     the first family's side (reach.py's reading) first differs in round r
    same for good both starts were read to a round whose groups no longer join the sides (the sides had come apart),
                  and everything outside the second side, knot by knot, was the same in both to that round.  By the
                  settled statement that parts act alone past their start (README, "Why") it is then the same in
                  every later round: an argument, checked here on the rounds read after that one.
    same to r     the same through the r rounds both read, with the sides still joined in one start or both: not
                  seen within those rounds, and no more."""
import sys, json, collections
runs = [json.loads(l) for l in open(sys.argv[1])]
by = {}
for r in runs:
    s = r['spec']; by[(s['d'], s['ration'], s['treatment'], s['m'])] = r

def apart(r):
    """the first round from 2 on whose groups do not join the sides"""
    return next((x['round'] for x in r['rounds'] if x['round'] >= 2 and x['groups joining the sides'] == 0), None)

def cap_key(c): return 0 if c == 'ORD' else int(c[4:])
out = []; table = collections.defaultdict(dict)
for d in (1, 2, 3):
    for ration in sorted({k[1] for k in by}, key=cap_key):
        for t in ('CANCEL-RETIRE', 'CANCEL-OFFSHOOT', 'CANCEL-WAIT'):
            if any((d, ration, t, m) not in by for m in (1, 2, 3)): continue
            cell = []
            for a, b in ((1, 2), (1, 3), (2, 3)):
                A, B = by[(d, ration, t, a)], by[(d, ration, t, b)]
                n = min(A['rounds read'], B['rounds read'])
                first = next((i + 1 for i in range(n) if A['rounds'][i]['first'] != B['rounds'][i]['first']), None)
                outside = next((i + 1 for i in range(n) if A['rounds'][i]['outside'] != B['rounds'][i]['outside']), None)
                ra, rb = apart(A), apart(B)
                both_apart = max(ra, rb) if (ra and rb and max(ra, rb) <= n) else None
                if first is not None: verdict = 'differs %d' % first
                elif outside is None and both_apart is not None: verdict = 'same for good (apart by %d, read to %d)' % (both_apart, n)
                elif outside is not None: verdict = 'first side same to %d, the rest differs from %d' % (n, outside)
                else: verdict = 'same to %d' % n
                rec = {'d': d, 'ration': ration, 'treatment': t, 'pair': [a, b], 'rounds compared': n, 'first side first differs': first,
                       'outside the second side first differs': outside, 'came apart': {str(a): ra, str(b): rb}, 'verdict': verdict,
                       'ended by': {str(a): A['ended by'], str(b): B['ended by']},
                       'first-side births compared': [sum(x['first'][0] for x in A['rounds'][:n]), sum(x['first'][0] for x in B['rounds'][:n])]}
                out.append(rec); cell.append(rec)
            table[(d, ration)][t] = cell

def short(cell):
    v = [c['verdict'] for c in cell]
    if len(set(v)) == 1: return v[0]
    return '; '.join('%d/%d %s' % (c['pair'][0], c['pair'][1], c['verdict']) for c in cell)

print('| steps | fresh distinctions at most | short knots retire | make offshoots | wait |'); print('|---|---|---|---|---|')
for (d, ration), row in table.items():
    print('| %d | %s | %s |' % (d, 'no cap' if ration == 'ORD' else ration[4:], ' | '.join(short(row[t]) if t in row else 'not read' for t in ('CANCEL-RETIRE', 'CANCEL-OFFSHOOT', 'CANCEL-WAIT'))))
c = collections.Counter((r['d'], r['verdict'].split(' (')[0].split(' to ')[0].rstrip('0123456789 ')) for r in out)
print(); print('pairs by distance and verdict:', {('%d: %s' % k): v for k, v in sorted(c.items())})
print('starts:', len(runs), '; ended by:', dict(collections.Counter(r['ended by'].split(' (')[0] for r in runs)), '; rounds read:', dict(sorted(collections.Counter(r['rounds read'] for r in runs).items())))
if len(sys.argv) > 2: json.dump(out, open(sys.argv[2], 'w'), indent=0)
