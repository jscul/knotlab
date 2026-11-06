#!/usr/bin/env python3
"""Independent check of KNOT-SPACE-20261020-001A-E001. It imports no producer code.

- The gauge law's allowed states are enumerated directly as edge differences
  of all vertex potentials. They are compared with a kernel computed here,
  from a freshly scrambled presentation of the law.
- A codeword c is taken as a minimal support exactly when the shortened code
  on supp(c) has dimension 1: dim C - rank(C restricted to the complement)
  equals 1.
- Matroid connectivity uses fundamental circuits relative to a basis chosen
  by scanning columns from the highest index down.
- Recovered vertices and faces, the sphere counts, the Whitney twists, the
  non-binary gauge circuits (with groups built here) and the local-law
  verdicts are all recomputed. 3-connectivity is tested by full separator
  search.
"""

from __future__ import annotations

import json
import random
import sys
from itertools import combinations, product
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
ART = ROOT / "artifacts" / "KNOT-SPACE-20261020-001A" / HERE.name


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


def group_states(n, edges, group):
    if group == "Z3":
        els = list(range(3))
        sub = lambda a, c: (a - c) % 3
    else:
        from itertools import permutations
        els = list(permutations(range(3)))

        def mul(p, r):
            return tuple(p[r[i]] for i in range(3))

        def inv(p):
            r = [0] * 3
            for i in range(3):
                r[p[i]] = i
            return tuple(r)

        sub = lambda a, c: mul(a, inv(c))
    out = set()
    for pot in product(els, repeat=n - 1):
        p = (els[0],) + pot
        out.add(tuple(sub(p[a], p[c]) for a, c in edges))
    return out


def relative_circuits(S, m):
    sizes = [len({t[i] for t in S}) for i in range(m)]

    def constrained(Y):
        full = 1
        for i in Y:
            full *= sizes[i]
        return len({tuple(t[i] for i in Y) for t in S}) < full

    return sorted(Y for size in range(1, m + 1) for Y in combinations(range(m), size)
                  if constrained(Y) and all(not constrained(tuple(v for v in Y if v != w)) for w in Y))


def main() -> int:
    result = json.loads((ART / "result.json").read_text())
    rows = [json.loads(line) for line in (ART / "raw_rows.jsonl").read_text().splitlines()]
    problems = []
    rng = random.Random(3)
    rec = [r for r in rows if r["part"] == "recovery"]
    counts = {"recovery_rows": 0, "gauge_ok": 0, "tseitin_ok": 0, "presentation_invariant": 0, "spheres": 0,
              "nonplanar_dual_fails": 0}
    for r in rec:
        n, m = r["n"], r["m"]
        edges = [tuple(e) for e in r["edges"]]
        if not r["three_connected_graph"]:
            continue
        counts["recovery_rows"] += 1
        cut = potentials_cut_space(n, edges)
        truth = span_key(stars(n, edges))
        star_family = sorted(stars(n, edges))
        ok, verts = reading(cut, m)
        g_ok = ok and sorted(verts) == star_family
        counts["gauge_ok"] += g_ok
        cyc = orthogonal(cut, m)
        dual_of_tseitin_code = orthogonal(cyc, m)
        ok2, verts2 = reading(dual_of_tseitin_code, m)
        counts["tseitin_ok"] += ok2 and sorted(verts2) == star_family
        rows_scr = list(cyc)
        for _ in range(3 * len(rows_scr)):
            i, j = rng.randrange(len(rows_scr)), rng.randrange(len(rows_scr))
            if i != j:
                rows_scr[i] ^= rows_scr[j]
        counts["presentation_invariant"] += span_key(orthogonal(rows_scr, m)) == span_key(cut)
        if (r["gauge_recovered"] == 3) != g_ok:
            problems.append(f"gauge recovery verdict differs for {r['name']}")
        okf, faces = reading(cyc, m)
        if r["planar"]:
            sphere = okf and all(sum(1 for f in faces if f >> j & 1) == 2 for j in range(m)) and n - m + len(faces) == 2
            counts["spheres"] += sphere
            if sphere != bool(r.get("sphere")):
                problems.append(f"sphere verdict differs for {r['name']}")
        else:
            counts["nonplanar_dual_fails"] += not okf
            if okf != bool(r.get("dual_reading")):
                problems.append(f"dual reading differs for {r['name']}")
        if truth != span_key(cut):
            problems.append(f"cut space mismatch for {r['name']}")

    tw = [r for r in rows if r["part"] == "twist"]
    twist_ok = 0
    for r in tw:
        n = r["n"]
        e1 = [tuple(e) for e in r["edges"]]
        e2 = [tuple(e) for e in r["edges_twisted"]]
        same = span_key(potentials_cut_space(n, e1)) == span_key(potentials_cut_space(n, e2))
        differ = sorted(stars(n, e1)) != sorted(stars(n, e2))
        twist_ok += same and differ
        if (same, differ) != (r["same_allowed_states"], r["stars_differ"]):
            problems.append("twist verdict differs")

    nb_ok = 0
    graphs = {"K4": (4, [(a, b) for a, b in combinations(range(4), 2)]),
              "prism 3": (6, [(0, 1), (1, 2), (2, 0), (3, 4), (4, 5), (5, 3), (0, 3), (1, 4), (2, 5)]),
              "W5": (6, [(0, i) for i in range(1, 6)] + [(i, i % 5 + 1) for i in range(1, 6)]),
              "K5": (5, [(a, b) for a, b in combinations(range(5), 2)])}
    nb = [r for r in rows if r["part"] == "nonbinary"]
    for r in nb:
        n, edges = graphs[r["name"]]
        m = len(edges)
        cyc = orthogonal(potentials_cut_space(n, edges), m)
        cycles = sorted(tuple(j for j in range(m) if c >> j & 1) for c in minimal_supports(cyc, m))
        circ = relative_circuits(group_states(n, edges, r["group"]), m)
        nb_ok += circ == cycles
        if (circ == cycles) != r["circuits_are_cycles"]:
            problems.append(f"non-binary verdict differs for {r['name']} {r['group']}")

    local = [r for r in rows if r["part"] == "local"]
    lc = {"three_connected": 0, "graphic_or_cographic": 0, "agree": 0, "checked": 0}
    for r in local:
        if r.get("three_connected") is None:
            continue
        m = r["m"]
        C = orthogonal(r["constraints"], m)
        dual = orthogonal(C, m)
        tc = three_connected(C, m)
        g = reading(C, m)[0]
        cg = reading(dual, m)[0]
        lc["checked"] += 1
        lc["agree"] += (tc, g, cg) == (r["three_connected"], r["graphic"], r["cographic"])
        if r["kind"].startswith("three per") and tc:
            lc["three_connected"] += 1
            lc["graphic_or_cographic"] += g or cg
    if lc["agree"] != lc["checked"]:
        problems.append(f"local-law verdicts differ on {lc['checked'] - lc['agree']} laws")

    report = {"counts": counts, "twists_ok": twist_ok, "twists": len(tw), "nonbinary_ok": nb_ok, "nonbinary": len(nb),
              "local": lc}
    status = "passed: recomputation agrees (V1, exploratory evidence only)" if not problems else "failed"
    text = json.dumps(report, indent=2, sort_keys=True) + "\n" + status + "\n" + "\n".join(problems) + "\n"
    (ART / "check_output.txt").write_text(text)
    print(text)
    return 0 if not problems else 1


if __name__ == "__main__":
    sys.exit(main())
