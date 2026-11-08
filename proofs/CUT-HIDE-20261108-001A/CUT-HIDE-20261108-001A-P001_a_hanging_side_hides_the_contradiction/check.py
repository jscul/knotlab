#!/usr/bin/env python3
"""Checks for CUT-HIDE-20261108-001A: a side K4^(3) without a line, hanging at a two-line cut, hides the contradiction.

    python3 -B check.py          verify result.json against a fresh run
    python3 -B check.py --write  write result.json from a fresh run
Run with the repository's .venv (numpy, networkx)."""
import os

for _v in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

import hashlib  # noqa: E402
import itertools  # noqa: E402
import json  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from pathlib import Path  # noqa: E402

import networkx as nx  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CRA = ROOT / "proofs/CONTRA-READ-20261108-001A/CONTRA-READ-20261108-001A-P001_every_row_singles_out_the_contradictory_class"
CPA = ROOT / "proofs/CONTRA-PROOF-20261108-001A/CONTRA-PROOF-20261108-001A-P001_where_one_row_reads_the_tie"
sys.path.insert(0, str(CRA))
import contra_lib as CL  # noqa: E402

TR = CL.TR
TL = TR.engine().TL
T0 = time.time()
OUT = {}


def check(name, ok, info):
    OUT[name] = {"pass": bool(ok), "info": info}
    print("PASS" if ok else "FAIL", name, json.dumps(info, default=str)[:3000], round(time.time() - T0, 1), "s", flush=True)
    if not ok:
        sys.exit(1)


def nae(v):
    return not (v[0] == v[1] == v[2])


def side_lemma():
    """the side S: centre c and points x0, y, z; lines {c,x0,y}, {c,x0,z}, {c,y,z}; c and x0 on no other line once a is removed, y and z
    on the cut line a'. Every signing of its nine incidences, classified by what its own lines force."""
    lines = [("c", "x0", "y"), ("c", "x0", "z"), ("c", "y", "z")]
    inc = [(i, p) for i, l in enumerate(lines) for p in l]
    rows = []
    for signs in itertools.product([0, 1], repeat=9):
        s = dict(zip(inc, signs))
        sols = [dict(zip(("c", "x0", "y", "z"), v)) for v in itertools.product([0, 1], repeat=4)
                if all(nae([dict(zip(("c", "x0", "y", "z"), v))[p] ^ s[(i, p)] for p in l]) for i, l in enumerate(lines))]
        yz = {(t["y"], t["z"]) for t in sols}
        tied = lambda p, q: len({t[p] ^ t[q] for t in sols}) == 1  # noqa: E731
        rigid = tied("x0", "y") and tied("y", "z")
        x0_function = all(len({t["x0"] for t in sols if (t["y"], t["z"]) == k}) == 1 for k in yz)
        c_free = all(len({t["c"] for t in sols if (t["x0"], t["y"], t["z"]) == (u["x0"], u["y"], u["z"])}) == 2 for u in sols)
        rows.append((rigid, len(yz), x0_function, c_free))
    return rows


# local relations on a gluing line Y and one or two near points, in the creation engine's layout (pattern index k of Y)
PY = [tuple(p) for p in TL.PY]
COMP = {k: PY.index(tuple(1 - v for v in p)) for k, p in enumerate(PY)}
REPS = sorted({min(k, COMP[k]) for k in range(6)})


def close1(rel):
    return frozenset(rel) | frozenset((COMP[k], 1 - x) for k, x in rel)


def close2(rel):
    return frozenset(rel) | frozenset((COMP[k], 1 - x, 1 - w) for k, x, w in rel)


def ev1(rel):
    m = sum(1 << (2 * k + x) for k, x in rel)
    return TL.evaluate(1, [m])[m]


def ev2(rel):
    m = sum(1 << (4 * k + x + 2 * w) for k, x, w in rel)
    return TL.evaluate(2, [m])[m]


def creates(e):
    return tuple(e[0] and v for v in e[1])


