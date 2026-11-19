"""Shared-runner job for the referee's check of THREE-WAY-20261119-001 (referee_three.py; no study code imported or run).

Cases:
- six-<i>: the 11 different-states rivals (truth and rival read from UNIQUE-TABLE's verify_rivals.json as data).  The truth is
  regrown from its start and round and compared with the recorded truth; both readings are computed on the recorded names; pairs
  and triples that differ are counted; and an exact search asks whether any renaming carries the rival's pair and three-way
  readings onto the truth's.
- stage-<case>: the six stages, the referee's count of same-states rivals within the bound (UNIQUE-TABLE-R1's samecode search).
- und-<i>: the 23 stages that forcing with pairs left undecided (start and round read from triples.json as data): forcing with
  pairs only, then with pairs and triples; whether every forced word is a bond of the truth; whether they span its equations; the
  same-states rivals within the bound.
- grown-<g>: each of GROWN-PAIR's 152 other-state groups, with its full membership (every grown stage carrying the group's study
  table hash, regrown and placed by exact states, as in GROWN-PAIR-R1's job_members.py), one arrangement per state group; for
  every two of them, an exact search for a renaming that keeps both readings.

  .venv/bin/python -B scripts/longrun.py launch research/THREE-WAY-20261119-001/referee-R1/job_three.py \\
      --out runs/referee-three-way --unit referee-three-way --workers 6 --case-timeout 1800 --case-mem 2G --mem-max 16G
"""
import gzip
import json
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
VR = ROOT / "artifacts/UNIQUE-TABLE-20261119-001A/UNIQUE-TABLE-20261119-001A-E001_unique/verify_rivals.json"
TW = ROOT / "artifacts/THREE-WAY-20261119-001A/THREE-WAY-20261119-001A-E001_triples/triples.json"
GP = ROOT / "artifacts/GROWN-PAIR-20261119-001A/GROWN-PAIR-20261119-001A-E001_pairs"
CASES = {}


def setup(params):
    rows = json.load(open(VR))
    for i, r in enumerate(rows):
        CASES[f"six-{i:02d}"] = {"kind": "six", "row": r}
    for r in rows:
        CASES[f"stage-{r['case']}"] = {"kind": "stage", "key": r["key"], "round": r["round"]}
    for i, r in enumerate(json.load(open(TW))["undecided"]):
        CASES[f"und-{i:02d}"] = {"kind": "und", "key": r["key"], "round": r["round"]}
    th, byh = {}, defaultdict(list)
    for line in gzip.open(GP / "results_grown-pair.jsonl.gz", "rt"):
        r = json.loads(line)
        if r.get("status") != "ok":
            continue
        for st in r["result"]["stages"]:
            th[(st["index"], st["round"])] = st["table_hash"]
            if st["round"] > 0:
                byh[st["table_hash"]].append((st["index"], st["round"]))
    keys = {}
    for line in open(ROOT / "runs/census-exact5/results.jsonl"):
        r = json.loads(line)
        if r.get("status") == "ok" and r["case"].startswith("census"):
            for a in r["result"]["arrangements"]:
                keys[a["index"]] = a["key"]
    for i, g in enumerate(json.load(open(GP / "other_states.json"))["group_list"]):
        h = th[tuple(g["reps"][0]["prov"][0])]
        CASES[f"grown-{i:03d}"] = {"kind": "grown", "reps": [rep["stars"] for rep in g["reps"]],
                                   "members": [[ix, rnd, keys[ix]] for ix, rnd in byh[h]]}


def cases():
    yield from CASES.items()


def iso_arr(A, B):
    import networkx as nx

    def inc(stars):
        G = nx.Graph()
        for j, s in enumerate(stars):
            G.add_node(("j", j), k="j")
            for b in s:
                G.add_node(("b", b), k="b")
                G.add_edge(("j", j), ("b", b))
        return G
    return nx.is_isomorphic(inc(A), inc(B), node_match=nx.algorithms.isomorphism.categorical_node_match("k", None))


