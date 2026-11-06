#!/usr/bin/env python3
"""Check of WALLS-WITH-CHOICES-20261024-001C-P001 (standard library only).

Uses the wall graph of WALLS-WITH-CHOICES-20261024-001A-P001's check and the shared machinery of DIRECTIONAL-RIGIDITY-20261023-001B-P001.

- The planted configurations of the proof for placements 147 and 54 (directed walls without choices), 155, 110, 203 and 62 (directed
  walls with a free place) and 151 and 109 (walls turning both ways, no free place), on every L x M torus with 3 <= L, M <= 9, in the
  twist of the proof:
  - the periodic walls are exactly those listed by the proof (the planted staircase W*, and for 151 and 109 also the braid W2, the
    two loops of ten states and the loops around interior vertices, whose lengths add up to all 12 L M states);
  - by Theorem 1 of WALLS-WITH-CHOICES-20261024-001A-P001, the configuration contradicts along (1, 0) and (0, 1) and has
    assignments along (1, 2) and (2, 1): it is selective.
- On 3 x 3, 3 x 4 and 4 x 4 the same four verdicts are certified directly by the own solver for every planted configuration.
- The honeycomb kind with a free place (159, 215, 111, 125): from the frozen rows of DIRECTIONAL-RIGIDITY-20261023-001A-E001, no
  configuration on 3 x 3 or 3 x 4 contradicts along every odd class, and the number contradicting along none.
- Controls: the planted configuration of 155 without the blocking of the column's left exits has another winding wall and is not
  selective on 3 x 3; in the fitting twist no class is odd, so nothing can contradict.

    python3 -B check.py          verify result.json against a fresh run
    python3 -B check.py --write  write result.json from a fresh run
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

sys.setrecursionlimit(20000)
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
_spec = importlib.util.spec_from_file_location(
    "wall_check", ROOT / "proofs/WALLS-WITH-CHOICES-20261024-001A/WALLS-WITH-CHOICES-20261024-001A-P001_wall_theorem/check.py")
A = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(A)
DR = A.DR

TWIST = (1, 1)                       # relative twist of the proof, in the constant frame
TARGETS = {(1, 0): True, (0, 1): True, (1, 2): False, (2, 1): False}   # True: must contradict


def fidx(typ, i, j, L, M):
    return 2 * ((j % M) * L + (i % L)) + typ


def setbit(x, k, v):
    return (x & ~(1 << k)) | (v << k)


# ------------------------------------------------------------------ planted configurations, in the constant frame

def plant_147(L, M):
    """Directed walls, no free place: up(S) decides which copy enters from the bottom (E = 1 + coin), dn(S) which copy leaves at
    the top (X = coin). Corner E = 1, X = 0; column E = X = 0; row E = X = 1; elsewhere E = X = 0."""
    x = 0
    for i in range(L):
        for j in range(M):
            if (i, j) == (0, 0):
                E, X = 1, 0
            elif i == 0:
                E, X = 0, 0
            elif j == 0:
                E, X = 1, 1
            else:
                E, X = 0, 0
            x = setbit(x, fidx(0, i, j, L, M), 1 ^ E)
            x = setbit(x, fidx(1, i, j, L, M), X)
    return x


def plant_155(L, M, block_column=True):
    """Directed walls with place 2 free: the up-bond into S is open for copy 1 + coin(up S), the left-bond out of S for copy
    1 + coin(dn S); entering from the right and leaving at the top are free."""
    x = 0
    for i in range(L):
        for j in range(M):
            if (i, j) == (0, 0):
                up, left = 1, 1
            elif i == 0:
                up, left = 0, (1 if block_column else 0)
            elif j == 0:
                up, left = 0, 0
            elif j == 1:
                up, left = 1, 0
            else:
                up, left = 0, 0
            x = setbit(x, fidx(0, i, j, L, M), 1 ^ up)
            x = setbit(x, fidx(1, i, j, L, M), 1 ^ left)
    return x


def plant_151(L, M):
    """Walls turning both ways, no free place: copy 1 + coin turns left. Coin 1 everywhere except the corner's two triangles,
    the column's down triangles and the row's up triangles."""
    x = 0
    for i in range(L):
        for j in range(M):
            for typ in (0, 1):
                v = 1
                if (i, j) == (0, 0) or (i == 0 and typ == 1) or (j == 0 and typ == 0):
                    v = 0
                x = setbit(x, fidx(typ, i, j, L, M), v)
    return x


def frame_image(x, L, M):
    """Lemma B's frame flip, followed by the global swap of coins that turns the flipped relation into the listed placement."""
    out = 0
    for i in range(L):
        for j in range(M):
            for typ in (0, 1):
                k = fidx(typ, i, j, L, M)
                out = setbit(out, k, ((x >> k) & 1) ^ ((i + j) & 1) ^ 1)
    return out


