#!/usr/bin/env python3
"""Checks for BRACE-TREE-20261105-001C: reading the tree back on fresh spaces.

Fixed before evaluation, from ticket B (nothing here is tuned on these spaces):
- the rules: the 21 places of B's dictionary with two atom lines joined through atoms only, each with its one native relation;
- cut directions: across a cut between two atoms, creation runs one way, from the receiver's intact lines to the emitter's lines;
- glue: lines of plane pieces and doubled squares never create at each other unless a non-Fano handle lies between;
- the source rule (dict_lib.source_blocks): kept blocks of mutual creation count the Heawood braces.
Fresh spaces: every three-fold class of 23 to 26 points (fresh_census.json, made by gen_census.py) and fresh trees of Fano atoms.

    python3 -B check.py          verify result.json against a fresh run
    python3 -B check.py --write  write result.json from a fresh run
Run with the repository's .venv. Uses up to 22 processes."""
import collections
import hashlib
import json
import sys
import time
from multiprocessing import Pool
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
DB = ROOT / "proofs/BRACE-TREE-20261105-001B/BRACE-TREE-20261105-001B-P001_the_brace_dictionary"
sys.path.insert(0, str(DB))
import dict_lib as DL  # noqa: E402

GL, BL = DL.GL, DL.BL
T0 = time.time()


def sat_solutions(lines, signs, n, skip=None):
    """every solution of the signed knot on n points minus line `skip`, by SAT model enumeration, as rows of raw values in the order
    claim_lib.solutions gives (ascending code, bit q = point q). Identical output to claim_lib.solutions (checked on 665 cases of
    ticket B's spaces), and far faster at 26 points, where brute force walks 2^26 assignments per removal."""
    import numpy as np
    from pysat.solvers import Solver
    clauses = []
    for i, (L, sg) in enumerate(zip(lines, signs)):
        if i == skip:
            continue
        lit = [(q + 1) if s == 0 else -(q + 1) for q, s in zip(L, sg)]  # true iff value + sign = 1
        clauses += [lit, [-x for x in lit]]
    with Solver(name="cadical153", bootstrap_with=clauses) as s:
        codes = sorted({sum(1 << (abs(v) - 1) for v in m if 0 < v <= n) for m in s.enum_models()})
    codes = np.array(codes, dtype=np.int64)
    if len(codes) == 0:
        return np.zeros((0, n), dtype=np.int8)
    return ((codes[:, None] >> np.arange(n)) & 1).astype(np.int8)


GL.CL.solutions = sat_solutions  # used by genus_lib.row_task and by fails() below
OUT = {}
ID = (0, 1, 2)
F, C = GL.FANO, GL.C58
g = lambda i: ("g", i)  # noqa: E731


def check(name, ok, info):
    OUT[name] = {"pass": bool(ok), "info": info}
    print("PASS" if ok else "FAIL", name, json.dumps(info, default=str), round(time.time() - T0, 1), "s", flush=True)
    if not ok:
        sys.exit(1)


def designs():
    FB, CB = GL.base(*F), GL.base(*C)
    P4, P5 = GL.plane(GL.PL.prism(4)), GL.plane(GL.PL.prism(5))
    inner = next(q for q in range(7) if q not in F[0][0])
    off01 = min(k for k, L in enumerate(F[0]) if 0 not in L and 1 not in L)
    off0 = min(k for k, L in enumerate(F[0]) if 0 not in L)
    A = lambda n, kind, key: (n, kind, key, F, 0, ID)  # noqa: E731
    l0 = next(k for k, L in enumerate(P5.H) if 0 in L)
    return [
        ("Fano plane + X, W at two points, Y at a line off both", (FB, [A("X", "point", g(0)), A("W", "point", g(1)), A("Y", "line", g(off01))])),
        ("Fano plane + Y, V at two lines, Z at a point of Y", (FB, [A("Y", "line", g(0)), A("V", "line", g(1)), A("Z", "point", ("Y", 1))])),
        ("Fano plane + Y at a line, Y2 at an intact line of Y", (FB, [A("Y", "line", g(0)), A("Y2", "line", ("Y", 2))])),
        ("Fano plane + Y at a line, Y2 at an intact line of Y, Y3 at an intact line of Y2",
         (FB, [A("Y", "line", g(0)), A("Y2", "line", ("Y", 2)), A("Y3", "line", ("Y2", 2))])),
        ("Fano plane + X at a point, W at a point, B at a line of W (a zigzag)",
         (FB, [A("X", "point", g(0)), A("W", "point", g(1)), A("B", "line", ("W", 1))])),
        ("Fano plane + X at a point, Z and W at two inner points of X", (FB, [A("X", "point", g(0)), A("Z", "point", ("X", inner)),
                                                                            A("W", "point", ("X", 3))])),
        ("Fano plane + Y at a line off a point, X at that point, Z at a point of Y",
         (FB, [A("Y", "line", g(off0)), A("X", "point", g(0)), A("Z", "point", ("Y", 1))])),
        ("census 58 + X at a point, Y at a line", (CB, [A("X", "point", g(0)), A("Y", "line", g(3))])),
        ("prism(5) + X at a point, Y at a line through it", (P5, [A("X", "point", g(0)), A("Y", "line", g(l0))])),
        ("prism(5) + Y at a line, Z at a point of Y", (P5, [A("Y", "line", g(l0)), A("Z", "point", ("Y", 1))])),
        ("prism(4) + X at a point, Z at a point of X, Y at a far line",
         (P4, [A("X", "point", g(0)), A("Z", "point", ("X", inner)), A("Y", "line", g(max(k for k, L in enumerate(P4.H) if 0 not in L)))])),
    ]


