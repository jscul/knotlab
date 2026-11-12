#!/usr/bin/env python3
"""Referee LINE-LOCK-R1, unlagged arrangements with site-dependent ranges: the theorem needs one set S for all three entries. In an
arrangement of copies along two shifts with knot (c, c + e1, c + e2), copies may instead range over sets S_g that depend on the site's
class g = phi(c) under a homomorphism phi from Z^2 onto a small group G (phi(e1) = g1, phi(e2) = g2): the knot at a site of class g has
ranges (S_g, S_(g+g1), S_(g+g2)). If every class's triple holds a Latin square of order 2, all copies in their S_g carry the law
x_c + x_(c+e1) + x_(c+e2) = e_phi(c) over F_2 (Ledrappier's, affine) on every torus that phi fits: exactly (no other triple held), or
inside a larger set of held triples. This searches G = Z_2 and Z_3 with every onto (g1, g2) up to automorphism, 2-sets S_g, for every
harmony of the census with at most 64 states (presentation as rebuilt by ref_line.py). G trivial is the theorem's case (none expected).

    python3 -B ref_line_sites.py      (writes result_sites.json)"""
import json
import sys
import time
from collections import defaultdict
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import ref_line as L  # noqa: E402
import ref_line_ranges as Gr  # noqa: E402

CASES = [(1, (0, 0))] + [(2, g) for g in ((1, 0), (0, 1), (1, 1))] + [(3, g) for g in ((1, 0), (0, 1), (1, 1), (1, 2))]


def latin_triples(ok):
    """T[A] = list of (B, C, held): 2-sets A, B, C (frozensets of state indices) with a Latin square A x B -> C inside R, and the number
    of the 8 triples of A x B x C held by R"""
    n = ok.shape[0]
    T = defaultdict(list)
    for a0 in range(n):
        for a1 in range(a0 + 1, n):
            M0, M1 = ok[a0], ok[a1]
            V0 = M0[:, None, :] & M1[None, :, :]
            for b0 in range(n):
                for b1 in range(b0 + 1, n):
                    c0s, c1s = np.nonzero(V0[b0, b1])[0], np.nonzero(V0[b1, b0])[0]
                    if not len(c0s) or not len(c1s):
                        continue
                    seen = set()
                    for c0 in c0s:
                        for c1 in c1s:
                            if c0 == c1:
                                continue
                            C = frozenset((int(c0), int(c1)))
                            if C in seen:
                                continue
                            seen.add(C)
                            held = int(sum(ok[a, b, c] for a in (a0, a1) for b in (b0, b1) for c in C))
                            T[frozenset((a0, a1))].append((frozenset((b0, b1)), C, held))
    return T


def search(T, k, g1, g2, limit=20):
    """assignments S_0..S_(k-1) with every class's triple in T; returns found (with the triples held per class)"""
    out = []
    lookup = {A: {(B, C): held for B, C, held in lst} for A, lst in T.items()}

    def dfs(g, S, held):
        if len(out) >= limit:
            return
        if g == k:
            out.append(([sorted(S[x]) for x in range(k)], held[:]))
            return
        i, j, l = g, (g + g1) % k, (g + g2) % k
        Ai = S.get(i)
        cands = [Ai] if Ai is not None else list(T.keys())
        for A in cands:
            for B, C, h in (T.get(A, []) if (S.get(j) is None or S.get(l) is None) else
                            ([(S[j], S[l], lookup.get(A, {}).get((S[j], S[l])))] if (S[j], S[l]) in lookup.get(A, {}) else [])):
                trial = dict(S)
                ok = True
                for idx, val in ((i, A), (j, B), (l, C)):
                    if idx in trial and trial[idx] != val:
                        ok = False
                        break
                    trial[idx] = val
                if ok:
                    dfs(g + 1, trial, held + [h])
                if len(out) >= limit:
                    return
    dfs(0, {}, [])
    return out


def main():
    t0 = time.time()
    hs = L.span8_harmonies() + [L.odd_harmony(n, S) for n, S in L.ODD_SETS]
    rows = []
    for h in hs:
        W, P = h["W"], h["P"]
        if len(W) > 64:
            rows.append({"harmony": h["name"], "states": len(W), "skipped": True})
            continue
        ok = Gr.relation(h)
        T = latin_triples(ok)
        row = {"harmony": h["name"], "P": P, "states": len(W), "Latin 2-set triples": sum(len(v) for v in T.values())}
        for k, (g1, g2) in CASES:
            f = search(T, k, g1, g2)
            row[f"Z{k} {g1},{g2}"] = {"found (first 20)": len(f), "exact (every class holds 4 triples)": sum(1 for _, hl in f if all(x == 4 for x in hl)),
                                     "examples": [{"sets": [[format(W[i], f"0{P}b")[::-1] for i in s] for s in S], "held": hl} for S, hl in f[:2]]}
        rows.append(row)
        print(h["name"][:50], len(W), row["Latin 2-set triples"], {c: row[c]["found (first 20)"] for c in row if c.startswith("Z")},
              round(time.time() - t0), "s", flush=True)
    srch = [r for r in rows if not r.get("skipped")]
    summ = {"harmonies searched": len(srch), "skipped (more than 64 states)": len(rows) - len(srch)}
    for k, (g1, g2) in CASES:
        c = f"Z{k} {g1},{g2}"
        summ[c] = {"harmonies with one": sum(1 for r in srch if r[c]["found (first 20)"]),
                   "harmonies with an exact one": sum(1 for r in srch if r[c]["exact (every class holds 4 triples)"])}
    (HERE / "result_sites.json").write_text(json.dumps({"summary": summ, "rows": rows}, indent=1) + "\n")
    print(json.dumps(summ, indent=1))
    print("done", round(time.time() - t0, 1), "s")


if __name__ == "__main__":
    main()