def within(a, b):
    return all((not x) or y for x, y in zip(a, b))


def local_lemmas():
    singles = sorted({close1((k, x) for k, xs in zip(REPS, ch) for x in xs) for ch in itertools.product([(0,), (1,), (0, 1)], repeat=3)}, key=sorted)
    vals = [(0, 0), (1, 0), (0, 1), (1, 1)]
    subs = [s for r in range(1, 5) for s in itertools.combinations(vals, r)]
    pairs = sorted({close2((k, x, w) for k, xw in zip(REPS, ch) for x, w in xw) for ch in itertools.product(subs, repeat=3)}, key=sorted)
    out = {"singles": len(singles), "pairs": len(pairs)}
    out["L1 a free single point creates nothing"] = not any(creates(ev1(close1((k, x) for k in range(6) for x in (0, 1)))))
    out["L2 a pair with one point free and independent creates no more than the other point alone"] = all(
        within(creates(ev2(close2(((k, x, w) if o == 0 else (k, w, x)) for k, w in R for x in (0, 1)))), creates(ev1(R)))
        for R in singles for o in (0, 1))
    out["L3 a pair independent of the gluing line creates nothing"] = all(
        not any(creates(ev2(close2((k, x, w) for k in range(6) for x, w in set(Q) | {(1 - x, 1 - w) for x, w in Q})))) for Q in subs)
    out["L4 a pair of tied points creates no more than one of them alone"] = all(
        within(creates(ev2(close2(((k, w ^ t, w) if o == 0 else (k, w, w ^ t)) for k, w in R))), creates(ev1(R)))
        for R in singles for t in (0, 1) for o in (0, 1))
    l5 = True
    for j in range(3):
        for t in (0, 1):
            l5 &= not ev1(close1((k, PY[k][j] ^ t) for k in range(6)))[0]
            for R in singles:
                for o in (0, 1):
                    l5 &= not ev2(close2(((k, PY[k][j] ^ t, w) if o == 0 else (k, w, PY[k][j] ^ t)) for k, w in R))[0]
    out["L5 a point tied to a point of the gluing line is degenerate, alone or in a pair"] = l5
    out["L6 complementing a near point changes nothing"] = all(ev1(R) == ev1(close1((k, 1 - x) for k, x in R)) for R in singles) and all(
        ev2(R) == ev2(close2((k, 1 - x, w) for k, x, w in R)) == ev2(close2((k, x, 1 - w) for k, x, w in R)) for R in pairs)
    return out


def row_of(G, S, a):
    signs = CL.PL.signs_of(G.lines, S)
    AN = TL.solutions(G.lines, signs, G.n, skip=a)
    row = [CL.verdict(TR.fast_masks(AN, list(G.lines[b]), signs[b], [q for q in range(G.n) if q not in G.lines[b]])) if len(AN) else None
           for b in range(G.g) if b != a]
    pats = {tuple(int(x) for x in r) for r in AN[:, list(G.lines[a])]} if len(AN) else set()
    return row, len(pats) == 2, AN


def tied(A, p, q):
    return len(set(A[:, p] ^ A[:, q])) == 1


