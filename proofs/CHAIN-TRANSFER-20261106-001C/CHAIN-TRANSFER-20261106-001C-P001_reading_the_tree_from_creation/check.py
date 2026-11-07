#!/usr/bin/env python3
"""Checks for CHAIN-TRANSFER-20261106-001C: reading the tree from creation.

    python3 -B check.py          verify result.json against a fresh run
    python3 -B check.py --write  write result.json from a fresh run
Run with the repository's .venv (numpy, networkx, python-sat). Uses up to 22 processes."""
import os

for _v in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

import collections  # noqa: E402
import hashlib  # noqa: E402
import json  # noqa: E402
import random  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from multiprocessing import Pool  # noqa: E402
from pathlib import Path  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
import read_lib as RD  # noqa: E402

TR, TL, DL = RD.TR, RD.TL, RD.DL
T0 = time.time()
OUT = {}


def check(name, ok, info):
    OUT[name] = {"pass": bool(ok), "info": info}
    print("PASS" if ok else "FAIL", name, json.dumps(info, default=str), round(time.time() - T0, 1), "s", flush=True)
    if not ok:
        sys.exit(1)


def outsets(res):
    return {a: {b for b, v in row.items() if v[0]} for a, row in res.items()}


def design_task(args):
    design, perms, lost = args
    S, cuts = TR.build(design, perms, lost)
    res = TR.relation(S, cuts)
    ok_atoms, ok_tree, uniform = RD.compare(S, cuts, outsets(res))
    cuts_at = collections.Counter([e for e, r, q in cuts] + [r for e, r, q in cuts])
    c = collections.Counter()
    c["trees"] += 1
    c["condition N"] += RD.condition_N(S, cuts)
    c["at most four cuts at every atom"] += max(cuts_at.values()) <= 4
    c["atoms recovered"] += ok_atoms
    c["directed tree recovered"] += ok_tree
    c["footprints uniform"] += uniform
    return c


def random_task(args):
    seed, natoms, heavy = args
    d, perms, lost = RD.random_design(random.Random(seed), natoms, heavy)
    S, cuts = TR.build(d, perms, lost)
    res = TR.relation(S, cuts)
    ok_atoms, ok_tree, uniform = RD.compare(S, cuts, outsets(res))
    N = RD.condition_N(S, cuts)
    return args, N, ok_atoms, ok_tree


