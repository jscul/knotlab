"""A probe for sub-goal B335, the takes that reach further (the thread's own run; not a registered study).

Written BEFORE its first run.  The engine is ticket B's with seven more taking rules (make_engine.py); the readings are
ticket B's, unchanged.  For each law and start: every part X that meets two or more other parts only through made knots
(all wholly apart after round s), its second parts sorted into classes of parts ALIKE (a renaming of the structure after
round s maps one onto the other and fixes every member of X), and the rounds in which X first meets each.  Four runs
(neither barred, Y1, Y2, both) are grown for pairs of second parts that are NOT alike, and for pairs first met in
DIFFERENT rounds, at most `max_tests` a run; the course from X only is compared and ticket B's reading m taken.
What would count: a pair not alike on which the course differs with which one is barred; or four courses that no one
value at one birth separates (m of 2 or more).
Expected, before the run: the wider reach (MET2) and the takes that are not of a sole candidate give second parts
that are not alike on some starts; whether the first part then responds is not known."""
import sys, os, json, time, itertools, collections, resource
from collections import Counter, defaultdict
sys.setrecursionlimit(100000)
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.environ.get('PROBE_ROOT') or os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
X = ROOT + '/experiments/WHAT-A-BIRTH-CARRIES-20261125-001B/WHAT-A-BIRTH-CARRIES-20261125-001B-E001_link_through_a_made_knot'
import eng                      # this folder's engine (the script's folder is first on the path)
assert os.path.dirname(os.path.abspath(eng.__file__)) == HERE and hasattr(eng, 'MET_KIND')
sys.path.append(X)
os.chdir(X)
import read
from read import View

def classes_by_course(views, last):
    cs = [read.course(v, last) for v in views]
    cls = []
    for i, c in enumerate(cs):
        for j in range(i):
            if read.same_course(cs[j], c):
                cls.append(cls[j]); break
        else:
            cls.append(i)
    return cls

