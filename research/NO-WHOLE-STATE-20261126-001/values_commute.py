"""values_commute.py: the advisor's cheapest test of the claim "every two distinctions have a joint value" (README.md,
part D), from the stored files of FOUR-READINGS-20261120-001A, and the reordering identity behind the closing sign.

Each distinction of a closed, twice-held parity pattern is read as an operator that squares to the identity (a signed
Pauli product, i^p X^x Z^z, the census's encoding); the places of one knot commute. Then the product of all knot
operators, taken knot by knot, equals (-1)^c times the identity, where c counts the pairs of distinctions that do not
commute and whose two occurrences interleave in that word (bringing each distinction's two copies together costs -1 per
such pair). So the sum of the knots' signs is c mod 2: with every value commuting c = 0 and the closing sign is forced
even (the GF(2) row sum the engines use); otherwise it is the cost of reordering.

    1  the stored five-knot witness (every two knots sharing one distinction): signs, commutation, the identity
    2  every stored operator-positive witness (115): the identity  sum of signs = c  holds
    3  the four-knot closure (every two of four knots share one) and the eight-knot closure (three-label subsets): no
       reading with each knot's product a signed identity (planar; the census's word reduction for the four-knot type)
    4  the four-knot closure read with knots as conditions on one state rather than identities: the rule "two
       distinctions commute exactly when some knot holds both" (the three-reader operators) forces the closing sign odd"""
import sys, json, itertools
from pathlib import Path
import networkx as nx
ROOT = Path(__file__).resolve().parents[2]
EXP = ROOT / 'experiments/FOUR-READINGS-20261120-001A/FOUR-READINGS-20261120-001A-E001_signed_rules'
ART = ROOT / 'artifacts/FOUR-READINGS-20261120-001A/FOUR-READINGS-20261120-001A-E001_signed_rules'
sys.path.insert(0, str(EXP))
from census import product, pauli_solution       # noqa: E402  (the census's own Pauli arithmetic)

I = (0, 0, 0)


def commute(a, b):
    return ((a[1] & b[2]).bit_count() + (a[2] & b[1]).bit_count()) % 2 == 0


def word(ends):
    """the closing sum written knot by knot: the list of distinction indices, each knot's places in index order"""
    n = 1 + max(v for e in ends for v in e)
    return [i for u in range(n) for i, e in enumerate(ends) if u in e]


def reorder_cost(ends, anti):
    """pairs of distinctions that do not commute (anti(i, j)) and whose two occurrences interleave in the word"""
    pos = {}
    for k, i in enumerate(word(ends)): pos.setdefault(i, []).append(k)
    c = 0
    for i, j in itertools.combinations(range(len(ends)), 2):
        a, b = pos[i]; x, y = pos[j]
        if (a < x < b < y or x < a < y < b) and anti(i, j): c += 1
    return c


def knot_products(ends, ops):
    n = 1 + max(v for e in ends for v in e)
    out = []
    for u in range(n):
        acc = I
        for i, e in enumerate(ends):
            if u in e: acc = product(acc, ops[i])
        out.append(acc)
    return out


def check_witness(entry):
    ends = [tuple(e) for e in entry['sharing']]; ops = [tuple(o) for o in entry['pauli_i_phase_X_bits_Z_bits']]
    n = entry['n']
    assert all(product(o, o) == I for o in ops), 'every value squares to +I'
    places_commute = all(commute(ops[i], ops[j]) for u in range(n)
                         for i, j in itertools.combinations([k for k, e in enumerate(ends) if u in e], 2))
    K = knot_products(ends, ops)
    signs = [None if k not in (I, (2, 0, 0)) else int(k == (2, 0, 0)) for k in K]
    total = I
    for k in [i for i in word(ends)]: total = product(total, ops[k])
    c = reorder_cost(ends, lambda i, j: not commute(ops[i], ops[j]))
    anti_pairs_unheld = all(not set(ends[i]) & set(ends[j])
                            for i, j in itertools.combinations(range(len(ends)), 2) if not commute(ops[i], ops[j]))
    return {'knots': n, 'distinctions': len(ends), 'places of a knot commute': places_commute, 'knot signs': signs,
            'product of the closing sum': 'I' if total == I else ('-I' if total == (2, 0, 0) else str(total)),
            'reorder cost c': c, 'sum of signs = c mod 2': sum(s for s in signs if s is not None) % 2 == c % 2,
            'pairs that do not commute are held by no common knot': anti_pairs_unheld}


