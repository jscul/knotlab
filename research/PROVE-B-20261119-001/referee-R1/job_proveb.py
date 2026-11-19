"""Shared-runner job for the referee's check of PROVE-B-20261119-001, with the referee's own code: its FIRST-KNOT-R1 engine with the
program's rule, its tables, its HUNT-SHORTEN-R1 coset-representative search and stage test, and its THREE-WAY-R1 readings (the
least bond holding three distinctions, or none).  No study code is run; Codex's starts are read from its artifacts as data.

Parts:
- PX: Proposition X built from the proof's text, as a start: the swap p1 <-> q1 an isometry of its table? keeps the reading?
  carries the equations? every reading-keeping, equation-breaking symmetry extended through the referee's own round.
- TW: the three failing swaps (Proposition X; GROWN-END-SWAP's meet-twice stage; GROWN-END-MEET-ONCE's seven-junction stage): how
  many triples' three-way readings the swap changes.
- TS (chunks): one in ten of the census stages where the referee's HUNT-SHORTEN-R1 run found reading-keeping, equation-breaking
  symmetries (runs/referee-selfpairs, read as the referee's own data): every such symmetry (at most 2,000 per stage) tested for
  keeping every three-way reading.

  .venv/bin/python -B scripts/longrun.py launch research/PROVE-B-20261119-001/referee-R1/job_proveb.py \\
      --out runs/referee-proveb --unit referee-proveb --workers 3 --case-timeout 7200 --case-mem 3G --mem-max 12G
"""
import itertools
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
for p in ("research/GROWN-END-MEET-ONCE-20261119-001/referee-R1", "research/HUNT-SHORTEN-20261119-001/referee-R1",
          "research/GROWN-END-SWAP-20261119-001/referee-R1", "research/EXTEND-ROUND-20261119-001/referee-R1",
          "research/CREATED-PAIR-20261119-001/referee-R1", "research/GROW-SMALL-20261119-001/referee-R1",
          "research/VARIABLE-OUTPUT-READER-20261118-001F/referee-R1", "research/FIRST-KNOT-20261118-001/referee-R1",
          "research/CENSUS-READ-20261118-001/referee-R1", "research/GROWN-PAIR-20261119-001/referee-R1",
          "research/MEET-ONCE-20261119-001/referee-R1", "research/PARENT-RULE-20261119-001/referee-R1",
          "research/RING-IDENT-20261119-001/referee-R1", "research/THREE-WAY-20261119-001/referee-R1",
          "research/UNIQUE-TABLE-20261119-001/referee-R1"):
    sys.path.insert(0, str(ROOT / p))
PARAMS = {}
NAMES = ["p1", "p2", "q1", "q2", "s1", "s2", "t1", "t2", "s1'", "s2'", "t1'", "t2'", "lu", "lv", "lu'", "lv'"]
IX = {x: i for i, x in enumerate(NAMES)}
PROPX = [[IX[x] for x in s] for s in (["p1", "p2", "q1", "q2"], ["p1", "p2", "s1", "s2", "t1", "t2"],
                                      ["q1", "q2", "s1'", "s2'", "t1'", "t2'"], ["s1", "s2", "lu"], ["t1", "t2", "lv"],
                                      ["s1'", "s2'", "lu'"], ["t1'", "t2'", "lv'"])]


def setup(params):
    PARAMS.update(params)


def one_round(stars):
    import job_meet1 as JM
    h = JM.history(stars, maxj=40, ages=1)
    return h[0]


def three_way(stars):
    import referee_three as R3
    labels = sorted({b for s in stars for b in s})
    idx = {b: i for i, b in enumerate(labels)}
    S = [sorted(idx[b] for b in s) for s in stars]
    _, _, T = R3.readings(S, len(labels))
    return T, labels, idx


def changed_triples(stars, perm):
    T, labels, idx = three_way(stars)
    p = {idx[x]: idx[perm.get(x, x)] for x in labels}
    return sum(1 for t, v in T.items() if T[tuple(sorted(p[x] for x in t))] != v)


