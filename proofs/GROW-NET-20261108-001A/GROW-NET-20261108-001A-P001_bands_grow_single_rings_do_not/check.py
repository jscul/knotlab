#!/usr/bin/env python3
"""Checks for GROW-NET-20261108-001A: bands grow, single rings do not.

    .venv/bin/python3 -B check.py          verify result.json against a fresh run
    .venv/bin/python3 -B check.py --write  write result.json from a fresh run
Needs numpy and networkx (the repository's .venv). 16 worker processes, under a minute. Every reading is exact: return counts are
followed until the next vector lies in the span of the earlier ones, generating functions are exact rational functions over GF(2), and
rows of M^T are followed until they repeat; no lag cutoff is used."""
import hashlib
import json
import sys
import time
from multiprocessing import Pool
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
import grow_lib as G  # noqa: E402

LN, Gl = G.LN, G.Gl
N = LN.N
T0 = time.time()
OUT = {}


def check(name, ok, info):
    OUT[name] = {"pass": bool(ok), "info": info}
    print("PASS" if ok else "FAIL", name, json.dumps(info, default=str)[:500], round(time.time() - T0, 1), "s", flush=True)
    if not ok:
        sys.exit(1)


def sha(p):
    return hashlib.sha256((ROOT / p).read_bytes()).hexdigest()


def seeds():
    out = {"loop of %d rings" % r: LN.dihedron(r) for r in (3, 4, 5)}
    out.update({"two rings sharing %d contacts" % k: LN.hosohedron(k) for k in (3, 4)})
    out.update({nm: LN.platonic(nm) for nm in ("tetrahedron", "cube", "octahedron")})
    out["square torus 3"] = LN.square_torus(3)
    out["genus-2 network of 16 rings"] = Gl.gl23_maps()[(3, 8)]
    return out


def rectangle(nm):
    n, m = nm
    rot, edges = G.rect_torus(n, m)
    flips = all(LN.flip(rot, edges, e) is not None for e in range(len(edges)))
    return n, m, flips, G.balanced(rot, len(edges))


def one_contact(name):
    rot, edges = seeds()[name]
    ok, n = True, 0
    for new_rot, new_edges in G.attachments(rot, edges, 1):
        c = new_rot["new"][0]
        out = G.out_sets(new_rot, len(new_edges))
        ok &= bool(out[c] >> c & 1) and not G.balanced(new_rot, len(new_edges))
        n += 1
    return name, ok, n


def two_contacts(name):
    """non-bubble two-contact attachments: a new contact with exactly one return of length 2; bubbles counted apart"""
    rot, edges = seeds()[name]
    ok, n, bubbles = True, 0, 0
    for new_rot, new_edges in G.attachments(rot, edges, 2):
        c1, c2 = new_rot["new"]
        X = new_edges[c1][0]
        lst = new_rot[X]
        consecutive = new_edges[c2][0] == X and (abs(lst.index(c1) - lst.index(c2)) in (1, len(lst) - 1))
        if consecutive:
            bubbles += 1
            continue
        out = G.out_sets(new_rot, len(new_edges))
        two = sum(1 for d in range(len(new_edges)) if out[c1] >> d & 1 and out[d] >> c1 & 1)
        ok &= two % 2 == 1 and not G.balanced(new_rot, len(new_edges))
        n += 1
    return name, ok, n, bubbles


def bubble_criterion(name):
    rot, edges = seeds()[name]
    E = len(edges)
    ok, n, kept = True, 0, 0
    for v in rot:
        for pos in range(len(rot[v])):
            nr, ne, (p, q) = G.bubble(rot, edges, v, pos)
            bal = G.balanced(nr, len(ne))
            crit = not any(G.reaches(rot, E, q, c) and G.reaches(rot, E, c, p) for c in range(E))
            ok &= bal == crit
            kept += bal
            n += 1
    return name, ok, n, kept


def sherman_morrison(args):
    """exact over GF(2)(z) with every corner of g - 1 = 1 cells: after a bubble on the corner p -> q, every old contact c has
    D'_cc = 1 + w D_cq D_pc / (1 + w D_pq), w = z a"""
    name, v, pos = args
    rot, edges = seeds()[name]
    sizes, contacts = LN.network(rot, edges, 2)
    D = LN.dmatrix(sizes, contacts)
    nr, ne, (p, q) = G.bubble(rot, edges, v, pos)
    sizes2, contacts2 = LN.network(nr, ne, 2)
    D2 = LN.dmatrix(sizes2, contacts2)
    w = LN.corner_weight(1)
    ok = True
    for c in range(len(edges)):
        num = LN.rmul(w, LN.rmul(D[c][q], D[p][c]))
        den = LN.radd(LN.ONE, LN.rmul(w, D[p][q]))
        want = LN.radd(LN.ONE, LN.rmul(num, LN.rinv(den)))
        ok &= D2[c][c] == want
    return name, ok


