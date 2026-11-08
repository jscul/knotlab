#!/usr/bin/env python3
"""Checks for SWITCH-PROOF-20261108-001A: creation between glue lines depends only on the switching class.

    python3 -B check.py          verify result.json against a fresh run
    python3 -B check.py --write  write result.json from a fresh run
Run with the repository's .venv (numpy, networkx). Uses up to 12 processes."""
import os

for _v in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

import gzip  # noqa: E402
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
import proof_lib as PL  # noqa: E402

PL.TR.engine()
T0 = time.time()
OUT = {}
TRB = ROOT / "proofs/TRISUM-READ-20261107-001B/TRISUM-READ-20261107-001B-P001_frozen_predictions_on_larger_trisum_spaces"
PLACE = json.loads((PL.SWA / "placements.json").read_text())
STORED = {**json.load(gzip.open(PL.TRA / "maps.json.gz", "rt")), **json.load(gzip.open(TRB / "maps.json.gz", "rt"))}
ALT = json.load(gzip.open(PL.SWA / "maps.json.gz", "rt"))
RUNS = {}
SIGNS = {}


def check(name, ok, info):
    OUT[name] = {"pass": bool(ok), "info": info}
    print("PASS" if ok else "FAIL", name, json.dumps(info, default=str), round(time.time() - T0, 1), "s", flush=True)
    if not ok:
        sys.exit(1)


def free(v):
    return None if v is None else (bool(v[0]), bool(v[2]), bool(v[3]))


def plain_map(seed, hs):
    return STORED[str(seed)] if hs == PLACE[str(seed)]["stored hash seed"] else ALT["%d/%d" % (seed, hs)]


def reduction_task(args):
    """the glue block of the plain space against the signed glue's creation map"""
    seed, hs = args
    glue = RUNS[0][seed]["glue"]
    signs = PL.signs_of(glue, SIGNS[(seed, hs)])
    m = plain_map(seed, hs)
    diff = total = 0
    for a in range(len(glue)):
        row = PL.signed_row(glue, signs, a)
        for b, v in row.items():
            total += 1
            diff += free(v) != free(m["rows"][str(a)]["row"][str(b)])
    return seed, hs, total, diff


def switching_task(args):
    """the signed glue's creation map under random switchings of its signing"""
    seed, k = args
    rec = RUNS[0][seed]
    glue = rec["glue"]
    base = [PL.signed_row(glue, PL.signs_of(glue, rec["minimal"]), a) for a in range(len(glue))]
    r = random.Random(1000 * seed + k)
    verts = [("L", i) for i in range(len(glue))] + [("P", p) for p in sorted({q for l in glue for q in l})]
    U = {v for v in verts if r.random() < 0.5}
    S2 = PL.switched(glue, rec["minimal"], U)
    rows = [PL.signed_row(glue, PL.signs_of(glue, S2), a) for a in range(len(glue))]
    same = all(free(base[a][b]) == free(rows[a][b]) for a in range(len(glue)) for b in base[a])
    exact = all(base[a][b] == rows[a][b] for a in range(len(glue)) for b in base[a])
    return seed, k, len(S2), same, exact


