"""A probe for sub-goal B335, second part (the thread's own run; not a registered study): is 'which' ever testable?

Written BEFORE its first run, after the two-by-two runs showed every triple with two second parts alike.
For each start and each round s, grow run A only, find each part X that meets two or more other parts only through made
knots (all wholly apart after round s, as in tbt.py), and sort X's partners into classes: two partners are ALIKE when a
renaming of the structure after round s onto itself (knots keeping their round made, kind and removal; distinctions their
bars) maps one onto the other and fixes every member of X.  Barring either of two alike partners gives the same run up to
renaming, so 'which' has a test only on a pair of partners that are NOT alike.  For each such pair (at most 12 a start) the
four runs of tbt.py are grown and the course from X only compared.
Expected, before the run: every pair alike (the partners are branches of one made knot), so no test of 'which' exists in
the class."""
import sys, os, json, time, itertools, collections, resource
from collections import Counter, defaultdict
sys.setrecursionlimit(100000)
import tbt
from tbt import eng, read, View, classes_by_course, kind_of, ROOT

def maps_onto(S, Ya, Yb, fixed, limit=200000):
    """Whether some renaming of S onto itself maps the members of Ya onto those of Yb and fixes each knot of `fixed`.
    The search of read.symmetry_exchanging with other labels; a found map is checked edge by edge."""
    if len(Ya) != len(Yb):
        return 'no: sizes differ'
    nodes = [('k', u) for u in range(S.n_knots)] + [('d', d) for d in range(S.n_distinctions) if S.holders[d]]
    idx = {v: i for i, v in enumerate(nodes)}
    n = len(nodes)
    edges = [(idx[('k', u)], idx[('d', d)]) for d in range(S.n_distinctions) for u in S.holders[d]]
    adj = [[] for _ in range(2 * n)]
    for a, b in edges:
        adj[a].append(b); adj[b].append(a); adj[n + a].append(n + b); adj[n + b].append(n + a)
    lab1, lab2 = {}, {}
    for v in nodes:
        if v[0] == 'k':
            u = v[1]
            lab1[v] = lab2[v] = 'k|%s|%s|%s' % (S.made[u], S.kind[u], u in S.removed)
        else:
            lab1[v] = lab2[v] = 'd%d' % S.barred[v[1]]
    for u in Ya: lab1[('k', u)] += '|T'
    for u in Yb: lab2[('k', u)] += '|T'
    for i, w in enumerate(sorted(fixed)):
        lab1[('k', w)] = lab2[('k', w)] = 'L%d' % i
    names = {x: i for i, x in enumerate(sorted(set(lab1.values()) | set(lab2.values())))}
    col0 = [names[lab1[v]] for v in nodes] + [names[lab2[v]] for v in nodes]
    count = [0]
    eset = set(edges)
    def search(col):
        count[0] += 1
        if count[0] > limit: raise read._Budget()
        col = read._refine(adj, col)
        if Counter(col[:n]) != Counter(col[n:]): return False
        cls = defaultdict(list)
        for v in range(n): cls[col[v]].append(v)
        big = [c for c, vs in cls.items() if len(vs) > 1]
        if not big:
            where = {col[n + v]: v for v in range(n)}
            phi = [where[col[v]] for v in range(n)]
            return all(((phi[a], phi[b]) in eset) for a, b in edges)
        c = min(big, key=lambda c_: (len(cls[c_]), c_))
        v = cls[c][0]
        fresh = max(col) + 1
        for w in range(n, 2 * n):
            if col[w] != c: continue
            col2 = list(col); col2[v] = fresh; col2[w] = fresh
            if search(col2): return True
        return False
    try:
        return 'yes' if search(col0) else 'no'
    except read._Budget:
        return 'undecided'

