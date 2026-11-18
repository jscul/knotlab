"""Referee R1 for PICK-TWO-20261118-001 (own code; the study's picklib.py, run.py and NEVER-NEST's nnlib.py are used only in
`fills_check`, to test the study's fills() against the referee's).

  ../../../.venv/bin/python -B referee_pick.py <part> [args] > referee_pick_<part>.json      (from this directory)

Moves, from the note: fills (one to three betweenness knots on the new distinction and old pairs, no state added, not a copy) and
subdivisions (one knot B(u, p, v) on a pair differing in exactly two states).  Fills two ways:
  closure   CUBE-DOUBLING-R1's brute force: every intersection of one to three knots' allowed masks, admitted, zero cost;
  fast      the referee's own: a fill needs a middle knot B(u, r, v) (only middle knots pin the all-equal states), which fixes r where
            u = v; one or two more knots consistent with that must pin the rest.
lambda by Eppstein's matching (KNOT-CAP-R1 `measure`), k the exact colour number of the crossing graph (COUNT-BALLS-R1).

Parts:
  fills_check   the study's fills() against the closure and the referee's fast fills on bases grown by the referee (lines, the
                rules below, n up to 18): equal sets?
  trees         SEED's first step from uncrossed starts that are not lines (trees with a branching distinction): the largest
                k and lambda one fill can make (on a line it is always two, S6).
  runs <rule> <start> <seeds> <nmax> [param]   the rules with the referee's own code: CAP d, QPRICE w, KEEP, CC, ODD, SEED;
                per step k, lambda, the clique number, full grid; summary.
"""
import itertools
import json
import random
import sys
from pathlib import Path

import networkx as nx
import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "research/CUBE-DOUBLING-20261118-001/referee-R1"))
sys.path.insert(0, str(ROOT / "research/KNOT-CAP-20261117-001/referee-R1"))
sys.path.insert(0, str(ROOT / "research/COUNT-BALLS-20261118-001/referee-R1"))
import referee_cube as RC  # noqa: E402
import referee_cap as KC  # noqa: E402
import referee_census as RCN  # noqa: E402

pc = RC.pc


def line(n):
    """The line of n: its cuts, the solution set of the chain bracketing's knots B(0, c, c + 1)."""
    S, n = from_splits(n, [list(range(c + 1)) for c in range(n - 1)])
    assert S == sorted(x for x in range(1 << n) if RC.allowed(x, n, [(0, c, c + 1) for c in range(1, n - 1)]))
    return S, n


def from_splits(n, splits):
    full = (1 << n) - 1
    st = {0, full}
    for A in splits:
        m = sum(1 << u for u in A)
        st |= {m, full ^ m}
    return sorted(st), n


def cube(d):
    n = 1 << d
    return from_splits(n, [[x for x in range(n) if (x >> i) & 1] for i in range(d)])


def tree_base(edges, m):
    T = nx.Graph()
    T.add_nodes_from(range(m))
    T.add_edges_from(edges)
    sp = []
    for u, v in edges:
        T.remove_edge(u, v)
        sp.append(sorted(nx.node_connected_component(T, u)))
        T.add_edge(u, v)
    return from_splits(m, sp)


# ---------------- fills ----------------

def fills_closure(S, n):
    ext, O, Z, full = RC.closure(list(S), n)
    N = len(S)
    return sorted({(a0, a1) for a0, a1 in ext if RC.admitted(a0, a1, O, Z, full, N) and pc(a0) + pc(a1) == N})


