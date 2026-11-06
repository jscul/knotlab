#!/usr/bin/env python3
"""Check PC-SIZE-GRID-20261020-001B-P001: PC and PCR size of Tseitin formulas on grids.

Executable checks of the lemmas of proof.md:

1. Cut lemma (exhaustive, compiled C): on the 4x4, 4x5, 5x5, 4x6, 3x8 and 4x7 grids, for every selection of
   non-corner faces at pairwise L-infinity distance >= 3 and every vertex set X, |cut_G(X)| <= 5 |cut_G'(X)|,
   and no nontrivial cut vanishes (so G' is connected). Controls: separation 2, or corner faces allowed, must
   break it.
2. Cut lemma (sampled): on 12x12, 20x20 and 30x17 grids, restrictions drawn from the distribution of the proof
   (activity p = 1/25 and the stress value p = 0.3), with vertex sets from rectangles, unions of rectangles,
   grown regions, random sets and sets hugging the deleted faces.
3. Isoperimetric lemma (exhaustive): on every grid with at most 28 vertices and both sides >= 3, every X with
   N/3 <= |X| <= 2N/3 has |cut(X)| >= min(a,b)/3.
4. Kill probabilities: the exact selection probability p(1-p)^|N(f)| of every face of a 30x30 grid against
   20,000 samples, and independence of the kill events of edges whose faces are 5 or more apart.
5. Degree sanity: on every damaged 5x5 grid of the exhaustive check, the polynomial calculus degree computed by
   the label closure of PC-DEGREE-20261020-001B is at least the tangle bound from the minimum balanced cut.
6. The explicit constant gamma of the theorem, and the +-1 control (restrictions there never kill a monomial).

    python3 -B check.py          verify result.json against a fresh run
    python3 -B check.py --write  write result.json
"""

from __future__ import annotations

import json
import math
import random
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent

C_SOURCE = r"""
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
static int A, B, NV, SEP, CORNERS, PERSEL;
static uint64_t star[64], faceedges[64];
static int facer[64], facec[64], cand[64], ncand;
static int eh(int r, int c) { return r * (B - 1) + c; }
static int ev(int r, int c) { return A * (B - 1) + r * B + c; }
static long nsel = 0, zerocut = 0; static double worst = 0; static int minbal_g = 1 << 30, minbal_gp = 1 << 30;
static int chosen[64], nchosen = 0;
static void check(uint64_t del) {
    uint64_t cut = 0, x = 0; double w = 0; int mb = 1 << 30, mbg = 1 << 30;
    uint64_t total = 1ULL << NV;
    for (uint64_t i = 1; i < total; i++) {
        int v = __builtin_ctzll(i);
        cut ^= star[v]; x ^= 1ULL << v;
        int g = __builtin_popcountll(cut), h = __builtin_popcountll(cut & ~del);
        int size = __builtin_popcountll(x);
        if (3 * size >= NV && 3 * size <= 2 * NV) { if (h < mb) mb = h; if (g < mbg) mbg = g; }
        if (h == 0) { if (g > 0) zerocut++; continue; }
        double ratio = (double)g / h;
        if (ratio > w) w = ratio;
    }
    if (w > worst) worst = w;
    if (mbg < minbal_g) minbal_g = mbg;
    if (mb < minbal_gp) minbal_gp = mb;
    if (PERSEL) printf("SEL %llu %d\n", (unsigned long long)del, mb);
    nsel++;
}
static void rec(int start, uint64_t del) {
    check(del);
    for (int t = start; t < ncand; t++) {
        int f = cand[t], ok = 1;
        for (int s = 0; s < nchosen; s++) {
            int g = chosen[s];
            if (abs(facer[f] - facer[g]) < SEP && abs(facec[f] - facec[g]) < SEP) { ok = 0; break; }
        }
        if (!ok) continue;
        chosen[nchosen++] = f;
        rec(t + 1, del | faceedges[f]);
        nchosen--;
    }
}
int main(int argc, char **argv) {
    A = atoi(argv[1]); B = atoi(argv[2]); SEP = atoi(argv[3]); CORNERS = atoi(argv[4]); PERSEL = atoi(argv[5]);
    NV = A * B;
    for (int r = 0; r < A; r++) for (int c = 0; c < B; c++) {
        int v = r * B + c; star[v] = 0;
        if (c + 1 < B) star[v] |= 1ULL << eh(r, c);
        if (c > 0) star[v] |= 1ULL << eh(r, c - 1);
        if (r + 1 < A) star[v] |= 1ULL << ev(r, c);
        if (r > 0) star[v] |= 1ULL << ev(r - 1, c);
    }
    ncand = 0;
    for (int r = 0; r < A - 1; r++) for (int c = 0; c < B - 1; c++) {
        int f = r * (B - 1) + c; facer[f] = r; facec[f] = c;
        faceedges[f] = (1ULL << eh(r, c)) | (1ULL << eh(r + 1, c)) | (1ULL << ev(r, c)) | (1ULL << ev(r, c + 1));
        int corner = (r == 0 || r == A - 2) && (c == 0 || c == B - 2);
        if (CORNERS || !corner) cand[ncand++] = f;
    }
    rec(0, 0);
    printf("RESULT %ld %.6f %ld %d %d\n", nsel, worst, zerocut, minbal_g, minbal_gp);
    return 0;
}
"""


