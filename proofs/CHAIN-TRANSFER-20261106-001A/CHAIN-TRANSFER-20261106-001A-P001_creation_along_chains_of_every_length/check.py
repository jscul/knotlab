#!/usr/bin/env python3
"""Checks for CHAIN-TRANSFER-20261106-001A: creation along chains of every length.

    python3 -B check.py          verify result.json against a fresh run
    python3 -B check.py --write  write result.json from a fresh run
Run with the repository's .venv (numpy, networkx, python-sat). Uses up to 22 processes. Solutions are enumerated point by point
(transfer_lib.solutions); check 2 compares that enumeration with SAT model enumeration (BRACE-TREE C's method) on every chain it builds."""
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

import numpy as np  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
import transfer_lib as TL  # noqa: E402

GL, CL, DL, CH = TL.GL, TL.GL.CL, TL.DL, TL.CH
CL.solutions = TL.solutions
FARS = [f for f, F in TL.SL.FARS]
T0 = time.time()
OUT = {}


def check(name, ok, info):
    OUT[name] = {"pass": bool(ok), "info": info}
    print("PASS" if ok else "FAIL", name, json.dumps(info, default=str), round(time.time() - T0, 1), "s", flush=True)
    if not ok:
        sys.exit(1)


def two_atom_task(spec):
    """check 1: the local verdict against the creation map on one two-atom chain, every removal and line"""
    S = CH.build_two(spec)
    out = collections.Counter()
    for M in range(len(S.H)):
        _, row = GL.row_task((S, M))
        AN = CL.solutions(S.H, S.s, S.n, skip=M)
        for L, v in row.items():
            Y = list(S.H[L])
            mine = TL.verdict_of_near_side(AN, Y, S.s[L], [q for q in range(S.n) if q not in Y])
            out["pairs"] += 1
            out["equal, far side by far side"] += mine == v
    return out


def chain_task(seed):
    """check 2: a random built chain of 2, 3 or 4 atoms: the automaton against the creation map at every line of the last atom"""
    r = random.Random(seed)
    k = 1 + seed % 3
    a, e, steps, last, kind = TL.random_chain(r, k)
    out = collections.Counter()
    S, M, b0, names = TL.build(a, e, steps, last)
    _, row = GL.row_task((S, M))
    st = TL.run_chain(a, e, steps)
    out["chains of %d atoms" % (k + 1)] += 1
    for b in TL.final_letters(kind):
        if b[:2] != last[:2]:
            continue
        bi = S.line((names[-1], b[2]))
        mine = TL.final_verdict(st, *b)
        out["lines of the last atom"] += 1
        out["equal, far side by far side"] += mine == row[bi]
        out["touching rule holds"] += ((row[bi] is not None and any(row[bi])) == TL.touching(kind, b[1], b[2]))
    AN = CL.solutions(S.H, S.s, S.n, skip=M)
    out["solutions equal to SAT model enumeration"] += np.array_equal(AN, TL.sat_solutions(S.H, S.s, S.n, skip=M))
    for nports, npat in TL.prefix_ports(S, names, M):
        out["cuts"] += 1
        out["cuts where the prefix shows every pattern on the points it shares with the rest"] += nports in (2, 3) and npat == 2 ** nports
        out["... of them sharing two points (the third port lies only on the removed line)"] += nports == 2
    t = DL.Tree(S)
    p = t.place(M, b0)
    out["tree distance equals the chain's"] += p[0] == "apart" and len(p[3]) == k
    return out


def tree_row_task(args):
    """check 3: one row of the exact creation map of a random small Fano tree, against the theorem's relation"""
    seed, natoms, M = args
    S = TL.random_tree(random.Random(seed), natoms)
    t = DL.Tree(S)
    thm = TL.relation_by_theorem(S, t)
    _, row = GL.row_task((S, M))
    out = collections.Counter()
    for L, v in row.items():
        same = t.owner[M] == t.owner[L]
        out["pairs" + (" in one atom" if same else " in different atoms")] += 1
        out["equal to the theorem"] += (v is not None and any(v)) == thm[M][L]
        out["lines showing fewer than six patterns"] += v is None
    return out


def final_task(st):
    """checks 5 and 6 on one profile"""
    kind = st[0]
    c = collections.Counter()
    for let in TL.final_letters(kind):
        v = TL.final_verdict(st, *let)
        vl = TL.final_verdict(st, *let, deep=False)
        cre = v is not None and any(v)
        tr = TL.touching(kind, let[1], let[2])
        role = TL.role(kind, let[1], let[2])
        c["last letters"] += 1
        c["touching rule holds"] += cre == tr
        c["the last atom alone gives the same verdict"] += vl == v
        c["six patterns missing"] += v is None
        c[("by role", role, "far sides creating", tuple(f for f, x in zip(FARS, v) if x) if v else ())] += 1
        c["mutation: every line receives, agrees"] += cre
        c["mutation: only cut lines receive, agrees"] += cre == (role == "cut line")
        c["mutation: only emitters' lines receive, agrees"] += cre == (role == "emitter's line")
    return c


