#!/usr/bin/env python3
"""Checks for NATIVE-GENUS-20261104-001B: counting and locating handles.

The statistic, fixed before evaluation (genus_lib, ticket A): the creation map, exact; the quiet part, every largest set of lines among
which no removal creates at a gluing line in either direction; the creative part, the rest; the native count, the number of pieces of
the creative part, through shared points and through interior points (points all of whose lines are creative), over every quiet part.
Ground truth: the SAT genus of the incidence graph.

    python3 -B check.py          verify result.json against a fresh run
    python3 -B check.py --write  write result.json from a fresh run
Run with the repository's .venv (numpy, networkx, python-sat). Uses up to 22 processes. About three hours."""
import collections
import hashlib
import itertools
import json
import os
import sys
import time
from multiprocessing import Pool
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "proofs/NATIVE-GENUS-20261104-001A/NATIVE-GENUS-20261104-001A-P001_the_creation_map_splits_by_atom"))
import genus_lib as GL  # noqa: E402

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


# ------------------------------------------------------------------------------------------------ families
GLUES = [("cube", lambda: GL.FL.octahedral(0)), ("prism(3)", lambda: GL.PL.prism(3)), ("prism(4)", lambda: GL.PL.prism(4)),
         ("prism(5)", lambda: GL.PL.prism(5)), ("prism(6)", lambda: GL.PL.prism(6)), ("grid16", lambda: GL.FL.octahedral(1))]
GL_ = dict(GLUES)


def singles():
    out = []
    for gname, mk in GLUES:
        S0 = GL.plane(mk())
        out += [(f"{gname}: Fano at point {p}", (S0, [("A", "point", g(p), F, 0, ID)])) for p in range(S0.n)]
        out += [(f"{gname}: Fano at line {l}", (S0, [("A", "line", g(l), F, 0, ID)])) for l in range(len(S0.H))]
    for gname in ("cube", "prism(3)", "prism(4)"):
        S0 = GL.plane(GL_[gname]())
        out += [(f"{gname}: census 58 minus line {e} at point {p}", (S0, [("A", "point", g(p), C, e, ID)]))
                for p in range(S0.n) for e in range(8)]
        out += [(f"{gname}: census 58 split at point {e} at line {l}", (S0, [("A", "line", g(l), C, e, ID)]))
                for l in range(len(S0.H)) for e in range(8)]
    S0 = GL.plane(GL_["cube"]())
    for perm in itertools.permutations(range(3)):
        if perm == ID:
            continue
        out += [(f"cube: census 58 minus line {e} at point {p}, ports {perm}", (S0, [("A", "point", g(p), C, e, perm)]))
                for p in range(S0.n) for e in range(8)]
        out += [(f"cube: census 58 split at point {e} at line {l}, ports {perm}", (S0, [("A", "line", g(l), C, e, perm)]))
                for l in range(len(S0.H)) for e in range(8)]
    return out


def pairs():
    out = []
    for gname in ("prism(4)", "prism(5)"):
        S0 = GL.plane(GL_[gname]())
        P, Ls = range(S0.n), range(len(S0.H))
        out += [(f"{gname}: Fano at points {p}, {q}", (S0, [("A", "point", g(p), F, 0, ID), ("B", "point", g(q), F, 0, ID)]))
                for p, q in itertools.combinations(P, 2)]
        out += [(f"{gname}: Fano at lines {l}, {m}", (S0, [("A", "line", g(l), F, 0, ID), ("B", "line", g(m), F, 0, ID)]))
                for l, m in itertools.combinations(Ls, 2)]
        out += [(f"{gname}: Fano at point {p} and line {l}", (S0, [("A", "point", g(p), F, 0, ID), ("B", "line", g(l), F, 0, ID)]))
                for p in P for l in Ls]
    S0 = GL.plane(GL_["prism(4)"]())
    P, Ls = range(S0.n), range(len(S0.H))
    out += [(f"prism(4): census 58 at point {p}, Fano at point {q}", (S0, [("A", "point", g(p), C, 0, ID), ("B", "point", g(q), F, 0, ID)]))
            for p in P for q in P if q != p]
    out += [(f"prism(4): census 58 at line {l}, Fano at line {m}", (S0, [("A", "line", g(l), C, 0, ID), ("B", "line", g(m), F, 0, ID)]))
            for l in Ls for m in Ls if m != l]
    out += [(f"prism(4): census 58 at point {p} and at line {l}", (S0, [("A", "point", g(p), C, 0, ID), ("B", "line", g(l), C, 0, ID)]))
            for p in P for l in Ls]
    return out


