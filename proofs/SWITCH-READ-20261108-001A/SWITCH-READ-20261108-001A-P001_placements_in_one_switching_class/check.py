#!/usr/bin/env python3
"""Checks for SWITCH-READ-20261108-001A: placements in one switching class.

    python3 -B check.py          verify result.json against a fresh run
    python3 -B check.py --write  write result.json from a fresh run
Run with the repository's .venv (numpy, networkx). Uses up to 12 processes."""
import os

for _v in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

import gzip  # noqa: E402
import hashlib  # noqa: E402
import itertools  # noqa: E402
import json  # noqa: E402
import random  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from multiprocessing import Pool  # noqa: E402
from pathlib import Path  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
import sw_lib as SW  # noqa: E402
sys.path.insert(0, str(SW.TRC))
import order_lib as OL  # noqa: E402

OL.TR.engine()
T0 = time.time()
OUT = {}
PLACEMENTS = json.loads((HERE / "placements.json").read_text())
MAPS = json.load(gzip.open(HERE / "maps.json.gz", "rt"))
STORED = {**json.load(gzip.open(SW.TRA / "maps.json.gz", "rt")), **json.load(gzip.open(SW.TRB / "maps.json.gz", "rt"))}


def check(name, ok, info):
    OUT[name] = {"pass": bool(ok), "info": info}
    print("PASS" if ok else "FAIL", name, json.dumps(info, default=str), round(time.time() - T0, 1), "s", flush=True)
    if not ok:
        sys.exit(1)


def the_map(seed, hs):
    """the stored map for the stored placement, else the one computed here"""
    return STORED[str(seed)] if hs == PLACEMENTS[str(seed)]["stored hash seed"] else MAPS["%d/%d" % (seed, hs)]


def row_task(args):
    seed, hs, M = args
    m = the_map(seed, hs)
    H = [tuple(l) for l in m["lines"]]
    w, s, order = OL.fixed_order(H, m["points"])
    out, ns = OL.exact_row(H, m["points"], M, order)
    stored = m["rows"][str(M)]
    return seed, hs, M, ns == stored["solutions"] and {str(L): (None if v is None else [int(x) for x in v]) for L, v in out.items()} == stored["row"]


def compare_task(args):
    seed, ha, hb = args
    g = PLACEMENTS[str(seed)]["glue lines"]
    na, ta = SW.table(the_map(seed, ha))
    nb, tb = SW.table(the_map(seed, hb))
    block = SW.glue_block_differences(ta, tb, g)
    fixed = SW.isomorphic_maps(na, ta, tb, g, True) is not None
    anyb = SW.isomorphic_maps(na, ta, tb, g, False) is not None
    return seed, ha, hb, {"lines": na, "glue lines": g, "glue block differences": len(block), "isomorphic with the glue fixed": fixed,
                          "isomorphic under some bijection": anyb, **SW.where_they_differ(na, ta, tb, g)}


RLG = None


def report_task(args):
    seed, hs = args
    RL = RLG
    m = MAPS["%d/%d" % (seed, hs)]
    H = [tuple(l) for l in m["lines"]]
    ex = {int(a): {int(b): (None if v is None else tuple(bool(x) for x in v)) for b, v in r["row"].items()} for a, r in m["rows"].items()}
    r = SW.FAM.TR.report(H, ex, RL)
    return "%d/%d" % (seed, hs), [k for k, v in r.items() if k.startswith("P") and v is not True]