def maps_onto(S, Ya, Yb, fixed, limit=200000):
    """Whether some renaming of S onto itself maps the members of Ya onto those of Yb and fixes each knot of `fixed`
    (knots keep their round made, kind and removal; distinctions their bars).  A found map is checked edge by edge."""
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
    KB = {} if knot_bound is None else {'knot_bound': knot_bound}
    runA = eng.Run(law, stars=stars, rounds=rounds, **KB)
    keysA = read.Keys(runA)
    out = {'law': law.name(), 'start': sname, 'rounds_read': runA.rounds_read, 'stop': runA.stop, 'knots': runA.S.n_knots,
           'takes made': sum(len(b['takes']) for r in runA.recs[1:] if r for b in r.get('births', [])) if True else None,
           'by_s': [], 'tests': []}
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
        anymeet = Counter()
        cache = {}
        for (i, j), (t, how) in meetA.items():
            if cls_parts[i] == cls_parts[j]: continue
            for a, b in ((i, j), (j, i)):
                v = View(runA, keysA, bitsA, a, b, s, parts[a], parts[b])
                if t not in cache:
                    cache[t] = (read.RoundIndex(runA.recs[t - 1], bitsA), read.ancestor_bits(runA.snaps[t]))
                L = read.linking(v, t, cache[t][0], cache[t][1])
                anymeet[(t, bool(L['strict']))] += 1
                if L['strict']:
                    strict[a][b] = t
        S = runA.snaps[s]
        rec = {'s': s, 'parts': len(parts), 'part sizes': sorted(Counter(len(P) for P in parts).items()),
               'first meetings (round, made only)': sorted((str(k), v) for k, v in anymeet.items()),
               'X with two or more': 0, 'X met in different rounds': 0, 'pairs': Counter(), 'orbit shapes': Counter()}
        barred = {}
        def run_with(barparts):
            key = tuple(sorted(barparts))
            if key not in barred:
                if not key: barred[key] = (runA, keysA, bitsA)
                else:
                    r = eng.Run(law, base=runA, base_round=s, bar=[u for p in key for u in parts[p]], rounds=rounds, **KB)
                    barred[key] = (r, read.Keys(r, base=keysA), read.desc_bits(r, s, member_part))
            return barred[key]
        def four(i, j, k, why):
            views = []
            for bar in ((), (j,), (k,), (j, k)):
                r, ky, b = run_with(bar)
                v = View(r, ky, b, i, j, s, parts[i], parts[j]); v.mj = (1 << j) | (1 << k)
                views.append(v)
            last = min(v.run.rounds_read for v in views)
            cls = classes_by_course(views, last)
            t = {'why': why, 's': s, 'X': list(parts[i]), 'Y1': list(parts[j]), 'Y2': list(parts[k]), 'meets': [strict[i][j], strict[i][k]],
                 'last': last, 'classes': cls,
                 'first differs': [read.first_course_difference(views[0], v, s, last)[0] for v in views[1:]]}
            if len(set(cls)) > 1:
                try:
                    m = read.m_reading(views, cls, s, last)
                    t['m'] = {'verdict': m['verdict'], 'm': m['m'], 'entries': m.get('entries', [])[:3]}
                except Exception as e:
                    t['m'] = {'error': repr(e)[:160]}
            out['tests'].append(t)
        for i in sorted(strict):
            ps = sorted(strict[i])
            if len(ps) < 2: continue
            rec['X with two or more'] += 1
            if len({strict[i][j] for j in ps}) > 1: rec['X met in different rounds'] += 1
            orbits = []
            for j in ps:
                for O in orbits:
                    a = maps_onto(S, list(parts[O[0]]), list(parts[j]), list(parts[i]))
                    if a == 'yes': O.append(j); break
                    if a == 'undecided': rec['pairs']['undecided'] += 1
                else:
                    orbits.append([j])
            rec['orbit shapes'][str(sorted(len(O) for O in orbits))] += 1
            orb = {j: n for n, O in enumerate(orbits) for j in O}
            done = False
            for j, k in itertools.combinations(ps, 2):
                if cls_parts[j] == cls_parts[k]: continue
                unlike = orb[j] != orb[k]
                diff_t = strict[i][j] != strict[i][k]
                rec['pairs']['not alike' if unlike else 'alike'] += 1
                if diff_t: rec['pairs']['first met in different rounds'] += 1
                if (unlike or diff_t) and tests < max_tests and not done:
                    tests += 1; done = True          # one test for each X, so the tests spread over first parts
                    four(i, j, k, ('not alike' if unlike else 'alike') + (', different rounds' if diff_t else ''))
        for k in ('pairs', 'orbit shapes'):
            rec[k] = sorted((str(a), b) for a, b in rec[k].items())
        out['by_s'].append(rec)
    return out

def stars_of(name):
    if name.startswith('ringk:'):
        # a ring of knots, each sharing one distinction with each neighbour, knot i holding ks[i] loose distinctions
        ks = [int(x) for x in name.split(':')[1].split(',')]
        n = len(ks); nxt = n; out = []
        for i in range(n):
            out.append([(i - 1) % n, i] + list(range(nxt, nxt + ks[i]))); nxt += ks[i]
        return out
    st = json.load(open(ROOT + '/research/WHAT-A-BIRTH-CARRIES-20261125-001B/starts.json'))
    if name.startswith('census:'):
        return json.load(open(ROOT + '/research/KNOTS-WITHIN-REACH-20261125-001A/census_starts.json'))[int(name.split(':')[1])]['stars']
    return st['extra']['stars'] if name == st['extra']['name'] else st['stars'][name]

if __name__ == '__main__':
    resource.setrlimit(resource.RLIMIT_AS, (8 << 30, 8 << 30))
    spec = json.loads(sys.argv[1])
    law = eng.Law(spec['ration'], spec['treatment'], spec['take'], spec['knot_law'])
    t0 = time.time()
    o = scan(law, spec['start'], stars_of(spec['start']), rounds=spec.get('rounds', 7), s_range=tuple(spec.get('s_range', (1, 2, 3, 4))),
             knot_bound=spec.get('knot_bound'), max_tests=spec.get('max_tests', 12))
    o['seconds'] = round(time.time() - t0, 1); o['spec'] = spec
    print(json.dumps(o))
