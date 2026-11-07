#!/usr/bin/env python3
"""Checks for GENUS-READ-20261107-001B: natively a Fano atom is homogeneous.

    python3 -B check.py          verify result.json against a fresh run
    python3 -B check.py --write  write result.json from a fresh run
Run with the repository's .venv (numpy, networkx). Uses up to 22 processes."""
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
import inside_lib as IN  # noqa: E402

GA = IN.load("gr_b_gluing_lib", ROOT / "proofs/GENUS-READ-20261107-001A/GENUS-READ-20261107-001A-P001_census_6_depends_on_how_it_is_glued/"
             "gluing_lib.py")
FL, TL = GA.FL, IN.TL
G, AT = FL.G, FL.AT
TR = G.TR
BL = IN.load("gr_b_bound_lib", ROOT / "proofs/ATOM-ONE-20261107-001B/ATOM-ONE-20261107-001B-P001_atoms_see_only_the_port_relation/"
             "bound_lib.py")
SIX = {"000/001/010/101/110/111", "000/001/011/100/110/111", "000/010/011/100/101/111", "001/010/101/110", "001/011/100/110",
       "010/011/100/101"}
RL = IN.load("gr_b_rule_lib", ROOT / "proofs/FAR-READ-20261106-001B/FAR-READ-20261106-001B-P001_a_rule_that_reads_every_saved_space/"
             "rule_lib.py")
T0 = time.time()
OUT = {}
NATIVE = (False, 2, True, True)
DESIGNS = [[("g", ("pt", 0))], [("g", ("ln", 0))], [("g", ("pt", 0)), ("g", ("pt", 3))], [("g", ("ln", 0)), ("g", ("pt", 3))],
           [("g", ("pt", 0)), ("g", ("ln", 3))], [("g", ("pt", 0)), ("g", ("pt", 3)), ("g", ("pt", 5))],
           [("g", ("ln", 0)), ("A1", ("pt", 1))], [("g", ("ln", 0)), ("A1", ("pt", 3))], [("g", ("ln", 0)), ("A1", ("ln", 1))],
           [("g", ("ln", 0)), ("A1", ("ln", 3))], [("g", ("pt", 0)), ("A1", ("pt", 2))], [("g", ("pt", 0)), ("A1", ("ln", 2))]]


def check(name, ok, info):
    OUT[name] = {"pass": bool(ok), "info": info}
    print("PASS" if ok else "FAIL", name, json.dumps(info, default=str), round(time.time() - T0, 1), "s", flush=True)
    if not ok:
        sys.exit(1)


def native_rows(S, rows_for, cols_for, slow=False):
    """{a: {b: native vector}} from full solution sets, every order of each gluing line (slow: six separate verdicts, ticket A's
    way; otherwise one set of masks relabeled for each order)"""
    out = {}
    for a in rows_for:
        AN = TL.solutions(S.H, S.s, S.n, skip=a)
        if slow:
            out[a] = {b: GA.native(GA.orders_verdicts(AN, S, b)) for b in cols_for if b != a}
        else:
            out[a] = {b: IN.native_of_near_side(AN, list(S.H[b]), list(S.s[b]), [q for q in range(S.n) if q not in S.H[b]])
                      for b in cols_for if b != a}
    return out


def design_task(design):
    """the composition against exact native creation on the centre of a built Fano tree"""
    S, cuts = TR.build(design)
    centre = [i for i, k in enumerate(S.lkey) if k[0] == "g"]
    idx = {i: S.lkey[i][1] for i in centre}
    X = frozenset((("P", el[1]) if el[0] == "pt" else ("L", el[1])) for h, el in design if h == "g")
    # each cut's side, as built: a leaf, or a leaf atom with its own children (one level, as in the designs)
    kids = collections.defaultdict(dict)
    for h, el in design:
        if h != "g":
            kids[h][("P", el[1]) if el[0] == "pt" else ("L", el[1])] = None
    leaves = IN.leaves()
    states = {}
    for j, (h, el) in enumerate(design, start=1):
        if h != "g":
            continue
        c = ("P", el[1]) if el[0] == "pt" else ("L", el[1])
        name = "A%d" % j
        side = "P" if c[0] == "P" else "L"
        if kids[name]:
            states[c] = IN.side_state(IN.SIDE_E[side], {k: leaves["P" if k[0] == "P" else "L"] for k in kids[name]})
        else:
            states[c] = leaves[side]
    model = IN.native_inner(X, states)
    exact = native_rows(S, centre, centre)
    slow = native_rows(S, centre, centre, slow=True)
    mism = sum(model[(idx[a], idx[b])] != exact[a][b] for a in centre for b in centre if a != b)
    fs = sum(slow[a][b] != exact[a][b] for a in centre for b in centre if a != b)
    return str(design), sum(1 for a in centre for b in centre if a != b), mism, fs


