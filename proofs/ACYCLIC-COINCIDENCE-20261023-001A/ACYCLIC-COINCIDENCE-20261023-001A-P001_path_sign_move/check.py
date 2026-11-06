#!/usr/bin/env python3
"""Check of ACYCLIC-COINCIDENCE-20261023-001A-P001 (standard library only).

- Lemma 1 and Theorem 2 on random signed graphs: a signed graph H with links of both signs between a and b, plus a path of k
  edges from a to b through new vertices of degree 2. Flipping one path edge leaves the chromatic polynomial (subset expansion)
  and the characteristic polynomial of the frame matroid unchanged, and chi(G) = chi(H) ((lambda-1)^k - (-1)^k) / lambda. Brute
  force over colourings confirms the subset expansion at lambda = 3 and 5 on the smaller graphs, and that the zero-free
  colourings (nonzero colours) at lambda = 2 and 4 are unchanged and obey the same closed form. The full Tutte polynomial is
  recorded as changed or not.
- Corollary 3 on the residue: the surface L(3,1,3,1) is rebuilt by its own construction and the residual skeletons are read
  from artifacts/TWIST-MAP-20261023-001B/.../raw_rows.jsonl (pairs of kind unexplained, skeletons whose shrunken graphs were
  not matched). For each skeleton and both twists the clusters, gauges and shrunken signed graph (the frame matroid contracted
  by the skeleton) are rebuilt. The check confirms:
  - c * A equals the recorded skeleton count, with c = T(0, 2) of the skeleton and A = T(2, 0) of the contraction;
  - the two shrunken graphs have equal characteristic polynomials but different Tutte polynomials;
  - flipping one path whose ends are joined by links of both signs makes them isomorphic frame matroids, by an explicit bijection
    of circuits.
- Controls (each must be rejected):
  - the flip with a link of only one sign between the ends changes some chromatic polynomial;
  - the flip of a path through a vertex of degree 3 changes some chromatic polynomial;
  - shrinking without the clusters' gauges breaks c * A = count on some skeleton;
  - the residual graphs are isomorphic without the flip.

    python3 -B check.py          verify result.json against a fresh run
    python3 -B check.py --write  write result.json from a fresh run
"""

from __future__ import annotations

import json
import random
import sys
from collections import Counter
from itertools import combinations, product
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
RAW = ROOT / "artifacts/TWIST-MAP-20261023-001B/TWIST-MAP-20261023-001B-E001_genus_two_map/raw_rows.jsonl"
SEED = 20261023


# ------------------------------------------------------------------ signed graphs
# An element is (kind, a, b, sign): "link" (a != b), "loop" (a == b) or "half" (a == b, sign 1); sign 0 positive, 1 negative.

def balanced(nodes, els, S):
    """Number of balanced components of (nodes, S)."""
    parent = {v: v for v in nodes}
    par = {v: 0 for v in nodes}
    bad = {v: False for v in nodes}

    def find(v):
        p = 0
        while parent[v] != v:
            p ^= par[v]
            v = parent[v]
        return v, p

    for i in S:
        kind, a, b, s = els[i]
        if kind == "half" or (kind == "loop" and s):
            bad[find(a)[0]] = True
        elif kind == "link":
            (ra, pa), (rb, pb) = find(a), find(b)
            if ra == rb:
                if pa ^ pb ^ s:
                    bad[ra] = True
            else:
                parent[rb], par[rb] = ra, pa ^ pb ^ s
                bad[ra] = bad[ra] or bad[rb]
    return sum(1 for v in nodes if parent[v] == v and not bad[v])


def rank(nodes, els, S):
    return len(nodes) - balanced(nodes, els, S)


def polys(nodes, els):
    """Chromatic polynomial {degree: coeff}, characteristic polynomial of the frame matroid, and the Tutte polynomial in the
    form {(r(E) - r(S), |S| - r(S)): count}, by subset expansion."""
    m = len(els)
    rE = rank(nodes, els, range(m))
    chi, char, tutte = Counter(), Counter(), Counter()
    for bits in range(1 << m):
        S = [i for i in range(m) if bits >> i & 1]
        b = balanced(nodes, els, S)
        r = len(nodes) - b
        sgn = -1 if len(S) & 1 else 1
        chi[b] += sgn
        char[rE - r] += sgn
        tutte[(rE - r, len(S) - r)] += 1
    clean = lambda c: {k: v for k, v in c.items() if v}
    return clean(chi), clean(char), dict(tutte)