def triples():
    out = []
    S0 = GL.plane(GL_["cube"]())
    P, Ls = range(S0.n), range(len(S0.H))
    out += [(f"cube: Fano at points {t}", (S0, [(n, "point", g(p), F, 0, ID) for n, p in zip("ABC", t)])) for t in itertools.combinations(P, 3)]
    out += [(f"cube: Fano at lines {t}", (S0, [(n, "line", g(l), F, 0, ID) for n, l in zip("ABC", t)])) for t in itertools.combinations(Ls, 3)]
    out += [(f"cube: Fano at points {t} and line {l}", (S0, [("A", "point", g(t[0]), F, 0, ID), ("B", "point", g(t[1]), F, 0, ID),
                                                          ("C", "line", g(l), F, 0, ID)])) for t in itertools.combinations(P, 2) for l in Ls]
    out += [(f"cube: Fano at point {p} and lines {t}", (S0, [("A", "point", g(p), F, 0, ID), ("B", "line", g(t[0]), F, 0, ID),
                                                          ("C", "line", g(t[1]), F, 0, ID)])) for p in P for t in itertools.combinations(Ls, 2)]
    S0 = GL.plane(GL_["prism(4)"]())
    coll = lambda p, q: any(p in L and q in L for L in S0.H)  # noqa: E731
    spread = sorted(itertools.combinations(range(S0.n), 3), key=lambda t: (sum(coll(a, b) for a, b in itertools.combinations(t, 2)), t))
    out += [(f"prism(4): Fano at points {t}", (S0, [(n, "point", g(p), F, 0, ID) for n, p in zip("ABC", t)])) for t in spread[:3]]
    p, q = next((a, b) for a, b in itertools.combinations(range(S0.n), 2) if not coll(a, b))
    l = min(k for k, L in enumerate(S0.H) if p not in L and q not in L)
    out.append((f"prism(4): Fano at points {p}, {q} and line {l}", (S0, [("A", "point", g(p), F, 0, ID), ("B", "point", g(q), F, 0, ID),
                                                                       ("C", "line", g(l), F, 0, ID)])))
    disj = [t for t in itertools.combinations(range(len(S0.H)), 3) if all(not set(S0.H[a]) & set(S0.H[b]) for a, b in itertools.combinations(t, 2))]
    if disj:
        out.append((f"prism(4): Fano at lines {disj[0]}", (S0, [(n, "line", g(l), F, 0, ID) for n, l in zip("ABC", disj[0])])))
    return out


def on_atoms():
    out = []
    FB, CB = GL.base(*F), GL.base(*C)
    out.append(("the Fano plane: Fano at point 0", (FB, [("A", "point", g(0), F, 0, ID)])))
    out.append(("the Fano plane: Fano at line 0", (FB, [("A", "line", g(0), F, 0, ID)])))
    out += [(f"census 58: Fano at point {p}", (CB, [("A", "point", g(p), F, 0, ID)])) for p in range(8)]
    out += [(f"census 58: Fano at line {l}", (CB, [("A", "line", g(l), F, 0, ID)])) for l in range(8)]
    out.append(("the Fano plane: Fano at points 0 and 1", (FB, [("A", "point", g(0), F, 0, ID), ("B", "point", g(1), F, 0, ID)])))
    l = min(k for k, L in enumerate(F[0]) if 0 not in L)
    out.append((f"the Fano plane: Fano at point 0 and line {l}", (FB, [("A", "point", g(0), F, 0, ID), ("B", "line", g(l), F, 0, ID)])))
    inner = next(q for q in range(7) if q not in F[0][0])
    out.append((f"the Fano plane: Fano at point 0, and Fano at point {inner} of that atom",
                (FB, [("A", "point", g(0), F, 0, ID), ("B", "point", ("A", inner), F, 0, ID)])))
    return out