def config_task(args):
    X, leaf, top = args
    lo = IN.native_inner(X, {c: leaf["P" if c[0] == "P" else "L"] for c in X})
    hi = IN.native_inner(X, {c: top["P" if c[0] == "P" else "L"] for c in X})
    return len(lo), sum(lo[k] == hi[k] for k in lo), sum(v == NATIVE for v in lo.values()), sum(v == NATIVE for v in hi.values())


def fano_tree_task(args):
    src, nm, S, ex = args
    parts, types, lown, xs, atoms = AT.atoms_of(S)
    n = len(S.H)
    nat = native_rows(S, range(n), range(n))
    c = collections.Counter()
    c["spaces"] += 1
    for A, L in atoms.items():
        c["atoms"] += 1
        inside = [nat[a][b] for a in L for b in L if a != b]
        c["ordered pairs inside atoms"] += len(inside)
        c["... with the native vector (no K4^(3), census 6 at two of six orders, Fano, census 58)"] += sum(v == NATIVE for v in inside)
        c["atoms acting as one natively"] += all(len({nat[a][x] for a in L}) == 1 for x in range(n) if x not in L)
        c["atoms of six or seven lines"] += len(L) >= 6
    out = G.creates(ex)
    c["yes/no two-stage rule reads the atoms"] += AT.reads_atoms(AT.two_stage(n, out)[1], atoms, lown, types)[0]
    c["the frozen far-side rule reads them with stored census 6"] += AT.reads_atoms(RL.read_atoms(n, ex), atoms, lown, types)[0]
    ok, big = AT.reads_atoms(RL.read_atoms(n, nat), atoms, lown, types)
    c["the frozen far-side rule reads them with native vectors"] += ok
    c["... spaces where it cuts an atom of six or seven lines"] += any(len(L) >= 6 and not any(set(L) == set(cl) for cl in big)
                                                                      for L in atoms.values())
    return c


def order_task(args):
    """ATOM-ONE B's bound (B's own masks; every deep relation of the removal's side and every mixed pair) read at every order of the
    gluing line, by relabeling the masks"""
    import numpy as np
    kind, perm, x, b, R = args
    fr = TL.frag_step(kind, perm, x, None)
    sols, idx = TL.solve(fr)
    slots, Y = fr["slots"], list(fr["lines"][b])
    rows = [m for m in sols if (R >> TL._bits3(m, idx, slots)) & 1]
    yp = {TL._bits3(m, idx, Y) for m in rows}
    if len(yp) != 6 or 0 in yp or 7 in yp:
        return args, None
    o1, o2 = TL.final_relations((kind, R, frozenset(), frozenset()), perm, x, b, deep=False)
    m1, m2 = TL.final_relations((kind, R, frozenset(BL.SINGLES[R]), frozenset(BL.PAIRS[R])), perm, x, b)
    elems = [("line", tuple(fr["lines"][i])) for i in fr["lines"] if i != b] + [("point", (v,)) for v in fr["vars"] if v[0] == "n"]
    yi = np.array([BL.PYI[TL._bits3(m, idx, Y)] for m in rows])
    sc = np.array([TL._bits3(m, idx, slots) for m in rows])
    ec = [np.array([sum(TL._val(m, idx, v) << j for j, v in enumerate(ev)) for m in rows]) for ek, ev in elems]
    S_of = [BL.LINE_S if ek == "line" else BL.PT_S for ek, ev in elems]
    far_s = BL.single_arrays(sorted(BL.SINGLES[R]))
    mixed = set()
    for e in range(len(elems)):
        T = np.zeros((6, 8, 8), dtype=bool)
        T[yi, ec[e], sc] = True
        mixed |= BL.masks2(np.einsum("yab,iav,jbw->ijyvw", T, S_of[e], far_s) > 0)
    m2 = set(m2) | mixed
    res = []
    for sg in IN.ORDER_MAPS:
        v0 = TL.verdict_from_masks(IN._relabel(set(o1), sg, 1), IN._relabel(set(o2), sg, 2))
        v2 = TL.verdict_from_masks(IN._relabel(set(m1), sg, 1), IN._relabel(m2, sg, 2))
        res.append((v0, v2))
    return args, res