# ---------------------------------------------------------------- grid helpers (Python)

class Grid:
    def __init__(self, a, b):
        self.a, self.b = a, b
        self.n = a * b
        self.edges = []
        self.index = {}
        for r in range(a):
            for c in range(b - 1):
                self.index[("h", r, c)] = len(self.edges)
                self.edges.append((r * b + c, r * b + c + 1))
        for r in range(a - 1):
            for c in range(b):
                self.index[("v", r, c)] = len(self.edges)
                self.edges.append((r * b + c, (r + 1) * b + c))
        self.m = len(self.edges)
        self.faces = [(r, c) for r in range(a - 1) for c in range(b - 1)]

    def face_edges(self, r, c):
        ix = self.index
        return [ix[("h", r, c)], ix[("h", r + 1, c)], ix[("v", r, c)], ix[("v", r, c + 1)]]

    def corner(self, r, c):
        return r in (0, self.a - 2) and c in (0, self.b - 2)

    def candidates(self):
        return [f for f in self.faces if not self.corner(*f)]

    def cut(self, X):
        return [i for i, (u, v) in enumerate(self.edges) if (u in X) != (v in X)]


def sample_selection(grid, p, rng):
    cand = grid.candidates()
    active = {f for f in cand if rng.random() < p}
    selected = [f for f in active if not any(g != f and abs(g[0] - f[0]) <= 2 and abs(g[1] - f[1]) <= 2
                                             for g in active)]
    return selected


def deleted_edges(grid, selected):
    out = set()
    for f in selected:
        out.update(grid.face_edges(*f))
    return out


def connected_without(grid, deleted):
    adj = [[] for _ in range(grid.n)]
    for i, (u, v) in enumerate(grid.edges):
        if i not in deleted:
            adj[u].append(v)
            adj[v].append(u)
    seen, todo = {0}, [0]
    while todo:
        for y in adj[todo.pop()]:
            if y not in seen:
                seen.add(y)
                todo.append(y)
    return len(seen) == grid.n


def vertex_sets(grid, selected, rng, count):
    a, b = grid.a, grid.b
    out = []
    for _ in range(count):
        kind = rng.randrange(5)
        if kind == 0:
            r0, r1 = sorted(rng.sample(range(a + 1), 2))
            c0, c1 = sorted(rng.sample(range(b + 1), 2))
            X = {r * b + c for r in range(r0, r1) for c in range(c0, c1)}
        elif kind == 1:
            X = set()
            for _ in range(rng.randrange(2, 6)):
                r0, r1 = sorted(rng.sample(range(a + 1), 2))
                c0, c1 = sorted(rng.sample(range(b + 1), 2))
                X ^= {r * b + c for r in range(r0, r1) for c in range(c0, c1)}
        elif kind == 2:
            start = rng.randrange(grid.n)
            target = rng.randrange(1, grid.n)
            X, frontier = {start}, [start]
            while len(X) < target and frontier:
                v = frontier.pop(rng.randrange(len(frontier)))
                r, c = divmod(v, b)
                for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    if 0 <= r + dr < a and 0 <= c + dc < b:
                        w = (r + dr) * b + c + dc
                        if w not in X:
                            X.add(w)
                            frontier.append(w)
        elif kind == 3:
            q = rng.random()
            X = {v for v in range(grid.n) if rng.random() < q}
        else:
            X = set()
            for (r, c) in selected:
                corners = [r * b + c, r * b + c + 1, (r + 1) * b + c, (r + 1) * b + c + 1]
                X.update(rng.sample(corners, rng.randrange(1, 5)))
            r0, r1 = sorted(rng.sample(range(a + 1), 2))
            X ^= {r * b + c for r in range(r0, r1) for c in range(b)}
        out.append(X)
    return out