def fills_fast(S, n):
    kv, O, Z, full = RC.knot_values(list(S), n)
    pins = {(a0 & ~a1 & full, a1 & ~a0 & full) for _, a0, a1 in kv}
    pins = [p for p in pins if p[0] | p[1]]
    P0 = np.array([p[0] for p in pins], dtype=object)
    P1 = np.array([p[1] for p in pins], dtype=object)
    cols = set(O)
    out = set()
    for u, v in itertools.combinations(range(n), 2):
        U1, U0 = O[u] & O[v], Z[u] & Z[v]
        R = full ^ (U0 | U1)
        if R == 0:
            continue
        cons = {(int(p0) & R, int(p1) & R) for p0, p1 in zip(P0, P1) if not (int(p0) & U1) and not (int(p1) & U0)}
        cons = [c for c in cons if c[0] | c[1]]
        for a, b in cons:
            if (a | b) == R:
                out.add(U1 | b)
        for (a, b), (c, d) in itertools.combinations(cons, 2):
            if (a | b | c | d) == R and not (a & d) and not (b & c):
                out.add(U1 | b | d)
    return sorted(((full ^ r), r) for r in out if r not in cols)


def subdivisions(S, n):
    O, Z, full = RC.cols(list(S), n)
    out = set()
    cols = set(O)
    for u, v in itertools.combinations(range(n), 2):
        eq = (O[u] & O[v]) | (Z[u] & Z[v])
        if pc(full ^ eq) == 2:
            a0, a1 = full ^ (O[u] & O[v]), full ^ (Z[u] & Z[v])
            out.add((a0, a1))
    return sorted(out)


def apply(S, n, a0, a1):
    return tuple(RC.apply(list(S), n, a0, a1))


# ---------------- readings ----------------

def crossing_graph(S, n):
    full = (1 << n) - 1
    sp = RC.splits_of(list(S), n)
    G = nx.Graph()
    G.add_nodes_from(range(len(sp)))
    for i, j in itertools.combinations(range(len(sp)), 2):
        a, b = sp[i], sp[j]
        if all(x for x in (a & b, a & (full ^ b), (full ^ a) & b, (full ^ a) & (full ^ b))):
            G.add_edge(i, j)
    return sp, G


def read(S, n):
    sp, G = crossing_graph(S, n)
    k = RCN.chromatic(sp, (1 << n) - 1)
    lam = KC.measure(list(S), n)["lam"]
    omega = max((len(c) for c in nx.find_cliques(G)), default=1) if G.number_of_edges() else 1
    full_grid = False
    if G.number_of_edges():
        parts = list(nx.connected_components(nx.complement(G)))
        ok = all(not G.has_edge(a, b) for P in parts for a, b in itertools.combinations(P, 2))
        ok = ok and G.number_of_edges() == (len(sp) ** 2 - sum(len(P) ** 2 for P in parts)) // 2
        prod = 1
        for P in parts:
            prod *= len(P) + 1
        full_grid = ok and prod == n and len(parts) >= 2
    return {"n": n, "N": len(S), "k": k, "lam": lam, "omega": omega, "full_grid": full_grid}


# ---------------- rules ----------------

