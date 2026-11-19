"""Shared-runner job: R1 of PARENT-RULE-20261119-001, rigidity of the reached meet-once tables.  The stages are the referee's own
meet-once grown census stages of up to 14 junctions (runs/referee-grown-meetonce, from GROWN-PAIR-R1's job_meetonce.py).  For each
open one (with a loose distinction): the exact table (the referee's shore enumeration); every symmetry of the table is a lift of a
map of its twin classes composed with a permutation inside the classes, so the states are kept by every symmetry exactly when they
are kept by every lift (the referee's 001F quotient maps) and by every swap of two neighbours inside a twin class.  Each such map is
tested by rank: the stars' images span the stars' space.

  .venv/bin/python -B scripts/longrun.py launch research/PARENT-RULE-20261119-001/referee-R1/job_rigid.py \\
      --out runs/referee-parent-rigid --unit referee-parent-rigid --workers 6 --case-timeout 1800 --case-mem 2G --mem-max 16G
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
for p in ("research/VARIABLE-OUTPUT-READER-20261118-001F/referee-R1", "research/CENSUS-READ-20261118-001/referee-R1"):
    sys.path.insert(0, str(ROOT / p))
STAGES = []


def setup(params):
    for line in open(ROOT / "runs/referee-grown-meetonce/results.jsonl"):
        STAGES.extend(json.loads(line)["result"]["stages"])


def cases():
    for a in range(0, len(STAGES), 50):
        yield f"R-{a // 50:03d}", {"stages": STAGES[a:a + 50]}


def span(words):
    basis = {}
    for r in words:
        while r:
            p = r.bit_length() - 1
            if p not in basis:
                basis[p] = r
                break
            r ^= basis[p]
    return basis


def keeps(stars, perm, basis):
    for s in stars:
        r = sum(1 << perm[x] for x in s)
        while r:
            p = r.bit_length() - 1
            if p not in basis:
                return False
            r ^= basis[p]
    return True


def run(case_id, p):
    import referee_census as RC
    import referee_f as F
    out = []
    for st in p["stages"]:
        stars = st["stars"]
        held = {}
        for s in stars:
            for b in s:
                held[b] = held.get(b, 0) + 1
        if not any(v == 1 for v in held.values()):
            out.append({"index": st["index"], "round": st["round"], "open": False})
            continue
        K, labels = RC.shore_table(stars)
        n = len(labels)
        basis = span([sum(1 << x for x in s) for s in stars])
        q = F.quotient(K)
        maps = F.quotient_maps(q, q, first_only=False)
        capped = maps is None or len(maps) >= 200000
        rigid = True
        for g in (maps or []):
            if not keeps(stars, F.lift(q, q, g), basis):
                rigid = False
                break
        if rigid:
            for c in q[0]:
                for a, b in zip(c, c[1:]):
                    perm = list(range(n))
                    perm[a], perm[b] = b, a
                    if not keeps(stars, perm, basis):
                        rigid = False
                        break
                if not rigid:
                    break
        out.append({"index": st["index"], "round": st["round"], "open": True, "junctions": len(stars), "rigid": rigid,
                    "symmetries of the twin quotient": len(maps or []), "capped": capped})
    return {"stages": out}
