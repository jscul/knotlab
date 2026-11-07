#!/usr/bin/env python3
"""Checks for CHAIN-TRANSFER-20261106-001B: the source rule on larger trees.

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
import tree_lib as TR  # noqa: E402

TL, GL, DL = TR.TL, TR.GL, TR.DL
T0 = time.time()
OUT = {}


def check(name, ok, info):
    OUT[name] = {"pass": bool(ok), "info": info}
    print("PASS" if ok else "FAIL", name, json.dumps(info, default=str), round(time.time() - T0, 1), "s", flush=True)
    if not ok:
        sys.exit(1)


def design_task(args):
    design, validate = args
    S, cuts = TR.build(design)
    res = TR.relation(S, cuts)
    natoms = len(design) + 1
    c = collections.Counter()
    c["trees of %d atoms" % natoms] += 1
    if validate:
        t = DL.Tree(S)
        thm = TL.relation_by_theorem(S, t)
        c["validated against the tight-cut decomposition"] += 1
        c["... bookkeeping relation equal and braces = atoms"] += (all(res[a][b][0] == thm[a][b] for a in res for b in res[a])
                                                                 and len(t.types) == natoms and all(x == "heawood" for x in t.types))
    first, counts, nq, one = TR.source_rule(S, res)
    c["first quiet part: kept blocks = atoms"] += first == natoms
    c["every quiet part: kept blocks = atoms"] += set(counts) == {natoms}
    c["every creative part one piece"] += one
    return c


def random_task(args):
    seed, natoms, shape = args
    S = TL.random_tree(random.Random(seed), natoms, shape)
    t = DL.Tree(S)
    res = {a: {b: (v,) for b, v in row.items()} for a, row in TL.relation_by_theorem(S, t).items()}
    first, counts, nq, one = TR.source_rule(S, res)
    return args, first, counts


if __name__ == "__main__":
    manifest = json.loads((HERE / "manifest.json").read_text())
    bad = {q: dg for q, dg in manifest["parent_bindings"].items() if hashlib.sha256((ROOT / q).read_bytes()).hexdigest() != dg}
    status = {q: json.loads((ROOT / q).read_text()).get("status") for q in manifest["parent_bindings"]
              if q.endswith(".json") and q.startswith("proofs/")}
    check("0 dependency artifacts bound by hash; upstream proofs Proved", not bad and all(s in ("Proved", "passed") for s in status.values()),
          {"mismatched": bad, "statuses": status})

    with Pool(22) as pool:
        # 1
        tasks = []
        for n in (2, 3, 4, 5):
            ds = TR.designs(n)
            tasks += [(d, i % 25 == 0) for i, d in enumerate(ds)]
        c1 = collections.Counter()
        for c in pool.imap_unordered(design_task, tasks, chunksize=16):
            c1.update(c)
        n1 = len(tasks)
        check("1 every Fano tree of at most five atoms (every splice sequence, up to choices that leave creation unchanged): the source rule "
              "keeps exactly one block per atom, for the first maximum quiet part and for every one; the relation read from the build "
              "equals the one read from the tight-cut decomposition on every 25th tree",
              c1["first quiet part: kept blocks = atoms"] == c1["every quiet part: kept blocks = atoms"] == n1 and
              c1["validated against the tight-cut decomposition"] == c1["... bookkeeping relation equal and braces = atoms"] > 0, dict(c1))

        # 2
        info2, ok2 = {}, True
        cases = {"six atoms: a receiver with two loaded cuts, emitting the line through their points": (TR.M1(), 5),
                 "the same without that line (five atoms)": (TR.M1(connecting_line=False), 5),
                 "the same with one load (five atoms)": (TR.M1(loads=(1, 0)), 5),
                 "seven atoms: three loaded cuts at non-collinear points": (TR.M2(), 6),
                 "seven atoms: three loaded cuts at collinear points": (TR.M2(collinear=True), 7)}
        for name, (d, expect) in cases.items():
            S, cuts = TR.build(d)
            res = TR.relation(S, cuts)
            first, counts, nq, one = TR.source_rule(S, res)
            info2[name] = {"atoms": len(d) + 1, "kept (first quiet part)": first, "kept over every quiet part": dict(counts),
                           "quiet parts": nq}
            ok2 &= first == expect and set(counts) == {expect}
        check("2 counterexamples: the source rule keeps one block too few on the six-atom tree and on the seven-atom tree with non-collinear "
              "points, for every maximum quiet part; removing the emitted line, a load, or making the points collinear restores it", ok2, info2)

        # 3
        info3, ok3 = {}, True
        for name, d, expect in (("six atoms", TR.M1(), 5), ("seven atoms, non-collinear", TR.M2(), 6)):
            S, cuts = TR.build(d)
            exact, nsol = {}, set()
            for M, row, ns in pool.imap_unordered(TR.exact_row, [(S, M) for M in range(len(S.H))], chunksize=1):
                exact[M] = row
                nsol.add(ns)
            thm = TR.relation(S, cuts)
            pairs = sum(len(r) for r in exact.values())
            eq = sum((v is not None and any(v)) == thm[a][b][0] for a, r in exact.items() for b, v in r.items())
            resx = {a: {b: (v is not None and any(v),) for b, v in r.items()} for a, r in exact.items()}
            first, counts, nq, one = TR.source_rule(S, resx)
            info3[name] = {"points": S.n, "solutions per removal": sorted(nsol), "pairs": pairs, "equal to the theorem": eq,
                           "source rule on the exact map (first quiet part)": first, "over every quiet part": dict(counts)}
            ok3 &= pairs == eq > 0 and first == expect and set(counts) == {expect}
        check("3 exact confirmation: the creation maps of the two counterexamples, computed from every solution by the two-round rule on "
              "the real near sides (no contraction, no automaton), equal the theorem's relation at every pair, and the source rule on them "
              "miscounts", ok3, info3)

        # 4
        tasks = [(1000 * n + s, n, shape) for n in (6, 7, 8, 10, 12) for shape in ("any", "path") for s in range(200)]
        c4 = collections.defaultdict(collections.Counter)
        for (seed, n, shape), first, counts in pool.imap_unordered(random_task, tasks, chunksize=2):
            k = "%d atoms, %s" % (n, "random trees" if shape == "any" else "paths")
            c4[k]["trees"] += 1
            c4[k]["first quiet part miscounts"] += first != n
            c4[k]["some quiet part miscounts"] += set(counts) != {n}
        paths_ok = all(v["some quiet part miscounts"] == 0 for k, v in c4.items() if "paths" in k)
        fails = sum(v["some quiet part miscounts"] for v in c4.values())
        check("4 random trees of six to twelve atoms: the source rule miscounts on some trees with branching atoms, never on paths",
              paths_ok and fails > 0, {k: dict(v) for k, v in sorted(c4.items())})

        # 5
        S, cuts = TR.build(TR.M1())
        res = TR.relation(S, cuts)
        owner, idx = [k[0] for k in S.lkey], [k[1] for k in S.lkey]
        base = [k for k in range(len(S.H)) if owner[k] == "g"]
        load = {name: [k for k in range(len(S.H)) if owner[k] == name] for name in ("A4", "A5")}
        blind = {a: {name: sum(1 for c in ls if res[c][a][0] and not res[a][c][0]) for name, ls in load.items()} for a in base}
        types = collections.Counter((tuple(sorted(n for n, v in blind[a].items() if v)), tuple(TR.F[idx[a]])) for a in base)
        through = {a: [p for p in (0, 1) if p in TR.F[idx[a]]] for a in base}
        ok5 = (all(bool(blind[a]["A4"]) == (0 in through[a]) and bool(blind[a]["A5"]) == (1 in through[a]) for a in base)
               and not any(len(through[a]) == 2 for a in base) and TR.L01 not in [idx[a] for a in base])
        check("5 the mechanism on the six-atom tree: a line of the receiver is blind to a load's intact lines exactly when it passes "
              "through the point that load's cut took; the only line through both points is the one the receiver emits, so no line of "
              "the receiver is blind to all the others are blind to, and its block has no source", ok5,
              {"receiver's lines: loads blind to, line": {"%s %s" % k: v for k, v in types.items()}})

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