def options(S, n, rule, param):
    if rule == "CC":
        O, Z, full = RC.cols(list(S), n)
        sp, G = crossing_graph(S, n)
        fulln = (1 << n) - 1                              # over the distinctions (full is over the states)
        idx = {}
        for i, a in enumerate(sp):
            for x in (a, fulln ^ a):
                idx[x] = i
        diff = {}
        for c, x in itertools.permutations(range(n), 2):
            D = O[c] ^ O[x]
            if pc(D) == 2:
                st = [s for j, s in enumerate(S) if (D >> j) & 1]
                diff[(c, x)] = (D, idx[st[0]])
        rs = set()
        for (c, x), (D1, t1) in diff.items():
            for (c2, y), (D2, t2) in diff.items():
                if c2 == c and t1 != t2 and G.has_edge(t1, t2):
                    r = (O[c] & ~(D1 | D2)) | (O[x] & D1) | (O[y] & D2)
                    if r not in set(O):
                        rs.add((full ^ r, r))
        if rs:
            return sorted(rs), "fill"
        return subdivisions(S, n), "sub"
    F = fills_fast(S, n)
    k0, l0 = read(S, n)["k"], KC.measure(list(S), n)["lam"]
    after = {}
    for f in F:
        S2 = apply(S, n, *f)
        sp2 = RC.splits_of(list(S2), n + 1)
        after[f] = (RCN.chromatic(sp2, (1 << (n + 1)) - 1), KC.measure(list(S2), n + 1)["lam"])
    if rule == "CAP":
        good = [f for f in F if after[f][1] <= param and (param != 2 or after[f][0] <= 2)]
    elif rule == "KEEP":
        good = [f for f in F if after[f][1] == l0]
    elif rule == "ODD":
        good = [f for f in F if after[f][0] <= 2]
    elif rule == "QPRICE":
        scored = [(param * after[f][1] ** 2, f) for f in F] + [(2 + param * l0 ** 2, s) for s in subdivisions(S, n)]
        low = min(x[0] for x in scored)
        return sorted({x[1] for x in scored if abs(x[0] - low) < 1e-9}), "price"
    elif rule == "SEED":
        sp, G = crossing_graph(S, n)
        active = {v for v in G if G.degree(v)}
        full = (1 << n) - 1
        good = []
        for f in F:
            if not active:
                good.append(f)
                continue
            S2 = apply(S, n, *f)
            sp2, G2 = crossing_graph(S2, n + 1)
            # map old splits to new ones: a fill keeps the splits, each side gaining the new distinction or not
            m = {i: next(j2 for j2, b in enumerate(sp2) if (b & full) in (a, full ^ a)) for i, a in enumerate(sp)}
            new = [(i, j) for i, j in itertools.combinations(range(len(sp)), 2) if not G.has_edge(i, j) and G2.has_edge(m[i], m[j])]
            if any(i in active and j in active for i, j in new):
                continue
            gained = {v for e in new for v in e if v not in active}
            nb = {v: frozenset(G2[m[v]]) for v in range(len(sp))}
            olds = {nb[v] for v in active}
            if all(nb[u] in olds for u in gained):
                good.append(f)
    else:
        raise ValueError(rule)
    if good:
        return good, "fill"
    return subdivisions(S, n), "sub"


def run(rule, start, seed, nmax, param=None):
    S, n = start
    S = tuple(S)
    rng = random.Random(f"{rule}:{param}:{seed}")
    trace = [read(S, n)]
    while n < nmax and len(S) <= 60:
        ops, kind = options(S, n, rule, param)
        if not ops:
            break
        a0, a1 = rng.choice(ops)
        S2 = apply(S, n, a0, a1)
        kind = "fill" if len(S2) == len(S) else "sub"
        S, n = S2, n + 1
        trace.append({**read(S, n), "kind": kind})
    return trace


def summary(trace):
    lam = [t["lam"] for t in trace]
    ff = next((i for i, t in enumerate(trace) if t["full_grid"]), None)
    return {"n_end": trace[-1]["n"], "lam_end": lam[-1], "lam_max": max(lam), "k_end": trace[-1]["k"],
            "first_fill_n": next((t["n"] for t in trace if t.get("kind") == "fill"), None),
            "full_grids": sum(t["full_grid"] for t in trace),
            "first_full_grid_n": trace[ff]["n"] if ff is not None else None,
            "subdivisions_before_first_full_grid": sum(1 for t in trace[:ff] if t.get("kind") == "sub") if ff is not None else None, "lam_equals_omega_every_step": all(t["lam"] == t["omega"] for t in trace),
            "lam_seq": lam}


def start_of(name):
    if name.startswith("line"):
        return line(int(name[4:]))
    if name.startswith("Q"):
        return cube(int(name[1:]))
    if name == "grid333":
        pts = list(itertools.product(range(3), repeat=3))
        return from_splits(27, [[i for i, p in enumerate(pts) if p[ax] <= c] for ax in range(3) for c in range(2)])
    raise ValueError(name)


def part_runs(rule, start, seeds, nmax, param=None):
    out = []
    for sd in range(seeds):
        tr = run(rule, start_of(start), sd, nmax, param)
        out.append(summary(tr))
        print(rule, start, param, sd, json.dumps({k: v for k, v in out[-1].items() if k != "lam_seq"}), file=sys.stderr, flush=True)
    return {"rule": rule, "start": start, "param": param, "nmax": nmax, "runs": out}


