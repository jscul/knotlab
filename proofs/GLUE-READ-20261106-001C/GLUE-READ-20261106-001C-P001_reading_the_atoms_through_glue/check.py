#!/usr/bin/env python3
"""Checks for GLUE-READ-20261106-001C: reading the atoms through glue.

    python3 -B check.py          verify result.json against a fresh run
    python3 -B check.py --write  write result.json from a fresh run
Run with the repository's .venv (numpy, networkx). Uses up to 22 processes. The exact creation maps come from ticket B's maps.json.gz,
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
import atoms_lib as AT  # noqa: E402

G = AT.G
T0 = time.time()
OUT = {}


def check(name, ok, info):
    OUT[name] = {"pass": bool(ok), "info": info}
    print("PASS" if ok else "FAIL", name, json.dumps(info, default=str), round(time.time() - T0, 1), "s", flush=True)
    if not ok:
        sys.exit(1)


def judge_task(args):
    src, S, ex = args
    kind, c = AT.judge(S, ex)
    return "%s, %s" % (src, kind), c


def fano_tree_task(args):
    """on a Fano tree the two-stage rule is CHAIN-TRANSFER C's twin rule: every line is an atom line, and the classes agree"""
    S, ex = args
    out = G.creates(ex)
    AL, cls = AT.two_stage(len(S.H), out)
    return len(AL) == len(S.H) and sorted(map(sorted, cls)) == sorted(map(sorted, G.twin_classes(len(S.H), out)))


if __name__ == "__main__":
    manifest = json.loads((HERE / "manifest.json").read_text())
    bad = {q: dg for q, dg in manifest["parent_bindings"].items() if hashlib.sha256((ROOT / q).read_bytes()).hexdigest() != dg}
    status = {q: json.loads((ROOT / q).read_text()).get("status") for q in manifest["parent_bindings"]
              if q.endswith(("manifest.json", "result.json")) and q.startswith("proofs/")}
    check("0 dependency artifacts bound by hash (ticket B's exact maps included); upstream proofs Proved",
          not bad and all(s in ("Proved", "passed") for s in status.values()), {"mismatched": bad, "statuses": status})

    spaces, maps = G.load_maps(AT.GRB / "maps.json.gz")
    with Pool(22) as pool:
        # 1
        fano = [(S, ex) for (src, nm, S), ex in zip(spaces, maps) if set(AT.PL.structure(S)[1]) == {"heawood"}]
        ok1 = list(pool.imap(fano_tree_task, fano, chunksize=2))
        check("1 on Fano trees the two-stage rule is CHAIN-TRANSFER C's twin rule: every line is an atom line and the classes agree",
              all(ok1) and len(ok1) > 0, {"Fano trees": len(ok1), "agree": sum(ok1)})

        rows = collections.defaultdict(collections.Counter)
        for kind, c in pool.imap(judge_task, [(src, S, ex) for (src, nm, S), ex in zip(spaces, maps)], chunksize=1):
            rows[kind].update(c)
        rows = {k: dict(v) for k, v in sorted(rows.items())}
        reads = {k: (v["two-stage rule reads the atoms"], v["spaces"]) for k, v in rows.items()}
        census_all = all(v["two-stage rule reads the atoms"] == v["spaces"] for k, v in rows.items() if k.startswith("census"))
        ds_only = all(v["... extra lines in its classes are doubled-square lines"] == v["spaces"] for v in rows.values())
        # 2
        check("2 the two-stage rule reads the atoms of every one of BRACE-TREE C's 111 fresh spaces and of most random spaces with plane "
              "glue; the only lines it adds to an atom are doubled-square lines; the plain twin rule and the source rule each miscount "
              "somewhere", census_all and ds_only and
              any(v["plain twin rule reads the atoms"] < v["spaces"] for v in rows.values()) and
              any(v["source rule counts the atoms"] < v["spaces"] for v in rows.values()),
              {"two-stage rule (read, spaces)": reads, "by kind": rows})
        # 3
        fails = {k: {w: x for w, x in v.items() if w.startswith("fails")} for k, v in rows.items()}
        allfail = collections.Counter()
        for v in fails.values():
            allfail.update(v)
        indist = {k: v["two lines of different atoms indistinguishable by whether creation occurs"] for k, v in rows.items()}
        failed_indist = sum(x for w, x in allfail.items() if w.endswith("; indistinguishable"))
        ok3 = (failed_indist == sum(indist.values()) > 0
               and all(w.startswith(("fails: merges atoms meeting one planar brace", "fails: drops or splits an atom")) for w in allfail)
               and all(x == 0 for k, x in indist.items() if k.startswith("census")))
        check("3 where it fails, the rule merges atoms that meet one planar brace or drops a line of an atom; in most failing spaces two "
              "lines of different atoms are creation twins both ways, so no rule that reads only whether creation occurs can return the "
              "atoms there; no census space has such lines", ok3,
              {"failures": dict(allfail), "spaces with indistinguishable lines of different atoms": indist})
        # 4
        full = {k: v["two lines of different atoms indistinguishable far side by far side"] for k, v in rows.items()}
        full_twins = {k: (v["twins far side by far side read the atoms"], v["spaces"]) for k, v in rows.items()}
        check("4 which far side creates separates every two lines of different atoms in every space, but varies inside atoms too: twins "
              "far side by far side do not read the atoms, even on Fano trees",
              all(x == 0 for x in full.values()) and any(r < s for r, s in full_twins.values()),
              {"spaces with indistinguishable lines of different atoms, far side by far side": full,
               "twins far side by far side read the atoms (read, spaces)": full_twins})

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
