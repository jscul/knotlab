#!/usr/bin/env python3
"""Checks for BAND-SURFACE-20261108-001A: one band makes the torus.

    .venv/bin/python3 -B check.py          verify result.json against a fresh run
    .venv/bin/python3 -B check.py --write  write result.json from a fresh run
Needs numpy and networkx (the repository's .venv). Under a minute. Exact: return counts are followed until the next vector lies in the
span of the earlier ones and rows of M^T until they repeat; no lag cutoff."""
import hashlib
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
import band_lib as B  # noqa: E402

G, LN = B.G, B.LN
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


def main():
    write = "--write" in sys.argv
    deps = {"GROW-NET-20261108-001A manifest": "proofs/GROW-NET-20261108-001A/GROW-NET-20261108-001A-P001_bands_grow_single_rings_do_not/manifest.json",
            "grow_lib": "proofs/GROW-NET-20261108-001A/GROW-NET-20261108-001A-P001_bands_grow_single_rings_do_not/grow_lib.py"}
    m = json.loads((HERE / "manifest.json").read_text())
    bound = {k: sha(p) for k, p in deps.items()}
    check("0_dependencies_bound", all(m["parent_bindings"].get(p) == bound[k] for k, p in deps.items()), bound)

    # 1. every n x m torus with n >= 3, m >= 2 (and m >= 3, n = 2) has a half-turn at every contact and is balanced
    rows = []
    for n in range(2, 11):
        for mm in range(2, 7):
            if n == 2 and mm == 2:
                continue
            rot, edges = G.rect_torus(n, mm)
            flips = all(LN.flip(rot, edges, e) is not None for e in range(len(edges)))
            rows.append((n, mm, flips and G.balanced(rot, len(edges))))
    check("1_tori_with_a_side_of_two", all(r[2] for r in rows), {"tori": len(rows)})

    # 2. the band law from a loop: loop -> n x 2 -> n x 3 -> n x 4, genus 0 then 1, every stage balanced
    seqs = {}
    for n in range(3, 13):
        loop_rot, loop_edges = LN.dihedron(n)
        stages = [("loop", loop_rot, loop_edges)] + [("%d x %d torus" % (n, mm), *G.rect_torus(n, mm)) for mm in (2, 3, 4)]
        out = []
        for name, rot, edges in stages:
            sizes, contacts = LN.network(rot, edges, 2)
            out.append((name, LN.faces(sizes, contacts)[1], G.balanced(rot, len(edges))))
        seqs[n] = out
    ok = all(all(s[2] for s in out) and [s[1] for s in out] == [0, 1, 1, 1] for out in seqs.values())
    check("2_band_law_from_a_loop", ok, {"n = 3 to 12": "loop (genus 0) then n x 2, n x 3, n x 4 tori (genus 1), every stage balanced"})

    # 3. the n x 2 torus is the loop plus one band with double rungs, its new contacts placed on both sides
    same = True
    for n in range(3, 9):
        rot, edges = G.rect_torus(n, 2)
        deg = {v: len(l) for v, l in rot.items()}
        pairs = {}
        for (u, w) in edges:
            if u[0] == w[0]:
                pairs[frozenset((u, w))] = pairs.get(frozenset((u, w)), 0) + 1
        same &= all(d == 4 for d in deg.values()) and all(c == 2 for c in pairs.values()) and len(pairs) == n
    check("3_two_row_torus_is_a_doubly_joined_band", same, {"n": "3 to 8"})

    # 4. cell level, exact: the n x 2 torus's witnesses hold at every lag
    cells = {}
    for n in (3, 4, 5):
        rot, edges = G.rect_torus(n, 2)
        sizes, contacts = LN.network(rot, edges, 2)
        rings, Nb, blocks = N.layout(sizes, contacts)
        rows_ = N.matrix(sizes, (60,) * len(sizes), contacts)[0]
        ok = True
        for c, (ra, pa, rb, pb, law) in enumerate(contacts):
            seq, T1, p = N.orbit(rows_, 1 << c, 10 ** 6)
            wa, wb = rings[ra][pa - 1], rings[rb][pb - 1]
            ok &= all(x >> wa & 1 and x >> wb & 1 for x in seq)
        cells[n] = ok
    check("4_cells_exact", all(cells.values()), cells)

    result = {"ticket": "BAND-SURFACE-20261108-001A", "checks": OUT, "status": "passed", "seconds": round(time.time() - T0, 1)}
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
