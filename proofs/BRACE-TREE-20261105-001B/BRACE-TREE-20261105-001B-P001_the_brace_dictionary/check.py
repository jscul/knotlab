#!/usr/bin/env python3
"""Checks for BRACE-TREE-20261105-001B: the brace dictionary.

For every ordered pair of distinct lines, in every three-fold space up to 22 points and in trees of atoms up to 25 points, the place of
the pair in the tight-cut decomposition (dict_lib) against its native relation (brace_lib, ticket A). Prediction, fixed before evaluation:
the relation is a function of the place for pairs of lines in Heawood braces (atoms) and for pairs inside glue braces; pairs of an atom
line and a glue line are recorded too, without a prediction, since halos depend on the glue's faces.

    python3 -B check.py          verify result.json against a fresh run
    python3 -B check.py --write  write result.json (and dictionary.json) from a fresh run
Run with the repository's .venv (numpy, networkx, python-sat). Uses up to 22 processes (8 for spaces of 24 points or more)."""
import collections
import hashlib
import json
import sys
import time
from multiprocessing import Pool
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
import dict_lib as DL  # noqa: E402

GL = DL.GL
T0 = time.time()
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
    P4 = GL.plane(GL.PL.prism(4))
    off0 = min(k for k, L in enumerate(F[0]) if 0 not in L)
    thr0 = min(k for k, L in enumerate(F[0]) if 0 in L)
    inner = next(q for q in range(7) if q not in F[0][0])               # a point of an atom off its removed line
    l0 = next(k for k, L in enumerate(P4.H) if 0 in L)
    far = next(k for k, L in enumerate(P4.H) if 0 not in L and not set(L) & set(P4.H[l0]))
    A = lambda n, kind, key: (n, kind, key, F, 0, ID)  # noqa: E731
    return [
        ("Fano plane + X at a point", (FB, [A("X", "point", g(0))])),
        ("Fano plane + Y at a line", (FB, [A("Y", "line", g(0))])),
        ("Fano plane + X, W at two points", (FB, [A("X", "point", g(0)), A("W", "point", g(1))])),
        ("Fano plane + X at a point, Y at a line off it", (FB, [A("X", "point", g(0)), A("Y", "line", g(off0))])),
        ("Fano plane + X at a point, Y at a line through it", (FB, [A("X", "point", g(0)), A("Y", "line", g(thr0))])),
        ("Fano plane + Y, V at two lines", (FB, [A("Y", "line", g(0)), A("V", "line", g(1))])),
        ("Fano plane + X at a point, Z at a point of X", (FB, [A("X", "point", g(0)), A("Z", "point", ("X", inner))])),
        ("Fano plane + X at a point, Y at a line of X", (FB, [A("X", "point", g(0)), A("Y", "line", ("X", 1))])),
        ("Fano plane + Y at a line, Z at a point of Y", (FB, [A("Y", "line", g(0)), A("Z", "point", ("Y", 1))])),
        ("Fano plane + X, W, U at three points", (FB, [A("X", "point", g(0)), A("W", "point", g(1)), A("U", "point", g(2))])),
        ("Fano plane + a chain X, Z, Z2 of points", (FB, [A("X", "point", g(0)), A("Z", "point", ("X", inner)), A("Z2", "point", ("Z", inner))])),
        ("Fano plane + X at a point, Y at a line off it, Z at a point of X",
         (FB, [A("X", "point", g(0)), A("Y", "line", g(off0)), A("Z", "point", ("X", inner))])),
        ("census 58 + X at a point", (CB, [A("X", "point", g(0))])),
        ("census 58 + Y at a line", (CB, [A("Y", "line", g(1))])),
        ("prism(4) + X at a point, Y at a line through it", (P4, [A("X", "point", g(0)), A("Y", "line", g(l0))])),
        ("prism(4) + X at a point, Y at a far line", (P4, [A("X", "point", g(0)), A("Y", "line", g(far))])),
        ("prism(4) + Y at a line, Z at a point of Y", (P4, [A("Y", "line", g(l0)), A("Z", "point", ("Y", 1))])),
        ("prism(4) + X at a point, Z at a point of X", (P4, [A("X", "point", g(0)), A("Z", "point", ("X", inner))])),
    ]