def half_turn_image(x, L, M, q):
    """Lemma B's half turn: up(i, j) goes to dn(-i-1, -j-1) and back, places 0 and 2 exchanged; then the global swap of coins."""
    out = 0
    for i in range(L):
        for j in range(M):
            for typ in (0, 1):
                v = (x >> fidx(typ, i, j, L, M)) & 1
                out = setbit(out, fidx(1 - typ, -i - 1, -j - 1, L, M), v ^ ((q[0] + q[1]) & 1) ^ 1)
    return out


def constructions(L, M):
    """(placement, twist in the placement's own frame, configuration, kind)."""
    flip_twist = (TWIST[0] ^ (L & 1), TWIST[1] ^ (M & 1))
    x147, x155, x151 = plant_147(L, M), plant_155(L, M), plant_151(L, M)
    x110 = frame_image(x155, L, M)
    return [
        (147, TWIST, x147, "directed, no free place"),
        (54, flip_twist, frame_image(x147, L, M), "directed, no free place"),
        (155, TWIST, x155, "directed, free place"),
        (110, flip_twist, x110, "directed, free place"),
        (203, TWIST, half_turn_image(x155, L, M, TWIST), "directed, free place"),
        (62, flip_twist, half_turn_image(x110, L, M, flip_twist), "directed, free place"),
        (151, TWIST, x151, "turning both ways, no free place"),
        (109, flip_twist, frame_image(x151, L, M), "turning both ways, no free place"),
    ]


# ------------------------------------------------------------------ closed walks of a wall graph

def scc(adj):
    """Strongly connected components (iterative Tarjan): component id per node."""
    n = len(adj)
    index, low, comp, onstack, stack = [-1] * n, [0] * n, [-1] * n, [False] * n, []
    counter = ncomp = 0
    for s in range(n):
        if index[s] != -1:
            continue
        work = [(s, 0)]
        index[s] = low[s] = counter
        counter += 1
        stack.append(s)
        onstack[s] = True
        while work:
            v, i = work[-1]
            if i < len(adj[v]):
                work[-1] = (v, i + 1)
                w = adj[v][i]
                if index[w] == -1:
                    index[w] = low[w] = counter
                    counter += 1
                    stack.append(w)
                    onstack[w] = True
                    work.append((w, 0))
                elif onstack[w]:
                    low[v] = min(low[v], index[w])
            else:
                work.pop()
                if work:
                    low[work[-1][0]] = min(low[work[-1][0]], low[v])
                if low[v] == index[v]:
                    while True:
                        w = stack.pop()
                        onstack[w] = False
                        comp[w] = ncomp
                        if w == v:
                            break
                    ncomp += 1
    return comp


def tarjan(G):
    nodes = list(G)
    idx = {v: n for n, v in enumerate(nodes)}
    adj = [[idx[w] for w, _dk in G[v]] for v in nodes]
    cid = scc(adj)
    comps = {}
    for n, c in enumerate(cid):
        comps.setdefault(c, []).append(nodes[n])
    return [c for c in comps.values() if len(c) > 1 or any(w == c[0] for w, _ in G[c[0]])]


def cycle_of(G, comp):
    """If the strongly connected component is one simple cycle, return it as ([(state, position)], displacement)."""
    cs = set(comp)
    for v in comp:
        if sum(1 for w, _ in G[v] if w in cs) != 1:
            return None
    s0 = comp[0]
    s, pos, path = s0, (0, 0), []
    while True:
        path.append((s, pos))
        (w, dk), = [(w, dk) for w, dk in G[s] if w in cs]
        pos = (pos[0] + dk[0], pos[1] + dk[1])
        s = w
        if s == s0:
            return path, pos


def analyse(R, L, M, q, x):
    """The closed walks (as simple cycles of single-cycle components) and the pattern on the four target classes."""
    G = A.wall_graph(R, L, M, q, x, DR.wall_moves(L, M))
    comps = tarjan(G)
    cycles, ok = [], True
    for comp in comps:
        cyc = cycle_of(G, comp)
        if cyc is None:
            ok = False
            continue
        cycles.append(cyc)
    winding = [(len(p), e) for p, e in cycles if e != (0, 0)]
    pattern = {}
    for c in TARGETS:
        pattern[c] = not any(A.good(c, e, A.overlaps(p)) for p, e in cycles)
    return ok, cycles, winding, pattern


