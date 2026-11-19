"""Shared-runner job for the referee's check of HUNT-SHORTEN-20261119-001 part 3, the self-pairs test of Claim B (own growth, own
full tables, own isometry enumeration, own reading test and extension; the touch census's arrangements read from
runs/touch-census as data; no study code imported or run).

Every census start regrown by the referee's FIRST-KNOT-R1 engine with the program's rule, to round 14.  For every open stage (some
junction holds a loose distinction) of round 1 or later with at most 14 junctions:
- its full table (CENSUS-READ-R1's shore enumeration, exact) and every isometry of the table onto itself, enumerated with no twin
  quotient and no cap of 20: one representative per coset of the holder-class permutations (within each holder class the images
  increase), so that isometries breaking holder classes are included.  Permuting distinctions of one holder class carries the
  equations, keeps the reading and leaves the extension's verdict unchanged (loose ones are re-paired by the extension; shared ones
  stay twins in the next stage), so one representative per coset decides the coset;
- those that carry the equation space are counted and skipped (Claim B* covers them);
- for the others: whether they keep the reading R (EXTEND-ROUND-R1's test: loose onto loose, live stars onto live stars, F onto F);
- every R-keeping one is extended through the stage's own next round (EXTEND-ROUND-R1's extension) and checked entry by entry on
  the next full table (GROW-SMALL-R1's full_table: shore enumeration to 22 junctions, else flow-bounded bonds until every pair of
  one block is reached).
Recorded per stage: its round, junctions, whether two junctions share two distinctions, whether a holder-breaking isometry exists.

  .venv/bin/python -B scripts/longrun.py launch research/HUNT-SHORTEN-20261119-001/referee-R1/job_selfpairs.py \\
      --out runs/referee-selfpairs --unit referee-selfpairs --workers 4 --case-timeout 7200 --case-mem 3G --mem-max 16G
"""
import itertools
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
for p in ("research/EXTEND-ROUND-20261119-001/referee-R1", "research/CREATED-PAIR-20261119-001/referee-R1",
          "research/GROW-SMALL-20261119-001/referee-R1", "research/VARIABLE-OUTPUT-READER-20261118-001F/referee-R1",
          "research/FIRST-KNOT-20261118-001/referee-R1", "research/CENSUS-READ-20261118-001/referee-R1",
          "research/GROWN-PAIR-20261119-001/referee-R1", "research/MEET-ONCE-20261119-001/referee-R1",
          "research/PARENT-RULE-20261119-001/referee-R1", "research/RING-IDENT-20261119-001/referee-R1"):
    sys.path.insert(0, str(ROOT / p))
FULL = 14
RMAX = 14
CAP = 200_000
PARAMS = {}


def setup(params):
    PARAMS.update(params)


def floored(G, info, rng):
    return [i["d"] if i["implied"] else max(i["d"], 3 - i["p"], 1) for i in info]


def rank(words):
    basis = {}
    for r in words:
        while r:
            p = r.bit_length() - 1
            if p not in basis:
                basis[p] = r
                break
            r ^= basis[p]
    return len(basis)


def reps(K, cls, cap=CAP):
    """One isometry of K onto itself per coset of the holder-class permutations: images increase inside each class."""
    import job_created as JC
    n = len(K)
    col = JC.colours([K, K])
    ca = col[0]
    vals = sorted({int(v) for v in K.flatten()})
    mask = {v: [sum(1 << w for w in range(n) if int(K[w][y]) == v) for y in range(n)] for v in vals}
    cand0 = [sum(1 << y for y in range(n) if ca[y] == ca[x]) for x in range(n)]
    members = defaultdict(list)
    for x in range(n):
        members[cls[x]].append(x)
    phi = [-1] * n
    out = []
    capped = [False]

    def rec(cand, used, todo):
        if len(out) >= cap:
            capped[0] = True
            return
        if not todo:
            out.append(list(phi))
            return
        x = min(todo, key=lambda z: (cand[z] & ~used).bit_count())
        m = cand[x] & ~used
        # order inside the holder class
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
            rec(nc, used | low, rest)
            phi[x] = -1
    rec(cand0, 0, list(range(n)))
    return out, capped[0]


def stages(start):
    """(round, stage, next, new junctions) for every round of the referee's growth, labels kept from the engine."""
    import referee_first as RFK
    G = RFK.Start([list(s) for s in start])
    out = []
    for r in range(RMAX):
        stage = [sorted(b) for b in G.bits]
        if len(stage) > FULL:
            break
        nj = len(stage)
        res = G.step(floored, None, None)
        if res != "ok":
            break
        nxt = [sorted(b) for b in G.bits]
        new = [{"j": j, "parents": sorted(G.parents[j]), "fresh": G.fresh[j]} for j in range(nj, len(nxt))]
        out.append((r, stage, nxt, new))
    return out


