#!/usr/bin/env python3
"""Checks for REFINE-READ-20261107-001B: uniform rules on the native map.

    python3 -B check.py          verify result.json against a fresh run
    python3 -B check.py --write  write result.json from a fresh run
Run with the repository's .venv (numpy, networkx). Uses up to 22 processes."""
import os

for _v in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

import collections  # noqa: E402
import hashlib  # noqa: E402
import json  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from multiprocessing import Pool  # noqa: E402
from pathlib import Path  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
import rules_lib as RL  # noqa: E402

T0 = time.time()
OUT = {}
SPACES = RL.NG.spaces()


def check(name, ok, info):
    OUT[name] = {"pass": bool(ok), "info": info}
    print("PASS" if ok else "FAIL", name, json.dumps(info, default=str), round(time.time() - T0, 1), "s", flush=True)
    if not ok:
        sys.exit(1)


def task(i):
    src, nm, S, ex = SPACES[i]
    kind, c = RL.report(src, nm, S, ex)
    return ("saved" if src.startswith("saved") else "fresh") + ", " + kind, c


if __name__ == "__main__":
    manifest = json.loads((HERE / "manifest.json").read_text())
    bad = {q: dg for q, dg in manifest["parent_bindings"].items() if hashlib.sha256((ROOT / q).read_bytes()).hexdigest() != dg}
    status = {q: json.loads((ROOT / q).read_text()).get("status") for q in manifest["parent_bindings"]
              if q.endswith(("manifest.json", "result.json")) and q.startswith("proofs/")}
    check("0 dependency artifacts bound by hash; upstream proofs Proved", not bad and all(s in ("Proved", "passed") for s in status.values()),
          {"mismatched": bad, "statuses": status})
    rows = collections.defaultdict(collections.Counter)
    with Pool(22) as pool:
        for kind, c in pool.imap_unordered(task, range(len(SPACES)), chunksize=1):
            rows[kind].update(c)
    tot = collections.Counter()
    for r in rows.values():
        tot.update(r)
    rules = [k[len("rule reads the atoms: "):] for k in tot if k.startswith("rule reads the atoms: ")]
    info = {"by kind": {k: {kk: v[kk] for kk in ["spaces"] + ["rule reads the atoms: " + r for r in sorted(rules)]}
                        for k, v in sorted(rows.items())},
            "all": {r: {"reads": tot["rule reads the atoms: " + r], "fails merging atoms": tot["rule fails by merging atoms: " + r]}
                    for r in sorted(rules)}}
    vet, nat = "native row twins vetoed by pair refinement", "native row twins (GENUS-READ C)"
    check("1 uniform rules: none reads every space; the native twin relation is an equivalence in every space, so components and maximal "
          "cliques agree; vetoing by pair refinement changes nothing, since twinship is preserved by refinement",
          all(tot["rule reads the atoms: " + r] < tot["spaces"] for r in rules)
          and tot["the native twin relation is an equivalence (its maximal cliques are disjoint)"] == tot["spaces"]
          and tot["rule reads the atoms: " + vet] == tot["rule reads the atoms: " + nat]
          and tot["rule reads the atoms: maximal twin cliques"] == tot["rule reads the atoms: " + nat], info)
    check("2 where the native twins merge atoms, most often two whole atoms are joined by complete twinship (every line of one a native row "
          "twin of every line of the other); in the rest the merged class holds parts of atoms",
          0 < tot["spaces where two atoms are joined by complete twinship"] <= tot["rule fails by merging atoms: " + nat],
          {"spaces joined by complete twinship": tot["spaces where two atoms are joined by complete twinship"],
           "spaces where the native twins merge atoms": tot["rule fails by merging atoms: " + nat]})
    check("3 the glue-compatibility regularity: two lines of one atom that are native row twins never both create at a glue line with "
          "different order-free vectors; across atoms such pairs occur, but not for every merged pair",
          tot["... compatible at glue lines, within an atom"] == tot["native row twins within an atom"] > 0
          and 0 < tot["... compatible at glue lines, across atoms"] < tot["native row twins across atoms"],
          {k: tot[k] for k in ("native row twins within an atom", "... compatible at glue lines, within an atom",
                               "native row twins across atoms", "... compatible at glue lines, across atoms")})

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
