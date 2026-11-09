"""Checks for HONEY-REACH-20261109-001A. Every reading follows walk counts, powers of M or rows of M^T until the next lies in the span of
the earlier ones (exact, no lag cutoff). Checks 8 and 9 are computations, not theorems.

    python3 -B check.py          verify against result.json
    python3 -B check.py --write  write result.json from a fresh run
"""
import hashlib
import json
import sys
import time
from multiprocessing import Pool
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import honey_lib as H  # noqa: E402

ROOT = H.ROOT
LN, T, N = H.LN, H.T, H.N
OUT = {}
T0 = time.time()
LATTICE = ROOT / "proofs/LATTICE-NET-20261108-001A/LATTICE-NET-20261108-001A-P001_odd_tori_compose_rings_of_cuts_separate"
LOOP = ROOT / "proofs/LOOP-NET-20261108-001A/LOOP-NET-20261108-001A-P001_symmetry_cancels_returns"
BIG = 200


def check(name, ok, info):
    OUT[name] = {"pass": bool(ok), "info": info}
    print(("PASS " if ok else "FAIL ") + name, "(%.0fs)" % (time.time() - T0), flush=True)
    if not ok:
        print(json.dumps(info, indent=1, default=str)[:3000])


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def cell_union(rows, start):
    """every first-row cell a value ever depends on: rows of M^T at lags 1, 2, ... until the next lies in the span of the earlier ones"""
    row, union, basis = start, 0, {}
    while True:
        row = LN.step(rows, row)
        x = row
        while x:
            top = x.bit_length() - 1
            if top not in basis:
                break
            x ^= basis[top]
        if not x:
            return union
        basis[x.bit_length() - 1] = x
        union |= row


# ---------- check 1: the contact graph is the model's
def task_graph(args):
    n, g = args
    rot, edges, sizes, contacts, ring, cidx = H.network(n, g)
    ins = T.in_sets(sizes, contacts)
    ok = True
    for i in range(n):
        for j in range(n):
            p = (i, j)
            pred = {
                0: [(2, p), (2, (i, (j + 1) % n))],
                1: [(0, p), (0, ((i - 1) % n, j))],
                2: [(1, p), (1, ((i + 1) % n, (j - 1) % n))],
            }
            for k in range(3):
                want = 0
                for d in pred[k]:
                    want ^= 1 << cidx[d]
                ok &= ins[cidx[(k, p)]] == want
    # ring contacts of A(p), B(p)
    for i in range(n):
        for j in range(n):
            for kind, s in (("A", 0), ("B", 1)):
                have = set(rot[(i, j, s)])
                want = {cidx[c] for c in H.ring_contacts_model(kind, (i, j), n)}
                ok &= have == want
    return n, g, ok


# ---------- check 2: three steps between contacts of one kind are M; the turn and the half-turn are automorphisms
def task_three_steps(n):
    rot, edges, sizes, contacts, ring, cidx = H.network(n, 2)
    ins = T.in_sets(sizes, contacts)
    ok = True
    Mn = H.M(n)
    for k in range(3):
        # walks of length 3 from e_k(0) to e_k(q): rows of A^3 read backwards from each target
        for i in range(n):
            for j in range(n):
                row = 1 << cidx[(k, (i, j))]
                for _ in range(3):
                    row = LN.step(ins, row)
                ok &= bool(row >> cidx[(k, (0, 0))] & 1) == bool(Mn[i, j])
    # the turn about A(0): (i, j) -> (-i - j, i) on A, and B(p) -> B(-p - (1, 1) ... ) checked through edges and rotation order
    def turn(v):
        i, j, s = v
        if s == 0:
            return ((-i - j) % n, i % n, 0)
        return ((-i - j - 1) % n, i % n, 1)

    def half(v):
        i, j, s = v
        return ((-i) % n, (-j) % n, 1 - s)
    autos = {}
    for name, f in (("turn", turn), ("half-turn", half)):
        emap = {}
        good = True
        for e, (u, w) in enumerate(edges):
            fu, fw = f(u), f(w)
            cand = [e2 for e2, (u2, w2) in enumerate(edges) if {u2, w2} == {fu, fw}]
            good &= len(cand) == 1
            if cand:
                emap[e] = cand[0]
        if good:
            for v, lst in rot.items():
                img = [emap[e] for e in lst]
                tgt = rot[f(v)]
                r = tgt.index(img[0])
                good &= img == tgt[r:] + tgt[:r]
        autos[name] = good
    return n, ok, autos


