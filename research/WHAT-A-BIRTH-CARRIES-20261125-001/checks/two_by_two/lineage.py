"""A probe for sub-goal B335, fourth part (the thread's own run; not a registered study): two meetings down one descent.

Written BEFORE its first run.  Parts of the roster after round 4 and parts of the roster after round 6 of one run read
to round 9.  For each meeting in round 7 of two parts P and Q of the later roster, only through made knots: from which
parts of the earlier roster do P's members and Q's members descend?  A second count could reach the descent of one
earlier part X at a second birth only where P descends from X alone and Q has no descent from X."""
import sys, json, time, collections, resource
from collections import Counter
import tbt
from tbt import eng, read, View, ROOT
def rosters(run, s):
    R = run.recs[s]['roster']
    parts = eng.roster_parts(R) if R.parts is None else R.parts
    return parts, {u: i for i, P in enumerate(parts) for u in P}
spec = json.loads(sys.argv[1])
st = json.load(open(ROOT + '/research/WHAT-A-BIRTH-CARRIES-20261125-001B/starts.json'))
if spec['start'].startswith('census:'):
    stars = json.load(open(ROOT + '/research/KNOTS-WITHIN-REACH-20261125-001A/census_starts.json'))[int(spec['start'].split(':')[1])]['stars']
else:
    stars = st['extra']['stars'] if spec['start'] == st['extra']['name'] else st['stars'][spec['start']]
law = eng.Law(spec['ration'], spec['treatment'], spec['take'], spec['knot_law'])
run = eng.Run(law, stars=stars, rounds=9, knot_bound=6000); keys = read.Keys(run)
out = {'start': spec['start'], 'rounds_read': run.rounds_read, 'stop': run.stop, 'knots': run.S.n_knots, 'spec': spec}
if run.rounds_read >= 8:
    p4, mp4 = rosters(run, 4); bits4 = read.desc_bits(run, 4, mp4)
    p6, mp6 = rosters(run, 6); bits6 = read.desc_bits(run, 6, mp6)
    cls6 = eng.classes_of_parts(run.snaps[6], p6)
    meet = read.first_meetings(run, 6, bits6)
    idx = None; tally = Counter()
    for (i, j), (t, how) in meet.items():
        if cls6[i] == cls6[j] or t != 7: continue
        if idx is None: idx = (read.RoundIndex(run.recs[6], bits6), read.ancestor_bits(run.snaps[7]))
        for a, b in ((i, j), (j, i)):
            v = View(run, keys, bits6, a, b, 6, p6[a], p6[b])
            if not read.linking(v, 7, idx[0], idx[1])['strict']: continue
            oa = 0; ob = 0
            for u in p6[a]: oa |= bits4[u]
            for u in p6[b]: ob |= bits4[u]
            na, nb = bin(oa).count('1'), bin(ob).count('1')
            if na == 1 and not (oa & ob): k = 'P from one earlier part, Q with no descent from it'
            elif na == 1 and oa == ob: k = 'P and Q from the same one earlier part'
            elif na == 1: k = 'P from one earlier part, Q from it and others'
            else: k = 'P from %s earlier parts' % ('none (after the start only)' if na == 0 else 'several')
            tally[k] += 1
    out['parts after round 4'] = len(p4); out['parts after round 6'] = len(p6)
    out['meetings in round 7'] = sorted(tally.items())
print(json.dumps(out))
