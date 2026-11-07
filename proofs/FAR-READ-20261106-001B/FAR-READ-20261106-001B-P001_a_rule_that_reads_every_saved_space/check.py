#!/usr/bin/env python3
"""Checks for FAR-READ-20261106-001B: a rule that reads every saved space.

    python3 -B check.py          verify result.json against a fresh run
    python3 -B check.py --write  write result.json from a fresh run
Run with the repository's .venv (numpy, networkx). Uses up to 22 processes. The exact creation maps are GLUE-READ B's maps.json.gz,
bound by hash."""
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
import rule_lib as RL  # noqa: E402

AT, G, FL = RL.AT, RL.G, RL.FL
T0 = time.time()
OUT = {}
SPACES, MAPS = FL.saved()


def check(name, ok, info):
    OUT[name] = {"pass": bool(ok), "info": info}
    print("PASS" if ok else "FAIL", name, json.dumps(info, default=str), round(time.time() - T0, 1), "s", flush=True)
    if not ok:
        sys.exit(1)


def task(i):
    src, nm, S = SPACES[i]
    ex = MAPS[i]
    parts, types, lown, xs, atoms = AT.atoms_of(S)
    n = len(S.H)
    kind = "%s, %s" % (src, G.kind_of_space(types))
    c = collections.Counter()
    c["spaces"] += 1
    variants = {"1-2 two-stage twins": dict(steps=2), "1-3 + split by parts acting as one": dict(steps=3),
                "1-4 with reattachment through whether creation occurs": dict(steps=4, reattach_through="any far side"),
                "the rule (1-4, reattachment through the Fano plane)": dict(steps=4)}
    for name, kw in variants.items():
        cls = RL.read_atoms(n, ex, **kw)
        ok, big = AT.reads_atoms(cls, atoms, lown, types)
        c[name] += ok
        if name.startswith("the rule"):
            c["the rule's count = number of Fano atoms"] += len(big) == len(atoms)
            c["Fano atoms"] += len(atoms)
    # the split without its size bounds
    keep = (RL.MIN_SPLIT, RL.MIN_PART)
    RL.MIN_SPLIT, RL.MIN_PART = 2, 2
    c["the rule with parts of two lines allowed"] += AT.reads_atoms(RL.read_atoms(n, ex), atoms, lown, types)[0]
    RL.MIN_SPLIT, RL.MIN_PART = keep
    return kind, c


if __name__ == "__main__":
    manifest = json.loads((HERE / "manifest.json").read_text())
    bad = {q: dg for q, dg in manifest["parent_bindings"].items() if hashlib.sha256((ROOT / q).read_bytes()).hexdigest() != dg}
    status = {q: json.loads((ROOT / q).read_text()).get("status") for q in manifest["parent_bindings"]
              if q.endswith(("manifest.json", "result.json")) and q.startswith("proofs/")}
    check("0 dependency artifacts bound by hash (GLUE-READ B's exact maps included); upstream proofs Proved",
          not bad and all(s in ("Proved", "passed") for s in status.values()), {"mismatched": bad, "statuses": status})

    rows = collections.defaultdict(collections.Counter)
    with Pool(22) as pool:
        for kind, c in pool.imap_unordered(task, range(len(SPACES))):
            rows[kind].update(c)
    rows = {k: dict(v) for k, v in sorted(rows.items())}
    total = collections.Counter()
    for v in rows.values():
        total.update(v)
    rule = "the rule (1-4, reattachment through the Fano plane)"
    check("1 the rule returns exactly the Fano atoms of all 191 saved spaces, and so counts them", total[rule] == total["spaces"] == 191
          and total["the rule's count = number of Fano atoms"] == 191, {"by kind": rows})
    steps = ["1-2 two-stage twins", "1-3 + split by parts acting as one", "1-4 with reattachment through whether creation occurs", rule]
    check("2 every step is needed: each refinement reads more spaces than the one before; allowing parts of two lines breaks atoms",
          all(total[a] < total[b] for a, b in zip(steps, steps[1:])) and total["the rule with parts of two lines allowed"] < 191,
          {s: total[s] for s in steps + ["the rule with parts of two lines allowed"]})

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