def main() -> int:
    manifest = json.loads((HERE / "manifest.json").read_text())
    result = {"schema_version": 3, "artifact_id": manifest["artifact_id"], "kind": "proof", "ticket": manifest["ticket"],
              "proof": manifest["proof"], "claim": manifest["claim"], "foundation_contract": manifest["foundation_contract"],
              "semantic_domains": manifest["semantic_domains"], "evidence_modes": manifest["evidence_modes"],
              "thesis_alignment": manifest["thesis_alignment"], "safe_conclusions": manifest["safe_to_conclude"]}
    checks = {"tori": "3 <= L, M <= 9", "per placement": {}}
    ok = True
    for L in range(3, 10):
        for M in range(3, 10):
            for R, q, x, kind in constructions(L, M):
                rec = checks["per placement"].setdefault(str(R), {"kind": kind, "tori": 0, "components are single cycles": 0,
                                                                 "winding walls as listed": 0, "states accounted for": 0,
                                                                 "selective by Theorem 1": 0, "certified directly": 0,
                                                                 "certified tori": 0})
                rec["tori"] += 1
                good_comp, cycles, winding, pattern = analyse(R, L, M, q, x)
                rec["components are single cycles"] += good_comp
                n2 = 2 * (L + M)
                if kind.startswith("directed"):
                    listed = sorted(winding) == sorted([(n2, (-1, 1)), (n2, (1, -1))]) or sorted(winding) == sorted([(n2, (1, -1)), (n2, (-1, 1))])
                    accounted = True
                else:
                    nb = 10 * (L + M) - 34
                    listed = sorted(winding) == sorted([(n2, (-1, 1)), (n2, (1, -1)), (nb, (1, 1)), (nb, (-1, -1))])
                    loops = sorted(len(p) for p, e in cycles if e == (0, 0))
                    accounted = (loops == sorted([10, 10] + [6] * (2 * (L - 2) * (M - 2)))
                                 and sum(len(p) for p, e in cycles) == 12 * L * M)
                rec["winding walls as listed"] += listed
                rec["states accounted for"] += accounted
                sel = all(pattern[c] == want for c, want in TARGETS.items())
                rec["selective by Theorem 1"] += sel
                if (L, M) in ((3, 3), (3, 4), (4, 4)):
                    rec["certified tori"] += 1
                    cert = {c: DR.certify(R, L, M, q, x, c) for c in TARGETS}
                    rec["certified directly"] += all(cert[c] is want for c, want in TARGETS.items())
        print("L", L, flush=True)
    for R, rec in checks["per placement"].items():
        ok = ok and rec["tori"] == 49 and all(rec[k] == 49 for k in ("components are single cycles", "winding walls as listed",
                                                                        "states accounted for", "selective by Theorem 1"))
        ok = ok and rec["certified directly"] == rec["certified tori"] == 3
    # the honeycomb kind with a free place, from the frozen exhaustive rows
    rows = [json.loads(l) for l in DR.A_ROWS.read_text().splitlines() if l.strip()]
    h1 = {}
    for r in rows:
        if r["R"] in (159, 215, 111, 125) and (r["L"], r["M"]) in ((3, 3), (3, 4)):
            for qs, t in r["twists"].items():
                if not t["odd_mask"]:
                    continue
                key = f'{r["L"]}x{r["M"]}'
                rec = h1.setdefault(key, {"configurations and twists": 0, "contradicting along every odd class": 0,
                                          "contradicting along none": 0})
                rec["configurations and twists"] += t["total"]
                rec["contradicting along every odd class"] += t["patterns"].get(str(t["odd_mask"]), 0)
                rec["contradicting along none"] += t["sat"] + t["patterns"].get("0", 0)
    checks["honeycomb with a free place (frozen rows)"] = h1
    ok = ok and all(v["contradicting along every odd class"] == 0 for v in h1.values()) and len(h1) == 2
    # controls
    controls = {}
    xc = plant_155(3, 3, block_column=False)
    Gc = A.wall_graph(155, 3, 3, TWIST, xc, DR.wall_moves(3, 3))
    cyc_c, _capped = A.simple_cycles(Gc)
    winding_c = [e for _p, e in cyc_c if e != (0, 0)]
    pattern_c = {c: not any(A.good(c, e, A.overlaps(p_)) for p_, e in cyc_c) for c in TARGETS}
    controls["155 without the column's blocking has another winding wall and is not selective"] = (
        len(winding_c) > 2 and not all(pattern_c[c] == want for c, want in TARGETS.items()))
    controls["147's planted configuration in the fitting twist has no odd class to contradict"] = not DR.odd_classes(
        DR.CLASSES, DR.fitting(147, 3, 3), (0, 0))
    ok = ok and all(controls.values())
    result["checks"], result["controls"] = checks, controls
    result["status"] = "passed" if ok else "failed"
    result["failures"] = [] if ok else ["a check or control did not come out as stated in proof.md"]
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if "--write" in sys.argv:
        (HERE / "result.json").write_text(text)
    else:
        old = (HERE / "result.json").read_text() if (HERE / "result.json").exists() else None
        print("result.json matches" if old == text else "result.json differs from a fresh run")
        ok = ok and old == text
    print(json.dumps({"status": result["status"], "checks": checks, "controls": controls}, indent=1))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