def census():
    """the 8 untwisted and 24 twisted three-fold classes up to 22 points, rebuilt as in THREEFOLD-SURFACES-20261030-001B, section 1"""
    TA = ROOT / "proofs/THREEFOLD-SPACES-20261030-001A/THREEFOLD-SPACES-20261030-001A-P001_three_fold_spaces_are_built_from_the_fano_plane"
    GA = ROOT / "proofs/THREEFOLD-GRAMMAR-20261030-001A/THREEFOLD-GRAMMAR-20261030-001A-P001_fano_leaves_and_planar_glue"
    GB = ROOT / "proofs/THREEFOLD-GRAMMAR-20261030-001B/THREEFOLD-GRAMMAR-20261030-001B-P001_census_with_doubled_incidences"
    for p in (TA, GA, GB):
        sys.path.insert(0, str(p))
    import threefold_lib as T  # noqa: E402
    import grammar_lib as M  # noqa: E402
    import census_lib as CE  # noqa: E402
    spaces = [("untwisted Fano (7)", T.FANO, None)]
    for tw in (False, True):
        byN = collections.defaultdict(list)
        for n in range(1, 11):
            for H, c in CE.census(n, tw):
                for L in range(2, 2 * n + 1):
                    if n + 6 * L > 22:
                        break
                    for Sset in CE.covers(H, L):
                        pts, lns = [p for k, p in Sset if k == 'P'], [i for k, i in Sset if k == 'L']
                        byN[n + 6 * L].append(CE.decorate_pieces(H, pts, lns, (0, 0)) if tw else (CE.decorate_pieces(H, pts, lns), None))
        for N in sorted(byN):
            cls = CE.classify([D for D, t in byN[N]], [t for D, t in byN[N]] if tw else None)
            for k, (H, cnt, t) in enumerate(cls):
                spaces.append((("twisted " if tw else "untwisted ") + f"{N}-point class {k}", H, t))
    out = []
    for name, H, t in spaces:
        H = [tuple(L) for L in H]
        n = T.npoints(H)
        signs = [[0, 0, 0] for _ in H]
        if t is not None:  # the twisted incidence (line, point) is complemented
            signs[t[0]][H[t[0]].index(t[1])] = 1
        kinds = collections.Counter(M.brace_type(b)[0] for b in M.decompose(M.multigraph(H)))
        out.append((name, GL.base(H, signs, n), dict(kinds)))
    return out


# ------------------------------------------------------------------------------------------------ evaluation
def row(args):
    S, M = args
    return GL.row_task((S, M))[1]


def evaluate(pool, spaces, big=24, big_procs=8):
    """spaces: list of Space; the exact creation map of each, with removals spread over the pool. Removals of spaces with at least `big`
    points run on a smaller pool, since each holds a large solution set in memory."""
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


def blocks(S, res, nat):
    """exploratory, fixed before evaluation: within each interior piece, the number of maximal blocks of lines that create at one another
    in both directions (maximal cliques of mutual creation on the creative lines through the piece's points), summed over pieces"""
    import networkx as nx
    total = 0
    for piece in nat["interior pieces"]:
        ls = sorted({k for k in nat["V"] if set(S.H[k]) & set(piece)})
        m = nx.Graph()
        m.add_nodes_from(ls)
        m.add_edges_from((a, b) for a in ls for b in ls if a < b and GL.creates(res, a, b) and GL.creates(res, b, a))
        total += sum(1 for _ in nx.find_cliques(m))
    return total


def touching(S):
    """atoms whose cuts share an edge: a line of one atom holding a point of another"""
    pown = [k[0] if k[0] != "g" else None for k in S.pkey]
    pairs = set()
    for k, L in enumerate(S.H):
        a = S.owner[k]
        if a is None:
            continue
        for q in L:
            b = pown[q]
            if b is not None and b != a:
                pairs.add(tuple(sorted((a, b))))
    return sorted(pairs)


def located(S, nat, names):
    """whether the interior pieces correspond one to one with the atoms (each piece's points all in one atom, each atom one piece), and
    whether the creative part holds only atom lines"""
    pown = [k[0] if k[0] != "g" else None for k in S.pkey]
    owners = [frozenset(pown[q] for q in piece) for piece in nat["interior pieces"]]
    one_each = all(len(o) == 1 and None not in o for o in owners) and sorted(next(iter(o)) for o in owners) == sorted(names)
    atom_lines_only = all(S.owner[k] is not None for k in nat["V"])
    return one_each, atom_lines_only


def fails(S):
    """no solution, by chunked enumeration (glue_lib's fails_globally holds every assignment in memory at once)"""
    return len(GL.CL.solutions(S.H, S.s, S.n)) == 0


