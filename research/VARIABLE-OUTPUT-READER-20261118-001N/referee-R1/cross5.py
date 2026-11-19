"""Cross-type isometries within the four-addition family through D = 5 (the table clipped at K = 6), from family_n.py's rows: every
pair of distinct members of one width sharing the D = 5 invariant, tested exactly; for each isometric pair, are menus and supports
carried?  (family_n.py's `cross` part tests D = 4 and the full table.)

  ../../../.venv/bin/python -B cross5.py W > referee_n_cross5_W.json
"""
import json
import sys
from collections import defaultdict
from multiprocessing import Pool
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "VARIABLE-OUTPUT-READER-20261118-001F/referee-R1"))
import referee_f as F  # noqa: E402


def pair(args):
    a, b = args
    Ts = []
    for r in (a, b):
        T = (r["T"][0], tuple(r["T"][1]), tuple(r["T"][2]))
        J, n = F.supports(T)
        Ts.append((T, J, F.clip(F.bond_table(J, n)[0], 6)))
    (T1, J1, C1), (T2, J2, C2) = Ts
    p = F.isometric(C1, C2)
    if p is None:
        return None
    m1 = {frozenset(p[x] for x in t) for t in F.legal_triples(T1, J1)}
    m2 = {frozenset(t) for t in F.legal_triples(T2, J2)}
    return {"legal": [a["legal"], b["legal"]], "menus carried": m1 == m2,
            "supports carried": {frozenset(p[x] for x in S) for S in J1} == {frozenset(S) for S in J2}}


if __name__ == "__main__":
    w = int(sys.argv[1])
    rows = [json.loads(l) for l in open(HERE / f"family_four_{w}.jsonl")]
    b = defaultdict(list)
    for r in rows:
        b[r["inv D5"]].append(r)
    jobs = [(g[i], g[j]) for g in b.values() if len(g) > 1 for i in range(len(g)) for j in range(i + 1, len(g))]
    with Pool(10) as pool:
        res = [x for x in pool.map(pair, jobs, chunksize=1) if x]
    print(json.dumps({"members": len(rows), "pairs tested": len(jobs), "isometric pairs of distinct types": len(res),
                      "... menus not carried": sum(not x["menus carried"] for x in res),
                      "... with a legal triple, supports not carried": sum(max(x["legal"]) > 0 and not x["supports carried"] for x in res)}, indent=1))
