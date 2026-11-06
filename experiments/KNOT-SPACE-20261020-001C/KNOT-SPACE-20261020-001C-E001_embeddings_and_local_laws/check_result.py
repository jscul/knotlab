#!/usr/bin/env python3
"""Independent check of KNOT-SPACE-20261020-001C-E001. It imports no producer code.

- Planarity is re-decided by a rotation-system search over vertices in
  reverse order, with the same cap.
- Allowed codes, readings (minimal supports by the shortened-code dimension,
  connectivity by reversed-order fundamental circuits) and 3-connectivity
  (full separator search) are recomputed with this file's own linear
  algebra, from the recorded edges and constraints.
- Ledrappier's dimensions are recomputed with this file's kernel.
- The predictions are recomputed.
"""

from __future__ import annotations

import json
import sys
from itertools import combinations, permutations, product
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
ART = ROOT / "artifacts" / "KNOT-SPACE-20261020-001C" / HERE.name


def basis_of(vectors):
    """Echelon basis built by scanning bits from the low end (a different elimination order)."""
    rows = []
    for v in vectors:
        for r in rows:
            low = r & -r
            if v & low:
                v ^= r
        if v:
            rows = [r ^ v if r & (v & -v) else r for r in rows]
            rows.append(v)
    return rows


def rank(vectors):
    return len(basis_of(vectors))


def span_key(vectors):
    b = basis_of(vectors)
    # canonical: fully reduce, then sort
    return tuple(sorted(b))


def all_words(b):
    words = {0}
    for v in b:
        words |= {w ^ v for w in words}
    return words


def orthogonal(b, m):
    """Dual code by brute force over a basis of the complement: solve via enumeration of free coordinates."""
    piv = {}
    for v in basis_of(b):
        piv[(v & -v).bit_length() - 1] = v
    free = [j for j in range(m) if j not in piv]
    out = []
    for f in free:
        x = 1 << f
        for p, v in piv.items():
            if v >> f & 1:
                x |= 1 << p
        out.append(x)
    return out


def minimal_supports(b, m):
    full = (1 << m) - 1
    k = rank(b)
    out = []
    for c in all_words(b):
        if c and k - rank([v & (full ^ c) for v in b]) == 1:
            out.append(c)
    return out


def connected(b, mask):
    elems = [j for j in range(mask.bit_length()) if mask >> j & 1]
    if not elems:
        return False
    rows = []
    for v in sorted((x & mask for x in b), reverse=True):
        for r in rows:
            hi = 1 << (r.bit_length() - 1)
            if v & hi:
                v ^= r
        if v:
            hi = 1 << (v.bit_length() - 1)
            rows = [r ^ v if r & hi else r for r in rows]
            rows.append(v)
    parent = {j: j for j in elems}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for r in rows:
        p = r.bit_length() - 1
        for j in elems:
            if j != p and r >> j & 1:
                parent[find(j)] = find(p)
    return len({find(j) for j in elems}) == 1


def reading(b, m):
    full = (1 << m) - 1
    verts = [c for c in minimal_supports(b, m) if connected(b, full ^ c)]
    if any(sum(1 for c in verts if c >> j & 1) != 2 for j in range(m)):
        return False, verts
    return span_key(verts) == span_key(b), verts


def three_connected(b, m):
    full = (1 << m) - 1
    if not connected(b, full):
        return False
    rE = rank(b)
    for X in range(1, full):
        if X & 1 == 0:
            continue
        Y = full ^ X
        if bin(X).count("1") >= 2 and bin(Y).count("1") >= 2 and \
                rank([v & X for v in b]) + rank([v & Y for v in b]) - rE <= 1:
            return False
    return True


def potentials_cut_space(n, edges):
    words = set()
    for pot in product((0, 1), repeat=n - 1):
        p = (0,) + pot
        words.add(sum(1 << i for i, (a, c) in enumerate(edges) if p[a] != p[c]))
    return basis_of(list(words))


def stars(n, edges):
    out = [0] * n
    for i, (a, c) in enumerate(edges):
        out[a] |= 1 << i
        out[c] |= 1 << i
    return out




