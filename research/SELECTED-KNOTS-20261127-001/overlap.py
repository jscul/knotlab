"""overlap.py OUT.json: the third-layer referee's witness reproduced with the thread's own code.  SELECTED-KNOTS-20261127-001.

Three rings of four knots, split attachments, double links (repro.rings_start), grown by the canonical engine.  Five
carriers: each ring's eight loose distinctions (the whole-ring facts R, S, T) and, for each of the first ring's two
families, the fresh distinctions of its round-1 births (P, Q).  At rounds 1 to 6: the joint values of the five (linear,
checked by a solver call per tuple), each triple's values, the least change flipping each (minflip), whether each is a
class fact held by no part at scale 12 (scale.held_by_no_part, rounds 4 to 6), and which single law removals free each
triple."""
import sys, json, itertools
from pathlib import Path
HERE = Path(__file__).resolve().parent; ROOT = HERE.parents[1]
for d in ('BUILT-BINDING-20261126-001', 'THIRD-LAYER-20261126-001'): sys.path.insert(0, str(ROOT / 'research' / d))
import repro as RP, minflip as MF, scale as SC, twokinds as TK, built as BU
S, rings, loose = RP.rings_start(R=3, n=4, attach='split', link='double')
fams, ls = TK.families(S)
f1 = [f for f in fams if set(f) <= set(rings[0])]
assert len(f1) == 2
out = {'families of ring 1': f1, 'stages': []}
st, status, births = RP.forbid.grown(S, 'parity', 'ordinary')
P = [x for b in births if set(b['parents']) <= set(f1[0]) for x in b['fresh']]
Q = [x for b in births if set(b['parents']) <= set(f1[1]) for x in b['fresh']]
cars = [loose[0], loose[1], loose[2], P, Q]
for t in range(1, 7):
    if t > 1: st, status, births = RP.forbid.grown(st, 'parity', 'ordinary')
    names, idx, rows = RP.space(st); fs = [sum(1 << idx[x] for x in c) for c in cars]
    occ = RP.tuples(rows, len(names), fs)
    rec = {'round': t, 'knots': len(st), 'distinctions': len(names), 'words of the five': len(occ),
           'R S T one rule': RP.one_rule({(o[0], o[1], o[2]) for o in occ}, 3),
           'P Q R one rule': RP.one_rule({(o[3], o[4], o[0]) for o in occ}, 3),
           'least flips': [MF.least(st, c, kmax=40) for c in cars]}
    if t <= 4:
        sol = {tuple(v) for v in BU.tuples_solver(st, cars)}; rec['solver agrees'] = sol == occ
    if t >= 4:
        res, nloc = SC.held_by_no_part(st, cars, 12); rec['scale 12'] = res; rec['single-knot class facts at 12'] = nloc
    if t == 5:
        free = {'R S T': [], 'P Q R': []}
        for j in range(len(rows)):
            o2 = RP.tuples(rows[:j] + rows[j + 1:], len(names), fs)
            if len({(o[0], o[1], o[2]) for o in o2}) == 8: free['R S T'].append('start' if j < len(S) else 'born')
            if len({(o[3], o[4], o[0]) for o in o2}) == 8: free['P Q R'].append('start' if j < len(S) else 'born')
        rec['single law removals freeing each triple'] = {k: {'start': v.count('start'), 'born': v.count('born')} for k, v in free.items()}
    out['stages'].append(rec); print(json.dumps(rec)[:400], flush=True)
json.dump(out, open(sys.argv[1], 'w'), indent=1)