def ev(poly, lam):
    return sum(c * lam ** k for k, c in poly.items())


def tutte_at(tutte, x, y):
    return sum(c * (x - 1) ** a * (y - 1) ** b for (a, b), c in tutte.items())


def colourings(nodes, els, lam):
    """Proper colourings by brute force: colours -k..k when lam = 2k + 1, and the nonzero colours -k..-1, 1..k (zero-free)
    when lam = 2k."""
    k = lam // 2
    palette = range(-k, k + 1) if lam & 1 else [c for c in range(-k, k + 1) if c]
    idx = {v: i for i, v in enumerate(nodes)}
    n = 0
    for col in product(palette, repeat=len(nodes)):
        ok = True
        for kind, a, b, s in els:
            ca, cb = col[idx[a]], col[idx[b]]
            if kind == "link":
                ok = cb != (-ca if s else ca)
            elif kind == "half" or s:
                ok = ca != 0
            else:
                ok = False
            if not ok:
                break
        n += ok
    return n


def circuits(nodes, els):
    m, out = len(els), []
    for size in range(1, m + 1):
        for S in combinations(range(m), size):
            if any(set(C) <= set(S) for C in out):
                continue
            if rank(nodes, els, S) == size - 1:
                out.append(S)
    return out


def matroid_iso(c1, c2, m):
    """A bijection of elements carrying the circuits of one matroid onto those of the other, or None."""
    if sorted(map(len, c1)) != sorted(map(len, c2)):
        return None
    inv = lambda cs: {i: tuple(sorted(len(C) for C in cs if i in C)) for i in range(m)}
    i1, i2 = inv(c1), inv(c2)
    if sorted(i1.values()) != sorted(i2.values()):
        return None
    S2 = {frozenset(C) for C in c2}
    order = sorted(range(m), key=lambda i: -len(i1[i]))
    phi, used = {}, set()

    def consistent():
        return all(frozenset(phi[i] for i in C) in S2 for C in c1 if all(i in phi for i in C))

    def extend(k):
        if k == m:
            return True
        i = order[k]
        for j in range(m):
            if j in used or i2[j] != i1[i]:
                continue
            phi[i] = j
            used.add(j)
            if consistent() and extend(k + 1):
                return True
            del phi[i]
            used.discard(j)
        return False

    return dict(phi) if extend(0) else None


def series_paths(nodes, els):
    """Maximal paths a - v1 - ... - b whose inner vertices meet exactly two element ends, both links: (a, b, indices)."""
    deg, inc = Counter(), {v: [] for v in nodes}
    for i, (kind, a, b, s) in enumerate(els):
        if kind == "link":
            deg[a] += 1
            deg[b] += 1
            inc[a].append(i)
            inc[b].append(i)
        else:
            deg[a] += 2 if kind == "loop" else 1
    inner = {v for v in nodes if deg[v] == 2 and len(inc[v]) == 2}
    out, done = [], set()
    for v in sorted(inner, key=repr):
        if v in done:
            continue
        ends = []
        for e0 in inc[v]:
            cur, e, seq = v, e0, []
            while True:
                seq.append(e)
                _k, a, b, _s = els[e]
                nxt = b if a == cur else a
                if nxt in inner and nxt != v:
                    done.add(nxt)
                    e = [f for f in inc[nxt] if f != e][0]
                    cur = nxt
                else:
                    ends.append((nxt, seq))
                    break
        done.add(v)
        (a, sa), (b, sb) = ends
        out.append((a, b, list(reversed(sa)) + sb))
    return out


def eligible(nodes, els, signs_needed=frozenset((0, 1))):
    out = []
    for a, b, idx in series_paths(nodes, els):
        if a == b:
            continue
        on = set(idx)
        signs = {s for i, (k, x, y, s) in enumerate(els) if k == "link" and i not in on and {x, y} == {a, b}}
        if signs >= signs_needed:
            out.append(idx)
    return out


