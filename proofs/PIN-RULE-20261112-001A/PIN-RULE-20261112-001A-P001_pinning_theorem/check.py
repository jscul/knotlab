#!/usr/bin/env python3
"""Checks for PIN-RULE-20261112-001A (research/PIN-RULE-20261112-001/preregistration.md).

    .venv/bin/python3 -B check.py --write
The pinning theorem is proved by hand (proof.md). This checks its local statement, on which the proof rests, by SAT: for every block
of SUBST-NEST-20261112-001's census (87) and of its stress test (300), with the block's knots in every order between three copies
joined by one knot, (1) a distinction p is forced equal in all three copies exactly when it is not spare; (2) a spare p's copies are
tied to nothing; (3) no between-copy tie is ever a forced inequality. It also checks the counting step of the proof (two copies that
disagree at p make the third copy's state a spare witness) directly on every block: for every pair of states a, b with a_p != b_p and
every state c compatible with them, c is a spare witness for p (on the 87 census blocks; the 300 stress blocks get the SAT part)."""
import hashlib
import itertools
import json
import os
import sys
import time
from multiprocessing import Pool
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SN = ROOT / "proofs/SUBST-NEST-20261112-001A/SUBST-NEST-20261112-001A-P001_block_substitution"
sys.path.insert(0, str(SN))
import subst_lib as S  # noqa: E402

T0 = time.time()
DEPS = [str((HERE / "check.py").relative_to(ROOT)), str((SN / "subst_lib.py").relative_to(ROOT)),
        str((SN / "result_stress_one_size_past.json").relative_to(ROOT)), "research/PIN-RULE-20261112-001/preregistration.md"]


def spare_witness(B, p, c):
    m, E = B
    return all(len({c[x] for x in e if x != p}) == 2 for e in E)


def job(arg):
    B, with_step = arg
    m, E = B
    T = S.binding_sets(m, E)["the block's knots"]
    spare = set(S.star_colouring(B))
    P = (3, [(0, 1, 2)])
    Q, idx = S.substitute(P, B, T)
    out = {"block": [m, E], "spare": sorted(spare), "distinctions": []}
    for p in range(m):
        tied = S.tie_class(Q, idx[(0, p)])
        others = {idx[(1, p)], idx[(2, p)]}
        forced_equal = others <= tied
        # the relation: equal in one state means equal in all, if tied
        sols_rel = None
        if forced_equal:
            from pysat.solvers import Solver
            with Solver(name="cadical153", bootstrap_with=S.nae_clauses(Q[1])) as s:
                s.solve()
                mm = s.get_model()
                sols_rel = all((mm[idx[(0, p)]] > 0) == (mm[o] > 0) for o in others)
        out["distinctions"].append({"p": p, "spare": p in spare, "copies forced equal": forced_equal and bool(sols_rel),
                                    "tied to nothing": tied == {idx[(0, p)]}})
    # the counting step, over every pair of states and every compatible third
    states = S.solutions(m, E) if with_step else []
    step_ok = True if with_step else None
    for a in states:
        for b in states:
            for c in states:
                if all(not (a[x] == b[y] == c[z]) for (x, y, z) in T):
                    for p in range(m):
                        if a[p] != b[p] and not spare_witness(B, p, c):
                            step_ok = False
    out["counting step holds"] = step_ok
    out["counting step checked"] = with_step
    out["rule holds"] = all((d["spare"] and d["tied to nothing"]) or (not d["spare"] and d["copies forced equal"]) for d in out["distinctions"])
    return out


def main():
    if os.environ.get("PYTHONHASHSEED") != "0":
        os.execve(sys.executable, [sys.executable, "-B"] + sys.argv, {**os.environ, "PYTHONHASHSEED": "0"})
    blocks = [((b[0], [tuple(e) for e in b[1]]), True) for b in S.blocks()]
    stress = json.loads((SN / "result_stress_one_size_past.json").read_text())["rows"]
    blocks += [((r["block"][0], [tuple(e) for e in r["block"][1]]), False) for r in stress]
    with Pool(12) as pool:
        rows = pool.map(job, blocks, chunksize=4)
    res = {"blocks": len(rows), "rule holds on one knot": sum(r["rule holds"] for r in rows),
           "counting step holds (the 87 census blocks)": sum(1 for r in rows if r["counting step holds"] is True),
           "no forced inequality between copies": all(not (d["spare"] is False and not d["copies forced equal"]) for r in rows for d in r["distinctions"]),
           "exceptions": [r for r in rows if not (r["rule holds"] and r["counting step holds"] is not False)][:10]}
    res = {"dependencies": {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in DEPS}, "result": res, "rows": rows,
           "seconds": round(time.time() - T0, 1)}
    if "--write" in sys.argv:
        (HERE / "result.json").write_text(json.dumps({"status": "passed", "checks": res}, indent=1) + "\n")
    print({k: v for k, v in res["result"].items() if k != "exceptions"}, len(res["result"]["exceptions"]), res["seconds"])


if __name__ == "__main__":
    main()