def run(case_id, p):
    import referee_three as R3
    if p["kind"] == "six":
        r = p["row"]
        truth, rival = r["truth"], r["rival"]
        labels = sorted({b for s in truth for b in s})
        assert labels == sorted({b for s in rival for b in s})
        idx = {b: i for i, b in enumerate(labels)}
        A = [sorted(idx[b] for b in s) for s in truth]
        B = [sorted(idx[b] for b in s) for s in rival]
        nb = len(labels)
        mine = R3.stage(r["key"], r["round"])
        _, KA, TA = R3.readings(A, nb)
        _, KB, TB = R3.readings(B, nb)
        pairs_differ = sum(KA[x][y] != KB[x][y] for x in range(nb) for y in range(x + 1, nb))
        triples_differ = sum(TA[t] != TB[t] for t in TA)
        return {"case": r["case"], "regrown truth = recorded truth (isomorphic)": iso_arr(mine, truth), "distinctions": nb,
                "pairs differing on the same names": pairs_differ, "triples": len(TA),
                "triples no bond holds (truth, rival)": [sum(v is None for v in TA.values()), sum(v is None for v in TB.values())],
                "triples differing on the same names": triples_differ,
                "a renaming keeps pairs and triples": R3.iso_both(KA, KB, TA, TB, nb),
                "a renaming keeps pairs (control)": R3.iso_both(KA, KB, {t: 0 for t in TA}, {t: 0 for t in TB}, nb)}
    if p["kind"] == "stage":
        from samecode import rivals
        stars = R3.stage(p["key"], p["round"])
        n, capped = rivals(stars)
        return {"same-states rivals within the bound": n, "capped": capped}
    if p["kind"] == "und":
        from samecode import rivals
        stars = R3.stage(p["key"], p["round"])
        S, nb = R3.relabel(stars)
        bonds, K, T = R3.readings(S, nb)
        bset = set(bonds)
        f2, s2 = R3.forcing(S, nb, K, {t: 0 for t in T})
        f3, s3 = R3.forcing(S, nb, K, T)
        n, capped = rivals(stars)
        return {"junctions": len(S), "distinctions": nb, "rank": len(R3.span(sum(1 << x for x in s) for s in S)),
                "pairs only: forced, spans": [len(f2), s2], "pairs and triples: forced, spans": [len(f3), s3],
                "every forced word a bond of the truth": all(f in bset for f in f2 + f3),
                "same-states rivals within the bound": n, "capped": capped}
    # grown
    import referee_f as F
    import referee_census as RC
    from job_grown import same_states
    reps = [R3.relabel(s) for s in p["reps"]]
    rt = [RC.shore_table(A)[0] for A, _ in reps]
    for ix, rnd, key in p["members"]:
        B, n = R3.relabel(R3.stage(key, rnd))
        KB = RC.shore_table(B)[0]
        if F.isometric(rt[0], KB) is None:
            continue
        if not any(same_states(A, B, KA, KB, n)[0] for (A, _), KA in zip(reps, rt)):
            reps.append((B, n))
            rt.append(KB)
    rd = [R3.readings(A, n)[1:] for A, n in reps]
    agree_shore = all(K[x][y] == (int(kk[x][y]) if kk[x][y] < F.INF else R3.INF_SIZE) for (K, _), kk, (_, n) in zip(rd, rt, reps)
                      for x in range(n) for y in range(n))
    out = []
    for a in range(len(reps)):
        for b in range(a + 1, len(reps)):
            (KA, TA), (KB, TB) = rd[a], rd[b]
            out.append({"pairs kept by a renaming": R3.iso_both(KA, KB, {t: 0 for t in TA}, {t: 0 for t in TB}, reps[a][1]),
                        "pairs and triples kept by a renaming": R3.iso_both(KA, KB, TA, TB, reps[a][1])})
    return {"state groups": len(reps), "bond pair table = shore table": agree_shore, "pairs": out}
