"""WITNESS-COUNT-20261112-001A: the least number of all-equal calls a living state of the usual limit needs at each dead depth.

Families: LIMIT-STATE-20261112-001's genuine families (LIMIT-ONLY's records, the usual limit). For depths t = T, T+1, T+2 of the
finite part to depth T+3 with the limit relation G at its bottom (exactly the restrictions of the limit's living states):
  N_t  - calls of depth t (SELF calls made from copies at level t - 1);
  A_t  - the number of disjoint copies dead on their own at depth t (a copy made by a call at depth s of definition i is dead when
         i's relation at depth t - s is empty); each needs its own witness among its depth-t calls, so A_t <= w_t (proved);
  B_t  - (one-definition families) the same with each dead copy needing its own least count w_(t-s), since the limit's state
         restricted to a copy is a living state of that copy's limit (the advisor's sharper bound): B_t <= w_t (proved);
         'multiplicative' when w_t = B_t at depths T+1 and T+2 (copies independent);
  w_t  - the least number of depth-t calls with all three ends equal over living states (exact: SAT with a cardinality bound);
  joint - whether one living state attains w_T, w_T+1, w_T+2 together, and in it the share of depth t+1 witnesses made inside the
         copy of a depth-t witness.
Run from the repository root:  census.py --run WORKER WORKERS  |  census.py --summary
"""
import glob, json, os, random, sys, time, importlib.util
from collections import Counter
import numpy as np
from pysat.solvers import Solver
from pysat.card import ITotalizer, CardEnc, EncType

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "../../SHORT-DESC-20261112-001A/SHORT-DESC-20261112-001A-E001_description_census"))
import dlang as L
_s = importlib.util.spec_from_file_location("ls", os.path.join(HERE, "../../LIMIT-STATE-20261112-001A/LIMIT-STATE-20261112-001A-E001_limit_states/census.py"))
LS = importlib.util.module_from_spec(_s); _s.loader.exec_module(LS)      # families, usual, relation_clauses, first_dead

ROOT = os.path.join(HERE, "../../..")
OUT = os.environ.get("WC_OUT") or os.path.join(ROOT, "artifacts/WITNESS-COUNT-20261112-001A/WITNESS-COUNT-20261112-001A-E001_witness_count")
EXTRA, KNOT_CAP, CALL_CAP = 3, 60000, 20000


def expand(defs, D, G):
    """As LIMIT-STATE's, also recording each SELF call's definition and enclosing call."""
    clauses, nv, calls, nknots = [], [0], [], [0]

    def call(i, actual, depth, lev, anc):
        k, l, body = defs[i]
        env = list(actual) + list(range(nv[0], nv[0] + l))
        nv[0] += l
        for callee, args in body:
            a = [env[x] for x in args]
            if callee == "K":
                clauses.extend([[x + 1 for x in a], [-(x + 1) for x in a]])
                nknots[0] += 1
                if nknots[0] > KNOT_CAP:
                    raise OverflowError
            elif callee == "SELF":
                cid = len(calls)
                calls.append(dict(depth=lev + 1, defn=i, ends=tuple(a), parent=anc))
                if depth <= 1:
                    clauses.extend(LS.relation_clauses(a, G[i]))
                else:
                    call(i, a, depth - 1, lev + 1, cid)
            else:
                call(callee, a, depth, lev, anc)

    k = defs[-1][0]
    nv[0] = k
    call(len(defs) - 1, list(range(k)), D, 0, None)
    return clauses, calls, nv[0]


def depth_relations(defs, D):
    """rels[d][i]: definition i's relation at depth d (d = 1: its SELF calls are knots)."""
    sl = LS.selfs_of(defs)
    prev = {i: L.NAE for i in sl}
    out = [None]
    for d in range(1, D + 1):
        rels = L.relations(defs, prev)
        out.append(rels)
        prev = {i: rels[i] for i in sl}
    return out


