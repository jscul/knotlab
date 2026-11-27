"""collapse.py OUT.json: an independent check of the bond search by the advisor's collapse rule.  RING-BOND-20261127-001.

A triple of agreement values (one per carrier) is missing exactly when the stage has no state with it.  Written as a
system: an agreeing carrier makes its distinctions equal, a disagreeing pair makes them unequal, and a disagreeing triple
adds the clause pair 'not all equal' on its three distinctions.  Each system is decided by a solver (pysat), with no
enumeration; the missing triples so found are compared with ringbond.bonds on the ring's rounds 1-3 (every bond) and on
the bonds of census starts 0-199 at round 0 and 1 found by ringbond.local_bonds (holders <= 4), under both laws."""
import sys, json, itertools
from pysat.solvers import Minisat22
import ringbond as RB


def law_clauses(sup, law, var):
    cl = []
    for r in sup:
        v = [var[x] for x in r]
        if law == 'nae': cl += [v, [-u for u in v]]
        else:
            for bits in itertools.product((0, 1), repeat=len(v)):
                if sum(bits) % 2: cl.append([-u if b else u for u, b in zip(v, bits)])
    return cl


def missing_by_collapse(sup, law, readings):
    names = sorted({x for r in sup for x in r}); var = {x: i + 1 for i, x in enumerate(names)}
    base = law_clauses(sup, law, var); out = []
    for w in range(8):
        cl = list(base)
        for p, C in enumerate(readings):
            xs = [var[x] for x in C]; agree = (w >> (2 - p)) & 1
            if agree:
                for x in xs[1:]: cl += [[-xs[0], x], [xs[0], -x]]
            elif len(xs) == 2: cl += [[xs[0], xs[1]], [-xs[0], -xs[1]]]
            else: cl += [list(xs), [-x for x in xs]]
        s = Minisat22(bootstrap_with=cl); ok = s.solve(); s.delete()
        if not ok: out.append('{:03b}'.format(w))
    return out


if __name__ == '__main__':
    res = {'ring': [], 'census': {'nae': [0, 0], 'parity': [0, 0]}}
    S = ((0, 1, 3), (1, 2, 4), (2, 0, 5))
    for t, (sup, born) in enumerate(RB.stages(S, 'nae', 3)):
        b = RB.bonds(RB.Stage(sup, 'nae'), 'agree', born=born)['bonds']
        agree = sum(missing_by_collapse(sup, 'nae', [C for C, lab in x['readings']]) == x['missing'] for x in b)
        res['ring'].append({'round': t, 'bonds': len(b), 'collapse agrees': agree})
    starts = RB.forbid.census()
    for law in ('nae', 'parity'):
        for i in range(200):
            S0 = RB.forbid.supports_of(starts[i])
            for sup in [S0] + ([RB.stages(S0, law, 1)[1][0]] if len(RB.stages(S0, law, 1)) > 1 else []):
                for x in RB.local_bonds(sup, law, 4):
                    if not x['same relation on the stage'] or x['read at a knot of the stage']: continue
                    res['census'][law][0] += 1
                    res['census'][law][1] += missing_by_collapse(sup, law, [C for C, lab in x['readings']]) == x['missing']
    json.dump(res, open(sys.argv[1], 'w'), indent=1); print(json.dumps(res))