if __name__ == "__main__":
    manifest = json.loads((HERE / "manifest.json").read_text())
    bad = {q: dg for q, dg in manifest["parent_bindings"].items() if hashlib.sha256((ROOT / q).read_bytes()).hexdigest() != dg}
    status = {q: json.loads((ROOT / q).read_text()).get("status") for q in manifest["parent_bindings"]
              if q.endswith(("manifest.json", "result.json")) and q.startswith("proofs/")}
    check("0 dependency artifacts bound by hash; upstream proofs Proved",
          not bad and all(s in ("Proved", "passed") for s in status.values()), {"mismatched": bad, "statuses": status})

    rows = side_lemma()
    rigid = [r for r in rows if r[0]]
    loose = [r for r in rows if not r[0]]
    check("1 the side alone: of the 512 signings of K4^(3) without a line (8 switching classes of 64), the 64 of one class make its own "
          "lines tie x0, y and z, with y and z showing two patterns and the centre free given the rest; in every other signing y and z "
          "show all four pairs and x0 is not a function of them",
          len(rows) == 512 and len(rigid) == 64 and all(r == (True, 2, True, True) for r in rigid)
          and all(r[1] == 4 and not r[2] for r in loose),
          {"rigid signings": len(rigid), "other signings": len(loose)})

    lem = local_lemmas()
    check("2 the local lemmas: over all 27 one-point and 3,375 two-point relations on a gluing line, a free point creates nothing, a point "
          "free of the rest adds nothing to a pair, a pair independent of the gluing line creates nothing, a tied pair adds nothing, a point "
          "tied to the gluing line is degenerate, and complementing a point changes nothing",
          all(v is True for k, v in lem.items() if k.startswith("L")) and lem["singles"] == 27 and lem["pairs"] == 3375, lem)

    glues = json.loads((CPA / "glues.json").read_text())
    found = []
    for k, g in enumerate(glues):
        G = CL.Glue(k, {"glue": [tuple(l) for l in g["lines"]], "minimal": []})
        if nx.node_connectivity(G.G) >= 3:
            continue
        kappa = [m for m in range(G.N) if len(G.solutions(m)) == 0]
        for a in range(G.g):
            H = G.G.copy()
            H.remove_node(("L", a))
            arts = [v for v in nx.articulation_points(H) if v[0] == "L"]
            if not arts:
                continue
            a2 = arts[0][1]
            K = H.copy()
            K.remove_node(("L", a2))
            S = [c for c in nx.connected_components(K) if len({v[1] for v in c if v[0] == "P"} & set(G.lines[a])) == 1][0]
            Sp = sorted(v[1] for v in S if v[0] == "P")
            Sl = [v[1] for v in S if v[0] == "L"]
            k4 = len(Sp) == 4 and len(Sl) == 3 and len(set.intersection(*[set(G.lines[i]) for i in Sl])) == 1
            y, z = sorted(set(G.lines[a2]) & set(Sp))
            x0 = (set(G.lines[a]) & set(Sp)).pop()
            u = (set(G.lines[a2]) - {y, z}).pop()
            sig = G.signing(kappa[0])
            rt, tt, AN = row_of(G, sig, a)
            flip = [e for e in sig if e != (a2, y)] + ([] if (a2, y) in sig else [(a2, y)])
            rf, tf, ANf = row_of(G, flip, a)
            found.append({"glue": k, "line": a, "cut partner": a2, "hanging side": Sp, "K4^(3) without a line": k4,
                          "one class without solutions": len(kappa) == 1, "contradictory restriction ties a": tt,
                          "side rigid": tied(AN, x0, y) and tied(AN, y, z), "coupled across a'": tied(AN, u, y),
                          "flip: same row": rf == rt, "flip: ties a": tf, "flip: decoupled": not tied(ANf, u, y) and not tied(ANf, x0, u)})
    k4n = sum(1 for f in found if f["K4^(3) without a line"])
    check("3 the theorem's prediction on CONTRA-PROOF's 16 failing lines: in the contradictory class's restriction the hanging side ties "
          "x0, y and z and a' ties its third point to them; flipping a''s sign at y decouples the side, keeps every entry of the row and "
          "breaks the tie of the removed line's points. 14 of the 16 hanging sides are K4^(3) without a line (the theorem's case); the other "
          "2, with six points, behave the same",
          len(found) == 16 and k4n == 14 and all(f["one class without solutions"] and f["contradictory restriction ties a"] and f["side rigid"]
                                                 and f["coupled across a'"] and f["flip: same row"] and not f["flip: ties a"] and f["flip: decoupled"]
                                                 for f in found),
          {"failing lines": len(found), "hanging sides K4^(3) without a line": k4n, "lines": found})

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