if __name__ == "__main__":
    manifest = json.loads((HERE / "manifest.json").read_text())
    bad = {q: dg for q, dg in manifest["parent_bindings"].items() if hashlib.sha256((ROOT / q).read_bytes()).hexdigest() != dg}
    status = {q: json.loads((ROOT / q).read_text()).get("status") for q in manifest["parent_bindings"]
              if q.endswith(("manifest.json", "result.json")) and q.startswith("proofs/")}
    check("0 dependency artifacts bound by hash; TRISUM-READ's tickets Proved",
          not bad and all(s in ("Proved", "passed") for s in status.values()), {"mismatched": bad, "statuses": status})

    seeds = sorted(int(s) for s in PLACEMENTS)
    with Pool(12) as pool:
        runs = dict(zip(SW.HASH_SEEDS, pool.starmap(SW.generate, [(seeds, hs) for hs in SW.HASH_SEEDS])))
    found, ok1 = {}, True
    for s in seeds:
        glue = runs[0][s]["glue"]
        g = SW.incidence_of_glue(glue)
        reps = []
        for hs in SW.HASH_SEEDS:
            H = [tuple(l) for l in runs[hs][s]["lines"]]
            if not any(SW.FAM.isomorphic(H, [tuple(l) for l in runs[r][s]["lines"]]) for r in reps):
                reps.append(hs)
        rec = PLACEMENTS[str(s)]
        stored_lines = [tuple(l) for l in STORED[str(s)]["lines"]]
        same_glue = all(runs[hs][s]["glue"] == glue for hs in SW.HASH_SEEDS)
        one_class = all(SW.is_coboundary(g, SW.incidences(runs[0][s]["minimal"]) ^ SW.incidences(runs[hs][s]["minimal"])) for hs in SW.HASH_SEEDS)
        pfaffian_one_class = all(SW.is_coboundary(g, SW.incidences(runs[0][s]["pfaffian"]) ^ SW.incidences(runs[hs][s]["pfaffian"]))
                                 for hs in SW.HASH_SEEDS)
        classes_match = sorted(reps) == sorted(rec["placements"]) and SW.FAM.isomorphic(
            [tuple(l) for l in runs[rec["stored hash seed"]][s]["lines"]], stored_lines)
        alt_lines = all(runs[hs][s]["lines"] == MAPS["%d/%d" % (s, hs)]["lines"] for hs in rec["mapped"])
        ok1 &= same_glue and one_class and pfaffian_one_class and classes_match and alt_lines and len(glue) == rec["glue lines"]
        found[str(s)] = {"placement classes": len(reps), "hash seeds representing them": sorted(reps), "glue the same": same_glue,
                         "minimal signings in one switching class": one_class, "Pfaffian signings in one switching class": pfaffian_one_class}
    multi = [s for s in seeds if len(PLACEMENTS[str(s)]["placements"]) > 1]
    mapped = [s for s in multi if PLACEMENTS[str(s)]["mapped"]]
    check("1 the placements: under hash seeds 0 to 23 the generator gives each of the 17 glues the same glue and Pfaffian and minimal "
          "signings that all lie in one switching class; the spaces fall into the recorded placement classes, the stored one among them, "
          "and every alternative map is of the regenerated lines",
          ok1 and sorted(MAPS) == sorted("%d/%d" % (s, hs) for s in seeds for hs in PLACEMENTS[str(s)]["mapped"]),
          {"glues with more than one placement": len(multi), "placements": sum(len(PLACEMENTS[str(s)]["placements"]) for s in multi),
           "alternative placements mapped here": len(MAPS), "by seed": found})

    jobs = []
    for s in mapped:
        for hs in PLACEMENTS[str(s)]["mapped"]:
            n = len(MAPS["%d/%d" % (s, hs)]["lines"])
            jobs += [(s, hs, M) for M in sorted({0, random.Random(1000 * s + hs).randrange(1, n)})]
    with Pool(12) as pool:
        rows = pool.map(row_task, jobs, chunksize=1)
    check("2 the alternative maps: two rows of each, recomputed by the fixed-order enumerator, equal the stored rows",
          all(r[3] for r in rows), {"rows": len(rows), "equal": sum(r[3] for r in rows), "maps": len(MAPS)})

    pairs = [(s, a, b) for s in mapped
             for a, b in itertools.combinations([PLACEMENTS[str(s)]["stored hash seed"]] + PLACEMENTS[str(s)]["mapped"], 2)]
    with Pool(12) as pool:
        cmp_ = pool.map(compare_task, pairs, chunksize=1)
    block_same = [c for c in cmp_ if c[3]["glue block differences"] == 0]
    iso_fixed = [c for c in cmp_ if c[3]["isomorphic with the glue fixed"]]
    iso_any = [c for c in cmp_ if c[3]["isomorphic under some bijection"]]
    rows_same = [c for c in cmp_ if not c[3]["glue lines whose row to atom lines changes"]]
    cols_change = [c for c in cmp_ if c[3]["glue lines whose column from atom removals changes"]]
    check("3 the comparisons: for every pair of mapped placements of one glue, the block of glue lines is identical, every glue line's "
          "removal creates at the atom lines with the same multiset of vectors, atom removals create differently at some glue line, and "
          "the whole native maps are not isomorphic, neither with the glue's lines fixed nor under any bijection",
          len(block_same) == len(rows_same) == len(cols_change) == len(cmp_) > 0 and not iso_fixed and not iso_any,
          {"pairs": len(cmp_), "glue block identical": len(block_same), "isomorphic with the glue fixed": len(iso_fixed),
           "isomorphic under some bijection": len(iso_any),
           "by pair": {"%d: %d vs %d" % (s, a, b): v for s, a, b, v in cmp_}})

    RLG = SW.FAM.TR.load("sw_refine_lib", ROOT / "proofs/REFINE-READ-20261107-001A/REFINE-READ-20261107-001A-P001_pair_refinement_determines_the_atoms"
                        / "refine_lib.py")
    with Pool(12) as pool:
        reps = pool.map(report_task, [(s, hs) for s in mapped for hs in PLACEMENTS[str(s)]["mapped"]])
    failing = {k: v for k, v in reps if v}
    check("4 TRISUM-READ's frozen statements P1 to P7 hold on every mapped alternative placement too",
          not failing and len(reps) == len(MAPS), {"placements": len(reps), "failing": failing})

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
