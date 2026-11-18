"""Shared-runner job for NAE-METRIC-20261118-001B-E001: cuts, blocks, rings, small blocks, graph-like bases and grown bases."""
import itertools
import math
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import naelib as N  # noqa: E402

M, nx = N.M, N.nx
ROOT = HERE.parents[2]


def triple_blocks(n, k, first=None):
    """Every set of k triples on n distinctions covering all n whose incidence graph is one block; with first, only the sets
    whose least triple is the first-th triple (a shard)."""
    tr = list(itertools.combinations(range(n), 3))
    if first is None:
        combos = itertools.combinations(tr, k)
    else:
        combos = ((tr[first],) + rest for rest in itertools.combinations(tr[first + 1:], k - 1))
    return [ts for ts in combos if M.covers(ts, n) and N.is_block(ts)]


def cases():
    for i in range(40):
        yield f"cut-{i}", {"kind": "cut", "seed": 100 + i}
    for m in range(3, 10):
        for tw in (False, True):
            yield f"ring-{m}-{'twisted' if tw else 'plain'}", {"kind": "ring", "m": m, "twisted": tw}
    for i in range(20):
        yield f"cactus-{i}", {"kind": "cactus", "seed": 300 + i}
    for n in range(4, 8):
        for k in range(2, 7):
            if n == 7 and k >= 5:
                for f in range(35):
                    yield f"block-n7-k{k}-f{f}", {"kind": "block", "n": 7, "k": k, "first": f}
            else:
                yield f"block-n{n}-k{k}", {"kind": "block", "n": n, "k": k, "first": None}
    for n in range(4, 7):
        for k in range(2, 5):
            yield f"classblock-n{n}-k{k}", {"kind": "classblock", "n": n, "k": k}
    for i in range(30):
        yield f"graph-{i}", {"kind": "graph", "seed": 500 + i}
    for i in range(20):
        yield f"sparse9-{i}", {"kind": "sparse9", "seed": 700 + i}
    for rule in ("SEED", "ODD", "FRESH", "NEWCROSS", "KEEP", "CC", "CAP2", "CAP3"):
        for start in ("line5", "line6", "line7", "line8", "2x2"):
            yield f"grown-{rule}-{start}", {"kind": "grown", "rule": rule, "start": start}
    for rule in ("KF3", "NN", "NN2", "SEEDK"):
        for n0 in (5, 6):
            yield f"knotgrown-{rule}-{n0}", {"kind": "knotgrown", "rule": rule, "n0": n0}


def glue_blocks(rng, pieces, laws_for):
    """A base made by gluing small pieces at single distinctions in a tree: each new piece shares exactly one distinction with
    what is there. pieces: list of piece specs (lists of tuples on local distinctions)."""
    knots, laws, n = [], [], 0
    for pi, piece in enumerate(pieces):
        local = sorted({v for t in piece for v in t})
        if pi == 0:
            m = {v: j for j, v in enumerate(local)}
            n = len(local)
        else:
            anchor = rng.randrange(n)
            pick = rng.choice(local)
            m = {pick: anchor}
            for v in local:
                if v != pick:
                    m[v] = n
                    n += 1
        for t in piece:
            knots.append(tuple(m[v] for v in t))
            laws.append(laws_for(len(t)))
    return n, knots, laws


def random_piece(rng):
    kind = rng.choice(["knot", "knot", "double", "ring3", "ring4", "pasch", "four"])
    if kind == "knot":
        return [(0, 1, 2)]
    if kind == "double":
        return [(0, 1, 2), (0, 1, 3)]
    if kind == "ring3":
        return [(0, 1, 2), (2, 3, 4), (4, 5, 0)]
    if kind == "ring4":
        return [(0, 1, 2), (2, 3, 4), (4, 5, 6), (6, 7, 0)]
    if kind == "pasch":
        return [(0, 1, 2), (0, 3, 4), (1, 3, 5), (2, 4, 5)]
    return [(0, 1, 2, 3)]