def part_px():
    import job_meet1 as JM
    age, stage, nxt, new = one_round(PROPX)
    c = JM.test(stage, nxt, new)
    import job_swap as JS
    K1, l1, i1 = JS.table(stage)
    perm = {IX["p1"]: IX["q1"], IX["q1"]: IX["p1"]}
    f = {x: perm.get(x, x) for x in l1}
    iso = all(K1[i1[x]][i1[y]] == K1[i1[f[x]]][i1[f[y]]] for x, y in itertools.combinations(l1, 2))
    return {"stage test (reading-keeping, equation-breaking symmetries; failing)": [c.get("keep R, not the equations", 0),
            c.get("extensions that fail (a Claim B counterexample)", 0)], "the swap p1 q1 is an isometry": iso,
            "new junctions (parents, fresh)": [[q["parents"], q["fresh"]] for q in new]}


def part_tw():
    out = {}
    out["Proposition X (p1 q1), at the start"] = changed_triples(PROPX, {IX["p1"]: IX["q1"], IX["q1"]: IX["p1"]})
    d = json.load(open(ROOT / "artifacts/GROWN-END-SWAP-20261119-001/GROWN-END-SWAP-20261119-001-E001_reached/construct_6.json"))
    out["meet twice (0 2), at round 1"] = changed_triples([sorted(s) for s in d["a"]["current"]], {0: 2, 2: 0})
    m = json.load(open(ROOT / "artifacts/GROWN-END-MEET-ONCE-20261119-001/GROWN-END-MEET-ONCE-20261119-001-E001_rounds/two_histories.json"))
    st = m["seven_at_round_one"]["stages"][1]
    out["meet once, seven (0 1), at round 1"] = changed_triples([sorted(s) for s in st], {0: 1, 1: 0})
    return out


def part_ts(lo, hi):
    import job_selfpairs as SP
    import job_extend as JE
    import job_growsmall as GS
    import job_ring as JR
    stages = []
    for line in open(ROOT / "runs/referee-selfpairs/results.jsonl"):
        stages += json.loads(line)["result"]["stages with R-keeping isometries"]
    pick = stages[::10][lo:hi]
    s = Counter()
    found = []
    for key, rnd, nj, keep, ok, hb, capped in pick:
        sizes, flat = json.loads(key)
        n = len(sizes)
        edges = []
        for (i, j), m in zip(itertools.combinations(range(n), 2), flat):
            edges += [(i, j)] * m
        st = [x for x in SP.stages(JR.stars_of(n, edges, list(sizes))) if x[0] == rnd]
        if not st:
            continue
        _, stage, nxt, new = st[0]
        S, N, old = JE.relabel_pair(stage, nxt)
        own = JE.owners(S)
        K, _, _, _ = GS.full_table([sorted(q) for q in S])
        lo_ = sorted(old)
        cls = [tuple(sorted(own[lo_[i]])) for i in range(len(lo_))]
        rs, cap = SP.reps(K, cls, cap=50000)
        R = JE.reading(S)
        rows = [sum(1 << x for x in q) for q in S]
        rk = SP.rank(rows)
        T, labels, idx = three_way(S)
        s["stages"] += 1
        tested = 0
        for phi0 in rs:
            phi = {lo_[x]: lo_[y] for x, y in enumerate(phi0)}
            img = [sum(1 << phi[x] for x in q) for q in S]
            if SP.rank(rows + img) == rk:
                continue
            psi, whole, top = JE.keeps(phi, S, S, R, R)
            if psi is None or not top:
                continue
            if tested >= 2000:
                s["not tested (over 2,000 in a stage)"] += 1
                continue
            tested += 1
            p = {idx[x]: idx[phi[x]] for x in labels}
            keeps3 = all(T[tuple(sorted(p[x] for x in t))] == v for t, v in T.items())
            s["reading-keeping, equation-breaking symmetries tested"] += 1
            s["... keeping every three-way reading"] += keeps3
            if keeps3 and len(found) < 5:
                found.append({"key": key, "round": rnd, "phi": phi})
        s["stages with an untested remainder"] += tested >= 2000
    return {"counts": dict(s), "keep three-way": found}


def cases():
    only = set(PARAMS["only"].split(",")) if PARAMS.get("only") else None
    allc = [("PX", {"part": "PX"}), ("TW", {"part": "TW"})] + [(f"TS-{c:02d}", {"part": "TS", "lo": 60 * c, "hi": 60 * (c + 1)})
                                                               for c in range(11)]
    for cid, p in allc:
        if only is None or cid in only:
            yield cid, p


def run(case_id, p):
    if p["part"] == "PX":
        return part_px()
    if p["part"] == "TW":
        return part_tw()
    return part_ts(p["lo"], p["hi"])
