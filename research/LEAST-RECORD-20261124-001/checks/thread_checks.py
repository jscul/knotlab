"""The thread's own check for LEAST-RECORD-20261124-001, written independently of the study's code.

Run from the repository root:  .venv/bin/python -B research/LEAST-RECORD-20261124-001/checks/thread_checks.py

On structures grown by complete rounds with the ring study's engine: every birth's parents have equal generations, and
the rule "the other holder of a shared place is a parent exactly when its generation is one less, modulo 3" gives every
shared place its kind. On the start-clause counterexample one birth has parents of unequal generations and the rule
gets places wrong.
"""
import pathlib, sys
ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'experiments/RING-IN-BALANCE-20261123-001A/RING-IN-BALANCE-20261123-001A-E001_ring'))
import engine as E

CASES = [
    ('cycle of four through dead knots', lambda: E.d2(4, 3), ('RATION-3', 'CANCEL-WAIT'), 9),
    ('ring of five', lambda: E.ring(5, 3), ('RATION-3', 'CANCEL-WAIT'), 8),
    ('ring of five', lambda: E.ring(5, 3), ('CAP-3', 'CANCEL-WAIT'), 8),
    ('two-knot start', lambda: E.from_stars([[0, 1, 2], [0, 3, 4]]), ('FLOOR1', 'CANCEL-OFFSHOOT'), 10),
    ('two-knot start', lambda: E.from_stars([[0, 1, 2], [0, 3, 4]]), ('FLOOR1', 'CANCEL-RETIRE'), 10),
    ('three-knot start', lambda: E.from_stars([[0, 1, 2, 3], [0, 1, 4, 5], [2, 3, 6, 7]]), ('FLOOR1', 'CANCEL-OFFSHOOT'), 10),
    ('lone four-place knot', lambda: E.from_stars([[0, 1, 2, 3]]), ('ORD', 'STALL'), 6),
    ('two-knot start', lambda: E.from_stars([[0, 1, 2], [0, 3, 4]]), ('ORD', 'STALL'), 9),
    ('seven-knot generator', E.generator7, ('FLOOR1', 'CANCEL-OFFSHOOT'), 6),
    ('start-clause counterexample', lambda: E.from_stars([[1,2,3,7,8],[1,4,9,10],[2,5,11,12],[3,6,13,14],[4,15,16],[5,17,18],[6,19,20]]), ('RATION-3', 'CANCEL-WAIT'), 7),
]
for name, make, (ration, treatment), rounds in CASES:
    S = make(); law = E.Law(ration=ration, treatment=treatment)
    for r in range(rounds):
        S, rec = E.round_step(S, law)
        if rec['n_births'] == 0: break
        if S.n_knots > 3000: break
    gen = {}
    for u in range(S.n_knots):
        gen[u] = 0 if not S.parents[u] else 1 + max(gen[p] for p in S.parents[u])
    unequal = [u for u in range(S.n_knots) if len(set(gen[p] for p in S.parents[u])) > 1]
    holders = {}
    for u in range(S.n_knots):
        for d in S.places[u]: holders.setdefault(d, []).append(u)
    places = wrong = 0
    for d, hs in holders.items():
        if len(hs) != 2: continue
        for x, y in (hs, hs[::-1]):
            places += 1
            truth = y in S.parents[x]
            said = (gen[y] % 3) == ((gen[x] - 1) % 3)
            wrong += truth != said
    print('%-28s %-9s %-15s knots %5d | births with parents of unequal generations %d %s | shared places %6d, rule wrong on %d'
          % (name, ration, treatment, S.n_knots, len(unequal), [(u, [gen[p] for p in S.parents[u]]) for u in unequal[:2]], places, wrong))