def flip(els, i):
    k, a, b, s = els[i]
    return els[:i] + [(k, a, b, s ^ 1)] + els[i + 1:]


# ------------------------------------------------------------------ Theorem 2 on random signed graphs

def random_case(rng, both=True, branch=False):
    n = rng.randint(2, 4)
    H = list(range(n))
    els = [("link", 0, 1, 0), ("link", 0, 1, 1)] if both else [("link", 0, 1, rng.randint(0, 1))] * rng.randint(0, 1)
    for _ in range(rng.randint(0, 5)):
        r = rng.random()
        u, w = rng.sample(H, 2)
        if r < 0.7:
            els.append(("link", u, w, rng.randint(0, 1)))
        else:
            els.append(("half" if r < 0.85 else "loop", u, u, 1))
    k = rng.randint(2, 4)
    inner = list(range(n, n + k - 1))
    seq = [0] + inner + [1]
    path = [("link", seq[i], seq[i + 1], rng.randint(0, 1)) for i in range(k)]
    if branch:
        path.append(("link", inner[0], rng.choice(H), rng.randint(0, 1)))
    return H + inner, els, path, k


def theorem_checks(rng, cases=300):
    out = Counter()
    for _ in range(cases):
        nodes, H, path, k = random_case(rng)
        G = H + path
        G2 = H + flip(path, rng.randrange(k))
        chi1, char1, t1 = polys(nodes, G)
        chi2, char2, t2 = polys(nodes, G2)
        out["cases"] += 1
        out["chromatic polynomial unchanged"] += chi1 == chi2
        out["characteristic polynomial unchanged"] += char1 == char2
        out["T(2,0) unchanged"] += tutte_at(t1, 2, 0) == tutte_at(t2, 2, 0)
        out["Tutte polynomial changed"] += t1 != t2
        chiH = polys(nodes[:len(nodes) - (k - 1)], H)[0]
        closed = all(ev(chi1, lam) * lam == ev(chiH, lam) * ((lam - 1) ** k - (-1) ** k) for lam in (3, 5, 7, 9))
        out["closed form chi(G) = chi(H) ((lam-1)^k - (-1)^k) / lam"] += closed
        if len(nodes) <= 6:
            out["brute-force colourings checked"] += 1
            out["brute force agrees at 3 and 5"] += all(colourings(nodes, G, lam) == ev(chi1, lam) and
                                                        colourings(nodes, G2, lam) == ev(chi2, lam) for lam in (3, 5))
            nH = len(nodes) - (k - 1)
            out["zero-free colourings at 2 and 4 unchanged and equal to the closed form"] += all(
                colourings(nodes, G, lam) == colourings(nodes, G2, lam)
                and colourings(nodes, G, lam) * lam == colourings(nodes[:nH], H, lam) * ((lam - 1) ** k - (-1) ** k)
                for lam in (2, 4))
    return dict(out)


def control_changes(rng, **kw):
    """Number of random cases (of 300) where a flip outside the hypothesis changes the chromatic polynomial."""
    changed = 0
    for _ in range(300):
        nodes, H, path, k = random_case(rng, **kw)
        if polys(nodes, H + path)[0] != polys(nodes, H + flip(path, 0))[0]:
            changed += 1
    return changed


# ------------------------------------------------------------------ the surface and its shrunken graphs

def l_surface(A, B, C, D):
    cells = [(x, y) for y in range(C) for x in range(A + B)] + [(x, y) for y in range(C, C + D) for x in range(A)]
    pos = {c: i for i, c in enumerate(cells)}
    right = [pos[((x + 1) % (A + B if y < C else A), y)] for x, y in cells]
    up = [pos[(x, (y + 1) % (C + D if x < A else C))] for x, y in cells]
    root = list(range(4 * len(cells)))

    def find(a):
        while root[a] != a:
            a = root[a]
        return a

    for s in range(len(cells)):
        for a, b in ((4 * s + 1, 4 * right[s]), (4 * s + 2, 4 * up[s]), (4 * s + 3, 4 * right[s] + 2), (4 * s + 3, 4 * up[s] + 1)):
            ra, rb = find(a), find(b)
            if ra != rb:
                root[rb] = ra
    names = {}
    corner = lambda s, k: names.setdefault(find(4 * s + k), len(names))
    edges = []
    for s, (x, y) in enumerate(cells):
        edges.append((corner(s, 0), corner(s, 1), (0, 0, int(x == 0), int(x == A))))      # bottom side, offsets mod 2
        edges.append((corner(s, 0), corner(s, 2), (int(y == 0), int(y == C + D - 1), 0, 0)))  # left side
    V = len(names)
    assert V - len(edges) + len(cells) == -2
    return V, edges, cells, right, up


