"""part_c.py: the bound under R with the counting state (README.md, part C). Where R makes a component's knots commute,
the state the signed knots fix, read by counting within each read set, gives each pair of commuting values a
correlation E(e, f) (the mean of the product of their signs). Two readers: Alice's settings two distinctions, Bob's
two, every Alice-Bob pair commuting. The largest CHSH value |E00 + E01 + E10 - E11| over every such choice and every
placement of the minus sign; the literature's limits are 2 for a list of values, 2*sqrt(2) for a quantum state, 4 with
no-signalling alone. On the census types where R1 holds (entailed at most 2 for products of values: if three of the four
pair products are laws the fourth is too, and if one reader's two settings fail to commute at most two are laws).
Three readers on the four-knot closure (the pairs no knot holds together): the literature's three-reader sum of the
four correlations with an odd number of minus signs; 2 for a list of values, 4 for a quantum state, which is also the
most a three-reader table can give. Under R every two readers' values must be held by a common knot to be read
together, so these are tables read inside knots.
    part_c.py"""
import sys, json, itertools
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE.parent / 'NO-WHOLE-STATE-20261126-001'))
import ops, part_b, values_commute as vc, rule_census as rc     # noqa: E402


def correlation(knots, vals, K, s, use, e, f):
    L, bad = ops.laws(knots, vals, K, s, (e, f), use)
    assert not bad
    law = dict(L); both = (1 << e) | (1 << f)
    if (1 << e) in law and (1 << f) in law: return (-1) ** (law[1 << e] + law[1 << f])
    if both in law: return (-1) ** law[both]
    return 0


def best_chsh(knots, vals, K, s, use):
    co = ops.coheld([knots[u] for u in use]); D = sorted({d for u in use for d in knots[u]})
    nb = {d: set() for d in D}
    for a, b in co: nb[a].add(b); nb[b].add(a)
    E = {}
    def corr(e, f):
        key = (min(e, f), max(e, f))
        if key not in E: E[key] = correlation(knots, vals, K, s, use, *key)
        return E[key]
    best = 0
    for e0, e1 in itertools.combinations(D, 2):
        common = sorted(nb[e0] & nb[e1] - {e0, e1})
        for f0, f1 in itertools.combinations(common, 2):
            c = [corr(e0, f0), corr(e0, f1), corr(e1, f0), corr(e1, f1)]
            for i in range(4):
                best = max(best, abs(sum(c) - 2 * c[i]))
    return best


def triple(knots, vals, K, s, a, b, c):
    L, bad = ops.laws(knots, vals, K, s, (a, b, c), range(len(knots)))
    assert not bad
    law = dict(L); allm = (1 << a) | (1 << b) | (1 << c)
    if allm in law: return (-1) ** law[allm]
    singles = [1 << a, 1 << b, 1 << c]
    if all(x in law for x in singles): return (-1) ** sum(law[x] for x in singles)
    return 0


def mermin(knots, vals, K, s, readers):
    E = {}
    for x in itertools.product((0, 1), repeat=3):
        trip = [readers[i][x[i]] for i in range(3)]
        assert all((min(p, q), max(p, q)) in ops.coheld(knots) for p, q in itertools.combinations(trip, 2)), 'readers read together'
        E[x] = triple(knots, vals, K, s, *trip)
    best = 0
    for signs in itertools.product((1, -1), repeat=4):
        if signs.count(-1) % 2 == 0: continue
        terms = [x for x in E if sum(x) % 2 == 0]           # the four settings of even weight, as Mermin's sum uses
        best = max(best, abs(sum(sg * E[x] for sg, x in zip(signs, terms))))
    classical = 0
    for w in itertools.product((1, -1), repeat=6):
        val = {readers[i][j]: w[2 * i + j] for i in range(3) for j in range(2)}
        for signs in itertools.product((1, -1), repeat=4):
            if signs.count(-1) % 2 == 0: continue
            terms = [x for x in E if sum(x) % 2 == 0]
            classical = max(classical, abs(sum(sg * val[readers[0][x[0]]] * val[readers[1][x[1]]] * val[readers[2][x[2]]]
                                               for sg, x in zip(signs, terms))))
    return {'correlations': {''.join(map(str, x)): E[x] for x in E}, 'three-reader value': best, 'a list of values at most': classical}


if __name__ == '__main__':
    census = json.load(open(vc.ART / 'census.json'))
    rows = []                          # the census rows of rule_census.py, recomputed (its .jsonl output is not kept)
    for t, e in enumerate(census):
        a = rc.analyse(rc.from_ends([tuple(x) for x in e['sharing']]))
        a.update({'type': t, 'reached by ordinary growth': bool(e['restored_last_holders'])}); rows.append(a)
    out = []
    for r in rows:
        if not r['R1 knots commute under R']: continue
        knots = rc.from_ends([tuple(x) for x in census[r['type']]['sharing']])
        m = 1 + max(d for k in knots for d in k)
        vals = ops.realise(m, ops.rule_R(knots, m)); K = ops.knot_ops(knots, vals); s, _ = ops.signs(knots, K)
        out.append({'type': r['type'], 'knots': r['knots'], 'best CHSH': best_chsh(knots, vals, K, s, range(len(knots)))})
    print(json.dumps({'census types with R1': len(out), 'largest CHSH': max(o['best CHSH'] for o in out),
                      'types reaching 2': sum(o['best CHSH'] == 2 for o in out)}))
    for o in out: print(json.dumps(o))
    k = [[0, 1, 2], [0, 3, 4], [1, 3, 5], [2, 4, 5]]                 # census type 0, every two of four knots sharing one
    vals = ops.realise(6, ops.rule_R(k, 6)); K = ops.knot_ops(k, vals); s, _ = ops.signs(k, K)
    readers = [(0, 5), (1, 4), (2, 3)]
    print(json.dumps({'four-knot closure, readers (0,5), (1,4), (2,3)': mermin(k, vals, K, s, readers)}))