def census():
    sys.path.insert(0, str(ROOT / "proofs/NATIVE-GENUS-20261104-001B/NATIVE-GENUS-20261104-001B-P001_counting_and_locating_handles"))
    import check as NGB  # noqa: E402
    return [(name, S) for name, S, kinds in NGB.census()]


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


def kind_of(place):
    if place[0] == "same":
        return "atom-atom" if place[1] == "heawood" else "glue-glue"
    ka = "atom" if place[1] == "heawood" else "glue"
    kb = "atom" if place[2] == "heawood" else "glue"
    return "atom-atom" if ka == kb == "atom" else ("glue-glue" if ka == kb == "glue" else "atom-glue")


def summarize(table):
    out = collections.defaultdict(lambda: {"places": 0, "places with one relation": 0, "pairs": 0, "pairs in such places": 0})
    for place, c in table.items():
        k = kind_of(place)
        n = sum(c.values())
        out[k]["places"] += 1
        out[k]["pairs"] += n
        if len(c) == 1:
            out[k]["places with one relation"] += 1
            out[k]["pairs in such places"] += n
    return dict(out)


if __name__ == "__main__":
    manifest = json.loads((HERE / "manifest.json").read_text())
    bad = {q: dg for q, dg in manifest["parent_bindings"].items() if hashlib.sha256((ROOT / q).read_bytes()).hexdigest() != dg}
    status = {q: json.loads((ROOT / q).read_text()).get("status") for q in manifest["parent_bindings"]
              if q.endswith(".json") and q.startswith("proofs/")}
    check("0 dependency artifacts bound by hash; upstream proofs Proved", not bad and all(s in ("Proved", "passed") for s in status.values()),
          {"mismatched": bad, "statuses": status})
    D = designs()
    cen = census()
    labels = [label for label, des in D] + [name for name, S in cen]
    spaces = [GL.build(des) for label, des in D] + [S for name, S in cen]
    with Pool(22) as pool:
        assert all(pool.map(fails, spaces, chunksize=1))
        res = evaluate(pool, spaces)
    table, where = DL.dictionary(list(zip(labels, spaces, res)))
    summ = summarize(table)
    mixed = {str(p): dict(c) for p, c in table.items() if len(c) > 1 and kind_of(p) != "atom-glue"}
    info = {"spaces": len(spaces), "designs": len(D), "census classes": len(cen), "summary": summ,
            "places with more than one relation (atom-atom and glue-glue)": mixed}
    check("1 the dictionary: places in the tight-cut decomposition against native relations, over every ordered pair of lines (the "
          "prediction, one relation per place for atom-atom and glue-glue pairs, is refuted where noted)", True, info)

    # -------------------------------------------------------------------------------------------- 2-4. where the tree decides
    trees = [DL.Tree(S) for S in spaces]
    atom_only = collections.defaultdict(collections.Counter)
    through_glue = collections.defaultdict(collections.Counter)
    glue_pairs = collections.Counter()
    cut_dirs = collections.Counter()
    for label, S, r, t in zip(labels, spaces, res, trees):
        for a in range(len(S.H)):
            for b in range(len(S.H)):
                if a == b:
                    continue
                ta, tb = t.types[t.owner[a]], t.types[t.owner[b]]
                between = DL.path_types(t, a, b)
                rel = DL.BL.relation(r, a, b)
                if ta == tb == "heawood":
                    p = t.place(a, b)
                    (atom_only if all(x == "heawood" for x in between) else through_glue)[p[:4] + (between,) + p[5:]][rel] += 1
                elif ta in ("planar", "doubled square") and tb in ("planar", "doubled square"):
                    glue_pairs[("through a non-Fano handle" if "other" in between else "plane glue only", rel)] += 1
        for k, (e, rcv, cl) in t.cuts.items():
            if t.types[e] == t.types[rcv] == "heawood":
                el = [x for x, b in t.owner.items() if b == e]
                rl = [x for x, b in t.owner.items() if b == rcv and x not in cl]
                rels = {DL.BL.relation(r, a, b) for a in el for b in rl}
                cut_dirs["one way, from the receiver's intact lines to the emitter" if rels == {"backward"} else "other: %s" % sorted(rels)] += 1
    det = lambda tab: (sum(1 for c in tab.values() if len(c) == 1), len(tab), sum(sum(c.values()) for c in tab.values() if len(c) == 1),  # noqa: E731
                       sum(sum(c.values()) for c in tab.values()))
    d1, d2 = det(atom_only), det(through_glue)
    rules = collections.Counter()
    for p, c in atom_only.items():
        rules[(p[0], p[3] if p[0] == "apart" else "", p[-2] if p[0] == "apart" else p[2], p[-1] if p[0] == "apart" else p[3],
               "/".join(sorted(c)))] += sum(c.values())
    info2 = {"atom-atom places with only atoms between (or adjacent, or the same atom)": {"places": d1[1], "with one relation": d1[0],
             "pairs": d1[3], "pairs in such places": d1[2]},
             "atom-atom places with plane glue between": {"places": d2[1], "with one relation": d2[0], "pairs": d2[3], "pairs in such places": d2[2]},
             "the rules (kind, arrows, role of a, role of b, relation): pairs": {" | ".join(k): v for k, v in sorted(rules.items())}}
    check("2 where the tree decides: every place whose two atoms are the same, adjacent, or joined through atoms only has one native "
          "relation; through plane glue (doubled squares, plane pieces) the relation can depend on more than the tree", d1[0] == d1[1], info2)
    check("3 glue is silent: lines of plane pieces and doubled squares never create at each other, unless a non-Fano handle lies between",
          all(rel == "silent" for (k, rel) in glue_pairs if k == "plane glue only"),
          {"%s: %s" % k: v for k, v in sorted(glue_pairs.items())})
    check("4 every cut between two atoms is read in its direction: creation runs one way, from the receiver's intact lines to the "
          "emitter's lines", set(cut_dirs) == {"one way, from the receiver's intact lines to the emitter"}, dict(cut_dirs))

    # -------------------------------------------------------------------------------------------- 5. the reconstruction fixed here
    rows5 = []
    for label, S, r, t in zip(labels, spaces, res, trees):
        kept, total = DL.source_blocks(S, r)
        heawood = sum(1 for x in t.types if x == "heawood")
        other = sum(1 for x in t.types if x == "other")
        rows5.append((label, GL.sat_genus(S), heawood, other, total, len(kept)))
    fano_only = [x for x in rows5 if x[3] == 0]
    info5 = {"spaces without a non-Fano brace": len(fano_only),
             "of them, kept blocks = Heawood braces = genus": sum(1 for x in fano_only if x[5] == x[2] == x[1]),
             "of them, all blocks = genus": sum(1 for x in fano_only if x[4] == x[1]),
             "spaces with a non-Fano brace (label, genus, Heawood, other, blocks, kept)": [x for x in rows5 if x[3] > 0],
             "(label, genus, Heawood braces, blocks, kept blocks) where blocks differ from kept": [(x[0], x[1], x[2], x[4], x[5]) for x in rows5 if x[4] != x[5]]}
    check("5 the source rule (fixed here, to be tested in ticket C): kept blocks of mutual creation count the Heawood braces, and the genus, "
          "on every space here without a non-Fano brace", all(x[5] == x[2] == x[1] for x in fano_only), info5)
    if "--write" in sys.argv:
        rows = [{"place": list(p), "relations": dict(c), "spaces": len({l for (pp, rel), ls in where.items() if pp == p for l in ls})}
                for p, c in sorted(table.items(), key=lambda kv: str(kv[0]))]
        (HERE / "dictionary.json").write_text(json.dumps(rows, indent=1, default=str) + "\n")

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