def antichain(calls, rels, t, need=None):
    """Disjoint copies dead on their own at depth t, each weighted by need(depth t - s) (1 when need is None): tree DP over calls,
    the root being the main copy, whose own need is 1."""
    kids = {}
    for j, c in enumerate(calls):
        if c["depth"] < t:
            kids.setdefault(c["parent"], []).append(j)

    def best(node, s, defn):
        if node is None:
            own = int(not rels[t][len(rels[t]) - 1].any())
        else:
            own = (need(t - s) if need else 1) if not rels[t - s][defn].any() else 0
        tot = sum(best(ch, calls[ch]["depth"], calls[ch]["defn"]) for ch in kids.get(node, []))
        return max(own, tot)
    return best(None, 0, None)


def read(defs0):
    defs, passes = LS.usual(defs0)
    _, _, G = L.depth_sequence(defs, L.TOP)
    if not L.relations(defs, G)[-1].any():
        return dict(genuine=False)
    T, after = LS.first_dead(defs)
    rec = dict(genuine=True, T=T, after=after, ndefs=len(defs), nself=len(LS.selfs_of(defs)))
    if T is None or after == "recurrent":
        rec["skipped"] = "recurrent"
        return rec
    D = T + EXTRA
    try:
        clauses, calls, n = expand(defs, D, G)
    except (OverflowError, RecursionError):
        rec["skipped"] = "size"
        return rec
    depths = list(range(T, D))
    by = {t: [j for j, c in enumerate(calls) if c["depth"] == t] for t in depths}
    rec["N"] = [len(by[t]) for t in depths]
    if max(rec["N"]) > CALL_CAP:
        rec["skipped"] = "calls"
        return rec
    rels = depth_relations(defs, D)
    rec["A"] = [antichain(calls, rels, t) for t in depths]
    top = [n + len(calls) + 1]
    e = {j: n + 1 + j for j in range(len(calls))}                    # e_j: call j's ends may be all equal only if e_j
    cl = list(clauses)
    for j, c in enumerate(calls):
        if c["depth"] in by:
            x, y, z = [u + 1 for u in c["ends"]]
            cl += [[x, y, z, e[j]], [-x, -y, -z, e[j]]]
    w, B, single = [], [], len(defs) == 1
    wd = {}
    with Solver(name="cadical153", bootstrap_with=cl) as s:
        tots = {}
        for t in depths:
            tot = ITotalizer(lits=[e[j] for j in by[t]], ubound=len(by[t]), top_id=top[0])
            top[0] = tot.top_id
            s.append_formula(tot.cnf.clauses)
            tots[t] = tot
            b = antichain(calls, rels, t, need=(lambda d: wd.get(d, 1)) if single else None)
            B.append(b)
            if b > 1 and s.solve(assumptions=[-tot.rhs[b - 1]] if b - 1 < len(tot.rhs) else []):
                rec["bound_violation"] = True                       # a state with fewer witnesses than the proved bound
            lo, hi = max(1, b), len(by[t])
            while lo < hi:                                           # least b with a living state of <= b witnesses
                mid = (lo + hi) // 2
                if s.solve(assumptions=[-tot.rhs[mid]] if mid < len(tot.rhs) else []):
                    hi = mid
                else:
                    lo = mid + 1
            w.append(lo)
            wd[t] = lo
        rec["w"], rec["B"], rec["single_def"] = w, B, single
        assum = [-tots[t].rhs[b] for t, b in zip(depths, w) if b < len(tots[t].rhs)]
        rec["joint"] = s.solve(assumptions=assum)
        if rec["joint"]:
            m = set(l for l in s.get_model() if l > 0)
            def alleq(j):
                x, y, z = calls[j]["ends"]
                return ((x + 1) in m) == ((y + 1) in m) == ((z + 1) in m)
            W = {t: set(j for j in by[t] if alleq(j)) for t in depths}
            def inside(j, Wt):
                p = calls[j]["parent"]
                while p is not None:
                    if p in Wt:
                        return True
                    p = calls[p]["parent"]
                return False
            rec["witnesses_in_state"] = [len(W[t]) for t in depths]
            rec["nested_share"] = [round(sum(inside(j, W[t]) for j in W[t + 1]) / len(W[t + 1]), 4) if W[t + 1] else None
                                   for t in depths[:-1]]
    return rec


