"""Thread-written post-hoc diagnostic (not Codex's, not pre-registered): where do the size-3 bonds sit?

For a one-definition family, build the bottomless pattern truncated at tree depth N, with every SELF call at depth N
replaced by the bottomless port relation G (exact: subtrees meet the rest only at their ports, and G is their port
relation by compactness). Then, for the depth-s ray copy C_s (C_j = first SELF call of C_{j-1}), look for minimal
non-shattered triples {p, v, w}: p a port of C_0, v a local of C_s, w any distinction of the subtree of C_{s-1}.
Projections are read by satisfiability under assumptions (CaDiCaL via pysat).

Usage: thread_witness_probe.py OUT.json IDX... (s = 2, 3; N = s + 2)
"""
import itertools
import json
import os
import sys

from pysat.solvers import Cadical153

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, *[".."] * 4))
TB = os.path.join(ROOT, "experiments/TRUE-BOND-20261113-001A/TRUE-BOND-20261113-001A-E001_side_branches/codex")
sys.path.insert(0, TB)
import true_bond  # noqa: E402


def bottomless_G(defs):
    bd = true_bond.bd_module()
    _, _, Gd = bd.L.depth_sequence(defs, bd.L.TOP)
    return [bool(x) for x in Gd[0]]


def build(defs, G, N):
    """Clauses of the truncation; copies[path] = list of variable ids (ports then locals)."""
    nports, nloc, body = defs[0]
    selfs = [i for i, (c, _) in enumerate(body) if c == "SELF"]
    nxt = [0]

    def fresh():
        nxt[0] += 1
        return nxt[0]

    clauses, copies = [], {}
    stack = [((), [fresh() for _ in range(nports)])]
    while stack:
        path, ports = stack.pop()
        var = ports + [fresh() for _ in range(nloc)]
        copies[path] = var
        for ci, (callee, args) in enumerate(body):
            a = [var[x] for x in args]
            if callee == "K":
                clauses += [a, [-x for x in a]]
            elif len(path) < N:
                stack.append((path + (ci,), a))
            else:
                for st in range(8):
                    if not G[st]:
                        clauses.append([(-a[b] if (st >> b) & 1 else a[b]) for b in range(3)])
    return clauses, copies, selfs[0]


def probe(defs, s, N):
    G = bottomless_G(defs)
    clauses, copies, ray = build(defs, G, N)
    nports, nloc, _ = defs[0]
    solver = Cadical153(bootstrap_with=clauses)
    memo = {}

    def sat(lits):
        key = tuple(sorted(lits))
        if key not in memo:
            memo[key] = solver.solve(assumptions=list(key))
        return memo[key]

    def free_pair(x, y):
        return all(sat([x * sx, y * sy]) for sx, sy in ((1, 1), (1, -1)))  # complement closure gives the rest

    def constrained_triple(x, y, z):
        return not all(sat([x, y * sy, z * sz]) for sy in (1, -1) for sz in (1, -1))

    ray_path = (ray,) * s
    top = copies[()][:nports]
    v_locals = copies[ray_path][nports:]
    sub = [p for p in copies if p[:s - 1] == ray_path[:s - 1] and len(p) >= s - 1]
    pool = sorted({x for p in sub for x in copies[p]})
    where = {}
    for p in sub:
        for k, x in enumerate(copies[p]):
            where.setdefault(x, (p, k))
    found = []
    for pi, p in enumerate(top):
        for v in v_locals:
            if not free_pair(p, v):
                found.append({"kind": "pair", "p": pi})
                continue
            for w in pool:
                if w in (p, v) or not free_pair(p, w) or not free_pair(v, w):
                    continue
                if constrained_triple(p, v, w):
                    path, k = where[w]
                    found.append({"kind": "triple", "p": pi, "v": copies[ray_path].index(v),
                                  "w_copy_rel": list(path[s - 1:]), "w_var": k,
                                  "w_on_ray": all(c == ray for c in path),
                                  "p_is_port_of_Cs": p in copies[ray_path][:nports]})
    solver.delete()
    return found


def main():
    out, ids = sys.argv[1], [int(x) for x in sys.argv[2:]]
    fam = true_bond.study_families()
    res = {}
    for idx in ids:
        res[idx] = {}
        for s in (2, 3):
            f = probe(fam[idx], s, s + 2)
            tri = [x for x in f if x["kind"] == "triple"]
            res[idx][s] = {"pairs": sum(1 for x in f if x["kind"] == "pair"), "triples": len(tri),
                           "carried_p_only": all(x["p_is_port_of_Cs"] for x in tri) if tri else None,
                           "any_w_on_ray": any(x["w_on_ray"] for x in tri),
                           "examples": tri[:3]}
            print(idx, s, json.dumps({k: v for k, v in res[idx][s].items() if k != "examples"}), flush=True)
    with open(out, "w") as fh:
        json.dump(res, fh, indent=1)


if __name__ == "__main__":
    main()
