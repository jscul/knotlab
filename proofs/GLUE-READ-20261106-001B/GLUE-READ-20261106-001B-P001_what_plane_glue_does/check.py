#!/usr/bin/env python3
"""Checks for GLUE-READ-20261106-001B: what plane glue does.

    python3 -B check.py          verify result.json (and maps.json.gz) against a fresh run
    python3 -B check.py --write  write result.json and maps.json.gz from a fresh run
Run with the repository's .venv (numpy, networkx). Uses up to 22 processes. maps.json.gz holds every exact creation map computed here,
for ticket C."""
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
import plane_glue_lib as G  # noqa: E402

TL, PL = G.TL, G.PL
T0 = time.time()
OUT = {}


def check(name, ok, info):
    OUT[name] = {"pass": bool(ok), "info": info}
    print("PASS" if ok else "FAIL", name, json.dumps(info, default=str), round(time.time() - T0, 1), "s", flush=True)
    if not ok:
        sys.exit(1)


def describe(args):
    src, nm, S = args
    parts, types, pown, lown, xs = PL.structure(S)
    return src, G.kind_of_space(types), S.n, len(TL.solutions(S.H, S.s, S.n)), sum(1 for t in types if t == "heawood"), \
        tuple(sorted(set(types)))


def effects(args):
    S, ex = args
    return G.pair_effects(S, ex), G.twin_effects(S, ex)


if __name__ == "__main__":
    manifest = json.loads((HERE / "manifest.json").read_text())
    bad = {q: dg for q, dg in manifest["parent_bindings"].items() if hashlib.sha256((ROOT / q).read_bytes()).hexdigest() != dg}
    status = {q: json.loads((ROOT / q).read_text()).get("status") for q in manifest["parent_bindings"]
              if q.endswith(("manifest.json", "result.json")) and q.startswith("proofs/")}
    check("0 dependency artifacts bound by hash; upstream proofs Proved", not bad and all(s in ("Proved", "passed") for s in status.values()),
          {"mismatched": bad, "statuses": status})

    spaces = G.all_spaces()
    with Pool(22) as pool:
        # 1
        desc = list(pool.imap(describe, spaces, chunksize=2))
        c1 = collections.Counter()
        for src, kind, n, nsol, atoms, types in desc:
            c1["%s, %s" % (src, kind)] += 1
            c1["%s: no solutions (knot spaces)" % src] += nsol == 0
        pts = {src: (min(d[2] for d in desc if d[0] == src), max(d[2] for d in desc if d[0] == src)) for src in ("census", "random")}
        atoms = {src: (min(d[4] for d in desc if d[0] == src), max(d[4] for d in desc if d[0] == src)) for src in ("census", "random")}
        maps = G.exact_maps(pool, spaces)
        path = HERE / "maps.json.gz"
        if "--write" in sys.argv:
            G.save(path, spaces, maps)
        stored_spaces, stored = G.load_maps(path)
        same = stored == maps and [(s[0], s[1], s[2].H, s[2].s) for s in stored_spaces] == [(s[0], s[1], s[2].H, s[2].s) for s in spaces]
        check("1 the spaces and their exact creation maps: BRACE-TREE C's 111 fresh spaces and 80 random spaces with plane glue (Fano atoms "
              "hung on random plane spaces or on census spaces), all knot spaces; every map computed from all solutions by the two-round "
              "rule and stored in maps.json.gz",
              c1["census: no solutions (knot spaces)"] == 111 and c1["random: no solutions (knot spaces)"] == 80 and same,
              {"spaces": dict(c1), "points": pts, "Fano atoms": atoms, "maps stored identically": same,
               "maps.json.gz sha256": hashlib.sha256(path.read_bytes()).hexdigest()})

        # 2, 3
        pair, twin = collections.Counter(), collections.Counter()
        for p, t in pool.imap(effects, [(S, ex) for (src, nm, S), ex in zip(spaces, maps)], chunksize=1):
            pair.update(p)
            twin.update(t)
        rows = collections.defaultdict(dict)
        for k, v in pair.items():
            rows["; ".join(k[:-1])][k[-1]] = v
        free_ok = all(v["pairs"] == v["touching rule holds"] for k, v in rows.items() if k.endswith("; free"))
        atoms_free = all(k.endswith("; free") for k in rows if "atoms only between" in k)
        fails_elsewhere = sum(v["pairs"] - v["touching rule holds"] for k, v in rows.items() if not k.endswith("; free"))
        check("2 creation through glue: wherever only atoms lie between, the removal's side leaves the facing cut free; the touching rule "
              "holds at every pair whose side is free, and fails only where glue constrains the ports (excluding a pattern pair or tying two "
              "ports, a doubled square sometimes making two ports one point)", free_ok and atoms_free and fails_elsewhere > 0,
              {"by kind, source, what lies between and the side's relation": dict(sorted(rows.items())),
               "failures, all at constrained sides": fails_elsewhere})
        joined = {k: v for k, v in twin.items() if k[0] == "glue line"}
        only_ds = all(k[1] == "doubled square" and k[2].startswith("meeting the atom's cuts at two") for k, v in joined.items()
                      if k[3] == "joins the atom's twin class")
        splits = {k: v for k, v in twin.items() if k[0] == "atom split"}
        by_port = all("into a planar brace" in k[1] or "only on glue lines" in k[1] for k in splits)
        check("3 the twin rule's two disturbances: every glue line that joins an atom's twin class is a doubled-square line meeting the "
              "atom's cuts at two or more ports (a point that is a port of two cuts counting for each); every atom that splits emits a "
              "line into a planar brace and splits into its lines through each point of that line, and its classes' out-sets differ only "
              "on glue lines",
              only_ds and by_port, {"glue lines": {" / ".join(k[1:]): v for k, v in sorted(joined.items())},
                                    "atoms": {k[1]: v for k, v in twin.items() if k[0] == "atom"},
                                    "splits": {k[1]: v for k, v in splits.items()}})

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
