"""SEQUENTIAL-WALL-R1, the referee's own check of Theorem 5's table (written fresh; reads the study's knots_table.json only as the
claim under test). Enumerates every relation R on three Boolean places that is a knot in the K1-K3 sense (nonempty, not full, every
pair of places free), tests closure under and, or, majority, minority, classifies by Schaefer with constants, and replays every
pp-definition in the table semantically."""
import itertools, json, sys
TABLE = sys.argv[1]
T = [tuple(t) for t in itertools.product((0, 1), repeat=3)]
def knots():
    out = []
    for mask in range(1, 255):
        R = {t for i, t in enumerate(T) if mask >> i & 1}
        if all({(t[i], t[j]) for t in R} == {(0, 0), (0, 1), (1, 0), (1, 1)} for i, j in ((0, 1), (0, 2), (1, 2))):
            out.append(frozenset(R))
    return out
def closed(R, f, k):
    return all(tuple(f(*col) for col in zip(*ts)) in R for ts in itertools.product(R, repeat=k))
AND = lambda x, y: x & y; OR = lambda x, y: x | y
MAJ = lambda x, y, z: (x & y) | (y & z) | (x & z); MIN = lambda x, y, z: x ^ y ^ z
def classify(R):
    a, o, mj, mn = closed(R, AND, 2), closed(R, OR, 2), closed(R, MAJ, 3), closed(R, MIN, 3)
    if mj: cls = 'NL or below (bijunctive)'
    elif mn: cls = 'parity-L-complete'
    elif a or o:
        single = R == frozenset(t for t in T if t != (1, 1, 1)) or R == frozenset(t for t in T if t != (0, 0, 0))
        cls = 'AC0 (single-sign clause)' if single else 'P-complete'
    else: cls = 'NP-complete'
    return dict(and_=a, or_=o, majority=mj, minority=mn, cls=cls)
def pp_defined(R, cons):
    """relation on (a, b, c) defined by the conjunction of R over the listed triples, hidden names existentially quantified"""
    names = sorted({x for c in cons for x in c} - {'a', 'b', 'c'})
    rel = set()
    for abc in T:
        env0 = dict(zip('abc', abc))
        for hv in itertools.product((0, 1), repeat=len(names)):
            env = dict(env0, **dict(zip(names, hv)))
            if all(tuple(env[x] for x in c) in R for c in cons):
                rel.add(abc); break
    return rel
ATOM = {t for t in T if t != (1, 1, 0)}           # not(a and b and not c): a, b demand c
DUAL = {t for t in T if t != (0, 0, 1)}           # its dual (flip every value)
K = knots()
tab = json.load(open(TABLE))
rows = {frozenset(r['excluded']): r for r in tab['rows']}
res = dict(n_knots=len(K), classes={}, mismatches=[], defs_checked=0, defs_bad=[])
for R in K:
    exc = frozenset(''.join(map(str, t)) for t in T if t not in R)
    c = classify(R); res['classes'][c['cls']] = res['classes'].get(c['cls'], 0) + 1
    r = rows.get(exc)
    if r is None or r['class'] != c['cls'] or (r['and'], r['or'], r['majority'], r['minority']) != (c['and_'], c['or_'], c['majority'], c['minority']):
        res['mismatches'].append(sorted(exc))
    if r and 'defines' in r:
        kind, _, cons = r['defines'].partition(' by ')
        target = ATOM if kind == 'atom' else DUAL
        got = pp_defined(R, json.loads(cons.replace("'", '"')))
        res['defs_checked'] += 1
        if got != target: res['defs_bad'].append(sorted(exc))
res['table_rows'] = len(rows)
print(json.dumps(res, indent=1))
