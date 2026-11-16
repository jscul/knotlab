"""Referee R1 (BLOCK-REACH-20261116-001), item 1: my own forgetting length, from Theorem F's statement, on my own block DP
(research/DIRECT-REACH-20261115-001/referee-R1/referee_blocks.py, written for the DIRECT-REACH referee; no study code).

Block step (proof.md, "Block step"): orbit O of type t, child orbit ci, remaining depth rho (levels below the child): the pairs
(x on O, z on the child) such that the block of O is completed with every knot placed at O holding and every OTHER child orbit's
assignment in F_rho; the path child is not restricted by its own subtree. x ranges over all assignments of O.
A window: r consecutive steps along any path of types, the first at remaining depth rho, then rho - 1, ..., rho - r + 1 >= 0.
r_all: least r with every window at every remaining depth rectangular (or empty). r_stable: the same at stable depth only (all
steps with F_{r0}), by a closure over the set of (end type, composed relation) that stops at the first repeat ("never").
Usage: referee_forget.py OUT.json [n_random]"""
import gzip
import json
import math
import random
import sys
import time
from pathlib import Path

sys.path.insert(0, '/home/jscul/p-vs-np-contact-first/research/DIRECT-REACH-20261115-001/referee-R1')
from referee_blocks import Blocks  # noqa: E402  (my own)

ROOT = Path('/home/jscul/p-vs-np-contact-first')
HERE = ROOT / 'research/BLOCK-REACH-20261116-001/referee-R1'
CENSUS = ROOT / 'artifacts/LEVEL-REACH-20261114-001A/LEVEL-REACH-20261114-001A-E001_level_reach/records_slim.jsonl.gz'


def compose(R, S):
    nxt = {}
    for a, b in S:
        nxt.setdefault(a, []).append(b)
    return frozenset((a, c) for a, b in R for c in nxt.get(b, ()))


def is_rect(R):
    if not R:
        return True
    A = {a for a, _ in R}
    Z = {z for _, z in R}
    return len(R) == len(A) * len(Z)


class Forget:
    def __init__(self, key):
        self.B = B = Blocks(key)
        self.r0, F = B.r0()
        self.F = F
        self._steps = {}

    def step(self, t, ci, rho):
        rho = min(rho, self.r0)
        k = (t, ci, rho)
        if k not in self._steps:
            B = self.B
            S = B.down(t, ci, self.F[rho], frozenset((x, x) for x in range(1 << B.m[t])))
            self._steps[k] = (B.kids[t][ci][0], S)
        return self._steps[k]

    def windows(self, r, rho):
        """The set of (end type, composed relation) over every start type and path of r steps from remaining depth rho."""
        B = self.B
        W = {self.step(t, ci, rho) for t in range(len(B.types)) for ci in range(len(B.kids[t]))}
        for i in range(1, r):
            W = {(c2, compose(R, S)) for c, R in W for ci in range(len(B.kids[c])) for c2, S in [self.step(c, ci, rho - i)]}
        return W

    def r_all(self, rmax=10):
        for r in range(1, rmax + 1):
            if all(is_rect(R) for rho in range(r - 1, self.r0 + r) for _, R in self.windows(r, rho)):
                return r
        return 'none<=%d' % rmax

    def r_stable(self, cap=400):
        B = self.B
        rho = self.r0
        W = frozenset(self.step(t, ci, rho) for t in range(len(B.types)) for ci in range(len(B.kids[t])))
        seen = set()
        for r in range(1, cap + 1):
            if all(is_rect(R) for _, R in W):
                return r
            if W in seen:
                return None
            seen.add(W)
            W = frozenset((c2, compose(R, S)) for c, R in W for ci in range(len(B.kids[c])) for c2, S in [self.step(c, ci, rho)])
        raise RuntimeError('no repeat')


def load_census():
    recs = {}
    for line in gzip.open(CENSUS, 'rt'):
        r = json.loads(line)
        recs[r['case']] = r
    return recs


if __name__ == '__main__':
    out_path = sys.argv[1]
    nrand = int(sys.argv[2]) if len(sys.argv) > 2 else 120
    rows = json.load(open(ROOT / 'research/BLOCK-REACH-20261116-001/census_forget.json'))['rows']
    recs = load_census()
    r01 = sorted(c for c, v in rows.items() if v['r0'] == 1)
    never = sorted(c for c, v in rows.items() if v['r_stable'] is None)
    rest = sorted(c for c in rows if c not in set(r01) | set(never))
    rng = random.Random(20261116)
    # stratified random sample over the census names of the rest
    by = {}
    for c in rest:
        by.setdefault(rows[c]['name'], []).append(c)
    pick = []
    tot = len(rest)
    for name, cs in sorted(by.items()):
        n = max(3, round(nrand * len(cs) / tot))
        pick += rng.sample(cs, min(n, len(cs)))
    todo = [(c, 'r0=1') for c in r01] + [(c, 'never') for c in never] + [(c, 'random') for c in pick]
    res, mism, below = {}, [], []
    t0 = time.time()
    for cid, why in todo:
        t1 = time.time()
        f = Forget(recs[cid]['key'])
        rs = f.r_stable()
        ra = f.r_all() if rs is not None else None
        cen = rows[cid]
        ok = (rs == cen['r_stable']) and (ra == cen['r_all']) and (f.r0 == cen['r0'])
        if not ok:
            mism.append(dict(case=cid, why=why, mine=dict(r_stable=rs, r_all=ra, r0=f.r0),
                             study=dict(r_stable=cen['r_stable'], r_all=cen['r_all'], r0=cen['r0'])))
        # the bound against the census's decided depth-9 values (my r)
        if isinstance(ra, int):
            for lv in recs[cid]['levels']:
                if isinstance(lv['L_N'], int) and lv['L_N'] < 1 + math.ceil(lv['s'] / ra):
                    below.append(dict(case=cid, s=lv['s'], L9=lv['L_N'], r=ra))
        res[cid] = dict(why=why, name=cen['name'], types=len(f.B.types), r0=f.r0, r_stable=rs, r_all=ra,
                        study_r_stable=cen['r_stable'], study_r_all=cen['r_all'], seconds=time.time() - t1)
        print(cid[:12], why, cen['name'], 'mine', rs, ra, f.r0, 'study', cen['r_stable'], cen['r_all'], cen['r0'],
              'OK' if ok else 'DIFF', '%.1fs' % (time.time() - t1), flush=True)
        json.dump(dict(mismatches=mism, census_values_below_bound=below, cases=res, seconds=time.time() - t0),
                  open(out_path, 'w'), indent=0)
    print('done', len(res), 'mismatches', len(mism), 'below bound', len(below), '%.0fs' % (time.time() - t0))