def edge_twists(edges, alpha):
    return [sum(a * o for a, o in zip(alpha, off)) & 1 for _u, _w, off in edges]


def shrink(V, edges, mask, alpha, use_gauge=True):
    """Skeleton frame matroid (nodes, elements) and the contraction by the skeleton, simplified."""
    t = edge_twists(edges, alpha)
    adj = {}
    for e, (u, w, _o) in enumerate(edges):
        if mask >> e & 1:
            adj.setdefault(u, []).append((w, t[e]))
            adj.setdefault(w, []).append((u, t[e]))
    cid, gauge, odd = {}, {}, []
    for v in sorted(adj):
        if v in cid:
            continue
        k = len(odd)
        odd.append(False)
        cid[v], gauge[v] = k, 0
        stack = [v]
        while stack:
            u = stack.pop()
            for w, f in adj[u]:
                if w not in cid:
                    cid[w], gauge[w] = k, gauge[u] ^ f
                    stack.append(w)
                elif gauge[w] != gauge[u] ^ f:
                    odd[k] = True
    skel = [("link", u, w, t[e]) for e, (u, w, _o) in enumerate(edges) if mask >> e & 1]
    node = lambda v: ("c", cid[v]) if v in cid else ("v", v)
    is_odd = lambda n: n[0] == "c" and odd[n[1]]
    nodes = sorted({node(v) for v in range(V)} - {n for n in {node(v) for v in range(V)} if is_odd(n)}, key=repr)
    raw, loops0 = [], 0
    for e, (u, w, _o) in enumerate(edges):
        if mask >> e & 1:
            continue
        a, b = node(u), node(w)
        th = t[e] ^ ((gauge.get(u, 0) ^ gauge.get(w, 0)) if use_gauge else 0)
        if is_odd(a) and is_odd(b):
            loops0 += 1                               # a loop of the contraction: no acyclic orientation
        elif is_odd(a) or is_odd(b):
            v = b if is_odd(a) else a
            raw.append(("half", v, v, 1))
        elif a == b:
            if th:
                raw.append(("loop", a, a, 1))
            else:
                loops0 += 1
        else:
            raw.append(("link", *sorted((a, b), key=repr), th))
    simple, seen = [], set()
    for kind, a, b, s in raw:
        key = (a, "unbalanced loop") if kind in ("half", "loop") else (a, b, s)
        if key not in seen:
            seen.add(key)
            simple.append((kind, a, b, s))
    return list(range(V)), skel, nodes, simple, loops0, len(raw) - len(simple)


def t02(nodes, els):
    m = len(els)
    rE = rank(nodes, els, range(m))
    return sum((-1) ** (rE - rank(nodes, els, [i for i in range(m) if bits >> i & 1])) for bits in range(1 << m))