def run(worker, workers):
    os.makedirs(OUT, exist_ok=True)
    fams = LS.families()
    f = open(os.path.join(OUT, f"runs_{worker}.jsonl"), "w")
    t0 = time.time()
    for idx, defs in enumerate(fams):
        if idx % workers != worker:
            continue
        r = read(defs)
        r["idx"] = idx
        if r.get("w") and r["w"][0] == 1 and max(r["w"]) == 1:
            r["defs"] = defs
        f.write(json.dumps(r) + "\n")
        f.flush()
    f.write(json.dumps(dict(kind="done", seconds=round(time.time() - t0))) + "\n")
    f.close()


def law(r):
    w, N = r["w"], r["N"]
    if w[-1] == w[0]:
        return "constant"
    ratio = (w[-1] / N[-1]) / (w[0] / N[0])
    return "fixed share" if 0.5 <= ratio <= 2 else "between"


def summarize():
    rows = [json.loads(x) for name in sorted(glob.glob(os.path.join(OUT, "runs_*.jsonl"))) for x in open(name)]
    rows = [r for r in rows if r.get("kind") != "done" and r["genuine"]]
    rd = [r for r in rows if "w" in r]
    S = dict(genuine=len(rows), read=len(rd), not_read=dict(Counter(r.get("skipped") for r in rows if "w" not in r)))
    S["bound_violations"] = sum(r.get("bound_violation", False) for r in rd)
    one = [r for r in rd if r["single_def"]]
    S["one_definition"] = len(one)
    S["P1_multiplicative_share"] = round(sum(r["w"][1:] == r["B"][1:] for r in one) / len(one), 4) if one else None
    S["excess_w_over_B"] = {str(k): v for k, v in Counter(tuple(round(b / a, 2) if a else None for a, b in zip(r["B"][1:], r["w"][1:]))
                                                           for r in one).most_common(8)}
    S["w_T"] = dict(Counter(r["w"][0] for r in rd))
    S["P2_joint_share"] = round(sum(r.get("joint", False) for r in rd) / len(rd), 4) if rd else None
    S["more_than_one_settled"] = dict(Counter((max(r["A"]) >= 2, max(r["w"]) >= 2) for r in rd if max(r["N"]) >= 2).items()) if rd else None
    S["more_than_one_settled"] = {f"bound>=2:{a}|w>=2:{b}": v for (a, b), v in Counter((max(r["A"]) >= 2, max(r["w"]) >= 2) for r in rd if max(r["N"]) >= 2).items()}
    br = [r for r in rd if max(r["N"]) >= 2]
    S["laws"] = dict(Counter(law(r) for r in br))
    S["median_w_over_N"] = [round(float(np.median([r["w"][j] / r["N"][j] for r in br])), 4) for j in range(EXTRA)] if br else None
    ns = [x for r in rd if r.get("nested_share") for x in r["nested_share"] if x is not None]
    S["nested_share_mean"] = round(float(np.mean(ns)), 4) if ns else None
    multi = [r for r in rd if not r["single_def"]]
    S["multi_definition"] = dict(n=len(multi), A_equals_w=sum(r["A"] == r["w"] for r in multi))
    S["single_witness_families"] = [dict(idx=r["idx"], ndefs=r["ndefs"], nself=r["nself"], T=r["T"], N=r["N"], A=r["A"], defs=r["defs"])
                                    for r in rd if "defs" in r]
    return S


if __name__ == "__main__":
    if sys.argv[1] == "--run":
        run(int(sys.argv[2]), int(sys.argv[3]))
    elif sys.argv[1] == "--summary":
        S = summarize()
        json.dump(S, open(os.path.join(OUT, "summary.json"), "w"), indent=1)
        print(json.dumps(S, indent=1))