def subsets_closure(k):
    """the closed structure of k-label subsets (two holders share when they differ by one label)"""
    V = list(itertools.product((0, 1), repeat=k))
    idx = {v: i for i, v in enumerate(V)}
    return [(idx[a], idx[b]) for a, b in itertools.combinations(V, 2) if sum(x != y for x, y in zip(a, b)) == 1]


def rule_R(ends):
    """Paulis whose anticommutation graph is 'no knot holds both': A_i = X_i Z^{j<i, i and j share no holder}"""
    m = len(ends)
    anti = lambda i, j: not set(ends[i]) & set(ends[j])
    ops = []
    for i in range(m):
        z = sum(1 << j for j in range(i) if anti(i, j))
        ops.append((((1 << i) & z).bit_count() % 4, 1 << i, z))
    for i, j in itertools.combinations(range(m), 2): assert commute(ops[i], ops[j]) == (not anti(i, j))
    K = knot_products(ends, ops)
    n = len(K)
    knots_commute = all(commute(K[u], K[v]) for u, v in itertools.combinations(range(n), 2))
    total = I
    for k in word(ends): total = product(total, ops[k])
    c = reorder_cost(ends, anti)
    # a state on which every older knot reads even always exists here (the X-parts of the values are independent, so no
    # product of a proper set of knots is a scalar); the closing knot's value on it is then forced: (-1)^c. A knot that
    # commutes with every value is a signed identity in an irreducible realisation (the state is then not needed).
    central = [all(commute(K[u], o) for o in ops) for u in range(n)]
    return {'knots': n, 'distinctions': m, 'knot operators commute': knots_commute,
            'knots commuting with every value': sum(central),
            'product of the closing sum': 'I' if total == I else ('-I' if total == (2, 0, 0) else str(total)),
            'reorder cost c': c, 'closing sign forced': 'odd' if c % 2 else 'even'}


if __name__ == '__main__':
    census = json.load(open(ART / 'census.json'))
    five = [e for e in census if e['n'] == 5 and e['operator']]
    print(json.dumps({'1 five-knot witness': check_witness(five[0])}))
    pos = [check_witness(e) for e in census if e['operator']]
    print(json.dumps({'2 stored positive witnesses': len(pos),
                      'places commute in all': all(p['places of a knot commute'] for p in pos),
                      'one odd knot in all': all(sum(s for s in p['knot signs'] if s is not None) == 1 for p in pos),
                      'sum of signs = c mod 2 in all': all(p['sum of signs = c mod 2'] for p in pos),
                      'non-commuting pairs unheld in all': all(p['pairs that do not commute are held by no common knot'] for p in pos)}))
    four = [tuple(e) for e in census[0]['sharing']]
    eight = subsets_closure(3)
    refut = [r for r in json.load(open(ART / 'arbitrary_operator_refutations.json')) if r['atlas'] == census[0]['atlas']]
    for name, ends in (('four-knot closure', four), ('eight-knot closure', eight)):
        odd = {1 + max(v for e in ends for v in e) - 1}
        print(json.dumps({'3 ' + name: {'planar': nx.check_planarity(nx.Graph(ends))[0],
                                         'signed-identity Pauli reading with one odd knot': pauli_solution(ends, odd) is not None,
                                         'stored word reduction to I = -I (any dimension)': bool(refut) if name.startswith('four') else 'not in the census (eight knots)'}}))
    for name, ends in (('four-knot closure', four), ('five-knot closure', [tuple(e) for e in five[0]['sharing']]),
                       ('eight-knot closure', eight)):
        print(json.dumps({'4 rule R, ' + name: rule_R(ends)}))
