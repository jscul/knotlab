"""LIMIT-STATE-R1: the referee's own recomputation of LIMIT-STATE-20261112-001, and the copy bound.

Independent of dlang.py and census.py: limit relations by LIMIT-ONLY-R1's bitset code (ref_limit.py, the referee's), its own
expansion with copy tracking, its own CNF; exactly-one by the ladder encoding (the census used sequential counters).

The copy bound. If a self-holding definition i, read as its own family (defs[:i+1]), is dead at depth s, then every copy of i made
by a SELF call at level j holds a witness (a call with all three ends equal) among the calls of depth j + s inside it, in every
living state: impose not-all-equal on those calls and the copy holds definition i's depth-s pattern. Copies made by SELF calls at
one level are disjoint, so depth t needs at least B(t) = max over j of the number of level-j SELF copies of definitions dead at
depth t - j (and 1 when the family itself is dead at t).

  ref_state.py run WORKER WORKERS   -> result_<worker>.jsonl
  ref_state.py summary              -> result_summary.json
"""
import glob
import gzip
import json
import sys
from collections import Counter
from pathlib import Path

import numpy as np
from pysat.card import CardEnc, EncType
from pysat.solvers import Solver

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "research" / "LIMIT-ONLY-20261112-001" / "referee-R1"))
import ref_limit as R                                     # the referee's own bitset evaluator (LIMIT-ONLY-R1)

SRC = ROOT / "artifacts" / "LIMIT-ONLY-20261112-001A" / "LIMIT-ONLY-20261112-001A-E001_limit_only"
EXTRA, KNOT_CAP = 3, 60000


def families():
    out = []
    for name in sorted(glob.glob(str(SRC / "sample_*.jsonl.gz"))):
        for line in gzip.open(name, "rt"):
            r = json.loads(line)
            if r.get("limit_only"):
                out.append([(k, l, [(c, tuple(a)) for c, a in calls]) for k, l, calls in r["defs"]])
    return out


def usual_limit(defs):
    """G of the usual limit (the knot on the ends of every copy of a pass-through definition), and the main relation at G."""
    F = R.Family(defs)
    pt = R.pass_through(F.defs)

    def rels(X):
        sx = dict(zip(F.selfs, X))
        out = []
        for i, (k, l, calls) in enumerate(F.defs):
            ok = F.kmask[i]
            for c, a in calls:
                if c == "SELF":
                    ok &= R.call_mask(k + l, a, sx[i])
                elif c != "K":
                    ok &= R.call_mask(k + l, a, out[c])
            r = R.fold(ok, k + l, k)
            out.append(r & R.N3 if i in pt else r)
        return out
    G = (R.TOP3,) * len(F.selfs)
    while True:
        r = rels(G)
        G2 = tuple(r[i] for i in F.selfs)
        if G2 == G:
            return dict(zip(F.selfs, G)), r[-1]
        G = G2


def alive_seq(defs, upto):
    """Alive at depths 1..upto, read as its own family (the last definition is the main one)."""
    F = R.Family(defs)
    X, out = (R.N3,) * len(F.selfs), []
    for _ in range(upto):
        X, a = F.step(X)
        out.append(a)
    return out


def expand(defs, D, G):
    """Finite part to depth D, bottom SELF calls held in G. Returns clauses, calls by depth (with parent call and calling copy),
    and SELF copies by level and definition."""
    pt = R.pass_through(defs)
    cl, nv, nk = [], [defs[-1][0]], [0]
    calls_at, copies = {}, Counter()

    def knot(a):
        cl.append([x + 1 for x in a])
        cl.append([-(x + 1) for x in a])
        nk[0] += 1
        if nk[0] > KNOT_CAP:
            raise OverflowError

    def go(i, actual, depth, lev, anc):
        k, l, calls = defs[i]
        env = list(actual) + list(range(nv[0], nv[0] + l))
        nv[0] += l
        if i in pt:
            knot(actual)                                  # the usual limit's knot on a pass-through copy's ends
        for c, args in calls:
            a = [env[x] for x in args]
            if c == "K":
                knot(a)
            elif c == "SELF":
                lst = calls_at.setdefault(lev + 1, [])
                cid = (lev + 1, len(lst))
                lst.append((tuple(a), anc))
                if depth <= 1:
                    rel = G[i]
                    for s in range(8):
                        if not rel >> s & 1:
                            cl.append([-(v + 1) if s >> j & 1 else v + 1 for j, v in enumerate(a)])
                else:
                    copies[(lev + 1, i)] += 1
                    go(i, a, depth - 1, lev + 1, cid)
            else:
                go(c, a, depth, lev, anc)
    go(len(defs) - 1, list(range(defs[-1][0])), D, 0, None)
    return cl, calls_at, nv[0], copies


