"""Checks for HANDLE-COUNT-20261106-001B-P001 (counts by number of atoms).

  0 dependency artifacts bound by the hashes recorded in manifest.json
  1 the spaces: the census of three-fold classes up to 26 points (census22.json, this directory, and GLUE-READ B's 111 census spaces),
    GLUE-READ B's 80 random spaces with plane glue, the larger spaces of THREEFOLD-SURFACES B, and fresh plain spaces whose glue is a trisum
    brace (decorated with as few atoms as a greedy switching finds); each is cubic and not 2-colourable under its signing
  2 structure by number of atoms: braces, junctions J, planar braces p, atoms a, signed incidences s; Theorem 2 of ticket A
    (J + p <= a + s - 2) with its slack; trisum braces' genera by SAT
  3 counts: Z at lam = 2 and lam = 1+i, and colourings under a random signing, by ticket A's decomposition and by an independent
    elimination; junctions violating MGI and planar evaluations per space
  4 the table by number of atoms
  5 controls that must fail
Run: .venv/bin/python -B check.py [--write]   (networkx, sympy, python-sat)"""
import collections
import gzip
import hashlib
import itertools
import json
import os
import random
import sys
import time

from pysat.solvers import Solver

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
A = "proofs/HANDLE-COUNT-20261106-001A/HANDLE-COUNT-20261106-001A-P001_junctions_are_paid_for_by_atoms"
for d in ("proofs/THREEFOLD-SPACES-20261030-001A/THREEFOLD-SPACES-20261030-001A-P001_three_fold_spaces_are_built_from_the_fano_plane",
          "proofs/THREEFOLD-GRAMMAR-20261030-001A/THREEFOLD-GRAMMAR-20261030-001A-P001_fano_leaves_and_planar_glue",
          "proofs/SEYMOUR-COUNT-20261030-001B/SEYMOUR-COUNT-20261030-001B-P001_polynomial_counting_on_seymours_cubic_bound",
          "proofs/TWIST-COUNT-20261030-001A/TWIST-COUNT-20261030-001A-P001_the_knots_junction_is_a_similitude",
          "proofs/THREEFOLD-SURFACES-20261030-001A/THREEFOLD-SURFACES-20261030-001A-P001_fano_atoms_are_handles", A):
    sys.path.insert(0, os.path.join(ROOT, d))
import threefold_lib as T  # noqa: E402
import grammar_lib as M  # noqa: E402
import surface_lib as SU  # noqa: E402
import junction_lib as JL  # noqa: E402
import families as FA  # noqa: E402

T0 = time.time()
OUT = {}
OK_ALL = True
DIRECT_MAX = 60          # points: the independent elimination count is run up to this size (all spaces here are within it)


def report(name, ok, detail):
    global OK_ALL
    OK_ALL &= bool(ok)
    OUT[name] = {"ok": bool(ok), "detail": detail}
    print(("PASS " if ok else "FAIL ") + name, f"({time.time() - T0:.0f}s)", flush=True)


def min_signs(H, negs):
    """the fewest negated incidences in the switching class of negs (MaxSAT: one switch variable per point and per line)"""
    from pysat.examples.rc2 import RC2
    from pysat.formula import WCNF
    if not negs:
        return 0
    neg = set(map(tuple, negs))
    n = 1 + max(max(l) for l in H)
    w = WCNF()
    for i, l in enumerate(H):
        for p in l:
            a, b = p + 1, n + i + 1
            if (i, p) in neg:          # keep the negation unless exactly one end switches: want a xor b
                w.append([a, b], weight=1)
                w.append([-a, -b], weight=1)
            else:                      # want a == b
                w.append([-a, b], weight=1)
                w.append([a, -b], weight=1)
    with RC2(w) as rc:
        rc.compute()
        return rc.cost


def colourable(H, negs):
    neg = set(map(tuple, negs))
    with Solver(name='cadical153') as s:
        for i, l in enumerate(H):
            lits = [(p + 1) * (-1 if (i, p) in neg else 1) for p in l]
            s.add_clause(lits)
            s.add_clause([-x for x in lits])
        return s.solve()


# ---------------------------------------------------------------- 0
man = json.load(open(os.path.join(HERE, "manifest.json")))
mism = {r: dg for r, dg in man["parent_bindings"].items()
        if hashlib.sha256(open(os.path.join(ROOT, r), "rb").read()).hexdigest() != dg}
report("0 dependency artifacts bound by hash", not mism, {"parents": len(man["parent_bindings"]), "mismatched": mism})

# ---------------------------------------------------------------- 1 the spaces
spaces = []                                     # (source, name, lines, signed incidences)
for d in json.load(open(os.path.join(HERE, "census22.json"))):
    spaces.append(("census <= 22", d["name"], [tuple(l) for l in d["lines"]], [tuple(d["twist"])] if d["twist"] else []))