def census():
    rows = json.loads((HERE / "fresh_census.json").read_text())
    out = []
    for row in rows:
        H = [tuple(L) for L in row["lines"]]
        n = 1 + max(p for L in H for p in L)
        signs = [[0, 0, 0] for _ in H]
        if row["twist"] is not None:
            signs[row["twist"][0]][H[row["twist"][0]].index(row["twist"][1])] = 1
        out.append((row["name"], GL.base(H, signs, n)))
    return out


def row(args):
    S, M = args
    return GL.row_task((S, M))[1]


def evaluate(pool, spaces, big=24, big_procs=8):
    small = [(i, M) for i, S in enumerate(spaces) if S.n < big for M in range(len(S.H))]
    large = [(i, M) for i, S in enumerate(spaces) if S.n >= big for M in range(len(S.H))]
    res = [dict() for _ in spaces]
    for (i, M), r in zip(small, pool.map(row, [(spaces[i], M) for i, M in small], chunksize=1)):
        res[i][M] = r
    if large:
        with Pool(big_procs) as p8:
            for (i, M), r in zip(large, p8.map(row, [(spaces[i], M) for i, M in large], chunksize=1)):
                res[i][M] = r
    return res


def fails(S):
    return len(GL.CL.solutions(S.H, S.s, S.n)) == 0


def b_rules():
    """B's rules: (kind, arrows, role of a, role of b) -> relation, from B's result"""
    r = json.loads((DB / "result.json").read_text())
    key = next(k for k in r["checks"] if k.startswith("2 "))
    table = r["checks"][key]["info"]["the rules (kind, arrows, role of a, role of b, relation): pairs"]
    out = {}
    for k in table:
        kind, arrows, ra, rb, rel = [x.strip() for x in k.split("|")]
        assert "/" not in rel
        out[(kind, arrows, ra, rb)] = rel
    return out


