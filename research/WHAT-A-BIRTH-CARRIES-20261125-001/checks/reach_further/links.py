"""For each four-run test of scan2.py on one start (every eligible first part tested): the linking knots of X with each
second part at their first meeting, in ticket B's reading, and its own question 'is it the start's after all?':
whether a START knot holds a distinction through which the link meets either part, and whether a linking knot is an
ancestor of both parts.  One JSON line."""
import sys, json, collections
import scan2
from scan2 import eng, read, View, stars_of
spec = json.loads(sys.argv[1])
law = eng.Law(spec['ration'], spec['treatment'], spec['take'], spec['knot_law'])
stars = stars_of(spec['start'])
o = scan2.scan(law, spec['start'], stars, max_tests=10 ** 6)
runA = eng.Run(law, stars=stars, rounds=7); keysA = read.Keys(runA)
rows = []
for t in o['tests']:
    s = t['s']
    R_s = runA.recs[s]['roster']; parts = eng.roster_parts(R_s) if R_s.parts is None else R_s.parts
    member_part = {u: i for i, P in enumerate(parts) for u in P}; pi = {tuple(P): i for i, P in enumerate(parts)}
    bits = read.desc_bits(runA, s, member_part)
    i = pi[tuple(t['X'])]
    link = []
    for nm, tm in (('Y1', t['meets'][0]), ('Y2', t['meets'][1])):
        j = pi[tuple(t[nm])]
        v = View(runA, keysA, bits, i, j, s, parts[i], parts[j])
        L = read.linking(v, tm, read.RoundIndex(runA.recs[tm - 1], bits), read.ancestor_bits(runA.snaps[tm]))
        link.append({'verdict': L['link_verdict'], 'start knot holds a linking distinction': L['start_knot_holds_linking_distinction'],
                     'ancestral': L['ancestral'], 'classes of linking knots': sorted(set(x['class'] for x in L['linking']))})
    rows.append({'why': t['why'], 's': s, 'classes': t['classes'], 'meets': t['meets'], 'm': (t.get('m') or {}).get('m'),
                 'sizes': [len(t['X']), len(t['Y1']), len(t['Y2'])], 'first differs': t['first differs'], 'links': link})
print(json.dumps({'spec': spec, 'law': law.name(), 'rounds_read': o['rounds_read'], 'stop': o['stop'], 'knots': o['knots'], 'rows': rows}))
