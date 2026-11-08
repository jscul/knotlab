#!/usr/bin/env python3
"""Checks for TRISUM-READ-20261107-001A: junctions in the native creation map.

    python3 -B check.py          verify result.json against a fresh run
    python3 -B check.py --write  write result.json from a fresh run
Run with the repository's .venv (numpy, networkx, python-sat). Uses up to 22 processes."""
import os

for _v in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

import collections  # noqa: E402
import gzip  # noqa: E402
import hashlib  # noqa: E402
import itertools  # noqa: E402
import json  # noqa: E402
import random  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from multiprocessing import Pool  # noqa: E402
from pathlib import Path  # noqa: E402

import networkx as nx  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
import tr_lib as TR  # noqa: E402
import family_lib as FAM  # noqa: E402
import grammar_lib as GM  # noqa: E402

FROZEN = "e15fce8fa9d18a219df2b6fa82eaff9ef96d4d0ff3adb7a9839335bfa0b94d29"   # predictions.json as frozen before ticket B's maps
RL = TR.load("tr_refine_lib", ROOT / "proofs/REFINE-READ-20261107-001A/REFINE-READ-20261107-001A-P001_pair_refinement_determines_the_atoms"
             / "refine_lib.py")
TR.engine()
T0 = time.time()
OUT = {}
SPACES = json.loads((HERE / "spaces.json").read_text())
MAPS = json.load(gzip.open(HERE / "maps.json.gz", "rt"))


def check(name, ok, info):
    OUT[name] = {"pass": bool(ok), "info": info}
    print("PASS" if ok else "FAIL", name, json.dumps(info, default=str), round(time.time() - T0, 1), "s", flush=True)
    if not ok:
        sys.exit(1)


def canon(H):
    st = TR.structure(H)
    leaves = collections.defaultdict(set)
    for l, i in st["leaf"].items():
        leaves[i].add(l)
    return (frozenset(frozenset(A["lines"]) for A in st["atoms"]), frozenset(st["mates"]), frozenset(map(frozenset, leaves.values())),
            frozenset(st["roots"]), frozenset(st["loaded"]), frozenset(st["skeleton"]))


def structure_task(sp):
    H = [tuple(l) for l in sp["lines"]]
    st = TR.structure(H)
    G = st["G"]
    kind = GM.brace_type({v: collections.Counter(list(G[v])) for v in G})[0]
    base = canon(H)
    r = random.Random(sp["seed"])
    inv_ok = True
    for _ in range(3):
        n = sp["points"]
        lp = list(range(len(H)))
        r.shuffle(lp)
        pp = list(range(n))
        r.shuffle(pp)
        H2 = [None] * len(H)
        for i, l in enumerate(H):
            q = [pp[x] for x in l]
            r.shuffle(q)
            H2[lp[i]] = tuple(q)
        back = {lp[i]: i for i in range(len(H))}
        c2 = canon(H2)
        mapped = tuple(frozenset(frozenset(back[x] for x in s) if isinstance(s, frozenset) else back[s] for s in part) for part in c2)
        inv_ok &= mapped == base
    return sp["seed"], {"atoms": len(st["atoms"]), "skeleton lines": len(st["skeleton"]), "skeleton brace": kind,
                        "junctions": len(st["trisectors"]), "junction lines": sorted(st["junction"]),
                        "junction lines carrying an atom": sorted(st["junction"] & st["loaded"]), "leaves": st["leaves"],
                        "relabeling-invariant": inv_ok}


def row_task(args):
    seed, M = args
    d = MAPS[str(seed)]
    out, ns = TR.exact_row([tuple(l) for l in d["lines"]], d["points"], M)
    stored = d["rows"][str(M)]
    same = ns == stored["solutions"] and {str(L): (None if v is None else [int(x) for x in v]) for L, v in out.items()} == stored["row"]
    return seed, M, same


