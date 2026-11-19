"""Shared-runner job for the referee's check of TRIPLE-GROWN-20261119-001 (own arrangements, own bonds, own pair and three-way
readings, an exact search; no study code imported or run).

Pairs:
- static: the 1,034 pairs in different state groups of PARENT-RULE-R1's own grouping of the 503,039 legal meet-once arrangements
  (runs/referee-parent-groups), each rebuilt from its atlas graph and loose counts;
- reached: GROW-SMALL's 87 pairs (their starts and rounds read from origin.json as data), regrown by the referee's engine with the
  program's rule, the created pair included.
For each arrangement: every bond (UNIQUE-TABLE-R1's closed-aware enumeration over junction sets), the pair readings (least bond
holding both) and three-way readings (least bond holding all three, or none), all exact; the rank of the span of the bonds of three
distinctions against the rank of the equations.  For each pair: whether some renaming keeps both readings (THREE-WAY-R1's exact
search), and whether the counts of triples per reading already differ.

  .venv/bin/python -B scripts/longrun.py launch research/TRIPLE-GROWN-20261119-001/referee-R1/job_triple.py \\
      --out runs/referee-triple --unit referee-triple --workers 4 --case-timeout 3600 --case-mem 3G --mem-max 16G
"""
import json
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
for p in ("research/THREE-WAY-20261119-001/referee-R1", "research/UNIQUE-TABLE-20261119-001/referee-R1",
          "research/PARENT-RULE-20261119-001/referee-R1", "research/GROW-SMALL-20261119-001/referee-R1",
          "research/FIRST-KNOT-20261118-001/referee-R1"):
    sys.path.insert(0, str(ROOT / p))
ORIGIN = ROOT / "artifacts/GROW-SMALL-20261119-001A/GROW-SMALL-20261119-001A-E001_grow/origin.json"


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


def readings(stars):
    import referee_three as R3
    S, nb = R3.relabel(stars)
    bonds, K, T = R3.readings(S, nb)
    eq = rank([sum(1 << x for x in s) for s in S])
    r3 = rank([w for w in bonds if w.bit_count() == 3])
    return S, nb, K, T, eq, r3


def compare(A, B):
    import referee_three as R3
    SA, na, KA, TA, eqa, r3a = readings(A)
    SB, nb_, KB, TB, eqb, r3b = readings(B)
    out = {"junctions": [len(SA), len(SB)], "distinctions": [na, nb_], "equations rank": [eqa, eqb],
           "three-distinction bonds rank": [r3a, r3b]}
    if na != nb_:
        out["separated"] = True
        return out
    out["a renaming keeps pairs"] = R3.iso_both(KA, KB, {t: 0 for t in TA}, {t: 0 for t in TB}, na)
    out["a renaming keeps pairs and triples"] = R3.iso_both(KA, KB, TA, TB, na)
    out["counts of triples per reading differ"] = Counter(TA.values()) != Counter(TB.values())
    return out


def static_pairs():
    pairs = []
    for line in open(ROOT / "runs/referee-parent-groups/results.jsonl"):
        r = json.loads(line)
        for g in r["result"]["other-states groups"]:
            sg = g["state groups"]
            for x in range(len(sg)):
                for y in range(x + 1, len(sg)):
                    for a in sg[x]:
                        for b in sg[y]:
                            pairs.append([a, b])
    return pairs


def cases():
    st = static_pairs()
    for a in range(0, len(st), 60):
        yield f"S-{a // 60:03d}", {"part": "S", "pairs": st[a:a + 60]}
    reached = json.load(open(ORIGIN))["pairs"]
    for i, p in enumerate(reached):
        yield f"R-{i:03d}", {"part": "R", "pair": p}


def floored(G, info, rng):
    return [i["d"] if i["implied"] else max(i["d"], 3 - i["p"], 1) for i in info]


def run(case_id, p):
    from job_parent_groups import stars_of
    if p["part"] == "S":
        out = []
        for a, b in p["pairs"]:
            A, B = stars_of(a[1], a[2]), stars_of(b[1], b[2])
            out.append({"members": [a, b], **compare(A, B)})
        return {"rows": out}
    import referee_first as RFK
    q = p["pair"]
    stages = []
    for _, gi, ell, rnd in q["starts"]:
        G = RFK.Start([list(s) for s in stars_of(gi, ell)])
        for _ in range(rnd):
            G.step(floored, None, None)
        stages.append([sorted(b) for b in G.bits])
    return {"rows": [{"kind": q["kind"], "starts": q["starts"], **compare(stages[0], stages[1])}]}