def residue_checks():
    rows = [json.loads(l) for l in RAW.read_text().splitlines() if l.strip()]
    row = next(r for r in rows if r["label"] == "L(3,1,3,1)")
    V, edges, *_ = l_surface(3, 1, 3, 1)
    out = Counter()
    relations = []
    for p in row["analysis"]["pairs"]:
        if p["kind"] != "unexplained":
            continue
        none = [s for s in p["per_skeleton"] if s[3][0] == "none"]
        if not none:
            continue
        relations.append({"twists": p["twists"], "label": p["label"], "counts": p["counts"], "skeletons": len(p["per_skeleton"]),
                          "skeletons without matched shrunken graphs": len(none)})
        q1, q2 = (tuple(int(ch) for ch in s) for s in p["twists"])
        for mask, x1, x2, _rel in none:
            out["skeletons"] += 1
            graphs = []
            for q, x in ((q1, x1), (q2, x2)):
                verts, skel, nodes, els, loops0, merged = shrink(V, edges, mask, q)
                c = t02(verts, skel)
                chi, char, tut = polys(nodes, els)
                A = 0 if loops0 else tutte_at(tut, 2, 0)
                out["c * A equals the recorded count"] += c * A == x
                out["parallel elements merged"] += merged
                graphs.append((nodes, els, char, tut))
            (n1, e1, ch1, t1), (n2, e2, ch2, t2) = graphs
            out["equal characteristic polynomials"] += ch1 == ch2
            out["different Tutte polynomials"] += t1 != t2
            m = len(e1)
            c1 = circuits(n1, e1)
            out["isomorphic without a flip (control)"] += len(e2) == m and matroid_iso(c1, circuits(n2, e2), m) is not None
            found = 0
            for idx in eligible(n2, e2):
                e2f = flip(e2, idx[0])
                if len(e2f) == m and matroid_iso(c1, circuits(n2, e2f), m) is not None:
                    found = 1
                    break
            out["one flip gives isomorphic frame matroids"] += found
            # control: shrinking without the clusters' gauges
            verts, skel, nodes, els, loops0, _m = shrink(V, edges, mask, q1, use_gauge=False)
            A = 0 if loops0 else tutte_at(polys(nodes, els)[2], 2, 0)
            out["without gauges c * A differs (control)"] += t02(verts, skel) * A != x1
    return dict(out), relations


def main() -> int:
    rng = random.Random(SEED)
    manifest = json.loads((HERE / "manifest.json").read_text())
    result = {"schema_version": 3, "artifact_id": manifest["artifact_id"], "kind": "proof", "ticket": manifest["ticket"],
              "proof": manifest["proof"], "claim": manifest["claim"], "foundation_contract": manifest["foundation_contract"],
              "semantic_domains": manifest["semantic_domains"], "evidence_modes": manifest["evidence_modes"],
              "thesis_alignment": manifest["thesis_alignment"], "safe_conclusions": manifest["safe_to_conclude"],
              "checks": {}, "controls": {}}
    result["checks"]["Theorem 2 on random signed graphs"] = theorem_checks(rng)
    res, rel = residue_checks()
    result["checks"]["Corollary 3 on the 48 residual skeletons of L(3,1,3,1)"] = res
    result["relations"] = rel
    result["controls"]["flip with one sign between the ends changes chi (cases of 300)"] = control_changes(rng, both=False)
    result["controls"]["flip through a vertex of degree 3 changes chi (cases of 300)"] = control_changes(rng, branch=True)
    th = result["checks"]["Theorem 2 on random signed graphs"]
    n = res.get("skeletons", 0)
    ok = (th["chromatic polynomial unchanged"] == th["characteristic polynomial unchanged"] == th["T(2,0) unchanged"]
          == th["closed form chi(G) = chi(H) ((lam-1)^k - (-1)^k) / lam"] == th["cases"]
          and th["brute force agrees at 3 and 5"] == th["brute-force colourings checked"] > 0 and th["Tutte polynomial changed"] > 0
          and th["zero-free colourings at 2 and 4 unchanged and equal to the closed form"] == th["brute-force colourings checked"]
          and n == 48 and res["c * A equals the recorded count"] == 2 * n and res["equal characteristic polynomials"] == n
          and res["different Tutte polynomials"] == n and res["one flip gives isomorphic frame matroids"] == n
          and res.get("isomorphic without a flip (control)", 0) == 0 and res.get("without gauges c * A differs (control)", 0) > 0
          and all(v > 0 for v in result["controls"].values()))
    result["status"] = "passed" if ok else "failed"
    result["failures"] = [] if ok else ["a check or control did not come out as stated in proof.md"]
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if "--write" in sys.argv:
        (HERE / "result.json").write_text(text)
    else:
        old = (HERE / "result.json").read_text() if (HERE / "result.json").exists() else None
        print("result.json matches" if old == text else "result.json differs from a fresh run")
        if old != text:
            ok = False
    print(text)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