def original_row(args):
    seed, M = args
    d = MAPS[str(seed)]
    H = [tuple(l) for l in d["lines"]]
    S = TR.load("tr_port_lib", ROOT / "proofs/GLUE-READ-20261106-001A/GLUE-READ-20261106-001A-P001_creation_is_decided_by_the_receiving_cut"
                / "port_lib.py").RD.GL.base(H, [[0, 0, 0] for _ in H], d["points"])
    M_, out, ns = TR.engine().exact_row((S, M))
    return seed, M, ns == d["rows"][str(M)]["solutions"] and \
        {str(L): (None if v is None else [int(x) for x in v]) for L, v in out.items()} == d["rows"][str(M)]["row"]


def report_task(seed):
    d = MAPS[str(seed)]
    H = [tuple(l) for l in d["lines"]]
    ex = {int(a): {int(b): (None if v is None else tuple(bool(x) for x in v)) for b, v in r["row"].items()} for a, r in d["rows"].items()}
    return seed, TR.report(H, ex, RL)


def control_task(i):
    src, nm, S, ex = CONTROL[i]
    n = len(S.H)
    parts, types, lown, xs, atoms = RL.AT.atoms_of(S)
    A = set().union(*atoms.values())
    p5, p6 = TR.pinned_apart(ex, n, A), TR.pinned_apart(ex, n, set())
    B, D = TR.blocks(ex, n)
    free_lines = {l for l in range(n) if not B[l]}
    tri = []
    for b, t in enumerate(types):
        if t == "other":
            g = nx.Graph([(u, w) for u in parts[b] for w in parts[b][u]])
            lines = {v for v in g if v[0] == 'L' or (v[0] == 'X' and v[1] == 'L')}
            tri += [frozenset(v[1] for v in T_ if v[0] == 'L') for T_ in TR.SL.all_trisectors(g, lines)]
    return nm, sorted(map(sorted, p5)), sorted(map(sorted, p6)), sorted(map(sorted, tri)), len(free_lines), len(free_lines & A)


CONTROL = None

