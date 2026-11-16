"""Referee R1 (BLOCK-REACH-20261116-001), item 3: Lemma U by SAT at depths 9, 12 and 13.

For 40 small-orbit census descriptions (all r0 = 1 ones with a bond, the rest drawn with a fixed seed across census names), and each
census depth-9 least bond counted as an upper bound at every depth (census_forget.json's upper_every_depth; the bond itself is the
census record's levels[s-1]['bond'], as run_census.py reads it), the projection of P_N onto the bond's members (my builder, every
assignment decided by SAT; complement symmetry used for half of them) at N = 9, 12 and 13; equal projections, and the set a bond
(constrained, every proper subset free) at each depth. Also: every member at level <= 9 - r0, as the lemma needs.
Usage: referee_lemmaU.py OUT.json n_descriptions [first:last slice of the sample]"""
import json
import random
import sys
import time
from pathlib import Path

sys.path.insert(0, '/home/jscul/p-vs-np-contact-first/research/DIRECT-REACH-20261115-001/referee-R1')
sys.path.insert(0, '/home/jscul/p-vs-np-contact-first/research/BLOCK-REACH-20261116-001/referee-R1')
from referee_pattern import Oracle  # noqa: E402  (my own)
from referee_forget import load_census  # noqa: E402  (my own)

ROOT = Path('/home/jscul/p-vs-np-contact-first')
DEPTHS = (9, 12, 13)


def level(h):
    return (h + 1).bit_length() - 1


def projection(O, members):
    b = len(members)
    full = (1 << b) - 1
    out = set()
    for p in range(0, 1 << b, 2):                 # first member = 0; the complement (NAE symmetry) gives the rest
        ass = [(m + 1) if (p >> i) & 1 else -(m + 1) for i, m in enumerate(members)]
        if O.solve(ass) is not None:
            out.add(p)
            out.add(p ^ full)
    return frozenset(out)


def is_bond(P, b):
    if len(P) == 1 << b:
        return False
    for drop in range(b):
        sub = {tuple((p >> i) & 1 for i in range(b) if i != drop) for p in P}
        if len(sub) < 1 << (b - 1):
            return False
    return True


if __name__ == '__main__':
    out_path, nd = sys.argv[1], int(sys.argv[2])
    sl = sys.argv[3] if len(sys.argv) > 3 else None
    rows = json.load(open(ROOT / 'research/BLOCK-REACH-20261116-001/census_forget.json'))['rows']
    recs = load_census()
    withb = sorted(c for c, v in rows.items() if v['upper_every_depth'])
    r01 = [c for c in withb if rows[c]['r0'] == 1]
    rest = [c for c in withb if c not in r01]
    rng = random.Random(4013)
    by = {}
    for c in rest:
        by.setdefault(rows[c]['name'], []).append(c)
    pick = list(r01)
    names = sorted(by)
    while len(pick) < nd:
        for nm in names:
            left = [c for c in by[nm] if c not in pick]
            if left and len(pick) < nd:
                pick.append(rng.choice(left))
    if sl:
        a, b = (int(x) for x in sl.split(':'))
        pick = pick[a:b]
    res, bad = {}, []
    t0 = time.time()
    for cid in pick:
        rec, row = recs[cid], rows[cid]
        bonds = {}
        for lv in rec['levels']:
            if str(lv['s']) in row['upper_every_depth'] or lv['s'] in row['upper_every_depth']:
                bonds[lv['s']] = [int(v) for v in lv['bond']]
        P = {}
        for N in DEPTHS:
            O = Oracle(rec['key'], N)
            assert O.alive()
            for s, mem in bonds.items():
                P[(s, N)] = projection(O, mem)
            O.close()
        out = {}
        for s, mem in bonds.items():
            eq = P[(s, 9)] == P[(s, 12)] == P[(s, 13)]
            bond = {N: is_bond(P[(s, N)], len(mem)) for N in DEPTHS}
            within = max(level(m) for m in mem) <= 9 - row['r0']
            out[s] = dict(members=mem, size=len(mem), census_L9=rec['levels'][s - 1]['L_N'], patterns={N: len(P[(s, N)]) for N in DEPTHS},
                          equal=eq, bond=bond, within_9_minus_r0=within, max_level=max(level(m) for m in mem))
            if not (eq and all(bond.values()) and within and len(mem) == rec['levels'][s - 1]['L_N']):
                bad.append(dict(case=cid, s=s, **out[s]))
        res[cid] = dict(name=row['name'], r0=row['r0'], bonds=out)
        print(cid[:12], row['name'], 'r0', row['r0'], {s: (v['size'], v['equal'], all(v['bond'].values())) for s, v in out.items()},
              '%.0fs' % (time.time() - t0), flush=True)
        json.dump(dict(depths=DEPTHS, problems=bad, cases=res, seconds=time.time() - t0), open(out_path, 'w'), indent=0)
    print('done', len(res), 'descriptions', sum(len(v['bonds']) for v in res.values()), 'bonds; problems', len(bad))
