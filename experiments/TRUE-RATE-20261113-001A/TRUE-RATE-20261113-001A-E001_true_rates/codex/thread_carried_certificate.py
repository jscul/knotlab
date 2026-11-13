"""Thread-written post-hoc certificate (not Codex's, not pre-registered): L(s) <= 3 at every depth via a carried port.

Setting (as TRUE-BOND): the bottomless pattern of a one-definition family D; C_0 = main, C_{j+1} = D's first SELF call
in C_j (the ray). C_{j+1}.port[i] = C_j.var[a_i] for the ray call's arguments a. A top port is *carried* when it sits at
a position on a cycle of i -> a_i (a_i < 3): it is then an end of every ray copy, by identity.

Exactness. The pattern is a tree of copies glued at ports, so the projection onto the distinctions of subtree(C_s)
is {states of subtree(C_s) whose port triple lies in R_s}, where R_s is the projection of the rest onto C_s's ports.
R_0 = all 8 states (main's ports are free) and R_{s+1} = projection onto the ray call's arguments of
[ports in R_s, C_s's knots, C_s's other SELF calls in G], G the bottomless port relation (compactness, LIMIT-STATE).
(R_s, position of the carried port) takes finitely many values, so the sequence is eventually periodic.

Certificate. For every state reached from s = 1 on, a minimal non-shattered triple {carried port, own local v of C_s,
w} exists in subtree(C_s) truncated at depth N below C_s (boundary SELF calls as G; exact by the same argument).
Then L(s) <= 3 for every s >= 1. A forced pair {carried port, v} (L(s) <= 2) is recorded too.

Usage: thread_carried_certificate.py OUT.json [N]   (all carried-port families of the 226; default N = 3)
"""
import json
import os
import sys

from pysat.solvers import Cadical153

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import thread_witness_probe as wp  # noqa: E402

true_bond = wp.true_bond


def ray_args(defs):
    return next(a for c, a in defs[0][2] if c == "SELF")


def carried_positions(defs):
    a = ray_args(defs)
    g = {i: a[i] for i in range(3) if a[i] < 3}
    cyc = set()
    for i in g:
        x, seen = i, []
        while x in g and x not in seen:
            seen.append(x)
            x = g[x]
        if x in seen:
            cyc |= set(seen[seen.index(x):])
    return g, sorted(cyc)


def step(defs, G, R):
    """R_{s+1} from R_s (8-bit relations as frozensets of port states)."""
    nports, nloc, body = defs[0]
    ray = next(i for i, (c, _) in enumerate(body) if c == "SELF")
    out = set()
    for asg in range(1 << (nports + nloc)):
        bit = lambda x: (asg >> x) & 1  # noqa: E731
        if (asg & 7) not in R:
            continue
        ok = True
        for ci, (callee, args) in enumerate(body):
            st = sum(bit(x) << b for b, x in enumerate(args))
            if callee == "K" and st in (0, 7):
                ok = False
            elif callee == "SELF" and ci != ray and not G[st]:
                ok = False
            if not ok:
                break
        if ok:
            out.add(sum(bit(x) << b for b, x in enumerate(body[ray][1])))
    return frozenset(out)


def local_bond(defs, G, R, pos, N):
    """In subtree(C) with ports in R: is there a bond {port pos, local v, w}? Returns (triple, forced_pair)."""
    clauses, copies, _ = wp.build(defs, G, N)
    root = copies[()]
    for st in range(8):
        if st not in R:
            clauses.append([(-root[b] if (st >> b) & 1 else root[b]) for b in range(3)])
    solver = Cadical153(bootstrap_with=clauses)
    memo = {}

    def sat(lits):
        key = tuple(sorted(lits))
        if key not in memo:
            memo[key] = solver.solve(assumptions=list(key))
        return memo[key]

    def free(x, y):
        return all(sat([x * sx, y * sy]) for sx, sy in ((1, 1), (1, -1)))

    p = root[pos]
    pool = sorted({x for c in copies.values() for x in c})
    triple, forced = None, False
    nports = defs[0][0]
    for v in root[nports:]:
        if not free(p, v):
            forced = True
            continue
        for w in pool:
            if triple is None and w not in (p, v) and free(p, w) and free(v, w) and \
                    not all(sat([p, v * sy, w * sz]) for sy in (1, -1) for sz in (1, -1)):
                triple = [root.index(v), w]
    solver.delete()
    return triple, forced


def certify(defs, N):
    G = wp.bottomless_G(defs)
    g, cyc = carried_positions(defs)
    if not cyc:
        return {"carried": False}
    inv = {g[i]: i for i in cyc}  # on the cycle g is a bijection: position at depth s+1 of the port at pos
    results = []
    for start in cyc:
        R, pos, seen, seq = frozenset(range(8)), start, {}, []
        s = 0
        while (R, pos) not in seen:
            seen[(R, pos)] = s
            seq.append((R, pos))
            R, pos, s = step(defs, G, R), inv[pos], s + 1
        pre, period = seen[(R, pos)], s - seen[(R, pos)]
        checks = []
        for k, (Rk, pk) in enumerate(seq):
            if k == 0:
                continue  # s = 0 is the top copy itself; the claim is for s >= 1
            triple, forced = local_bond(defs, G, Rk, pk, N)
            checks.append({"s": k, "R": sorted(Rk), "pos": pk, "triple": triple, "forced_pair": forced})
        # Sequence states cover s = 1..pre+period-1; s = 0 repeats only if pre == 0 (then state 0 recurs at s = period).
        covered = all(c["triple"] or c["forced_pair"] for c in checks)
        if pre == 0:
            t, f = local_bond(defs, G, seq[0][0], seq[0][1], N)
            covered = covered and bool(t or f)
            checks.append({"s": "cycle-return to state 0", "triple": t, "forced_pair": f})
        results.append({"top_port": start, "preperiod": pre, "period": period,
                        "bounded_by_3_all_s": covered, "checks": checks})
    return {"carried": True, "cycle": cyc, "by_port": results,
            "bounded_by_3_all_s": any(r["bounded_by_3_all_s"] for r in results)}


def main():
    out = sys.argv[1]
    N = int(sys.argv[2]) if len(sys.argv) > 2 else 3
    fam = true_bond.study_families()
    res = {}
    for idx in sorted(fam):
        if not carried_positions(fam[idx])[1]:
            continue
        r = certify(fam[idx], N)
        res[idx] = r
        print(idx, r["cycle"], "bounded<=3 all s:", r["bounded_by_3_all_s"],
              [(b["top_port"], b["preperiod"], b["period"]) for b in r["by_port"]], flush=True)
    with open(out, "w") as fh:
        json.dump(res, fh, indent=1)


if __name__ == "__main__":
    main()