def run_family(pool, fam, items):
    spaces = [GL.build(des) for label, des in items]
    assert all(pool.map(fails, spaces, chunksize=1))
    res = evaluate(pool, spaces)
    rows = []
    for (label, des), S, r in zip(items, spaces, res):
        nat = GL.native(S, r)
        names = [a[0] for a in des[1]]
        genus = GL.sat_genus(S)
        one_each, atom_only = located(S, nat, names)
        rows.append({"label": label, "points": S.n, "atoms": len(names), "genus": genus, "touching": touching(S),
                     "quiet size": nat["quiet size"], "quiet parts": nat["quiet parts"], "counts": nat["counts"],
                     "blocks": blocks(S, r, nat), "located": one_each, "creative part only atom lines": atom_only})
    return rows


def summary(rows):
    c = collections.Counter()
    for r in rows:
        kind = "touching" if r["touching"] else "separated"
        c[(r["atoms"], kind, "genus %d" % r["genus"], "counts %s" % r["counts"], "blocks %d" % r["blocks"], "located %s" % r["located"],
           "quiet parts %s" % ("one" if r["quiet parts"] == 1 else "several"))] += 1
    return {" | ".join(str(x) for x in k): v for k, v in sorted(c.items(), key=str)}


if __name__ == "__main__":
    manifest = json.loads((HERE / "manifest.json").read_text())
    bad = {q: dg for q, dg in manifest["parent_bindings"].items() if hashlib.sha256((ROOT / q).read_bytes()).hexdigest() != dg}
    status = {q: json.loads((ROOT / q).read_text()).get("status") for q in manifest["parent_bindings"]
              if q.endswith(".json") and q.startswith("proofs/")}
    check("0 dependency artifacts bound by hash; upstream proofs Proved", not bad and all(s in ("Proved", "passed") for s in status.values()),
          {"mismatched": bad, "statuses": status})
    detail = {}
    with Pool(22) as pool:
        for key, fam, base_genus in [("1 single atoms", singles, 0), ("2 pairs", pairs, 0), ("3 triples", triples, 0),
                                     ("4 atoms on atoms (the base is an atom too)", on_atoms, 1)]:
            items = fam()
            rows = run_family(pool, key, items)
            detail[key] = rows
            ok = all(r["genus"] == r["atoms"] + base_genus for r in rows)
            sep = [r for r in rows if not r["touching"]]
            if key.startswith("1"):  # one piece through points everywhere; through interior points but for census 58 minus line 4 or 5
                ok &= all(r["quiet parts"] == 1 and r["counts"][0][0] == 1 for r in rows)
                ok &= sum(1 for r in rows if r["counts"] != [(1, 1)]) == 76
            if key.startswith("2"):  # separated pairs: two pieces through interior points, located; touching pairs merge through points
                ok &= all(len(r["counts"]) == 1 and r["counts"][0][1] == 2 and r["located"] for r in sep)
                ok &= all(r["counts"][0][0] == 1 for r in rows if r["touching"])
            if key.startswith("3"):  # separated triples: three pieces except three receivers on the cube
                ok &= sum(1 for r in sep if r["counts"] == [(3, 3)] and r["located"]) == len(sep) - 4
            check(key + ": native counts against SAT genus (summary: atoms | placement | genus | (count through points, through interior "
                  "points) over every quiet part | blocks | located | quiet parts)", ok, {"spaces": len(rows), "summary": summary(rows)})
        cen = census()
        spaces = [S for name, S, kinds in cen]
        assert all(pool.map(fails, spaces, chunksize=1))
        res = evaluate(pool, spaces)
        rows = []
        for (name, S, kinds), r in zip(cen, res):
            nat = GL.native(S, r)
            rows.append({"label": name, "points": S.n, "braces": kinds, "genus": GL.sat_genus(S), "quiet size": nat["quiet size"],
                         "quiet parts": nat["quiet parts"], "counts": nat["counts"], "blocks": blocks(S, r, nat)})
        detail["5 census"] = rows
        c5 = collections.Counter((r["genus"], str(r["counts"]), "blocks %d" % r["blocks"]) for r in rows)
        ok5 = len(rows) == 32 and sum(1 for r in rows if r["blocks"] == r["genus"]) == 29 and \
            sum(1 for r in rows if r["counts"] == [(r["genus"], r["genus"])]) == 10
        check("5 every three-fold space up to 22 points: native counts against SAT genus", ok5,
              {"classes": len(rows), "(genus, counts, blocks)": {str(k): v for k, v in sorted(c5.items(), key=str)}})
    (HERE / "detail.json").write_text(json.dumps(detail, indent=1, default=str) + "\n") if "--write" in sys.argv else None

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
