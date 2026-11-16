"""Referee R1 (MARK-RATE-20261116-001), item 3: Theorem M's conclusion directly, by my SAT oracle, for newly passing cyclic rulers
(r = 2, census_marks no_skip True) at depth N (default 10).

  s = 2: exact ties from level 3 to level 5 (Theorem M: L >= 3); and an exhaustive search over every three-member set
         {x at level 3, y at level 5, z any other address} (a three-member bond would put L at 3, below the census value 4).
  s = 3: exact ties from level 3 to level 6, and an exhaustive search over every three-member set {x at 3, y at 6, z any}
         (Theorem M: L >= 4); then a RESTRICTED exhaustive search over four-member sets {x at 3, y at 6, z, w} with z, w in the band of
         levels 3..6 (a four-member bond would put L at 4, below the census value 5): sets seen with all 16 patterns in 1,024
         checked models are excluded; a set containing a tied pair or a constrained triple (exact) is not a bond; the rest get their
         unseen patterns by SAT.
Three-member searches reuse referee_check_s5.run (my own, DIRECT-REACH referee folder).
Usage: referee_no_skip_sat.py OUT.json N n first:last"""
import itertools
import json
import random
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path('/home/jscul/p-vs-np-contact-first')
sys.path.insert(0, str(ROOT / 'research/DIRECT-REACH-20261115-001/referee-R1'))
sys.path.insert(0, str(ROOT / 'research/BLOCK-REACH-20261116-001/referee-R1'))
from referee_pattern import Oracle, hid  # noqa: E402
from referee_check_s5 import run as three_search  # noqa: E402
from referee_forget import load_census  # noqa: E402


def four_band(key, N, nsamp=512):
    O = Oracle(key, N, seed=41)
    X = O.samples(nsamp)
    band = [h for h in range(7, 127)]                    # levels 3..6 (heap ids 7..126)
    top = list(range(7, 15))
    deep = list(range(63, 127))
    bi = {h: i for i, h in enumerate(band)}
    Xb = X[:, band]
    # exact status of pairs and triples inside the band, filtered by the models
    pair_tied = {}

    def tied(a, b):
        a, b = min(a, b), max(a, b)
        if (a, b) not in pair_tied:
            col = X[:, a] ^ X[:, b]
            if col.min() != col.max():
                pair_tied[(a, b)] = False
            else:
                lit = -(b + 1) if col[0] else (b + 1)
                pair_tied[(a, b)] = O.solve([-(a + 1), lit]) is None
        return pair_tied[(a, b)]
    tri_con = {}

    def tri_constrained(tri):
        tri = tuple(sorted(tri))
        if tri not in tri_con:
            cols = Xb[:, [bi[h] for h in tri]].astype(np.int64)
            seen = set((cols @ np.array([1, 2, 4])).tolist())
            tri_con[tri] = len(seen) < 8 and len(O.patterns(list(tri), X)) < 8
        return tri_con[tri]
    Pb = np.packbits(Xb, axis=0).T.copy()            # (band, S/8): bit-packed values of each band variable over the models
    Pn = np.packbits(~Xb, axis=0).T.copy()
    n_sets = n_uncov = n_exact = 0
    bonds = []
    for x in top:
        for y in deep:
            mxy = [(Pb[bi[x]] if a_ else Pn[bi[x]]) & (Pb[bi[y]] if b_ else Pn[bi[y]]) for a_ in (0, 1) for b_ in (0, 1)]
            rest = [h for h in band if h not in (x, y)]
            ridx = np.array([bi[h] for h in rest])
            Rb, Rn = Pb[ridx], Pn[ridx]
            for i in range(len(rest)):
                masks = np.array([m & Rb[i] for m in mxy] + [m & Rn[i] for m in mxy])      # (8, S/8): patterns on x, y, z
                hit1 = np.any((masks[:, None, :] & Rb[None, i + 1:, :]) != 0, axis=2)     # (8, remaining)
                hit0 = np.any((masks[:, None, :] & Rn[None, i + 1:, :]) != 0, axis=2)
                cov = hit1.sum(axis=0) + hit0.sum(axis=0)
                n_sets += len(cov)
                for j in np.nonzero(cov < 16)[0]:
                    z, w = rest[i], rest[i + 1 + j]
                    n_uncov += 1
                    quad = (x, y, z, w)
                    if any(tied(a_, b_) for a_, b_ in itertools.combinations(quad, 2)):
                        continue
                    if any(tri_constrained(t) for t in itertools.combinations(quad, 3)):
                        continue
                    n_exact += 1
                    P = O.patterns(list(quad), X)
                    if len(P) < 16:
                        bonds.append([x, y, z, w, sorted(P)])
    O.close()
    return dict(band='levels 3..6', sets=n_sets, uncovered=n_uncov, exact_checked=n_exact, bonds_found=len(bonds),
                bond_examples=bonds[:5], sat_calls=O.calls)


if __name__ == '__main__':
    out_path, N, n = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
    a, b = (int(x) for x in sys.argv[4].split(':'))
    rows = json.load(open(ROOT / 'research/MARK-RATE-20261116-001/census_marks.json'))['rows']
    recs = load_census()
    new = sorted(c for c, v in rows.items() if v['name'] == 'ruler' and v['cyclic'] and v['r'] == 2 and v['no_skip'] is True)
    pick = random.Random(333).sample(new, n)[a:b]
    res, problems = {}, []
    t0 = time.time()
    for cid in pick:
        t1 = time.time()
        key = recs[cid]['key']
        s2 = three_search(key, N=N, k=3, s=2, nsamp=256)
        s3 = three_search(key, N=N, k=3, s=3, nsamp=256)
        f4 = four_band(key, N)
        ties = {int(k) for k in s3['ties_by_s']}
        out = dict(census_L9=[lv['L_N'] for lv in recs[cid]['levels']], ties_by_s=s3['ties_by_s'],
                   s2=dict(tie=2 in ties, three_bonds=s2['bonds_found'], uncovered=s2['uncovered_by_samples'],
                           exact=s2['exact_checked']),
                   s3=dict(tie=3 in ties, three_bonds=s3['bonds_found'], uncovered=s3['uncovered_by_samples'],
                           exact=s3['exact_checked'], four_band=f4))
        out['theorem_M_holds'] = (2 not in ties) and (3 not in ties) and s3['bonds_found'] == 0
        out['census_values_hold'] = out['theorem_M_holds'] and s2['bonds_found'] == 0 and f4['bonds_found'] == 0
        if not out['theorem_M_holds']:
            problems.append(cid)
        out['seconds'] = time.time() - t1
        res[cid] = out
        print(cid[:12], 'M holds', out['theorem_M_holds'], 's2 3-bonds', s2['bonds_found'], 's3 3-bonds', s3['bonds_found'],
              '4-band', f4['bonds_found'], f4['sets'], f4['uncovered'], f4['exact_checked'], '%.0fs' % out['seconds'], flush=True)
        json.dump(dict(N=N, problems=problems, cases=res, seconds=time.time() - t0), open(out_path, 'w'), indent=0)
    print('done', len(res), 'problems', len(problems))