# ---------- check 3: the window lemma, and B(0)'s rings are the half-turn image of A(0)'s
def task_windows(n):
    Z = H.zero_set(n)
    R = H.reach_sets(n)
    a_pts, b_pts = H.never_need_A0(n, Z)
    by_windows = {("A", p) for p in a_pts} | {("B", p) for p in b_pts}
    by_pairs = H.never_needs_model(n, ("A", (0, 0)), R)
    fromB = H.never_needs_model(n, ("B", (0, 0)), R)
    image = {("B" if k == "A" else "A", ((-p[0]) % n, (-p[1]) % n)) for k, p in by_pairs}
    return n, by_windows == by_pairs, fromB == image, len(by_pairs)


# ---------- check 4: contact level, every pair of rings
def task_contact_level(n):
    rot, edges, sizes, contacts, ring, cidx = H.network(n, 2)
    ins = T.in_sets(sizes, contacts)
    reach = [T.reach(ins, c)[0] for c in range(len(contacts))]
    rc = {ring[v]: rot[v] for v in rot}
    masks = {X: sum(1 << e for e in cs) for X, cs in rc.items()}
    R = H.reach_sets(n)
    ok, pairs = True, 0
    model = {}
    for kind, s in (("A", 0), ("B", 1)):
        model[kind] = H.never_needs_model(n, (kind, (0, 0)), R)
    for (i0, j0, s0), X in ring.items():
        for (i1, j1, s1), Y in ring.items():
            lib = not any(reach[c] & masks[X] for c in rc[Y])
            # translate the source to the origin
            kind = "AB"[s0]
            rel = ("AB"[s1], ((i1 - i0) % n, (j1 - j0) % n))
            ok &= lib == (rel in model[kind])
            pairs += 1
    return n, ok, pairs


# ---------- check 5: cell level
def task_cells(args):
    n, g = args
    rot, edges, sizes, contacts, ring, cidx = H.network(n, g)
    ins = T.in_sets(sizes, contacts)
    rows, Nb, blocks = N.matrix(sizes, (60,) * len(sizes), contacts)
    rc = {ring[v]: rot[v] for v in rot}
    masks = {X: sum(1 << e for e in cs) for X, cs in rc.items()}
    ok, pairs = True, 0
    for c in range(len(contacts)):
        walk = T.reach(ins, c)[0]
        cells = cell_union(rows, 1 << c)
        for X in rc:
            ok &= bool(walk & masks[X]) == bool(cells & N.mask(blocks, X))
            pairs += 1
    return n, g, ok, pairs


# ---------- check 6: every power M^k, k >= 1, vanishes on the mirror lines
def task_mirrors(n):
    rows = H.krylov(H.M(n))
    U = H.union(rows, n)
    return n, not (U & H.mirror_lines(n)).any(), len(rows)


# ---------- checks 7 to 9
def task_census(n):
    Z = H.zero_set(n)
    a_pts, b_pts = H.never_need_A0(n, Z)
    D = H.mirror_lines(n)
    out = {"n": n, "A": len(a_pts), "B": len(b_pts), "extra zeros": int((Z & ~D).sum())}
    if n % 3:
        t = (-pow(3, -1, n)) % n
        pts = [((t + a) % n, (t + b) % n) for a, b in H.HEX]
        out["t"] = t
        out["hexagram on mirrors"] = all(D[p] for p in pts)
        out["B(t,t) never needs A(0)"] = (t, t) in b_pts
    return out


