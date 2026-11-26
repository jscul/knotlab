"""reach.py: can growth reach a pattern with no state of the whole once the requirement is dropped? (README.md, part B)
Under even parity every pattern allows the all-zero state, and under not-all-equal a pattern whose distinctions have at
most two holders and whose knots have three or more places always has an allowed state (FORBIDDING-JOIN's survival
proof), so growth can reach such a pattern only through a join with no fresh distinction (a forbidding law) together with
a take that gives a distinction a third holder. Read: a seeded sample of census starts (random.Random(20261126), 300),
not-all-equal, the recent line's engine, grown up to four rounds under the forbidding law one fewer (the record's form)
and the arity floor, each with no take and with the recorded takes; after each round, whether the whole has an allowed
state (an exact solver), the most holders of a distinction, and the joins with no fresh distinction.

    reach.py COUNT ROUNDS"""
import sys, json, random, collections
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / 'SHORT-AGAIN-20261126-001')); sys.path.insert(0, str(HERE.parent / 'FORBID-EDITS-20261126-001'))
import ring_line, forbid
eng = ring_line.eng
import z3


class ArityFloor(eng.Law):
    def __init__(self, take=None, choice=None):
        eng.Law.__init__(self, 'ORD', 'CANCEL-WAIT', take, 'nae', choice)
    def fresh(self, kind, p, D, o):
        q = max(D, 3 - p, 1); return min(q, max(3 - p, 0))


class OneFewer(eng.Law):
    def __init__(self, take=None, choice=None):
        eng.Law.__init__(self, 'ORD', 'CANCEL-WAIT', take, 'nae', choice)
    def fresh(self, kind, p, D, o):
        q = max(D, 3 - p, 1); return min(q, max(3 - p, 0, q - 1))


def whole_allowed(S):
    s = z3.Solver(); v = {}
    for row in S.places:
        xs = [v.setdefault(d, z3.Bool('x%d' % d)) for d in row]
        s.add(z3.Or(*xs)); s.add(z3.Or(*[z3.Not(x) for x in xs]))
    return s.check() == z3.sat


if __name__ == '__main__':
    count, rounds = int(sys.argv[1]), int(sys.argv[2])
    S0 = forbid.census(); picks = sorted(random.Random(20261126).sample(range(len(S0)), count))
    takes = [(None, None), ('MET', 'OLDEST'), ('MET', 'NEWEST'), ('MET-SOLE', None)]
    c = collections.Counter(); ex = []
    for i in picks:
        stars = [list(r) for r in forbid.supports_of(S0[i])]
        for lawname, L in (('one fewer', OneFewer), ('arity floor', ArityFloor)):
            for take, choice in takes:
                law = L(take, choice); S = eng.from_stars(stars); G = eng.Guard(4); maxh = 2; zero = 0
                for r in range(1, rounds + 1):
                    T = S.copy()
                    try: rec = eng.play_round(T, law, G)
                    except Exception as e: c[(lawname, str(take), 'stopped: %s' % type(e).__name__)] += 1; break
                    if not rec['births']: c[(lawname, str(take), 'no births')] += 1; break
                    S = T
                    maxh = max(maxh, max(len(h) for h in S.holders if h))
                    zero += sum(1 for k in range(S.n_knots) if S.made[k] == S.round and all(len(S.holders[d]) > 1 for d in S.places[k]))
                    if not whole_allowed(S):
                        c[(lawname, str(take), 'no whole state reached')] += 1
                        if len(ex) < 4: ex.append((i, lawname, take, r, S.n_knots, maxh))
                        break
                else:
                    c[(lawname, str(take), 'whole state kept')] += 1
                c[(lawname, str(take), 'most holders %d' % min(maxh, 9))] += 1
    for k, v in sorted(c.items(), key=str): print(k, v)
    print('examples', ex)