def run(case_id, p):
    kind = p["kind"]
    if kind == "cut":
        rng = random.Random(p["seed"])
        out = {"bases": 0, "sep_triples": 0, "additivity_fail": 0, "formula_fail": 0, "metric_mismatch": 0, "count_checked": 0,
               "count_fail": 0, "gate_fail": 0, "examples": []}
        family = ["nae", "nae", "nae4", "parity"][p["seed"] % 4]
        while out["bases"] < 25:
            pieces = [random_piece(rng) for _ in range(rng.randint(2, 4))]
            if family != "nae4":
                pieces = [pc for pc in pieces if len(pc[0]) == 3] or [[(0, 1, 2)]]
            if family == "parity":
                lf = lambda a: rng.choice((M.P0, M.P1))
            else:
                lf = lambda a: rng.choice(N.NAE_CLASS) if a == 3 else N.NAE4
            n, ts, ls = glue_blocks(rng, pieces, lf)
            if n > 12:
                continue
            st = N.states_any(n, list(zip(ls, ts)))
            if len(st) == 0:
                continue
            # parity: only balanced cuts (no frozen distinction)
            if family == "parity" and any(len({(int(s) >> v) & 1 for s in st}) < 2 for v in range(n)):
                continue
            out["bases"] += 1
            D = M.bond_matrix(n, st)
            G = N.incidence(ts)
            for x, y, z in itertools.permutations(range(n), 3):
                if x < z and N.separates(G, y, x, z):
                    out["sep_triples"] += 1
                    lhs, rhs = D[x][z] - 1, (D[x][y] - 1) + (D[y][z] - 1)
                    if not (lhs == rhs or (math.isinf(lhs) and math.isinf(rhs))):
                        out["additivity_fail"] += 1
                        if len(out["examples"]) < 3:
                            out["examples"].append({"family": family, "knots": [list(t) for t in ts], "xyz": [x, y, z]})
            if all(len(t) == 3 for t in ts):
                F = N.block_formula(ls, ts, n)
                out["formula_fail"] += F != D
            # metric iff every block metric (primal blocks, any arity)
            glob = bool(M.violations(D, n))
            loc = False
            for vs, idx in N.primal_blocks(ts):
                if not idx:
                    continue
                k, kn, mm = N.sub_base(ls, ts, idx)
                st2 = N.states_any(k, kn)
                D2 = M.bond_matrix(k, st2)
                loc |= bool(M.violations(D2, k))
            out["metric_mismatch"] += glob != loc
            # bond count identity at one separating distinction
            cuts = [v for v in range(n) if ("v", v) in G and not nx.is_connected(G.subgraph([u for u in G if u != ("v", v)]))]
            if cuts:
                y = rng.choice(cuts)
                H = G.copy()
                H.remove_node(("v", y))
                comps = list(nx.connected_components(H))
                side = comps[0]
                Lk = [i for i in range(len(ts)) if ("k", i) in side]
                Rk = [i for i in range(len(ts)) if ("k", i) not in side]
                bB = N.bonds_list(n, st)
                cnt = {}
                for name, idx in (("L", Lk), ("R", Rk)):
                    k, kn, mm = N.sub_base(ls, ts, idx)
                    bl = N.bonds_list(k, N.states_any(k, kn))
                    cnt[name] = (len(bl), sum(1 for b in bl if b >> mm[y] & 1))
                out["count_checked"] += 1
                out["count_fail"] += len(bB) != cnt["L"][0] + cnt["R"][0] + cnt["L"][1] * cnt["R"][1]
        out["family"] = family
        return out
    if kind == "ring":
        n, kn = N.ring(p["m"], p["twisted"])
        st = M.states(n, kn)
        D = M.bond_matrix(n, st)
        S = N.steps([t for _, t in kn], n)
        off = [[x, y, S[x][y], D[x][y]] for x, y in itertools.combinations(range(n), 2) if D[x][y] != S[x][y] + 1]
        bl = N.bonds_list(n, st)
        thirds = sum(1 << (2 * i + 1) for i in range(p["m"]))
        missing_third = sum(1 for b in bl if b & thirds != thirds)
        big = [bin(b).count("1") for b in bl if b & thirds == thirds]
        return {"m": p["m"], "twisted": p["twisted"], "states": len(st), "off": off[:5], "n_off": len(off),
                "violations": len(M.violations(D, n)), "bonds_missing_a_third": missing_third, "other_bonds_min_size": min(big) if big else None,
                "max_b": max(D[x][y] for x, y in itertools.combinations(range(n), 2))}
    if kind == "cactus":
        rng = random.Random(p["seed"])
        out = {"bases": 0, "off": 0, "violations": 0, "examples": []}
        while out["bases"] < 10:
            pieces = []
            for _ in range(rng.randint(2, 4)):
                m = rng.randint(3, 5)
                pieces.append([(2 * i, 2 * i + 1, (2 * i + 2) % (2 * m)) for i in range(m)] if rng.random() < 0.6 else [(0, 1, 2)])
            n, ts, ls = glue_blocks(rng, pieces, lambda a: rng.choice(N.NAE_CLASS))
            if n > 14:
                continue
            st = M.states(n, list(zip(ls, ts)))
            if len(st) == 0:
                continue
            out["bases"] += 1
            D = M.bond_matrix(n, st)
            S = N.steps(ts, n)
            bad = sum(1 for x, y in itertools.combinations(range(n), 2) if D[x][y] != S[x][y] + 1)
            out["off"] += bad
            out["violations"] += len(M.violations(D, n))
            if bad and len(out["examples"]) < 2:
                out["examples"].append([list(t) for t in ts])
        return out
    if kind in ("block", "classblock"):
        laws = [N.NAE3] if kind == "block" else N.NAE_CLASS
        tsl = triple_blocks(p["n"], p["k"], p.get("first"))
        out = {"blocks": 0, "failing": 0, "failing_without_double": 0, "linear_failing": 0, "graphlike_failing": 0, "examples": [],
               "nostate": 0}
        for ts in tsl:
            dbl = N.double_meetings(ts)
            deg = max(sum(v in t for t in ts) for v in range(p["n"]))
            for ls in itertools.product(laws, repeat=p["k"]):
                st = M.states(p["n"], list(zip(ls, ts)))
                if len(st) == 0:
                    out["nostate"] += 1
                    continue
                out["blocks"] += 1
                D = M.bond_matrix(p["n"], st)
                if M.violations(D, p["n"]):
                    out["failing"] += 1
                    if dbl == 0:
                        out["failing_without_double"] += 1
                        out["linear_failing"] += 1
                        if deg <= 2:
                            out["graphlike_failing"] += 1
                        if len(out["examples"]) < 3:
                            out["examples"].append({"knots": [list(t) for t in ts], "laws": [sorted(R) for R in ls]})
        out.update({"n": p["n"], "k": p["k"]})
        return out
    if kind == "graph":
        # graph-like bases: knots = vertices of a random connected graph of max degree 3, distinctions = its edges plus one
        # private distinction for each missing degree; pure or twisted not-all-equal
        rng = random.Random(p["seed"])
        out = {"bases": 0, "rows": []}
        while out["bases"] < 12:
            k = rng.randint(3, 8)
            G = nx.Graph()
            G.add_nodes_from(range(k))
            for _ in range(rng.randint(k - 1, int(1.5 * k))):
                a, b = rng.sample(range(k), 2)
                if G.degree(a) < 3 and G.degree(b) < 3:
                    G.add_edge(a, b)
            if not nx.is_connected(G):
                continue
            slots = {v: [] for v in range(k)}
            n = 0
            for a, b in G.edges():
                slots[a].append(n)
                slots[b].append(n)
                n += 1
            for v in range(k):
                while len(slots[v]) < 3:
                    slots[v].append(n)
                    n += 1
            if n > 14:
                continue
            ts = [tuple(slots[v]) for v in range(k)]
            twisted = rng.random() < 0.5
            ls = [N.NAE3] * k
            if twisted:
                ls[rng.randrange(k)] = M.switch(N.NAE3, 1 << rng.randrange(3))
            st = M.states(n, list(zip(ls, ts)))
            if len(st) == 0:
                continue
            out["bases"] += 1
            D = M.bond_matrix(n, st)
            out["rows"].append({"k": k, "n": n, "twisted": twisted, "series_parallel": N.series_parallel(G),
                                "two_connected": nx.is_biconnected(G) if k > 2 else False, "fails": bool(M.violations(D, n)),
                                "edges": [list(e) for e in G.edges()]})
        return out
    if kind == "sparse9":
        rng = random.Random(p["seed"])
        out = {"bases": 0, "failing": 0, "spanning_violations": 0, "metric_mismatch": 0}
        while out["bases"] < 50:
            n = 9
            ts = []
            for _ in range(rng.randint(3, 9)):
                t = tuple(sorted(rng.sample(range(n), 3)))
                if t not in ts and all(len(set(t) & set(u)) <= 1 for u in ts):
                    ts.append(t)
            if not M.covers(ts, n) or not nx.is_connected(N.incidence(ts)):
                continue
            st = M.states(n, [(N.NAE3, t) for t in ts])
            if len(st) == 0:
                continue
            out["bases"] += 1
            D = M.bond_matrix(n, st)
            v = M.violations(D, n)
            out["failing"] += bool(v)
            bl = N.primal_blocks(ts)
            vb = [set(vs) for vs, idx in bl]
            out["spanning_violations"] += sum(1 for x, y, z, *_ in v if not any({x, y, z} <= b for b in vb))
            loc = False
            for vs, idx in bl:
                k, kn, mm = N.sub_base([N.NAE3] * len(ts), ts, idx)
                loc |= bool(M.violations(M.bond_matrix(k, M.states(k, kn)), k))
            out["metric_mismatch"] += bool(v) != loc
        return out
    if kind == "grown":
        sys.path.insert(0, str(ROOT / "experiments/PICK-TWO-20261118-001B/PICK-TWO-20261118-001B-E001_pick"))
        import picklib as P
        out = {"runs": 0, "steps": 0, "max_b": 0, "brute_checked": 0, "brute_mismatch": 0}
        rule, param = p["rule"], None
        if rule.startswith("CAP"):
            rule, param = "CAP", int(p["rule"][3:])
        for seed in range(5):
            S, n = P.start(p["start"])
            S = tuple(sorted(S))
            rng = random.Random(9100 + seed)
            out["runs"] += 1
            for _ in range(30):
                bs = N.split_b(S, n)
                out["steps"] += 1
                out["max_b"] = max(out["max_b"], max(bs.values()))
                if n <= 12:
                    D = M.bond_matrix(n, M.np.array(S, dtype=M.np.int64))
                    out["brute_checked"] += 1
                    out["brute_mismatch"] += any(min(D[x][y], 3) != v for (x, y), v in bs.items())
                if len(S) > 60:
                    break
                ops, _ = P.options(S, n, rule, param)
                if not ops:
                    break
                a0, a1 = rng.choice(ops)
                S, n = tuple(sorted(P.M.apply(S, n, a0, a1))), n + 1
        return out
    if kind == "knotgrown":
        sys.path.insert(0, str(ROOT / "experiments/KNOT-SWITCH-20261118-001B/KNOT-SWITCH-20261118-001B-E001_switch"))
        import knotlib as K
        out = {"runs": 0, "steps": 0, "max_b": 0, "brute_checked": 0, "brute_mismatch": 0}
        n0 = p["n0"]
        for i, ks in enumerate(K.M.bracketings(0, n0 - 1)):
            if i >= 6:
                break
            S = K.M.base(n0, ks)
            G = K.M.pairs_of(ks)
            knots = list(ks)
            n = n0
            rng = random.Random(9300 + i)
            out["runs"] += 1
            for _ in range(30):
                bs = N.split_b(S, n)
                out["steps"] += 1
                out["max_b"] = max(out["max_b"], max(bs.values()))
                if n <= 12:
                    D = M.bond_matrix(n, M.np.array(sorted(S), dtype=M.np.int64))
                    out["brute_checked"] += 1
                    out["brute_mismatch"] += any(min(D[x][y], 3) != v for (x, y), v in bs.items())
                if len(S) > 60:
                    break
                if p["rule"] == "SEEDK":
                    ops, _ = K.seedk_options(S, n, G, K.betti(n, knots)["b2"])
                else:
                    ops, _ = K.L.options(S, n, G, p["rule"])
                if not ops:
                    break
                a0, a1, kk = rng.choice(ops)
                S = K.M.apply(S, n, a0, a1)
                G = G | K.M.pairs_of(kk)
                knots += list(kk)
                n += 1
        return out
    raise ValueError(kind)