def witness_vars(cl, calls, top):
    """One variable per call: true -> its ends all equal, false -> not all equal."""
    vs = []
    for a, _ in calls:
        top += 1
        v = top
        x, y, z = [u + 1 for u in a]
        cl += [[-v, -x, y], [-v, x, -y], [-v, -y, z], [-v, y, -z], [v, x, y, z], [v, -x, -y, -z]]
        vs.append(v)
    return vs, top


def solve(base, n, calls_at, bounds, ray=False):
    """bounds: {depth: (kind, k)} with kind 'eq' or 'le'. Ray: a chosen call's parent call is chosen too."""
    cl, top, var = list(base), n + 1, {}
    for t in sorted(bounds):
        vs, top = witness_vars(cl, calls_at[t], top)
        var[t] = vs
        kind, k = bounds[t]
        if kind == "eq":                                  # exactly one: the ladder encoding, O(n) clauses
            enc = CardEnc.equals(lits=vs, bound=1, top_id=top, encoding=EncType.ladder)
        else:
            enc = CardEnc.atmost(lits=vs, bound=k, top_id=top, encoding=EncType.seqcounter)
        top = max(top, enc.nv)
        cl += enc.clauses
    if ray:
        ts = sorted(bounds)
        for t in ts[1:]:
            for j, (_, anc) in enumerate(calls_at[t]):
                if anc is not None and anc[0] in var:
                    cl.append([-var[t][j], var[anc[0]][anc[1]]])
                else:
                    cl.append([-var[t][j]])
    with Solver(name="glucose4", bootstrap_with=cl) as s:
        return s.solve()


def read(defs):
    G, main = usual_limit(defs)
    reach = R.reachable(defs)
    rec = dict(genuine=main != 0, pt_any=bool(R.pass_through(defs)), pt_reachable=bool(R.pass_through(defs) & reach),
               ndefs=len(defs))
    if not rec["genuine"]:
        return rec
    base = R.read(defs)
    T = base["first_dead"]
    rec.update(T=T, after=base["after"], kinds=[R.kind_of(G[i]) for i in sorted(G)], main_free=main == 0xFF if defs[-1][0] == 3
               else main == (1 << (1 << defs[-1][0])) - 1)
    rec["loose"] = all(k == "free" for k in rec["kinds"]) and rec["main_free"]
    if base["after"] == "recurrent":
        rec["skipped"] = "recurrent"
        return rec
    D = T + EXTRA
    try:
        cl, calls_at, n, copies = expand(defs, D, G)
    except OverflowError:
        rec["skipped"] = "size"
        return rec
    depths = list(range(T, D))
    rec["calls"] = [len(calls_at.get(t, [])) for t in depths]
    # the copy bound
    seqs = {i: alive_seq(defs[:i + 1], D) for i in R.Family(defs).selfs}
    fam = alive_seq(defs, D)
    B = []
    for t in depths:
        b = 0 if fam[t - 1] else 1
        for j in range(1, t):
            b = max(b, sum(c for (lev, i), c in copies.items() if lev == j and not seqs[i][t - j - 1]))
        B.append(b)
    rec["bound"] = B
    with Solver(name="glucose4", bootstrap_with=cl) as s:
        rec["alive_part"] = s.solve()
    rec["gates"] = []
    for t in depths:
        g = list(cl)
        for a, _ in calls_at[t]:
            g += [[x + 1 for x in a], [-(x + 1) for x in a]]
        with Solver(name="glucose4", bootstrap_with=g) as s:
            rec["gates"].append(not s.solve())
    rec["single"] = solve(cl, n, calls_at, {t: ("eq", 1) for t in depths})
    rec["single_ray"] = solve(cl, n, calls_at, {t: ("eq", 1) for t in depths}, ray=True) if rec["single"] else False
    rec["single_at"] = [solve(cl, n, calls_at, {t: ("eq", 1)}) for t in depths]
    # is the copy bound reached at each depth separately?
    rec["bound_reached"] = [solve(cl, n, calls_at, {t: ("le", b)}) if b * len(calls_at[t]) <= 1_500_000 else None
                            for t, b in zip(depths, B)]
    return rec