def cells(args):
    """at cell level (rows of M^T until they repeat): the contact predicted to fail loses its witnesses at some lag"""
    name, kind = args
    rot, edges = seeds()[name]
    if kind == "bubble":
        nr, ne, (p, q) = G.bubble(rot, edges, next(iter(rot)), 0)
        target = G.odd_contacts(nr, len(ne))[0]
    else:
        def non_bubble(r, e):
            c1, c2 = r["new"]
            X = e[c1][0]
            lst = r[X]
            return not (e[c2][0] == X and abs(lst.index(c1) - lst.index(c2)) in (1, len(lst) - 1))
        nr, ne = next((r, e) for r, e in G.attachments(rot, edges, 2) if non_bubble(r, e))
        target = nr["new"][0]
    sizes, contacts = LN.network(nr, ne, 2)
    rings, Nb, blocks = N.layout(sizes, contacts)
    rows = N.matrix(sizes, (60,) * len(sizes), contacts)[0]
    ra, pa, rb, pb, law = contacts[target]
    wa, wb = rings[ra][pa - 1], rings[rb][pb - 1]
    seq, T1, per = N.orbit(rows, 1 << target, 10 ** 6)
    lapses = [t + 1 for t, x in enumerate(seq) if not (x >> wa & 1 and x >> wb & 1)]
    return name, kind, bool(lapses), lapses[:1]


def growth(seq_name):
    """growth sequences: bands added round the 3 x m torus, and blocks (every ring split k x k) from 3 x 3 and 4 x 4"""
    if seq_name == "bands":
        shapes = [(3, m) for m in range(3, 13)] + [(4, m) for m in range(4, 13)]
    else:
        shapes = [(3, 3), (6, 6), (9, 9), (12, 12), (4, 4), (8, 8), (12, 12)]
    return seq_name, all(G.balanced(*(lambda r, e: (r, len(e)))(*G.rect_torus(n, m))) for n, m in shapes), len(shapes)


def main():
    write = "--write" in sys.argv
    deps = {"GENUS-CUT-20261108-001A manifest": "proofs/GENUS-CUT-20261108-001A/GENUS-CUT-20261108-001A-P001_two_rings_of_cuts_per_handle/manifest.json",
            "genus_lib": "proofs/GENUS-CUT-20261108-001A/GENUS-CUT-20261108-001A-P001_two_rings_of_cuts_per_handle/genus_lib.py"}
    m = json.loads((HERE / "manifest.json").read_text())
    bound = {k: sha(p) for k, p in deps.items()}
    check("0_dependencies_bound", all(m["parent_bindings"].get(p) == bound[k] for k, p in deps.items()), bound)
    S = seeds()
    check("1_seeds_balanced", all(G.balanced(rot, len(edges)) for rot, edges in S.values()), {"seeds": list(S)})
    with Pool(16) as pool:
        res = pool.map(rectangle, [(n, mm) for n in range(3, 9) for mm in range(3, 13)])
        check("2_rectangular_tori_flip_and_persist", all(r[2] and r[3] for r in res), {"tori": len(res)})
        res = pool.map(growth, ["bands", "blocks"])
        check("3_growth_by_bands_and_blocks", all(r[1] for r in res), {r[0]: "%d stages balanced" % r[2] for r in res})
        res = pool.map(one_contact, list(S))
        check("4_one_contact_returns_at_once", all(r[1] for r in res), {"attachments": sum(r[2] for r in res)})
        res = pool.map(two_contacts, list(S))
        check("5_two_contacts_unpaired_return", all(r[1] for r in res), {"non-bubble attachments": sum(r[2] for r in res), "bubbles set apart": sum(r[3] for r in res)})
        res = pool.map(bubble_criterion, list(S))
        check("6_bubble_criterion", all(r[1] for r in res), {"bubbles": sum(r[2] for r in res), "bubbles keeping every contact persistent": sum(r[3] for r in res)})
        res = pool.map(sherman_morrison, [("loop of 4 rings", 0, 0), ("loop of 4 rings", 1, 1), ("tetrahedron", 0, 0), ("tetrahedron", 2, 1),
                                          ("two rings sharing 3 contacts", 0, 1), ("cube", 0, 0)], chunksize=1)
        check("7_sherman_morrison_exact", all(r[1] for r in res), {"bubbles": len(res)})
        res = pool.map(cells, [("loop of 4 rings", "bubble"), ("tetrahedron", "bubble"), ("tetrahedron", "two"), ("square torus 3", "two")], chunksize=1)
        check("8_cells_exact", all(r[2] for r in res), {"%s, %s: first lapse" % (r[0], r[1]): r[3] for r in res})
    result = {"ticket": "GROW-NET-20261108-001A", "checks": OUT, "status": "passed", "seconds": round(time.time() - T0, 1)}
    path = HERE / "result.json"
    if write:
        path.write_text(json.dumps(result, indent=1, default=str) + "\n")
        print("wrote", path)
    else:
        old = json.loads(path.read_text())
        same = {k: v["pass"] for k, v in old["checks"].items()} == {k: v["pass"] for k, v in OUT.items()}
        print("matches result.json" if same else "DIFFERS from result.json")
        sys.exit(0 if same else 1)


if __name__ == "__main__":
    main()