with gzip.open(os.path.join(ROOT, "proofs/GLUE-READ-20261106-001B/GLUE-READ-20261106-001B-P001_what_plane_glue_does/maps.json.gz"),
               "rt") as f:
    payload = json.load(f)
for d in payload["spaces"]:
    negs = [(i, p) for i, (l, bits) in enumerate(zip(d["lines"], d["signs"])) for p, b in zip(l, bits) if b]
    spaces.append(("GLUE-READ " + d["source"], d["name"], [tuple(l) for l in d["lines"]], negs))
F7 = T.FANO
comp = T.point_splice(F7, 0, F7, F7[0])
for k in range(3, 5):
    comp = T.point_splice(comp, 0, F7, F7[0])
    spaces.append(("THREEFOLD-SURFACES B", f"Fano composition of {k} planes", [tuple(l) for l in comp], []))
spaces.append(("THREEFOLD-SURFACES B", "5-cycle of Fano blocks", M.decorate([(0, 1, 1), (1, 2, 2), (2, 3, 3), (3, 4, 4), (4, 0, 0)], []), []))
spaces.append(("THREEFOLD-SURFACES B", "twisted cube", M.decorate(M.K4, M.kasteleyn_signing(M.K4)), []))
P6 = M.cubic_planar_bipartite('hexagonal prism')
spaces.append(("THREEFOLD-SURFACES B", "hexagonal prism as glue", M.decorate(P6, M.kasteleyn_signing(P6)), []))
CORE35 = [(0, 1, 2), (0, 1, 3), (0, 4, 5), (1, 6, 7), (2, 6, 8), (2, 7, 9), (3, 4, 6), (3, 5, 7), (4, 8, 8), (5, 9, 9)]
spaces.append(("THREEFOLD-SURFACES B", "trisum of three cubes as glue (35)", M.decorate(CORE35, [(0, 0)]), []))
pool = FA.planar_pool()
cube_pool = {'cube': pool['cube']}
fresh = []
for seed in range(1, 41):
    nsum = 1 + seed % 3
    G = FA.trisum_brace(seed, nsum, cube_pool if seed % 2 else pool)
    Hg, kap, nsq = FA.pfaffian_signing(G)
    negs, cost = FA.cheap_switching(Hg, kap, seed=seed)
    D = M.decorate(Hg, negs)
    if len(D) <= DIRECT_MAX:
        fresh.append(("fresh trisum glue (T14 decoration)", f"seed {seed}: {nsum} trisums, glue {len(Hg)} points", D, []))
    # the same glue with a knot's edge atom on each sign of a fewest-sign Pfaffian signing (ticket A, Proposition 6)
    mn, nu = FA.min_signing(Hg, kap)
    E = FA.edge_atoms(Hg, mn)
    if len(E) <= DIRECT_MAX:
        fresh.append(("fresh trisum glue (edge atoms)", f"seed {seed}: {nsum} trisums, glue {len(Hg)} points, {nu} signs", E, []))
seen_fresh = set()
for src, nm, H, negs in fresh:
    key = tuple(sorted(tuple(sorted(l)) for l in H))
    if key not in seen_fresh:                      # identical systems from different seeds are counted once
        seen_fresh.add(key)
        spaces.append((src, nm, H, negs))
ok1 = True
d1 = collections.Counter()
for src, nm, H, negs in spaces:
    cubic = T.is_cubic(H) and all(len(set(l)) == 3 for l in H)
    ok1 &= cubic and not colourable(H, negs)
    d1[src] += 1
report("1 the spaces: cubic, simple, not 2-colourable under their signings", ok1, dict(d1))

# ---------------------------------------------------------------- 2 structure by atoms
rows = []
ok2 = True
genus_cache = {}
for src, nm, H, negs in spaces:
    a, p, js, kinds = JL.structure(H)
    J = sum(js)
    s = min_signs(H, negs)
    heawood_only = dict(kinds) == {'heawood': 1}       # B(H) is the Heawood graph (H is the Fano plane): excluded by Theorem 2
    holds = J + p <= a + s - 2 or heawood_only
    ok2 &= holds
    tg = []
    if js:
        for b in JL.decompose(JL.labelled(H)):
            if JL.brace_kind(b) == 'other':
                edges = [(u, w) for u in b for e, w in b[u] if str(u) < str(w)]
                key = tuple(sorted(map(str, edges)))
                if key not in genus_cache:
                    genus_cache[key] = SU.genus(edges)
                tg.append(genus_cache[key])
    rows.append({"source": src, "name": nm, "points": len(H), "atoms": a, "planar": p, "junctions": js, "J": J, "signed": s, "signed as given": len(negs),
                 "doubled squares": kinds.get('doubled square', 0), "trisum brace genera": tg, "slack": a + s - 2 - J - p,
                 "holds": holds, "Heawood graph (excluded)": heawood_only})