if __name__ == "__main__":
    manifest = json.loads((HERE / "manifest.json").read_text())
    bad = {q: dg for q, dg in manifest["parent_bindings"].items() if hashlib.sha256((ROOT / q).read_bytes()).hexdigest() != dg}
    status = {q: json.loads((ROOT / q).read_text()).get("status") for q in manifest["parent_bindings"]
              if q.endswith(("manifest.json", "result.json")) and q.startswith("proofs/")}
    check("0 dependency artifacts bound by hash; upstream proofs Proved", not bad and all(s in ("Proved", "passed") for s in status.values()),
          {"mismatched": bad, "statuses": status})

    with Pool(22) as pool:
        # 1
        tasks = [(d, None, None) for n in (2, 3, 4, 5) for d in TR.designs(n)]
        c1 = collections.Counter()
        for c in pool.imap_unordered(design_task, tasks, chunksize=32):
            c1.update(c)
        n1 = c1["trees"]
        check("1 every Fano tree of at most five atoms: condition N holds, and the rule recovers the atoms (as twin classes) and every cut "
              "with its direction (from the receivers' footprints)",
              n1 == c1["condition N"] == c1["atoms recovered"] == c1["directed tree recovered"] == c1["footprints uniform"] > 0, dict(c1))

        # 2
        tasks = [(1000 * n + s + (500 if h else 0), n, h) for n in (6, 8, 12, 20, 30) for h in (False, True) for s in range(200)]
        c2 = collections.defaultdict(collections.Counter)
        for (seed, n, h), N, ok_atoms, ok_tree in pool.imap_unordered(random_task, tasks, chunksize=4):
            k = "%d atoms, %s" % (n, "loaded atoms" if h else "random")
            c2[k]["trees"] += 1
            c2[k]["condition N"] += N
            c2[k]["N, tree recovered"] += N and ok_tree
            c2[k]["not N, tree recovered"] += (not N) and ok_tree
        allN = sum(v["condition N"] for v in c2.values())
        check("2 random trees of six to thirty atoms (random lost elements and permutations; some with many atoms hanging from two): "
              "wherever condition N holds the rule recovers the directed tree", allN == sum(v["N, tree recovered"] for v in c2.values()) > 0,
              {k: dict(v) for k, v in sorted(c2.items())})

        # 3
        S, cuts = TR.build(TR.M1())
        exact = {}
        for M, row, ns in pool.imap_unordered(TR.exact_row, [(S, M) for M in range(len(S.H))], chunksize=1):
            exact[M] = row
        out = {a: {b for b, v in r.items() if v is not None and any(v)} for a, r in exact.items()}
        ok_atoms, ok_tree, uniform = RD.compare(S, cuts, out)
        check("3 on the exact creation map of ticket B's six-atom counterexample (where the source rule fails) the rule recovers the atoms "
              "and the directed tree", ok_atoms and ok_tree and uniform, {"points": S.n, "atoms recovered": ok_atoms,
                                                                           "directed tree recovered": ok_tree})

        # 4
        info4 = {}
        F, L01 = TR.F, TR.L01
        off0 = [l for l in range(7) if 0 not in F[l]]
        examples = {"an atom with every line lost (seven receivers on the base's lines)": [("g", ("ln", l)) for l in range(7)],
                    "a lost point whose four lines off it are all lost": [("g", ("pt", 0))] + [("g", ("ln", l)) for l in off0],
                    "two lost points with the same surviving lines": [("g", ("pt", 0)), ("g", ("pt", 1))] +
                    [("g", ("ln", l)) for l in range(7) if (0 in F[l]) != (1 in F[l])]}
        ok4 = True
        for name, d in examples.items():
            S, cuts = TR.build(d)
            res = TR.relation(S, cuts)
            ok_atoms, ok_tree, uniform = RD.compare(S, cuts, outsets(res))
            info4[name] = {"atoms": len(d) + 1, "condition N": RD.condition_N(S, cuts), "atoms recovered": ok_atoms,
                           "directed tree recovered": ok_tree}
            ok4 &= not RD.condition_N(S, cuts) and not ok_tree
        check("4 where condition N fails the rule loses the tree: an atom with no lines is invisible, and a receiving cut whose footprint is "
              "all of its atom's lines, or equals another's, is not read", ok4, info4)

        # 5
        spaces = RD.census_spaces()
        tasks = [(i, M) for i, (name, S) in enumerate(spaces) for M in range(len(S.H))]
        exact = [dict() for _ in spaces]
        for (i, M), (M_, row, ns) in zip(tasks, pool.imap(TR.exact_row, [(spaces[i][1], M) for i, M in tasks], chunksize=1)):
            exact[i][M] = row
        c5 = collections.defaultdict(collections.Counter)
        for (name, S), ex in zip(spaces, exact):
            kind, c = RD.twin_report(S, ex)
            c5[kind]["spaces"] += 1
            c5[kind].update(c)
        ft = c5["Fano tree"]
        check("5 computed, on BRACE-TREE C's 111 fresh spaces (exact creation maps): in every Fano tree each atom is exactly one twin class; "
              "through plane glue the rule does not extend as stated, since a glue line can join an atom's class and an atom can split; no "
              "twin class ever mixes two atoms", ft["spaces"] > 0 and ft["exact atom"] == ft["atoms"] and
              all(v["class spanning two atoms"] == 0 for v in c5.values()), {k: dict(v) for k, v in sorted(c5.items())})

    OUT["seconds"] = round(time.time() - T0, 1)
    print("ALL OK", OUT["seconds"], "s")
    result = {"schema_version": 3, "artifact_id": manifest["artifact_id"], "kind": "proof", "ticket": manifest["ticket"],
              "proof": manifest["proof"], "status": "passed", "claim": manifest["claim"],
              "checks": {k: v for k, v in OUT.items() if k != "seconds"}}
    text = json.dumps(result, indent=1, sort_keys=True, default=str) + "\n"
    if "--write" in sys.argv:
        (HERE / "result.json").write_text(text)
    elif not (HERE / "result.json").exists() or json.loads((HERE / "result.json").read_text()) != json.loads(text):
        print("result.json does not match a fresh run; rerun with --write after review")
        sys.exit(1)
