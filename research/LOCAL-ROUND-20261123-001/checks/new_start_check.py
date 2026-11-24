"""The thread's check of the cycle of eight with three extra dead knots, on the earlier study's engine (the reference).

Run from the repository root:  .venv/bin/python -B research/LOCAL-ROUND-20261123-001/checks/new_start_check.py
It prints the places and loose distinctions of the start, and for rounds 1 to 6 under (RATION-3, CANCEL-WAIT) the births,
the members that are short, and the verdict of the parity knot test (both methods) on every knot.
"""
import pathlib, sys
ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'experiments/RING-IN-BALANCE-20261123-001A/RING-IN-BALANCE-20261123-001A-E001_ring'))
import engine as E

STARS = [[0,1,30,31,32,33,34,56,57],[4,5,2,3,35,36,37,60,61],[8,9,6,7,38,39,40,64,65],[12,13,10,11,41,42,43],
         [16,17,14,15,44,45,46,58,59],[20,21,18,19,47,48,49,62,63],[24,25,22,23,50,51,52,66,67],[28,29,26,27,53,54,55],
         [0,1,2,3],[4,5,6,7],[8,9,10,11],[12,13,14,15],[16,17,18,19],[20,21,22,23],[24,25,26,27],[28,29,30,31],
         [56,57,58,59],[60,61,62,63],[64,65,66,67]]
S = E.from_stars(STARS)
print('knots', S.n_knots, 'places', [len(S.places[u]) for u in range(S.n_knots)])
print('loose', [len(S.loose(u)) for u in range(S.n_knots)])
t = E.parity_knot_test(S)
print('start: every knot passes', t['all_pass'], 'rank', t['rank_H'], 'of', t['n_knots'])
law = E.Law(ration='RATION-3', treatment='CANCEL-WAIT')
for r in range(1, 7):
    S, rec = E.round_step(S, law)
    t = E.parity_knot_test(S)
    print('round', r, 'births', rec['n_births'], 'joins', rec['n_joins'], 'offshoots', rec['n_offshoots'], 'short', rec['short'],
          'waiting', rec['waiting'], '| knots', S.n_knots, 'every knot passes', t['all_pass'], 'methods disagree', len(t['disagree']))
