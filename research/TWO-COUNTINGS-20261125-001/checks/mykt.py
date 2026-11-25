"""Independent knot test in the whole structure (checker's own code, not the engine's).

A structure: list of (law, places). law in even/odd/nae. States enumerated by an incremental join over the rules.
Induced relation of a rule: the set of its place assignments that extend to an allowed state of the whole.
K1: the relation is not every assignment; K2 (forgetting): dropping any one place leaves every assignment of the rest;
K3: the relation is nonempty.
"""
import itertools
import json
import resource
import sys

resource.setrlimit(resource.RLIMIT_AS, (6 * 1024 ** 3, 6 * 1024 ** 3))


def ok(law, bits):
    s = sum(bits)
    if law == 'even':
        return s % 2 == 0
    if law == 'odd':
        return s % 2 == 1
    if law == 'nae':
        return 0 < s < len(bits)
    raise ValueError(law)


def allowed_states(rules):
    """Return (variables, list of dict-free tuples) by incremental join; order rules greedily by overlap."""
    rules = [(l, tuple(p)) for l, p in rules]
    remaining = list(range(len(rules)))
    order_vars = []
    pos = {}
    states = [()]
    while remaining:
        # pick the rule with most places already held (ties: first)
        best = max(remaining, key=lambda i: (sum(p in pos for p in rules[i][1]), -i))
        remaining.remove(best)
        law, P = rules[best]
        new = [p for p in P if p not in pos]
        for p in new:
            pos[p] = len(order_vars)
            order_vars.append(p)
        idx = [pos[p] for p in P]
        out = []
        for s in states:
            for ext in itertools.product((0, 1), repeat=len(new)):
                t = s + ext
                if ok(law, [t[i] for i in idx]):
                    out.append(t)
        states = out
    return order_vars, states


def induced(order_vars, states, P):
    pos = {v: i for i, v in enumerate(order_vars)}
    idx = [pos[p] for p in P]
    return sorted({tuple(s[i] for i in idx) for s in states})


def k_test(P, rel):
    n = len(P)
    rel = set(rel)
    K1 = len(rel) < 2 ** n
    K3 = len(rel) > 0
    K2 = True
    for d in range(n):
        proj = {tuple(r[i] for i in range(n) if i != d) for r in rel}
        if len(proj) < 2 ** (n - 1):
            K2 = False
    return K1, K2, K3


def test_structure(rules):
    order_vars, states = allowed_states(rules)
    rows = []
    for law, P in rules:
        rel = induced(order_vars, states, P)
        K1, K2, K3 = k_test(P, rel)
        own = [b for b in itertools.product((0, 1), repeat=len(P)) if ok(law, b)]
        o1, o2, o3 = k_test(P, own)
        rows.append({'rule': '%s(%s)' % (law, ','.join(P)), 'induced': [''.join(map(str, r)) for r in rel],
                     'K1': K1, 'K2': K2, 'K3': K3, 'whole': K1 and K2 and K3, 'own': o1 and o2 and o3})
    return {'n_vars': len(order_vars), 'n_states': len(states), 'rules': rows}


if __name__ == '__main__':
    S = json.load(open(sys.argv[1]))
    out = {}
    for name, rules in S.items():
        r = test_structure(rules)
        out[name] = r
        fails = [x['rule'] + ' ' + ''.join(k for k in ('K1', 'K2', 'K3') if not x[k]) + ' ' + str(x['induced'])
                 for x in r['rules'] if not x['whole']]
        ownf = [x['rule'] for x in r['rules'] if not x['own']]
        print('%-45s rules %2d vars %2d states %5d  fail-whole: %s  fail-own: %s' % (
            name, len(rules), r['n_vars'], r['n_states'], fails or 'none', ownf or 'none'))
    json.dump(out, open(sys.argv[2], 'w'), indent=1)