inc = [r for r in rows if not r["Heawood graph (excluded)"]]
report("2 Theorem 2 of ticket A on every space other than the Fano plane: J + p <= a + s - 2", ok2,
       {"spaces": len(rows), "excluded (the Fano plane)": len(rows) - len(inc), "with trisum glue": sum(1 for r in inc if r["J"]),
        "minimum slack": min(r["slack"] for r in inc),
        "spaces at slack 0": [(r["name"], r["atoms"], r["J"], r["planar"], r["signed"]) for r in inc if r["slack"] == 0][:12]})

# ---------------------------------------------------------------- 3 counts
LAMS = [2, JL.GQ(1, 1)]
r3 = random.Random(3)
ok3 = True
for row, (src, nm, H, negs) in zip(rows, spaces):
    row["counts"] = {}
    rnd = [(i, p) for i, l in enumerate(H) for p in l if r3.random() < 0.15]
    cases = [(f"lam {lm}", negs, lm) for lm in LAMS] + [("colourings, random signing", rnd, 0)]
    for label, sg, lm in cases:
        v, rep = JL.count_by_braces(H, sg, lm)
        recs = [x for rr in rep["trisum records"] for x in rr]
        d = JL.direct_count(H, sg, lm) if len(H) <= DIRECT_MAX else None
        agree = d is None or d == v
        ok3 &= agree and rep["ternary tensors even"] and all(nev == 2 ** bad for _, h, bad, nev in recs)
        row["counts"][label] = {"value": JL.num_json(v), "direct agrees": agree if d is not None else "not run",
                                "violating junctions": sum(b for _, h, b, n in recs),
                                "max violating per piece": max([b for _, h, b, n in recs], default=0),
                                "piece evaluations": sum(n for *_, n in recs)}
report("3 counts by ticket A's decomposition = independent elimination, at lam = 2, lam = 1+i and for colourings under a random signing",
       ok3, {"spaces counted": len(rows), "direct counts": sum(1 for r in rows if r["points"] <= DIRECT_MAX)})

# ---------------------------------------------------------------- 4 the table by number of atoms
table = collections.defaultdict(lambda: collections.Counter())
for r in rows:
    t = table[r["atoms"]]
    t["spaces"] += 1
    t["with trisum glue"] += r["J"] > 0
    t["max J"] = max(t["max J"], r["J"])
    t["max planar braces"] = max(t["max planar braces"], r["planar"])
    for label, c in r["counts"].items():
        key = "max violating per piece (" + label + ")"
        t[key] = max(t[key], c["max violating per piece"])
by_atoms = {a: dict(t) for a, t in sorted(table.items())}
ok4 = len(by_atoms) > 1 and all(len(r["counts"]) == 3 for r in rows) and sum(t["spaces"] for t in by_atoms.values()) == len(rows)
report("4 the table by number of atoms", ok4, by_atoms)

# ---------------------------------------------------------------- 5 controls
c = {}
src, nm, H, negs = next(s for s in spaces if s[1].startswith("trisum of three cubes"))
v_direct = JL.direct_count(H, [], 2)
orig = JL.split_hat
JL.split_hat = lambda hat: (lambda M_, C_: (M_, {k: 2 * v for k, v in C_.items()}))(*orig(hat))
v_bad, _ = JL.count_by_braces(H, [], 2)
JL.split_hat = orig
c["a doubled split remainder makes the decomposition disagree with the direct count"] = v_bad != v_direct
tw = [r for r in rows if r["J"] > 0 and r["signed"] > 0]
c["with the signs ignored the bound fails on a signed space with trisum glue"] = bool(tw) and any(
    r["J"] + r["planar"] > r["atoms"] - 2 for r in tw)
orig_vf = JL.vertex_factor
first_line = [('L', 0)]
def bent(g, v, sign, lam, tensors):
    e, t = orig_vf(g, v, sign, lam, tensors)
    if v == first_line[0]:
        # double one complementary pair of entries: the factor stays symmetric under flipping every colour (even in the y-basis),
        # so the decomposition runs and only the count can disagree
        k0 = min(t)
        k1 = tuple(1 - b for b in k0)
        t = {k: (2 * x if k in (k0, k1) else x) for k, x in t.items()}
    return e, t
JL.vertex_factor = bent
v_w, _ = JL.count_by_braces(H, [], 2)
JL.vertex_factor = orig_vf
c["one line's table changed inside the decomposition makes it disagree with the direct count"] = v_w != v_direct
report("5 controls: a wrong split, ignored signs and a changed line are caught", all(c.values()), c)

res = {"schema_version": 1, "artifact_id": "HANDLE-COUNT-20261106-001B-P001", "status": "passed" if OK_ALL else "failed",
       "checks": OUT, "rows": rows, "seconds": round(time.time() - T0, 1)}
print("all ok" if OK_ALL else "SOME CHECK FAILED", res["seconds"], "s")
if "--write" in sys.argv:
    with open(os.path.join(HERE, "result.json"), "w") as fh:
        json.dump(res, fh, indent=1, default=str)