def run(worker, workers):
    """Resumable: a family whose read killed the worker (memory) is recorded as skipped on the next start."""
    fams = families()
    out, mark = HERE / f"result_{worker}.jsonl", HERE / f"started_{worker}.txt"
    done = {json.loads(x)["idx"] for x in open(out)} if out.exists() else set()
    crashed = int(mark.read_text()) if mark.exists() and mark.read_text().strip() else None
    with open(out, "a") as f:
        for idx, defs in enumerate(fams):
            if idx % workers != worker or idx in done:
                continue
            if idx == crashed:
                r = dict(genuine=True, skipped="memory")
            else:
                mark.write_text(str(idx))
                r = read(defs)
            r["idx"] = idx
            f.write(json.dumps(r) + "\n")
            f.flush()
    mark.write_text("")


def summarize():
    rows = [json.loads(x) for name in sorted(HERE.glob("result_*.jsonl")) for x in open(name)]
    g = [r for r in rows if r["genuine"]]
    S = dict(families=len(rows), genuine=len(g))
    S["genuine_by_pass_through"] = dict(any_definition=sum(r["pt_any"] for r in g), reachable=sum(r["pt_reachable"] for r in g),
                                        unreachable_only=sum(r["pt_any"] and not r["pt_reachable"] for r in g))
    S["loose"] = [sum(r["loose"] for r in g), len(g)]
    S["limit_kinds"] = dict(Counter(k for r in g for k in r["kinds"]))
    rd = [r for r in g if "single" in r]
    S["read"], S["not_read"] = len(rd), dict(Counter(r.get("skipped") for r in g if "single" not in r))
    S["gate_failures"] = sum(not x for r in rd for x in r["gates"]) + sum(not r["alive_part"] for r in rd)
    br = [r for r in rd if max(r["calls"]) >= 2]
    S["chains"], S["branching"] = len(rd) - len(br), len(br)
    S["single"] = [sum(r["single"] for r in br), sum(r["single_ray"] for r in br)]
    S["single_by_loose"] = {str(a): [sum(r["single"] for r in br if r["loose"] == a), sum(r["loose"] == a for r in br)] for a in (True, False)}
    S["single_at_each_depth_alone"] = [sum(r["single_at"][j] for r in br) for j in range(EXTRA)]
    S["calls_median"] = [float(np.median([r["calls"][j] for r in br])) for j in range(EXTRA)]
    # the copy bound
    S["bound_forces_two_somewhere"] = sum(max(r["bound"]) >= 2 for r in br)
    S["bound_forces_two_and_single_found"] = sum(max(r["bound"]) >= 2 and r["single"] for r in br)
    S["bound_allows_single_but_none"] = sum(max(r["bound"]) <= 1 and not r["single"] for r in br)
    S["bound_allows_single"] = [dict(idx=r["idx"], ndefs=r["ndefs"], calls=r["calls"], bound=r["bound"], single=r["single"],
                                     single_at=r["single_at"]) for r in br if max(r["bound"]) <= 1]
    S["bound_at_T_plus_1_ge_2"] = sum(r["bound"][1] >= 2 for r in br)
    S["bound_reached"] = {f"T+{j}": dict(Counter(str(r["bound_reached"][j]) for r in br)) for j in range(EXTRA)}
    S["bound_share_of_calls_median"] = [float(np.median([r["bound"][j] / r["calls"][j] for r in br])) for j in range(EXTRA)]
    S["one_definition_branching"] = sum(r["ndefs"] == 1 for r in br)
    json.dump(S, open(HERE / "result_summary.json", "w"), indent=1)
    print(json.dumps(S, indent=1))


if __name__ == "__main__":
    if sys.argv[1] == "run":
        run(int(sys.argv[2]), int(sys.argv[3]))
    else:
        summarize()
