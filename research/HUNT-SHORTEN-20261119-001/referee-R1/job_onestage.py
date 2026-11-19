"""Shared-runner job: the one census stage where job_selfpairs.py hit its cap of 200,000 coset representatives (start
[[4, 4, 4, 4, 4], [0, 0, 1, 2, 2, 0, 2, 2, 0, 0]], the stage of round 2, 11 junctions), finished with the representatives streamed
rather than stored, and no cap.  Same tests as job_selfpairs.test_stage.

  .venv/bin/python -B scripts/longrun.py launch research/HUNT-SHORTEN-20261119-001/referee-R1/job_onestage.py \\
      --out runs/referee-onestage --unit referee-onestage --workers 1 --case-timeout 14400 --case-mem 6G --mem-max 8G
"""
import itertools
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import job_selfpairs as SP  # noqa: E402  (the referee's own; sets the paths)

KEY = [[4, 4, 4, 4, 4], [0, 0, 1, 2, 2, 0, 2, 2, 0, 0]]
ROUND = 2


def stream(K, cls):
    import job_created as JC
    n = len(K)
    ca = JC.colours([K, K])[0]
    vals = sorted({int(v) for v in K.flatten()})
    mask = {v: [sum(1 << w for w in range(n) if int(K[w][y]) == v) for y in range(n)] for v in vals}
    cand0 = [sum(1 << y for y in range(n) if ca[y] == ca[x]) for x in range(n)]
    members = defaultdict(list)
    for x in range(n):
        members[cls[x]].append(x)
    phi = [-1] * n

    def rec(cand, used, todo):
        if not todo:
            yield list(phi)
            return
        x = min(todo, key=lambda z: (cand[z] & ~used).bit_count())
        m = cand[x] & ~used
        lo, hi = -1, n
        for z in members[cls[x]]:
            if phi[z] >= 0:
                if z < x:
                    lo = max(lo, phi[z])
                else:
                    hi = min(hi, phi[z])
        rest = [z for z in todo if z != x]
        while m:
            low = m & -m
            y = low.bit_length() - 1
            m ^= low
            if not lo < y < hi:
                continue
            nc = cand[:]
            ok = True
            for z in rest:
                nc[z] &= mask[int(K[z][x])][y]
                if not nc[z] & ~(used | low):
                    ok = False
                    break
            if not ok:
                continue
            phi[x] = y
            yield from rec(nc, used | low, rest)
            phi[x] = -1
    yield from rec(cand0, 0, list(range(n)))


def cases():
    yield "S-0", {}


def run(case_id, p):
    import job_extend as JE
    import job_growsmall as GS
    import job_ring as JR
    sizes, flat = KEY
    n = len(sizes)
    edges = []
    for (i, j), m in zip(itertools.combinations(range(n), 2), flat):
        edges += [(i, j)] * m
    st = [x for x in SP.stages(JR.stars_of(n, edges, list(sizes))) if x[0] == ROUND][0]
    _, stage, nxt, new = st
    S, N, old = JE.relabel_pair(stage, nxt)
    own = JE.owners(S)
    K, _, _, _ = GS.full_table([sorted(s) for s in S])
    lo_ = sorted(old)
    cls = [tuple(sorted(own[lo_[i]])) for i in range(len(lo_))]
    R = JE.reading(S)
    A = {"S": S, "N": N, "old": old, "new": new, "own": own}
    rows = [sum(1 << x for x in s) for s in S]
    rk = SP.rank(rows)
    KN = GS.full_table(N)[0]
    n1 = len(KN)
    out = Counter()
    hclass = defaultdict(set)
    for i in range(len(lo_)):
        hclass[cls[i]].add(i)
    for phi0 in stream(K, cls):
        out["coset representatives"] += 1
        phi = {lo_[x]: lo_[y] for x, y in enumerate(phi0)}
        img = [sum(1 << phi[x] for x in s) for s in S]
        if SP.rank(rows + img) == rk:
            out["carry the equations"] += 1
            continue
        psi, whole, top = JE.keeps(phi, S, S, R, R)
        if psi is None or not top:
            out["do not keep R"] += 1
            continue
        out["keep R, not the equations"] += 1
        out["keep R, not the equations, holder-breaking"] += any(
            {phi0[i] for i in mem} != hclass[cls[phi0[min(mem)]]] for mem in hclass.values())
        phi2 = JE.extend(phi, psi, A, A)
        if phi2 is None:
            out["rounds do not correspond"] += 1
            continue
        ok = all(KN[x][y] == KN[phi2[x]][phi2[y]] for x in range(n1) for y in range(x + 1, n1))
        out["extensions that are isometries" if ok else "extensions that fail (a Claim B counterexample)"] += 1
    out["junctions"] = len(S)
    out["distinctions"] = len(lo_)
    return dict(out)