# ---------------- the checks ----------------

def part_fills_check():
    sys.path.insert(0, str(ROOT / "experiments/PICK-TWO-20261118-001B/PICK-TWO-20261118-001B-E001_pick"))
    import picklib as STUDY  # noqa: E402  (tested here, not used for results)
    bases = []
    for m in (4, 5, 6, 7, 8):
        bases.append(line(m))
    bases += [cube(2), cube(3)]
    for rule, param, st in (("CAP", 3, "line5"), ("SEED", None, "line5"), ("ODD", None, "line6"), ("CAP", 4, "line5"),
                            ("QPRICE", 0.35, "line5"), ("SEED", None, "line6")):
        S, n = start_of(st)
        rng = random.Random(f"fills-check-{rule}-{st}")
        S = tuple(S)
        while n < 17:
            ops, _ = options(S, n, rule, param)
            a0, a1 = rng.choice(ops)
            S, n = apply(S, n, a0, a1), n + 1
            bases.append((S, n))
    rows = []
    for S, n in bases:
        A = set(fills_closure(S, n))
        B = set(fills_fast(S, n))
        C = set(map(tuple, STUDY.fills(tuple(S), n)))
        rows.append({"n": n, "N": len(S), "closure": len(A), "fast_equal": A == B, "study_equal": A == C})
        print("fills", rows[-1], file=sys.stderr, flush=True)
    return {"bases": len(rows), "fast_equal_all": all(r["fast_equal"] for r in rows),
            "study_equal_all": all(r["study_equal"] for r in rows), "rows": rows}


def part_trees():
    """Uncrossed starts that are not lines: trees with a distinction of degree three or more (spiders, a star, a caterpillar).
    Every fill (closure), and the largest k and lambda after one fill."""
    shapes = {
        "spider 1,1,1 (star of 4)": [(0, 1), (0, 2), (0, 3)],
        "spider 2,1,1": [(0, 1), (1, 2), (0, 3), (0, 4)],
        "spider 2,2,1": [(0, 1), (1, 2), (0, 3), (3, 4), (0, 5)],
        "spider 2,2,2": [(0, 1), (1, 2), (0, 3), (3, 4), (0, 5), (5, 6)],
        "spider 1,1,1,1 (star of 5)": [(0, 1), (0, 2), (0, 3), (0, 4)],
        "spider 2,2,2,2": [(0, 1), (1, 2), (0, 3), (3, 4), (0, 5), (5, 6), (0, 7), (7, 8)],
        "two branch points": [(0, 1), (1, 2), (2, 3), (1, 4), (2, 5)],
    }
    out = {}
    for name, edges in shapes.items():
        m = 1 + max(max(e) for e in edges)
        S, n = tree_base(edges, m)
        F = fills_closure(S, n)
        after = [read(apply(S, n, *f), n + 1) for f in F]
        out[name] = {"n": n, "states": len(S), "fills": len(F), "lam_after": sorted({a["lam"] for a in after}),
                     "k_after": sorted({a["k"] for a in after}), "lam_3_fills": sum(a["lam"] >= 3 for a in after)}
        print("trees", name, out[name], file=sys.stderr, flush=True)
    return out


if __name__ == "__main__":
    part = sys.argv[1]
    if part == "fills_check":
        res = part_fills_check()
    elif part == "trees":
        res = part_trees()
    elif part == "runs":
        rule, st, seeds, nmax = sys.argv[2], sys.argv[3], int(sys.argv[4]), int(sys.argv[5])
        param = float(sys.argv[6]) if len(sys.argv) > 6 else None
        if rule == "CAP" and param is not None:
            param = int(param)
        res = part_runs(rule, st, seeds, nmax, param)
    print(json.dumps(res, indent=1, default=str))