def test_stage(stage, nxt, new):
    import job_extend as JE
    import job_growsmall as GS
    S, N, old = JE.relabel_pair(stage, nxt)
    own = JE.owners(S)
    K, _, _, _ = GS.full_table([sorted(s) for s in S])
    lo_ = sorted(old)
    holders = {x: tuple(sorted(own[lo_[i]])) for i, x in enumerate(range(len(lo_)))}
    cls = [holders[i] for i in range(len(lo_))]
    out = Counter()
    rs, capped = reps(K, cls)
    out["coset representatives"] = len(rs)
    out["capped"] = capped
    R = JE.reading(S)
    A = {"S": S, "N": N, "old": old, "new": new, "own": own}
    rows = [sum(1 << x for x in s) for s in S]
    rk = rank(rows)
    hclass = defaultdict(set)
    for i in range(len(lo_)):
        hclass[cls[i]].add(i)
    KN = None
    for phi0 in rs:
        phi = {lo_[x]: lo_[y] for x, y in enumerate(phi0)}
        breaks = any({phi0[i] for i in mem} != hclass[cls[phi0[min(mem)]]] for mem in hclass.values())
        out["holder-breaking"] += breaks
        img = [sum(1 << phi[x] for x in s) for s in S]
        if rank(rows + img) == rk:
            out["carry the equations"] += 1
            continue
        out["do not carry the equations"] += 1
        psi, whole, top = JE.keeps(phi, S, S, R, R)
        if psi is None or not top:
            continue
        out["keep R, not the equations"] += 1
        out["keep R, not the equations, holder-breaking"] += breaks
        phi2 = JE.extend(phi, psi, A, A)
        if phi2 is None:
            out["rounds do not correspond"] += 1
            continue
        if KN is None:
            KN, _, _, how = GS.full_table(N)
            out["next table by " + how.split(" (")[0]] += 1
        n1 = len(KN)
        ok = all(KN[x][y] == KN[phi2[x]][phi2[y]] for x in range(n1) for y in range(x + 1, n1))
        out["extensions that are isometries"] += ok
        out["extensions that fail (a Claim B counterexample)"] += not ok
    return out


def census():
    rows = []
    for line in open(ROOT / "runs/touch-census/results.jsonl"):
        r = json.loads(line)
        if r.get("status") == "ok":
            rows += [a["key"] for a in r["result"]["arrangements"]]
    rows.sort(key=str)
    return rows


def cases():
    only = set(PARAMS["only"].split(",")) if PARAMS.get("only") else None
    rows = census()
    for a in range(0, len(rows), 100):
        cid = f"C-{a // 100:04d}"
        if only is None or cid in only:
            yield cid, {"keys": rows[a:a + 100]}


def run(case_id, p):
    import job_ring as JR
    tot = Counter()
    fails = []
    per_stage = []
    for key in p["keys"]:
        sizes, flat = key
        n = len(sizes)
        edges = []
        for (i, j), m in zip(itertools.combinations(range(n), 2), flat):
            edges += [(i, j)] * m
        tot["starts"] += 1
        for r, stage, nxt, new in stages(JR.stars_of(n, edges, list(sizes))):
            own = defaultdict(list)
            for j, s in enumerate(stage):
                for x in s:
                    own[x].append(j)
            if r < 1 or not any(len(v) == 1 for v in own.values()):
                continue
            two = max(Counter(tuple(v) for v in own.values() if len(v) == 2).values(), default=0) >= 2
            c = test_stage(stage, nxt, new)
            band = "rounds 1-7" if r <= 7 else "rounds 8+"
            tot[f"open stages, {band}"] += 1
            tot[f"open stages, {band}, two junctions sharing two"] += two
            for k, v in c.items():
                tot[f"{band}: {k}"] += v
            tot[f"{band}: stages with an R-keeping isometry not carrying the equations"] += c["keep R, not the equations"] > 0
            if c["extensions that fail (a Claim B counterexample)"]:
                fails.append({"key": key, "round": r, "stage": stage})
            if c["keep R, not the equations"]:
                per_stage.append([str(key), r, len(stage), c["keep R, not the equations"], c["extensions that are isometries"],
                                  c["keep R, not the equations, holder-breaking"], c["capped"]])
    return {"counts": dict(tot), "failures": fails, "stages with R-keeping isometries": per_stage}