# ---------------------------------------------------------------- label closure (from PC-DEGREE-20261020-001B)

def popcount(x):
    return bin(x).count("1")


def pc_balanced_refutes(n, edges, d):
    """Reduced PC closure of the balanced binomial Tseitin system at degree d; labels are vertex sets."""
    m = len(edges)
    star = [0] * n
    for i, (u, v) in enumerate(edges):
        star[u] |= 1 << i
        star[v] |= 1 << i
    deg = [popcount(s) for s in star]
    if max((x + 1) // 2 for x in deg) > d:
        return False
    full = (1 << n) - 1
    parent, pot, members, bad = {}, {}, {}, set()

    def find(x):
        path = []
        while parent.get(x, x) != x:
            path.append(x)
            x = parent[x]
        acc = 0
        for node in reversed(path):
            acc ^= pot[node]
            pot[node], parent[node] = acc, x
        return x, (pot[path[0]] if path else 0)

    def relate(x, y, U):
        rx, lx = find(x)
        ry, ly = find(y)
        if rx == ry:
            if (lx ^ ly ^ U) and rx not in bad:
                bad.add(rx)
                members.setdefault(rx, [rx])
                return True
            return False
        mx, my = members.get(rx, [rx]), members.get(ry, [ry])
        if len(mx) < len(my):
            rx, ry, lx, ly, mx, my = ry, rx, ly, lx, my, mx
        parent[ry], pot[ry] = rx, lx ^ ly ^ U
        members[rx] = mx + my
        members.pop(ry, None)
        if ry in bad:
            bad.discard(ry)
            bad.add(rx)
        return True

    def mark(x):
        rx, _ = find(x)
        if rx in bad:
            return False
        bad.add(rx)
        members.setdefault(rx, [rx])
        return True

    for v in range(n):
        bits = [i for i in range(m) if star[v] >> i & 1]
        A = sum(1 << i for i in bits[:(len(bits) + 1) // 2])
        relate(A, star[v] ^ A, 1 << v)
    changed = True
    while changed:
        changed = False
        for r in list(members):
            if r not in members:
                continue
            M = list(members[r])
            isbad = r in bad
            if not isbad and len(M) < 2:
                continue
            lab = None if isbad else {x: find(x)[1] for x in M}
            low = [x for x in M if popcount(x) <= d - 1]
            top = [x for x in M if popcount(x) == d]
            for e in range(m):
                bit = 1 << e
                elig = low + [x for x in top if x & bit]
                if not elig:
                    continue
                if isbad:
                    for x in elig:
                        changed |= mark(x ^ bit)
                elif len(elig) >= 2:
                    x0 = elig[0]
                    for x in elig[1:]:
                        changed |= relate(x0 ^ bit, x ^ bit, lab[x0] ^ lab[x])
        if find(0)[0] in bad:
            return True
    return find(0)[0] in bad


# ---------------------------------------------------------------- run

def run():
    checks, controls = {}, {}
    with tempfile.TemporaryDirectory() as tmp:
        src, exe = Path(tmp) / "cut.c", Path(tmp) / "cut"
        src.write_text(C_SOURCE)
        built = subprocess.run(["gcc", "-O2", "-o", str(exe), str(src)], capture_output=True, text=True)
        checks["c_checker_built"] = built.returncode == 0

        def run_c(a, b, sep, corners, persel=0):
            out = subprocess.run([str(exe), str(a), str(b), str(sep), str(corners), str(persel)],
                                 capture_output=True, text=True, timeout=3600).stdout.splitlines()
            fields = out[-1].split()
            res = {"selections": int(fields[1]), "max_ratio": float(fields[2]), "vanishing_cuts": int(fields[3]),
                   "min_balanced_cut_G": int(fields[4]), "min_balanced_cut_any_G_prime": int(fields[5])}
            persel_rows = [(int(x.split()[1]), int(x.split()[2])) for x in out if x.startswith("SEL ")]
            return res, persel_rows

        exhaustive, ok = {}, True
        for a, b in ((4, 4), (4, 5), (5, 5), (4, 6), (3, 8), (4, 7)):
            res, _ = run_c(a, b, 3, 0)
            exhaustive[f"{a}x{b}"] = res
            ok &= res["max_ratio"] <= 5.0 + 1e-9 and res["vanishing_cuts"] == 0
            ok &= res["min_balanced_cut_G"] >= min(a, b) / 3
        checks["cut_lemma_exhaustive"] = {"holds": ok, "grids": exhaustive,
                                          "factor_five_attained": any(r["max_ratio"] == 5.0 for r in exhaustive.values())}
        sep2, _ = run_c(5, 5, 2, 0)
        corners, _ = run_c(5, 5, 3, 1)
        controls["separation_two_breaks_the_lemma"] = sep2["max_ratio"] > 5 or sep2["vanishing_cuts"] > 0
        controls["corner_faces_break_the_lemma"] = corners["max_ratio"] > 5 or corners["vanishing_cuts"] > 0

        iso_ok, iso = True, {}
        for a in range(3, 8):
            for b in range(a, 10):
                if a * b > 28:
                    continue
                res, _ = run_c(a, b, 3, 0)
                iso[f"{a}x{b}"] = res["min_balanced_cut_G"]
                iso_ok &= res["min_balanced_cut_G"] >= min(a, b) / 3
        checks["isoperimetric_lemma_exhaustive"] = {"holds": iso_ok, "min_balanced_cut": iso}

        _, persel = run_c(5, 5, 3, 0, persel=1)

    rng = random.Random(20261020)
    sampled_ok, samples, connected_ok = True, 0, True
    for (a, b) in ((12, 12), (20, 20), (30, 17)):
        grid = Grid(a, b)
        for p in (1 / 25, 0.3):
            for _ in range(10):
                sel = sample_selection(grid, p, rng)
                deleted = deleted_edges(grid, sel)
                connected_ok &= connected_without(grid, deleted)
                for X in vertex_sets(grid, sel, rng, 60):
                    if not X or len(X) == grid.n:
                        continue
                    cut = grid.cut(X)
                    kept = [e for e in cut if e not in deleted]
                    samples += 1
                    if len(cut) > 5 * len(kept):
                        sampled_ok = False
    checks["cut_lemma_sampled"] = {"holds": sampled_ok, "vertex_sets": samples, "restricted_grids_connected": connected_ok}

    # kill probabilities on a 30x30 grid
    grid = Grid(30, 30)
    p = 1 / 25
    cand = grid.candidates()
    neighbours = {f: [g for g in cand if g != f and abs(g[0] - f[0]) <= 2 and abs(g[1] - f[1]) <= 2] for f in cand}
    exact = {f: p * (1 - p) ** len(neighbours[f]) for f in cand}
    q = p * (1 - p) ** 24 / 2
    trials = 20000
    counts = {f: 0 for f in cand}
    probe = [(10, 10), (10, 15), (15, 10), (20, 20)]           # faces pairwise at distance >= 5
    probe_edges = [grid.face_edges(*f)[0] for f in probe]
    joint = 0
    single = [0] * len(probe)
    for _ in range(trials):
        sel = sample_selection(grid, p, rng)
        for f in sel:
            counts[f] += 1
        deleted = deleted_edges(grid, sel)
        kills = []
        for e in probe_edges:
            kills.append(e in deleted and rng.random() < 0.5)
        for i, k in enumerate(kills):
            single[i] += k
        joint += kills[0] and kills[1]
    worst_z = max(abs(counts[f] / trials - exact[f]) / math.sqrt(exact[f] * (1 - exact[f]) / trials) for f in cand)
    min_kill = min(exact[f] for f in cand) / 2
    pa, pb = single[0] / trials, single[1] / trials
    expected_joint = pa * pb
    z_joint = (joint / trials - expected_joint) / math.sqrt(max(expected_joint, 1e-9) / trials)
    checks["kill_probabilities"] = {
        "selection_matches_exact_formula": worst_z < 5.0,
        "largest_z_score": round(worst_z, 2),
        "min_kill_probability_of_a_literal": round(min_kill, 6),
        "q_used_in_proof": round(q, 6),
        "every_candidate_face_at_least_q_bound": min_kill >= q - 1e-12,
        "far_edges_independent": abs(z_joint) < 5.0,
        "joint_kill_z_score": round(z_joint, 2),
    }

    # degree sanity on damaged 5x5 grids
    grid = Grid(5, 5)
    sanity_ok, rows = True, []
    for mask, beta in persel:
        deleted = {i for i in range(grid.m) if mask >> i & 1}
        keep = [e for i, e in enumerate(grid.edges) if i not in deleted]
        k = beta                                    # tangle of order beta from the balanced cut
        bound = (k - 1) // 2 + 1 if k - 1 >= 4 else None   # needs max degree 4 <= k - 1
        degree = next(d for d in range(1, 10) if pc_balanced_refutes(grid.n, keep, d))
        rows.append({"deleted_edges": len(deleted), "min_balanced_cut": beta, "tangle_bound": bound,
                     "pc_degree_balanced": degree})
        if bound is not None and degree < bound:
            sanity_ok = False
    checks["degree_sanity_damaged_5x5"] = {"holds": sanity_ok, "grids": len(rows),
                                           "distinct_rows": sorted({json.dumps(r, sort_keys=True) for r in rows})}

    # constants of the theorem
    R = 360
    gamma = math.log2(1 / (1 - q)) / (R * 30)
    checks["constants"] = {"p": round(p, 4), "q": round(q, 6), "independence_spacing_edges": R,
                           "gamma_bits_per_unit_side": gamma, "gamma_at_least_1e-6": gamma >= 1e-6}

    # +-1 control: a restriction y_e = +-1 never kills a monomial
    killed = 0
    for _ in range(1000):
        mono = rng.sample(range(40), rng.randrange(1, 12))
        restriction = {e: rng.choice((1, -1)) for e in rng.sample(range(40), 20)}
        coefficient = 1
        for e in mono:
            coefficient *= restriction.get(e, 1)
        killed += coefficient == 0
    controls["pm1_restrictions_never_kill"] = killed == 0

    expected = [checks["c_checker_built"], checks["cut_lemma_exhaustive"]["holds"],
                checks["cut_lemma_sampled"]["holds"], checks["cut_lemma_sampled"]["restricted_grids_connected"],
                checks["isoperimetric_lemma_exhaustive"]["holds"],
                checks["kill_probabilities"]["selection_matches_exact_formula"],
                checks["kill_probabilities"]["every_candidate_face_at_least_q_bound"],
                checks["kill_probabilities"]["far_edges_independent"],
                checks["degree_sanity_damaged_5x5"]["holds"], checks["constants"]["gamma_at_least_1e-6"]]
    failures = [i for i, ok in enumerate(expected) if not ok] + [k for k, ok in controls.items() if not ok]
    return checks, controls, failures


def main() -> int:
    write = "--write" in sys.argv[1:]
    checks, controls, failures = run()
    manifest = json.loads((HERE / "manifest.json").read_text())
    result = {
        "schema_version": 3, "artifact_id": manifest["artifact_id"], "kind": "proof", "ticket": manifest["ticket"],
        "proof": manifest["proof"], "status": "passed" if not failures else "failed", "claim": manifest["claim"],
        "foundation_contract": manifest["foundation_contract"], "semantic_domains": manifest["semantic_domains"],
        "evidence_modes": manifest["evidence_modes"], "thesis_alignment": manifest["thesis_alignment"],
        "safe_conclusions": manifest["safe_to_conclude"], "checks": checks, "controls": controls,
        "failures": failures,
    }
    path = HERE / "result.json"
    text = json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    if write:
        path.write_text(text)
    elif not path.exists() or json.loads(path.read_text()) != json.loads(text):
        print("result.json does not match a fresh run; rerun with --write after review")
        return 1
    print(f"{result['status']}: failures {failures}")
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
