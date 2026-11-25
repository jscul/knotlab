"""A probe for sub-goal B335, third part (the thread's own run; not a registered study): partners at two births.

Written BEFORE its first run, after the scans showed that every partner of a part arrives at one birth (the round after
the parts are chosen).  Parts are chosen after round s = 4 and the run read to round 9.  For a part X with a partner Y1
first met in round 5 and a part Y2 first met in a LATER round (all three wholly apart after round s), the four runs of
tbt.py are grown (neither barred, Y1, Y2, both) and the course from X only compared; m is ticket B's reading.
A composed case in the registered sense is four courses that no one value at one birth separates (m of 2 or more).
Expected, before the run: unknown.  If X's descent meets Y2's only after it has merged with Y1's, the course from X only
may not see Y2 at all (no difference between 'neither' and 'Y2 barred')."""
import sys, os, json, time, itertools, collections, resource
from collections import Counter
sys.setrecursionlimit(100000)
import tbt
from tbt import eng, read, View, classes_by_course, ROOT

def go(law, sname, stars, rounds=9, s=4, knot_bound=6000, max_tests=24, explore=False):
    runA = eng.Run(law, stars=stars, rounds=rounds, knot_bound=knot_bound)
    keysA = read.Keys(runA)
    out = {'law': law.name(), 'start': sname, 'rounds_read': runA.rounds_read, 'stop': runA.stop, 'knots': runA.S.n_knots, 'tests': []}
    if runA.rounds_read <= s + 2: return out
    R_s = runA.recs[s]['roster']
    parts = eng.roster_parts(R_s) if R_s.parts is None else R_s.parts
    member_part = {u: i for i, P in enumerate(parts) for u in P}
    cls_parts = eng.classes_of_parts(runA.snaps[s], parts)
    bitsA = read.desc_bits(runA, s, member_part)
    meetA = read.first_meetings(runA, s, bitsA)
    met = collections.defaultdict(dict); cache = {}
    for (i, j), (t, how) in meetA.items():
        if cls_parts[i] == cls_parts[j]: continue
        for a, b in ((i, j), (j, i)):
            v = View(runA, keysA, bitsA, a, b, s, parts[a], parts[b])
            if t not in cache:
                cache[t] = (read.RoundIndex(runA.recs[t - 1], bitsA), read.ancestor_bits(runA.snaps[t]))
            met[a][b] = (t, bool(read.linking(v, t, cache[t][0], cache[t][1])['strict']))
    out['parts'] = len(parts)
    out['first meetings by round and made-only'] = sorted((str(k), v) for k, v in Counter(x for d in met.values() for x in d.values()).items())
    cand = []
    for i in sorted(met):
        early = [j for j, (t, st) in met[i].items() if t == s + 1 and st]
        late = [k for k, (t, st) in met[i].items() if t > s + 1]
        for j in early:
            for k in late:
                if cls_parts[j] != cls_parts[k]: cand.append((i, j, k))
    out['candidate triples'] = len(cand)
    if explore: return out
    barred = {}
    def run_with(barparts):
        key = tuple(sorted(barparts))
        if key not in barred:
            if not key: barred[key] = (runA, keysA, bitsA)
            else:
                r = eng.Run(law, base=runA, base_round=s, bar=[u for p in key for u in parts[p]], rounds=rounds, knot_bound=knot_bound)
                barred[key] = (r, read.Keys(r, base=keysA), read.desc_bits(r, s, member_part))
        return barred[key]
    # spread the tests over different X
    seen = Counter(); picked = []
    for c in cand:
        if seen[c[0]] < 2 and len(picked) < max_tests: picked.append(c); seen[c[0]] += 1
    for i, j, k in picked:
        views = []
        for bar in ((), (j,), (k,), (j, k)):
            r, ky, b = run_with(bar)
            v = View(r, ky, b, i, j, s, parts[i], parts[j]); v.mj = (1 << j) | (1 << k)
            views.append(v)
        last = min(v.run.rounds_read for v in views)
        cls = classes_by_course(views, last)
        rec = {'X': list(parts[i]), 'Y1': list(parts[j]), 'Y2': list(parts[k]), 'meets': [list(met[i][j]), list(met[i][k])], 'last': last,
               'classes': cls, 'first differs': [read.first_course_difference(views[0], v, s, last)[0] for v in views[1:]]}
        if len(set(cls)) > 1:
            try:
                m = read.m_reading(views, cls, s, last)
                rec['m'] = {'verdict': m['verdict'], 'm': m['m'], 'entries': m.get('entries', [])[:4]}
            except Exception as e:
                rec['m'] = {'error': repr(e)[:200]}
        out['tests'].append(rec)
    return out

if __name__ == '__main__':
    resource.setrlimit(resource.RLIMIT_AS, (8 << 30, 8 << 30))
    spec = json.loads(sys.argv[1])
    st = json.load(open(ROOT + '/research/WHAT-A-BIRTH-CARRIES-20261125-001B/starts.json'))
    if spec['start'].startswith('census:'):
        stars = json.load(open(ROOT + '/research/KNOTS-WITHIN-REACH-20261125-001A/census_starts.json'))[int(spec['start'].split(':')[1])]['stars']
    else:
        stars = st['extra']['stars'] if spec['start'] == st['extra']['name'] else st['stars'][spec['start']]
    law = eng.Law(spec['ration'], spec['treatment'], spec['take'], spec['knot_law'])
    t0 = time.time()
    o = go(law, spec['start'], stars, rounds=spec.get('rounds', 9), s=spec.get('s', 4), explore=spec.get('explore', False))
    o['seconds'] = round(time.time() - t0, 1); o['spec'] = spec
    print(json.dumps(o))
