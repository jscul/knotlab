"""Referee R1 (BLOCK-REACH-20261116-001), item 4: Theorem F's bound against exact values, by my SAT oracle.

mode 'bound' (N = 11): for small-orbit rulers with r = 1 and half-rate descriptions, s <= 3: exact ties from level 3 to every deeper
  level (backbone), and an exhaustive search for three-member bonds meeting levels 3 and 6 (every {x at level 3, y at level 6, z any
  other address}; referee_check_s5.run from the DIRECT-REACH referee folder, my own code). Then the least bond meeting levels 3 and
  3 + s is >= 3 when there is no tie, and >= 4 at s = 3 when there is also no three-member bond; compared with 1 + ceil(s/r).
mode 'upgrade' (N = 12): for half-rate descriptions, L_N(3, s) = 3 at s = 1, 2: no tie from level 3 to levels 4 and 5 (exact), and
  the census's depth-9 three-member bond for that s is still constrained with every pair free at N = 12 (SAT on all 8 patterns).
Usage: referee_bound.py OUT.json mode n first:last"""
import json
import math
import random
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, '/home/jscul/p-vs-np-contact-first/research/DIRECT-REACH-20261115-001/referee-R1')
sys.path.insert(0, '/home/jscul/p-vs-np-contact-first/research/BLOCK-REACH-20261116-001/referee-R1')
from referee_pattern import Oracle, hid  # noqa: E402  (my own)
from referee_check_s5 import run as exhaustive  # noqa: E402  (my own)
from referee_forget import load_census  # noqa: E402  (my own)

ROOT = Path('/home/jscul/p-vs-np-contact-first')

if __name__ == '__main__':
    out_path, mode, n = sys.argv[1], sys.argv[2], int(sys.argv[3])
    a, b = (int(x) for x in sys.argv[4].split(':'))
    rows = json.load(open(ROOT / 'research/BLOCK-REACH-20261116-001/census_forget.json'))['rows']
    recs = load_census()
    rng = random.Random(77)
    if mode == 'bound':
        rul = sorted(c for c, v in rows.items() if v['name'] == 'ruler' and v['r_all'] == 1)
        cyc = [c for c in rul if rows[c]['cyclic']]
        acy = [c for c in rul if not rows[c]['cyclic']]
        half = sorted(c for c, v in rows.items() if v['name'] == 'half-rate')
        pick = rng.sample(acy, n // 2) + rng.sample(cyc, n - n // 2) + rng.sample(half, n)
    else:
        half = sorted(c for c, v in rows.items() if v['name'] == 'half-rate')
        pick = rng.sample(half, n)
    pick = pick[a:b]
    res, problems = {}, []
    t0 = time.time()
    for cid in pick:
        row, rec = rows[cid], recs[cid]
        t1 = time.time()
        if mode == 'bound':
            N = 11
            e = exhaustive(rec['key'], N=N, k=3, s=3, nsamp=256)
            ties = {int(k): v for k, v in e['ties_by_s'].items()}
            out = dict(name=row['name'], cyclic=row['cyclic'], r=row['r_all'], N=N, census_L9=[lv['L_N'] for lv in rec['levels']],
                       ties_by_s=e['ties_by_s'], three_bonds_s3=e['bonds_found'], uncovered=e['uncovered_by_samples'],
                       exact_checked=e['exact_checked'])
            cells = {}
            for s in (1, 2, 3):
                lower = 2 if ties.get(s) else (3 if s < 3 else (3 if e['bonds_found'] else 4))
                bound = 1 + math.ceil(s / row['r_all'])
                cells[s] = dict(exact_lower=lower, theorem_bound=bound, ok=lower >= bound,
                                census_L9=rec['levels'][s - 1]['L_N'])
                if lower < bound:
                    problems.append(dict(case=cid, s=s, lower=lower, bound=bound))
            out['cells'] = cells
        else:
            N = 12
            O = Oracle(rec['key'], N, seed=3)
            X = O.samples(96)
            cand = np.arange((1 << 4) - 1, (1 << 6) - 1)          # levels 4 and 5
            tie = {}
            for u in range(8):
                for v, sg in O.tie_partners(hid(u, 3), cand, X).items():
                    s = (v + 1).bit_length() - 1 - 3
                    tie[s] = tie.get(s, 0) + 1
            cells = {}
            for s in (1, 2):
                mem = [int(v) for v in rec['levels'][s - 1]['bond']]
                P = O.patterns(mem, np.zeros((0, O.nv), dtype=bool)) if len(mem) == 3 else None
                pairs_free = P is not None and all(len({((p >> i) & 1, (p >> j) & 1) for p in P}) == 4
                                                     for i, j in ((0, 1), (0, 2), (1, 2)))
                lv = sorted({(m + 1).bit_length() - 1 for m in mem})
                ok = (not tie.get(s)) and P is not None and len(P) < 8 and pairs_free and 3 in lv and 3 + s in lv
                cells[s] = dict(census_L9=rec['levels'][s - 1]['L_N'], bond=mem, bond_levels=lv, no_tie=not tie.get(s),
                                patterns=None if P is None else len(P), pairs_free=pairs_free, L_is_3=ok)
                if not ok:
                    problems.append(dict(case=cid, s=s, **cells[s]))
            O.close()
            out = dict(name=row['name'], r=row['r_all'], r0=row['r0'], N=N, cells=cells)
        out['seconds'] = time.time() - t1
        res[cid] = out
        print(cid[:12], mode, json.dumps(out['cells'])[:300], '%.0fs' % out['seconds'], flush=True)
        json.dump(dict(mode=mode, problems=problems, cases=res, seconds=time.time() - t0), open(out_path, 'w'), indent=0)
    print('done', len(res), 'problems', len(problems))