def scan(law, sname, stars, rounds=7, s_range=(1, 2, 3, 4), max_tests=12, knot_bound=None):
    KB = {} if knot_bound is None else {'knot_bound': knot_bound}      # None: ticket B's bound of 1,500 knots
    runA = eng.Run(law, stars=stars, rounds=rounds, **KB)
    keysA = read.Keys(runA)
    out = {'law': law.name(), 'start': sname, 'rounds_read': runA.rounds_read, 'stop': runA.stop, 'knots': runA.S.n_knots, 'by_s': [], 'tests': []}
    tests = 0
    for s in s_range:
        if runA.rounds_read <= s: continue
        R_s = runA.recs[s]['roster']
        parts = eng.roster_parts(R_s) if R_s.parts is None else R_s.parts
        member_part = {u: i for i, P in enumerate(parts) for u in P}
        cls_parts = eng.classes_of_parts(runA.snaps[s], parts)
        bitsA = read.desc_bits(runA, s, member_part)
        meetA = read.first_meetings(runA, s, bitsA)
        strict = collections.defaultdict(dict)
        cache = {}
        for (i, j), (t, how) in meetA.items():
            if cls_parts[i] == cls_parts[j]: continue
            for a, b in ((i, j), (j, i)):
                v = View(runA, keysA, bitsA, a, b, s, parts[a], parts[b])
                if t not in cache:
                    cache[t] = (read.RoundIndex(runA.recs[t - 1], bitsA), read.ancestor_bits(runA.snaps[t]))
                if read.linking(v, t, cache[t][0], cache[t][1])['strict']:
                    strict[a][b] = t
        S = runA.snaps[s]
        rec = {'s': s, 'parts': len(parts), 'part sizes': sorted(Counter(len(P) for P in parts).items()),
               'X with two or more partners': 0, 'partners per X': Counter(), 'pairs': Counter(), 'meeting rounds': Counter(), 'orbit shapes': Counter()}
        barred = {}
        def run_with(barparts):
            key = tuple(sorted(barparts))
            if key not in barred:
                if not key: barred[key] = (runA, keysA, bitsA)
                else:
                    r = eng.Run(law, base=runA, base_round=s, bar=[u for p in key for u in parts[p]], rounds=rounds, **KB)
                    barred[key] = (r, read.Keys(r, base=keysA), read.desc_bits(r, s, member_part))
            return barred[key]
        for i in sorted(strict):
            ps = sorted(strict[i])
            if len(ps) < 2: continue
            rec['X with two or more partners'] += 1
            rec['partners per X'][len(ps)] += 1
            for j in ps: rec['meeting rounds'][strict[i][j]] += 1
            orbits = []                      # classes of partners alike, by representative
            for j in ps:
                for O in orbits:
                    a = maps_onto(S, list(parts[O[0]]), list(parts[j]), list(parts[i]))
                    if a == 'yes': O.append(j); break
                    if a == 'undecided': rec['pairs']['undecided'] += 1
                else:
                    orbits.append([j])
            rec['orbit shapes'][str(sorted(len(O) for O in orbits))] += 1
            for O in orbits:
                rec['pairs']['alike'] += sum(1 for a, b in itertools.combinations(O, 2) if cls_parts[a] != cls_parts[b])
            for O1, O2 in itertools.combinations(orbits, 2):
                for j in O1:
                    for k in O2:
                        if cls_parts[j] == cls_parts[k]: continue
                        rec['pairs']['not alike'] += 1
                        if tests >= max_tests: continue
                        tests += 1
                        views = []
                        for bar in ((), (j,), (k,), (j, k)):
                            r, ky, b = run_with(bar)
                            v = View(r, ky, b, i, j, s, parts[i], parts[j]); v.mj = (1 << j) | (1 << k)
                            views.append(v)
                        last = min(v.run.rounds_read for v in views)
                        cls = classes_by_course(views, last)
                        out['tests'].append({'s': s, 'X': list(parts[i]), 'Y1': list(parts[j]), 'Y2': list(parts[k]),
                                             'meets': [strict[i][j], strict[i][k]], 'last': last, 'classes': cls, 'kind': kind_of(cls),
                                             'first differs': [read.first_course_difference(views[0], v, s, last)[0] for v in views[1:]]})
        for k in ('partners per X', 'pairs', 'meeting rounds', 'orbit shapes'):
            rec[k] = sorted((str(a), b) for a, b in rec[k].items())
        out['by_s'].append(rec)
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
    o = scan(law, spec['start'], stars, rounds=spec.get('rounds', 7), s_range=tuple(spec.get('s_range', (1, 2, 3, 4))), knot_bound=spec.get('knot_bound'))
    o['seconds'] = round(time.time() - t0, 1); o['spec'] = spec
    print(json.dumps(o))