def main():
    deps = {"LATTICE-NET-20261108-001A manifest": sha(LATTICE / "manifest.json"), "lattice_lib": sha(LATTICE / "lattice_lib.py"),
            "LOOP-NET-20261108-001A manifest": sha(LOOP / "manifest.json"), "loopnet_lib": sha(LOOP / "loopnet_lib.py")}
    man = json.loads((HERE / "manifest.json").read_text())
    bound = man.get("parent_bindings", {})
    check("0_dependencies_bound", all(bound.get(str(p.relative_to(ROOT))) == sha(p) for p in
                                      [LATTICE / "manifest.json", LATTICE / "lattice_lib.py", LOOP / "manifest.json", LOOP / "loopnet_lib.py"]),
          deps)
    with Pool(12) as pool:
        r1 = pool.map(task_graph, [(n, g) for n in range(3, 11) for g in (2, 3)])
        check("1_contact_graph_is_the_model", all(ok for n, g, ok in r1), {"sides": list(range(3, 11)), "spacings": [2, 3]})
        r2 = pool.map(task_three_steps, range(3, 11))
        check("2_three_steps_are_M_turn_and_half_turn_are_automorphisms", all(ok and all(a.values()) for n, ok, a in r2),
              {str(n): {"three steps = M": ok, **a} for n, ok, a in r2})
        r3 = pool.map(task_windows, range(3, 31))
        check("3_window_lemma_and_half_turn", all(w and h for n, w, h, c in r3),
              {str(n): {"windows = nine pairs": w, "B(0) = half-turn of A(0)": h, "rings never needing A(0)": c} for n, w, h, c in r3})
        r4 = pool.map(task_contact_level, range(3, 17))
        check("4_contact_level_every_pair_of_rings", all(ok for n, ok, p in r4), {str(n): p for n, ok, p in r4})
        r5 = pool.map(task_cells, [(3, 2), (4, 2), (5, 2), (6, 2), (7, 2), (4, 3), (5, 3)])
        check("5_cell_level_needs_equal_walk_reach", all(ok for n, g, ok, p in r5), {"%d/g=%d" % (n, g): p for n, g, ok, p in r5})
        r6 = pool.map(task_mirrors, range(3, BIG + 1))
        check("6_powers_vanish_on_the_mirror_lines", all(ok for n, ok, d in r6),
              {"sides": [3, BIG], "Krylov dimensions": {str(n): d for n, ok, d in r6}})
        cen = pool.map(task_census, range(3, BIG + 1))
    t7 = [c for c in cen if c["n"] % 3]
    check("7_three_does_not_divide_n_the_turn_fixed_ring_never_needs_A0",
          all(c["hexagram on mirrors"] and c["B(t,t) never needs A(0)"] for c in t7),
          {str(c["n"]): c["t"] for c in t7})
    check("8_computed_three_divides_n_full_reach", all(c["A"] + c["B"] == 0 for c in cen if c["n"] % 3 == 0) and
          all(c["A"] + c["B"] > 0 for c in t7), {"sides": [3, BIG], "full reach at": [c["n"] for c in cen if c["A"] + c["B"] == 0]})
    check("9_computed_count_of_rings_that_never_need_a_ring", all(c["A"] + c["B"] == H.predicted_misses(c["n"]) for c in cen),
          {"counts": {str(c["n"]): [c["A"], c["B"]] for c in cen},
           "extra zeros off the mirror lines": {str(c["n"]): c["extra zeros"] for c in cen if c["extra zeros"]}})
    allok = all(v["pass"] for v in OUT.values())
    result = {"ticket": "HONEY-REACH-20261109-001A", "checks": OUT, "status": "passed" if allok else "failed",
              "seconds": round(time.time() - T0, 1)}
    path = HERE / "result.json"
    if "--write" in sys.argv:
        path.write_text(json.dumps(result, indent=1, default=str) + "\n")
        print("wrote", path)
    else:
        old = json.loads(path.read_text())
        same = {k: v["pass"] for k, v in old["checks"].items()} == {k: v["pass"] for k, v in OUT.items()}
        print("matches result.json" if same else "DIFFERS from result.json")
        sys.exit(0 if same and allok else 1)


if __name__ == "__main__":
    main()