if __name__ == "__main__":
    manifest = json.loads((HERE / "manifest.json").read_text())
    bad = {q: dg for q, dg in manifest["parent_bindings"].items() if hashlib.sha256((ROOT / q).read_bytes()).hexdigest() != dg}
    status = {q: json.loads((ROOT / q).read_text()).get("status") for q in manifest["parent_bindings"]
              if q.endswith(("manifest.json", "result.json")) and q.startswith("proofs/")}
    check("0 dependency artifacts bound by hash; upstream proofs Proved",
          not bad and all(s in ("Proved", "passed") for s in status.values()), {"mismatched": bad, "statuses": status})

    atom = PL.atom_report()
    check("1 the edge atom, over all 256 assignments of its eight points: its own seven lines force r0 = r1 = r2 = not p, and leave its "
          "four inner points five configurations for each value of p, each inner point taking both values for each p, each pair of "
          "inner points taking all four pairs, the configurations for p = 1 being those for p = 0 complemented",
          atom["solutions"] == 10 and atom["per value of p"] == {0: 5, 1: 5} and atom["r0 = r1 = r2 = not p"]
          and atom["each inner point takes both values for each p"] and atom["each pair of inner points takes all four pairs"]
          and atom["the inner configurations for p = 1 are those for p = 0 complemented"], atom)

    seeds = sorted(int(s) for s in PLACE)
    hss = sorted({h for s in seeds for h in [PLACE[str(s)]["stored hash seed"]] + PLACE[str(s)]["mapped"]} | {0})
    with Pool(12) as pool:
        RUNS.update(zip(hss, pool.starmap(PL.SW.generate, [(seeds, h) for h in hss])))
    contacts, witnesses, read_ok = [], [], True
    TL = PL.TR.engine().TL
    SIGN = {}
    for s in seeds:
        glue = RUNS[0][s]["glue"]
        same_glue = all(RUNS[h][s]["glue"] == glue for h in RUNS)
        for h in [PLACE[str(s)]["stored hash seed"]] + PLACE[str(s)]["mapped"]:
            H = [tuple(l) for l in plain_map(s, h)["lines"]]
            S, ok = PL.signing_of_space(H, glue)
            SIGN[(s, h)] = S
            okc, k = PL.atom_contacts(H, [tuple(l) for l in glue])
            contacts.append(okc and k == len(S))
            read_ok &= ok and same_glue
        hs = [PLACE[str(s)]["stored hash seed"]] + PLACE[str(s)]["mapped"]
        n = 1 + max(max(l) for l in glue)
        for h in hs[1:]:
            U = PL.switching_witness(glue, SIGN[(s, hs[0])], SIGN[(s, h)])
            good = U is not None
            if good:
                flip = [int(("P", q) in U) for q in range(n)]
                sa, sb = PL.signs_of(glue, SIGN[(s, hs[0])]), PL.signs_of(glue, SIGN[(s, h)])
                for a in range(len(glue)):
                    A1 = TL.solutions([tuple(l) for l in glue], sa, n, skip=a)
                    A2 = TL.solutions([tuple(l) for l in glue], sb, n, skip=a)
                    good &= {tuple(int(x) ^ flip[q] for q, x in enumerate(r)) for r in A1} == {tuple(int(x) for x in r) for r in A2}
            witnesses.append(good)
    check("2 the spaces and switching: every stored and mapped placement is the generator's glue with an atom point in place of the glue "
          "point at each incidence of its signing, and each atom meets the rest only at its glue point and at r0 on one glue line; for "
          "every pair of mapped placements of one glue, complementing the points of a switching set maps the signed glue's solutions, "
          "with any one line removed, onto the other placement's",
          all(contacts) and all(witnesses) and read_ok, {"placements checked": len(contacts), "pairs of placements": len(witnesses)})

    SIGNS.update(SIGN)
    jobs = [(s, h) for s in seeds for h in [PLACE[str(s)]["stored hash seed"]] + PLACE[str(s)]["mapped"]]
    with Pool(12) as pool:
        red = pool.map(reduction_task, jobs, chunksize=1)
    check("3 the reduction, computed: in every stored and mapped placement the block of glue lines of the plain space's native map "
          "equals the signed glue's creation map, entry by entry",
          all(d == 0 for s, h, t, d in red), {"placements": len(red), "entries": sum(t for s, h, t, d in red),
                                              "differing": sum(d for s, h, t, d in red)})

    with Pool(12) as pool:
        sw = pool.map(switching_task, [(s, k) for s in seeds for k in range(8)], chunksize=1)
    check("4 the theorem, computed on random switchings: for each of the 17 glues and eight random switching sets, the signed glue's "
          "creation map is unchanged (order-free vectors and degeneracy)",
          all(x[3] for x in sw), {"switchings": len(sw), "order-free vectors unchanged": sum(x[3] for x in sw),
                                  "all four far sides unchanged": sum(x[4] for x in sw),
                                           "signs after switching (min, max)": [min(x[2] for x in sw), max(x[2] for x in sw)]})

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