if __name__ == "__main__":
    manifest = json.loads((HERE / "manifest.json").read_text())
    bad = {q: dg for q, dg in manifest["parent_bindings"].items() if hashlib.sha256((ROOT / q).read_bytes()).hexdigest() != dg}
    status = {q: json.loads((ROOT / q).read_text()).get("status") for q in manifest["parent_bindings"]
              if q.endswith(("manifest.json", "result.json")) and q.startswith("proofs/")}
    check("0 dependency artifacts bound by hash; upstream proofs Proved", not bad and all(s in ("Proved", "passed") for s in status.values()),
          {"mismatched": bad, "statuses": status})
    with Pool(22) as pool:
        # 1
        res = list(pool.imap_unordered(design_task, DESIGNS, chunksize=1))
        check("1 the composition is exact: on built Fano trees (stars, two levels, two cuts meeting), the native vectors it gives inside "
              "the centre atom equal those of the exact creation map at every order of every gluing line (computed once from relabeled "
              "masks and once from six separate verdicts, which agree)",
              all(m == 0 and f == 0 for d, n_, m, f in res),
              {"designs": len(res), "ordered pairs": sum(r[1] for r in res), "mismatches": sum(r[2] for r in res),
               "relabeled masks against six verdicts, mismatches": sum(r[3] for r in res)})
        # 2
        leaf = IN.leaves()
        top, rounds = IN.reachable_max(pool)
        check("2 the states closed Fano-tree sides can show: from the leaves, hanging children until nothing new appears, the union is "
              "reached in finitely many rounds",
              all(leaf[k][0] <= top[k][0] and leaf[k][1] <= top[k][1] for k in leaf),
              {"rounds": rounds, "leaf (singles, pairs)": {k: (len(v[0]), len(v[1])) for k, v in leaf.items()},
               "union (singles, pairs)": {k: (len(v[0]), len(v[1])) for k, v in top.items()}})
        # 3
        confs = IN.configurations()
        c3 = collections.Counter()
        for n_, same, lo_nat, hi_nat in pool.imap_unordered(config_task, [(X, leaf, top) for X in confs], chunksize=1):
            c3["configurations"] += 1
            c3["ordered pairs"] += n_
            c3["floor = ceiling"] += same
            c3["floor native vector"] += lo_nat
            c3["ceiling native vector"] += hi_nat
        check("3 native homogeneity: for every configuration of a Fano atom (253, up to collineations), with a leaf behind every cut and "
              "with the union of all reachable states behind every cut, every ordered pair of its lines gets the native vector (no "
              "K4^(3), census 6 at two of the six orders, the Fano plane, census 58)",
              c3["ordered pairs"] == c3["floor = ceiling"] == c3["floor native vector"] == c3["ceiling native vector"] > 0, dict(c3))
        # 4
        spaces, maps = FL.saved()
        fs, fm = G.load_maps(ROOT / "proofs/FAR-READ-20261106-001C/FAR-READ-20261106-001C-P001_fresh_spaces/maps.json.gz")
        trees = [(s[0], s[1], s[2], m) for s, m in list(zip(spaces, maps)) + list(zip(fs, fm))
                 if set(AT.atoms_of(s[2])[1]) == {"heawood"}]
        c4 = collections.Counter()
        for c in pool.imap_unordered(fano_tree_task, trees, chunksize=1):
            c4.update(c)
    check("4 computed, on every saved and fresh Fano-tree space: inside every atom every ordered pair carries the native vector, every "
          "atom acts as one natively; the yes/no two-stage rule reads every space, while the frozen far-side rule, given native vectors, "
          "cuts atoms",
          c4["ordered pairs inside atoms"] == c4["... with the native vector (no K4^(3), census 6 at two of six orders, Fano, census 58)"]
          and c4["atoms acting as one natively"] == c4["atoms"] and c4["yes/no two-stage rule reads the atoms"] == c4["spaces"],
          dict(sorted(c4.items())))

    # 5
    tasks5 = [(kind, perm, x, b, R) for kind, perm, x, b in BL.letters() if tuple(perm) == (0, 1, 2) for R in BL.PL.PORT_RELATIONS]
    c5 = collections.Counter()
    with Pool(22) as pool:
        for (kind, perm, x, b, R), res in pool.imap_unordered(order_task, tasks5, chunksize=2):
            if res is None:
                continue
            c5["cases"] += 1
            exc = TL.role(kind, x, b) == "cut line" and BL.PL.name(R) in SIX
            changed = [v0 != v2 for v0, v2 in res]
            c5["creation changed at some order"] += any((v0 is not None and any(v0)) != (v2 is not None and any(v2)) for v0, v2 in res)
            if any(changed):
                c5["far sides changed at some order: " + ("the exception" if exc else "elsewhere")] += 1
            if R == 255:
                c5["free port relation: cases"] += 1
                c5["free port relation: unchanged at every order"] += not any(changed)
    check("5 ATOM-ONE B's bound at every order of the gluing line (masks relabeled; one slot order with all 15 port relations): deep points "
          "of the removal's side and mixed pairs never change creation, change far sides only in the exception, and with a free port "
          "relation change nothing at any order, so on Fano trees every atom acts as one natively",
          c5["creation changed at some order"] == 0 and c5["far sides changed at some order: elsewhere"] == 0
          and c5["free port relation: cases"] == c5["free port relation: unchanged at every order"] > 0, dict(sorted(c5.items())))

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