if __name__ == "__main__":
    manifest = json.loads((HERE / "manifest.json").read_text())
    bad = {q: dg for q, dg in manifest["parent_bindings"].items() if hashlib.sha256((ROOT / q).read_bytes()).hexdigest() != dg}
    status = {q: json.loads((ROOT / q).read_text()).get("status") for q in manifest["parent_bindings"]
              if q.endswith(".json") and q.startswith("proofs/")}
    check("0 dependency artifacts bound by hash; upstream proofs Proved", not bad and all(s in ("Proved", "passed") for s in status.values()),
          {"mismatched": bad, "statuses": status})

    with Pool(22) as pool:
        # 1
        c1 = collections.Counter()
        for c in pool.imap_unordered(two_atom_task, CH.two_specs(), chunksize=2):
            c1.update(c)
        check("1 the reduction at the gluing line: on every two-atom chain (294 gluings), at every removal and every gluing line, creation "
              "computed from the near side's relations on the line and up to two further points (PENDANT-LINE A's two-round rule) equals "
              "the creation map far side by far side", c1["pairs"] == c1["equal, far side by far side"] > 0, dict(c1))

        # 2
        c2 = collections.Counter()
        for c in pool.imap_unordered(chain_task, range(240), chunksize=1):
            c2.update(c)
        check("2 the automaton on built chains: random chains of two, three and four atoms built by the creation map's own splices; at "
              "every line of the last atom the automaton's verdict equals the creation map far side by far side; at every cut the prefix "
              "(the atoms before it, minus the removal) shows every pattern on the points it shares with the rest, so its ports are free; "
              "the tree distance is the chain's",
              c2["lines of the last atom"] == c2["equal, far side by far side"] == c2["touching rule holds"] > 0
              and c2["cuts"] == c2["cuts where the prefix shows every pattern on the points it shares with the rest"] and c2["tree distance equals the chain's"] == 240
              and c2["solutions equal to SAT model enumeration"] == 240, dict(c2))

        # 3
        tasks = []
        for natoms, seeds in ((3, range(100, 112)), (4, range(200, 208))):
            for seed in seeds:
                S = TL.random_tree(random.Random(seed), natoms)
                tasks += [(seed, natoms, M) for M in range(len(S.H))]
        c3 = collections.Counter()
        for c in pool.imap_unordered(tree_row_task, tasks, chunksize=1):
            c3.update(c)
        check("3 the whole relation on random Fano trees (12 of three atoms, 8 of four, any shape): the exact creation map equals the "
              "block lemma with the touching rule at every pair of lines",
              c3["equal to the theorem"] == c3["pairs in one atom"] + c3["pairs in different atoms"] > 0, dict(c3))

        # 4
        S4, depth, per_depth = TL.closure(pool)
        info4 = {"initial profiles": per_depth[0], "new profiles at each further atom": per_depth[1:], "profiles": len(S4),
                 "by kind of the next splice": dict(collections.Counter(s[0] for s in S4)),
                 "port relations": dict(collections.Counter(bin(s[1]).count("1") for s in S4)),
                 "singles per profile": dict(sorted(collections.Counter(len(s[2]) for s in S4).items())),
                 "pairs per profile": dict(sorted(collections.Counter(len(s[3]) for s in S4).items()))}
        check("4 the reachable profiles: starting from every removal and first element, closing under every splice (every element, "
              "every lost element of the new atom, every port permutation) reaches a fixed point; every profile leaves the three ports "
              "free (all eight patterns)", per_depth[-1] == 0 and all(s[1] == 255 for s in S4), info4)

        # 5, 6
        c5 = collections.Counter()
        for c in pool.imap_unordered(final_task, sorted(S4, key=str), chunksize=1):
            c5.update(c)
        n = c5["last letters"]
        roles = {"%s; far sides creating: %s" % (k[1], ", ".join(k[3]) or "none"): v for k, v in c5.items() if isinstance(k, tuple)}
        check("5 the touching rule at every distance: on every reachable profile, for every last atom (lost element and port permutation) "
              "and every line of it, creation by the two-round rule holds exactly when the line touches the last cut; the last atom "
              "alone, with free ports and no point behind the cut, gives the same verdict", n == c5["touching rule holds"] ==
              c5["the last atom alone gives the same verdict"] > 0 and c5["six patterns missing"] == 0,
              {"last letters": n, "touching rule holds": c5["touching rule holds"],
               "last atom alone": c5["the last atom alone gives the same verdict"], "by role and far side": roles})
        mut = {k: v for k, v in c5.items() if isinstance(k, str) and k.startswith("mutation")}
        check("6 controls: the check is not vacuous; each simpler rule disagrees with the verdicts somewhere",
              all(v < n for v in mut.values()), dict(mut, **{"last letters": n}))

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
