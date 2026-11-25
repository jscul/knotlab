"""A probe for sub-goal B335 (the thread's own run; not a registered study): the two-by-two class.

Written BEFORE the first run.  For a part X of the roster after round s that meets two other parts Y1 and Y2, each only
through made knots, grow four runs: neither barred (A), Y1 barred (B1), Y2 barred (B2), both barred (B12); read the course
from X only (knots descended from X and from neither Y1 nor Y2) in each, with ticket B's program unchanged.
  - 'no difference'            : the four courses are the same;
  - 'one of the two only'      : the course depends on one of Y1, Y2 and not the other;
  - 'a count'                  : B1 and B2 give the same course and it differs from A or from B12;
  - 'which, at equal count'    : B1 and B2 give different courses.
Expected, before any run: 'a count' wherever X's join meets both (its demand counts the joins of the parts it meets), and
never 'which'.  Where B1 = B2, a renaming of the structure after round s that exchanges Y1 and Y2 and fixes X's members makes
the equality uninformative ('equal by symmetry'); without one it is 'a count, not which'.
Planted control: the rule that looks at parts (J-EACH-PART); if it never gives 'which', the probe cannot see one.
m is ticket B's reading: the least number of values, at distinct births of X's descent, that separate the four cases."""
import sys, os, json, itertools, time, collections, resource
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', '..'))
X = ROOT + '/experiments/WHAT-A-BIRTH-CARRIES-20261125-001B/WHAT-A-BIRTH-CARRIES-20261125-001B-E001_link_through_a_made_knot'
sys.dont_write_bytecode = True
sys.path.insert(0, X)
os.chdir(X)
import eng, read
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

def kind_of(cls):
    A, B1, B2, B12 = cls
    if len(set(cls)) == 1: return 'no difference'
    if B1 != B2: return 'which, at equal count'
    if A == B1 == B2 or B1 == B2 == B12 or (A != B1 and B1 != B12): return 'a count'
    return 'a count'

def analyse(law, sname, stars, rounds=7, s_range=(1, 2, 3, 4), max_triples=400):
    runA = eng.Run(law, stars=stars, rounds=rounds)
    keysA = read.Keys(runA)
    out = {'law': law.name(), 'start': sname, 'rounds_read': runA.rounds_read, 'stop': runA.stop, 'knots': runA.S.n_knots, 'triples': []}
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
                k = t
                if k not in cache:
                    cache[k] = (read.RoundIndex(runA.recs[t - 1], bitsA), read.ancestor_bits(runA.snaps[t]))
                L = read.linking(v, t, cache[k][0], cache[k][1])
                if L['strict']:
                    strict[a][b] = t
        barred = {}
        def run_with(barparts):
            key = tuple(sorted(barparts))
            if key not in barred:
                if not key:
                    barred[key] = (runA, keysA, bitsA)
                else:
                    r = eng.Run(law, base=runA, base_round=s, bar=[u for p in key for u in parts[p]], rounds=rounds)
                    barred[key] = (r, read.Keys(r, base=keysA), read.desc_bits(r, s, member_part))
            return barred[key]
        n = 0
        for i in sorted(strict):
            ps = sorted(strict[i])
            for j, k in itertools.combinations(ps, 2):
                if cls_parts[j] == cls_parts[k]: continue
                if n >= max_triples: break
                n += 1
                views = []
                for bar in ((), (j,), (k,), (j, k)):
                    r, ky, b = run_with(bar)
                    v = View(r, ky, b, i, j, s, parts[i], parts[j])
                    v.mj = (1 << j) | (1 << k)          # 'Y' is Y1 and Y2 together: X only = from X and from neither
                    views.append(v)
                last = min(v.run.rounds_read for v in views)
                cls = classes_by_course(views, last)
                rec = {'s': s, 'X': list(parts[i]), 'Y1': list(parts[j]), 'Y2': list(parts[k]), 'meets': [strict[i][j], strict[i][k]],
                       'Y1 meets Y2 only through made knots': k in strict.get(j, {}), 'last': last, 'classes': cls, 'kind': kind_of(cls)}
                # the first round at which each barred run's course leaves run A's
                rec['first differs'] = [read.first_course_difference(views[0], v, s, last)[0] for v in views[1:]]
                if cls[1] == cls[2] and len(set(cls)) > 1:
                    sym = read.symmetry_exchanging(runA.snaps[s], list(parts[j]), list(parts[k]), list(parts[i]), limit=200000)
                    rec['renaming exchanging Y1 and Y2 fixing X'] = sym.get('answer')
                if len(set(cls)) > 1:
                    try:
                        m = read.m_reading(views, cls, s, last)
                        rec['m'] = {'verdict': m['verdict'], 'm': m['m'], 'entries': m.get('entries', [])[:4]}
                    except Exception as e:
                        rec['m'] = {'error': repr(e)[:200]}
                out['triples'].append(rec)
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
    o = analyse(law, spec['start'], stars, rounds=spec.get('rounds', 7), s_range=tuple(spec.get('s_range', (1, 2, 3, 4))))
    o['seconds'] = round(time.time() - t0, 1)
    print(json.dumps(o))