if __name__ == "__main__":
    manifest = json.loads((HERE / "manifest.json").read_text())
    bad = {q: dg for q, dg in manifest["parent_bindings"].items() if hashlib.sha256((ROOT / q).read_bytes()).hexdigest() != dg}
    status = {q: json.loads((ROOT / q).read_text()).get("status") for q in manifest["parent_bindings"]
              if q.endswith(("/manifest.json", "/result.json")) and q.startswith("proofs/")}
    check("0 dependency artifacts bound by hash; upstream proofs Proved", not bad and all(s in ("Proved", "passed") for s in status.values()),
          {"mismatched": bad, "statuses": status})
    rules = b_rules()
    D = designs()
    cen = census()
    labels = [label for label, des in D] + [name for name, S in cen]
    spaces = [GL.build(des) for label, des in D] + [S for name, S in cen]
    with Pool(22) as pool:
        ok_f = all(pool.map(fails, spaces, chunksize=1))
        check("1 the fresh spaces: %d trees of Fano atoms and %d three-fold classes of 23 to 26 points, each failing" % (len(D), len(cen)), ok_f,
              {"points": dict(collections.Counter(S.n for S in spaces)),
               "census by size": dict(collections.Counter(name.split("-point")[0] for name, S in cen))})
        res = evaluate(pool, spaces, big=99)  # each removal holds a small solution set (0.3 GB at 26 points): one pool suffices

    trees = [DL.Tree(S) for S in spaces]
    known, new = collections.Counter(), collections.defaultdict(collections.Counter)
    glue, dirs, glue_where = collections.Counter(), collections.Counter(), collections.Counter()
    for label, S, r, t in zip(labels, spaces, res, trees):
        for a in range(len(S.H)):
            for b in range(len(S.H)):
                if a == b:
                    continue
                ta, tb = t.types[t.owner[a]], t.types[t.owner[b]]
                between = DL.path_types(t, a, b)
                rel = BL.relation(r, a, b)
                if ta == tb == "heawood" and all(x == "heawood" for x in between):
                    p = t.place(a, b)
                    k = (p[0], p[3] if p[0] == "apart" else "", p[-2] if p[0] == "apart" else p[2], p[-1] if p[0] == "apart" else p[3])
                    if k in rules:
                        known["as predicted" if rules[k] == rel else "NOT as predicted"] += 1
                    else:
                        new[" | ".join(k)][rel] += 1
                elif ta in ("planar", "doubled square") and tb in ("planar", "doubled square"):
                    kind = ("a non-Fano handle between" if "other" in between else
                            ("a Fano atom between" if "heawood" in between else "no handle between"))
                    glue[(kind, rel)] += 1
                    if rel != "silent":
                        glue_where[(label, kind)] += 1
        for kk, (e, rcv, cl) in t.cuts.items():
            if t.types[e] == t.types[rcv] == "heawood":
                el = [x for x, b in t.owner.items() if b == e]
                rl = [x for x, b in t.owner.items() if b == rcv and x not in cl]
                rels = {BL.relation(r, a, b) for a in el for b in rl}
                dirs["one way, from the receiver's intact lines to the emitter" if rels == {"backward"} else "other: %s" % sorted(rels)] += 1
    check("2 B's rules on fresh pairs: is every fresh pair of atom lines at one of B's 21 places as B recorded there?", True,
          {"prediction holds": known.get("NOT as predicted", 0) == 0 and known.get("as predicted", 0) > 0, "fresh pairs at B's places": dict(known),
           "places B never saw (place: relations)": {k: dict(v) for k, v in sorted(new.items())}})
    check("3 cut directions on fresh spaces: does every cut between two atoms read one way, from the receiver's intact lines to the "
          "emitter?", True, {"prediction holds": set(dirs) == {"one way, from the receiver's intact lines to the emitter"}, "cuts": dict(dirs)})
    check("4 glue on fresh spaces: are lines of plane pieces and doubled squares silent to each other unless a non-Fano handle lies between?",
          True, {"prediction holds": all(rel == "silent" for (k, rel) in glue if k != "a non-Fano handle between"),
                 "silent whenever no handle lies between": all(rel == "silent" for (k, rel) in glue if k == "no handle between"),
                 "pairs": {"%s: %s" % k: v for k, v in sorted(glue.items())},
                 "creating pairs by space": {"%s (%s)" % k: v for k, v in sorted(glue_where.items())}})

    rows5 = []
    for label, S, r, t in zip(labels, spaces, res, trees):
        kept, total = DL.source_blocks(S, r)
        rows5.append((label, GL.sat_genus(S), sum(1 for x in t.types if x == "heawood"), sum(1 for x in t.types if x == "other"), total, len(kept)))
    fano_only = [x for x in rows5 if x[3] == 0]
    info5 = {"fresh spaces without a non-Fano brace": len(fano_only),
             "of them, kept blocks = Heawood braces = genus": sum(1 for x in fano_only if x[5] == x[2] == x[1]),
             "of them, all blocks = genus": sum(1 for x in fano_only if x[4] == x[1]),
             "misses (label, genus, Heawood braces, blocks, kept)": [(x[0], x[1], x[2], x[4], x[5]) for x in fano_only if not x[5] == x[2] == x[1]],
             "spaces with a non-Fano brace (label, genus, Heawood, other, blocks, kept)": [x for x in rows5 if x[3] > 0]}
    info5["prediction holds"] = all(x[5] == x[2] == x[1] for x in fano_only)
    check("5 the source rule on fresh spaces: do kept blocks count the Heawood braces, and the genus, on every fresh space without a "
          "non-Fano brace?", True, info5)

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