def planar(n, edges, cap=2_000_000):
    nbrs = {v: [] for v in range(n)}
    for a, b in edges:
        nbrs[a].append(b)
        nbrs[b].append(a)
    order = list(reversed(range(n)))
    options = []
    total = 1
    for v in order:
        ns = sorted(nbrs[v], reverse=True)
        opts = [tuple(ns)] if len(ns) <= 2 else [(ns[0],) + p for p in permutations(ns[1:])]
        options.append((v, opts))
        total *= len(opts)
    if total > cap:
        return None
    m = len(edges)
    for choice in product(*(o for _, o in options)):
        succ = {}
        for (v, _), cyc in zip(options, choice):
            for i, w in enumerate(cyc):
                succ[(v, w)] = cyc[(i + 1) % len(cyc)]
        seen = set()
        faces = 0
        for a, b in edges:
            for dart in ((a, b), (b, a)):
                if dart in seen:
                    continue
                faces += 1
                d = dart
                while d not in seen:
                    seen.add(d)
                    u, w = d
                    d = (w, succ[(w, u)])
        if n - m + faces == 2:
            return True
    return False


def ledrappier_dim(L):
    idx = lambda i, j: (i % L) * L + (j % L)
    rows = [(1 << idx(i, j)) | (1 << idx(i + 1, j)) | (1 << idx(i, j + 1)) for i in range(L) for j in range(L)]
    return len(orthogonal(rows, L * L))


def main() -> int:
    result = json.loads((ART / "result.json").read_text())
    rows = [json.loads(line) for line in (ART / "raw_rows.jsonl").read_text().splitlines()]
    problems = []
    plan = {"graphs": 0, "agree": 0, "planarity_matches": 0}
    for r in rows:
        if r["part"] != "planarity":
            continue
        n, m = r["n"], r["m"]
        edges = [tuple(e) for e in r["edges"]]
        p = planar(n, edges)
        if p != r["planar_by_embeddings"]:
            problems.append(f"planarity differs for {r['name']}")
        else:
            plan["planarity_matches"] += 1
        if not r["three_connected_graph"] or p is None:
            continue
        plan["graphs"] += 1
        cyc = orthogonal(potentials_cut_space(n, edges), m)
        ok, _ = reading(cyc, m)
        plan["agree"] += ok == p
        if ok != r["dual_reading"]:
            problems.append(f"dual reading differs for {r['name']}")
    local = {"checked": 0, "agree": 0, "three_connected": 0, "graphic_or_cographic": 0}
    for r in rows:
        if r["part"] != "local" or r.get("three_connected") is None:
            continue
        m = r["m"]
        C = orthogonal(r["constraints"], m)
        dual = orthogonal(C, m)
        tc = three_connected(C, m)
        g, cg = reading(C, m)[0], reading(dual, m)[0]
        local["checked"] += 1
        local["agree"] += (tc, g, cg) == (r["three_connected"], r["graphic"], r["cographic"])
        if tc:
            local["three_connected"] += 1
            local["graphic_or_cographic"] += g or cg
    if local["agree"] != local["checked"]:
        problems.append(f"local verdicts differ on {local['checked'] - local['agree']} laws")
    ledr_ok = all(ledrappier_dim(r["L"]) == r["dim"] for r in rows if r["part"] == "ledrappier")
    if not ledr_ok:
        problems.append("Ledrappier dimensions differ")
    t1 = plan["agree"] == plan["graphs"]
    t2 = local["three_connected"] >= 20 and local["graphic_or_cographic"] <= 0.05 * local["three_connected"]
    if {"T1": t1, "T2": t2} != result["predictions"]:
        problems.append(f"prediction flags differ: {t1, t2} vs {result['predictions']}")
    report = {"planarity": plan, "local": local, "ledrappier_dims_match": ledr_ok, "predictions_recomputed": {"T1": t1, "T2": t2}}
    status = "passed: recomputation agrees (V1, exploratory evidence only)" if not problems else "failed"
    text = json.dumps(report, indent=2, sort_keys=True) + "\n" + status + "\n" + "\n".join(problems) + "\n"
    (ART / "check_output.txt").write_text(text)
    print(text)
    return 0 if not problems else 1


if __name__ == "__main__":
    sys.exit(main())
