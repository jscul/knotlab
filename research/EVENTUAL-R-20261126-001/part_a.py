"""part_a.py: part counting against the state's counts on the closed census types where R makes every knot commute
(README.md, part A). For every subset of every maximal read set (values pairwise commuting under R), the laws on it by
    (i)   the closed part rule: the knots lying wholly inside it, each with its own sign
    (ii)  products of knots whose leftover lies inside it, the parity the GF(2) sum of the knots' signs
    (iii) the same products, the parity the sign of the operator product (ops.laws)
    (iv)  an independent count: every element of the group the signed knots generate, enumerated, kept when it is a
          signed product of the read set's values
Two rules agree on a read set when they allow the same words (the counts within it are uniform on the allowed words)."""
import sys, json, itertools
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE.parent / 'NO-WHOLE-STATE-20261126-001'))
import ops, values_commute as vc, rule_census as rc     # noqa: E402


def rule_i(knots, s, P):
    return ops.reduce_laws([(sum(1 << d for d in k), s[u]) for u, k in enumerate(knots) if set(k) <= set(P)])


def rule_ii(knots, s, P):
    # the products of (iii) with something left over, signed by the GF(2) sum (the whole product, with nothing left
    # over, would read 0 = 1 at every odd closing)
    P = set(P); n = len(knots); out = []
    for size in range(1, n + 1):
        for U in itertools.combinations(range(n), size):
            S = 0
            for u in U: S ^= sum(1 << d for d in knots[u])
            if S and all(d in P for d in range(S.bit_length()) if S >> d & 1):
                out.append((S, sum(s[u] for u in U) % 2))
    return ops.reduce_laws(out)


def rule_iv(knots, vals, K, s, P):
    n = len(knots); P = set(P); out = []
    gens = [ops.product((2 * s[u], 0, 0), K[u]) for u in range(n)]
    for size in range(0, n + 1):
        for U in itertools.combinations(range(n), size):
            g = ops.mul([gens[u] for u in U])
            S = g[1]                                     # the X part names the distinctions (one qubit each)
            if not all(d in P for d in range(S.bit_length()) if S >> d & 1): continue
            rest = ops.product(g, ops.mul([vals[d] for d in sorted(d for d in P if S >> d & 1)]))
            if rest[1] or rest[2]: continue              # not a product of the read set's values
            out.append((S, rest[0] // 2))
    return ops.reduce_laws(out)


def subsets(P):
    for r in range(1, len(P) + 1):
        yield from itertools.combinations(P, r)


if __name__ == '__main__':
    census = json.load(open(vc.ART / 'census.json'))
    rows = []                          # the census rows of rule_census.py, recomputed (its .jsonl output is not kept)
    for t, e in enumerate(census):
        a = rc.analyse(rc.from_ends([tuple(x) for x in e['sharing']]))
        a.update({'type': t, 'reached by ordinary growth': bool(e['restored_last_holders'])}); rows.append(a)
    tally = {'types': 0, 'read sets': 0, 'state exists': 0, '(iii) = (iv)': 0, '(i) = (iv)': 0, '(ii) = (iv)': 0}
    per = []
    for r in rows:
        if not r['R1 knots commute under R']: continue
        knots = rc.from_ends([tuple(x) for x in census[r['type']]['sharing']])
        m = 1 + max(d for k in knots for d in k)
        vals = ops.realise(m, ops.rule_R(knots, m)); K = ops.knot_ops(knots, vals); s, closed = ops.signs(knots, K)
        assert ops.r1(K)
        seen = set(); diff_i = diff_ii = 0; n_sets = 0
        for P in ops.maximal_read_sets(knots):
            for Q in subsets(P):
                if Q in seen: continue
                seen.add(Q); n_sets += 1
                a3, a4 = ops.laws(knots, vals, K, s, Q, range(len(knots))), rule_iv(knots, vals, K, s, Q)
                tally['(iii) = (iv)'] += a3 == a4
                tally['state exists'] += not a4[1]
                tally['(i) = (iv)'] += rule_i(knots, s, Q) == a4
                same_ii = rule_ii(knots, s, Q) == a4
                tally['(ii) = (iv)'] += same_ii
                diff_i += rule_i(knots, s, Q) != a4; diff_ii += not same_ii
        tally['types'] += 1; tally['read sets'] += n_sets
        per.append({'type': r['type'], 'knots': r['knots'], 'reached': r['reached by ordinary growth'],
                    'forced closing sign': r['R2 sum forced under R'], 'read sets': n_sets,
                    'closed part rule differs': diff_i, 'GF(2)-signed products differ': diff_ii})
    print(json.dumps(tally))
    for p in per: print(json.dumps(p))
