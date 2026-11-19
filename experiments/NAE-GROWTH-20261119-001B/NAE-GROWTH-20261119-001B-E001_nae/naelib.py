"""The cheapest growth under the not-all-equal law (NAE-GROWTH-20261119-001B).

The joining policy and the fewest counts are FRESH-COUNT's (through joinlib/fastlib).  Every junction is read as a not-all-equal
constraint on its distinctions instead of an even-parity one.  The law enters in one place only: a new junction with no demand gets
no fresh distinction exactly when its constraint is implied by the junctions before it, i.e. when no state allowed by them makes
its old distinctions all equal (two SAT calls, all 0 and all 1, by pysat's Minisat).  With one fresh distinction or more, a
not-all-equal junction never removes an old state (a fresh distinction can always differ), so the policy's other clause holds."""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / 'experiments/JOIN-GROWTH-20261118-001B/JOIN-GROWTH-20261118-001B-E001_joins'))
import joinlib as J  # noqa: E402
S, F = J.S, J.F


def _solver(P, upto):
    from pysat.solvers import Minisat22
    s = Minisat22()
    for j in range(upto):
        bits = P.bits_of[j]
        if len(bits) >= 1:
            s.add_clause([b + 1 for b in bits])
            s.add_clause([-(b + 1) for b in bits])
    return s


def nae_implied(P, old_count, bits):
    """Is NAE(bits) forced by the first old_count junctions?"""
    s = _solver(P, old_count)
    try:
        a0 = s.solve(assumptions=[-(b + 1) for b in bits])
        a1 = s.solve(assumptions=[b + 1 for b in bits])
        return not a0 and not a1
    finally:
        s.delete()


def nae_rule(rule, log=None):
    def r(P, info, rng):
        old = min(i['j'] for i in info) if info else len(P.bits_of)
        s = _solver(P, old) if info else None
        try:
            for i in info:
                bits = P.bits_of[i['j']][:i['p']]
                a0 = s.solve(assumptions=[-(b + 1) for b in bits])
                a1 = s.solve(assumptions=[b + 1 for b in bits])
                i['implied'] = not a0 and not a1
                if log is not None and i['implied']:
                    log.append((P.rounds, i['j'], i['d']))
        finally:
            if s is not None:
                s.delete()
        return rule(P, info, rng)
    r.__name__ = 'nae_' + getattr(rule, '__name__', 'rule')
    return r


def parity_rule(rule):
    return S.gf2(rule)


def grow(sizes, edges, law, rounds=20, maxj=20000, log=None):
    P = S.from_junctions(J.stars_from(sizes, edges))
    rule = nae_rule(F.fewest, log) if law == 'nae' else parity_rule(F.fewest)
    out = 'alive'
    implied_count = 0
    for _ in range(rounds):
        r = P.step(rule, None)
        if r is None:
            out = 'stall'
            break
        if r['new'] == 0:
            out = 'closed'
            break
        if len(P.bits_of) > maxj:
            out = 'cap'
            break
    return P, out


def satisfiable(P):
    s = _solver(P, len(P.bits_of))
    try:
        return s.solve()
    finally:
        s.delete()