if __name__ == "__main__":
    manifest = json.loads((HERE / "manifest.json").read_text())
    bad = {q: dg for q, dg in manifest["parent_bindings"].items() if hashlib.sha256((ROOT / q).read_bytes()).hexdigest() != dg}
    status = {q: json.loads((ROOT / q).read_text()).get("status") for q in manifest["parent_bindings"]
              if q.endswith(("manifest.json", "result.json")) and q.startswith("proofs/")}
    check("0 dependency artifacts bound by hash; upstream proofs Proved",
          not bad and all(s in ("Proved", "passed") for s in status.values()), {"mismatched": bad, "statuses": status})

    stored = {sp["seed"]: (sp["trisums"], [tuple(l) for l in sp["lines"]]) for sp in SPACES}
    by_hash = collections.defaultdict(list)
    for s in stored:
        by_hash[FAM.HASH_SEEDS[s]].append(s)
    regen = {}
    for hs, seeds in sorted(by_hash.items()):
        regen.update(FAM.generated(seeds, hs))
    reproduced = {s: s in regen and regen[s][0] == stored[s][0] and FAM.isomorphic(regen[s][1], stored[s][1]) for s in stored}
    distinct = all(not FAM.isomorphic(stored[a][1], stored[b][1]) for a, b in itertools.combinations(sorted(stored), 2))
    check("1 the spaces: each of the 17 stored spaces is the generator's edge-atom space at its own seed (1 to 400, at most 60 lines), "
          "reproduced up to isomorphism under its recorded hash seed (the generator's Pfaffian signing depends on set order); they are "
          "pairwise non-isomorphic, and 7 come from HANDLE-COUNT B's seeds 1 to 40",
          len(stored) == 17 and set(stored) == set(FAM.HASH_SEEDS) and all(reproduced.values()) and distinct,
          {"seeds": sorted(stored), "hash seeds used": sorted(by_hash), "reproduced": sum(reproduced.values()),
           "pairwise non-isomorphic": distinct, "from seeds 1 to 40": sum(s <= 40 for s in stored)})

    with Pool(17) as pool:
        st = dict(pool.map(structure_task, SPACES))
    check("2 canonical structure: atoms are the 2-edge-cut sides (7 lines, 7 points), contracting them leaves a cubic brace that is neither "
          "planar nor Heawood, its trisectors are the trisum tree's squares, and atoms, junction line pairs, leaves, roots, loaded lines and "
          "skeleton are unchanged by relabeling lines and points (3 random relabelings each)",
          all(v["skeleton brace"] == "other" and v["relabeling-invariant"] for v in st.values()),
          {str(k): v for k, v in sorted(st.items())})

    train = [sp for sp in SPACES if sp["split"] == "training"]
    jobs = [(sp["seed"], M) for sp in train for M in range(len(sp["lines"]))]
    with Pool(22) as pool:
        rows = pool.map(row_task, jobs, chunksize=1)
        orig = pool.map(original_row, [(sp["seed"], 0) for sp in train], chunksize=1)
    costs = {sp["seed"]: MAPS[str(sp["seed"])]["rows"]["0"]["solutions"] for sp in train}
    check("3 the training maps: every row (293) recomputed by tr_lib.exact_row (one matrix product per pattern) equals the stored map, "
          "row 0 of each recomputed by CHAIN-TRANSFER B's exact_row equals it too; the training spaces cost at most 200,000 solutions",
          all(r[2] for r in rows) and len(rows) == 293 and all(r[2] for r in orig) and all(c <= 200000 for c in costs.values()),
          {"rows equal": sum(r[2] for r in rows), "rows": len(rows), "original-engine rows equal": sum(r[2] for r in orig),
           "costs": costs})

    with Pool(7) as pool:
        reps_ = dict(pool.map(report_task, [sp["seed"] for sp in train]))
    preds = [k for k in next(iter(reps_.values())) if k.startswith("P")]
    check("4 on the seven training spaces every frozen statement P1 to P7 holds",
          all(r[k] is True for r in reps_.values() for k in preds),
          {str(s): {k: v for k, v in r.items() if not k.startswith("P")} for s, r in sorted(reps_.items())})

    CONTROL = RL.NG.spaces()
    with Pool(22) as pool:
        ctl = pool.map(control_task, range(len(CONTROL)), chunksize=4)
    p5 = [(nm, p, t) for nm, p, q, t, f, fa in ctl if p]
    check("5 control on REFINE-READ's 277 spaces (atoms = lines of Heawood braces): a pair pinned apart from the atoms occurs once, in "
          "design 7, and is the line pair of the one trisector of its one non-planar brace; no pinned pair of yes/no creation alone occurs; "
          "every line no removal blocks is an atom line",
          len(p5) == 1 and p5[0][0] == "design 7" and p5[0][1] == p5[0][2] and not any(q for nm, p, q, t, f, fa in ctl)
          and all(f == fa for nm, p, q, t, f, fa in ctl),
          {"spaces": len(ctl), "pinned apart from atoms": p5, "pinned pairs (yes/no alone)": sum(len(q) for nm, p, q, t, f, fa in ctl),
           "lines no removal blocks": sum(f for nm, p, q, t, f, fa in ctl), "of them atom lines": sum(fa for nm, p, q, t, f, fa in ctl)})

    pr = (HERE / "predictions.json").read_bytes()
    fr = json.loads(pr)
    test_sha = sorted(r["lines sha256"] for r in fr["spaces"]["test"])
    have_sha = sorted(hashlib.sha256(json.dumps(sp["lines"]).encode()).hexdigest() for sp in SPACES if sp["split"] == "test")
    check("6 the freeze: predictions.json is the frozen file, names this library by hash, and lists as ticket B's spaces exactly the ten "
          "classes beyond the cost cap (none of whose maps had been computed when it was written)",
          hashlib.sha256(pr).hexdigest() == FROZEN and fr["library sha256 (tr_lib.py)"] == hashlib.sha256((HERE / "tr_lib.py").read_bytes()).hexdigest()
          and test_sha == have_sha and len(test_sha) == 10,
          {"frozen at": fr["frozen at"], "predictions": len(fr["predictions"]), "test spaces": [r["seed"] for r in fr["spaces"]["test"]]})

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
