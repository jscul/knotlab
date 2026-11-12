"""WITNESS-COUNT-R1: the least witness counts recomputed without SAT, by a table over end states; the joint query by SAT.

Independent of dlang.py and both census scripts. Limit relations by LIMIT-ONLY-R1's bitset code; the expansion and SAT encodings
of LIMIT-STATE-R1 (the referee's own) for the joint query.

The table. Given the distinctions of a copy (its ends and its own locals), the copies it makes share nothing else with each other,
so the least number of witnesses at relative depth d inside a copy of definition i with ends s is
    f_i,d(s) = min over assignments of the copy's distinctions with ends s, its knots satisfied and every callee's ends in the
               callee's limit relation, of  sum over its SELF calls of g_d(callee ends) + sum over its calls of earlier
               definitions j of f_j,d(callee ends),
with g_1(e) = [e all equal] (the call itself is at relative depth 1) and g_d = f_i,d-1 for d >= 2. Exact, by independence given the
calling copy's distinctions (the fixed-point property of the limit relations). w_t = min over s of f_main,t(s).

  ref_wc.py run WORKER WORKERS   -> result_<worker>.jsonl (with WC_NOJOINT=1: the table only -> dp_<worker>.jsonl)
  ref_wc.py summary              -> result_summary.json
"""
import glob
import json
import os
import sys
from collections import Counter
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "research" / "LIMIT-ONLY-20261112-001" / "referee-R1"))
sys.path.insert(0, str(ROOT / "research" / "LIMIT-STATE-20261112-001" / "referee-R1"))
import ref_limit as R                                     # bitset relations (LIMIT-ONLY-R1)
import ref_state as RS                                    # expansion and SAT queries (LIMIT-STATE-R1)

CENSUS = ROOT / "artifacts" / "WITNESS-COUNT-20261112-001A" / "WITNESS-COUNT-20261112-001A-E001_witness_count"
EXTRA_DP = 7                                              # depths T .. T+6 by the table
INF = 10 ** 9


def usual_defs(defs):
    pt = R.pass_through(defs)
    return [(k, l, list(calls) + ([("K", (0, 1, 2))] if i in pt else [])) for i, (k, l, calls) in enumerate(defs)]


def limit_relations(defs):
    """Every definition's relation at the usual limit's greatest fixed point."""
    F = R.Family(defs)
    G = (R.TOP3,) * len(F.selfs)
    while True:
        G2, _ = F.step(G)
        if G2 == G:
            return F.rels(G)
        G = G2


class Table:
    def __init__(self, defs, rl):
        self.defs = defs
        self.info = []
        for i, (k, l, calls) in enumerate(defs):
            V = k + l
            a = np.arange(1 << V)
            bits = (a[:, None] >> np.arange(V)) & 1
            ok = np.ones(1 << V, bool)
            ends = []
            for c, args in calls:
                st = (bits[:, list(args)] << np.arange(len(args))).sum(1)
                rel = R.N3 if c == "K" else (rl[i] if c == "SELF" else rl[c])
                ok &= (rel >> st) & 1 == 1
                ends.append(st)
            sel = np.nonzero(ok)[0]
            self.info.append(dict(k=k, port=sel & ((1 << k) - 1), ends=[e[sel] for e in ends], calls=calls))

    def f(self, D):
        """f[d][i]: array over end states of definition i, d = 1..D."""
        f = [None]
        for d in range(1, D + 1):
            row = []
            for i, inf in enumerate(self.info):
                cost = np.zeros(len(inf["port"]), np.int64)
                for (c, _), e in zip(inf["calls"], inf["ends"]):
                    if c == "K":
                        continue
                    if c == "SELF":
                        g = ((e == 0) | (e == 7)).astype(np.int64) if d == 1 else f[d - 1][i][e]
                    else:
                        g = row[c][e]
                    cost = cost + g
                out = np.full(1 << inf["k"], INF, np.int64)
                np.minimum.at(out, inf["port"], np.minimum(cost, INF))
                row.append(out)
            f.append(row)
        return f

    def counts(self, D):
        """n[d][i]: calls at relative depth d inside a copy of definition i."""
        n = [None]
        for d in range(1, D + 1):
            row = []
            for i, (k, l, calls) in enumerate(self.defs):
                row.append(sum((1 if d == 1 else n[d - 1][i]) if c == "SELF" else (0 if c == "K" else row[c]) for c, _ in calls))
            n.append(row)
        return n


def read(defs0, census):
    defs = usual_defs(defs0)
    rl = limit_relations(defs)
    if rl[-1] == 0:
        return dict(genuine=False)
    base = R.read(defs0)
    T = base["first_dead"]
    rec = dict(genuine=True, T=T, ndefs=len(defs))
    if base["after"] == "recurrent":
        rec["skipped"] = "recurrent"
        return rec
    tab = Table(defs, rl)
    D = T + EXTRA_DP - 1
    f, n = tab.f(D), tab.counts(D)
    rec["w_dp"] = [int(f[t][-1].min()) for t in range(T, D + 1)]
    rec["N_dp"] = [int(n[t][-1]) for t in range(T, D + 1)]
    selfs = R.Family(defs).selfs
    if len(defs) == 1:
        c = sum(cl == "SELF" for cl, _ in defs[0][2])
        w = dict(zip(range(T, D + 1), rec["w_dp"]))
        rec["B_dp"] = [max([1] + [c ** s * w[t - s] for s in range(1, t - T + 1)]) for t in range(T, D + 1)]
        ft = f[T][0]
        vals = sorted({int(x) for x in ft if x < INF})
        rec["fT_values"] = vals                                    # the least count at depth T by end state of the copy
        rec["fT_all_equal"] = int(ft[0]) if ft[0] < INF else None
        rec["fT_min_states"] = [s for s in range(8) if ft[s] == ft.min()]
    if census and "w" in census:
        rec["census_match"] = dict(w=census["w"] == rec["w_dp"][:3], N=census["N"] == rec["N_dp"][:3],
                                   B=(census["B"] == rec["B_dp"][:3]) if len(defs) == 1 else None)
        # the joint query by SAT on the referee's expansion, where the encoding is small enough
        w3 = rec["w_dp"][:3]
        if not os.environ.get("WC_NOJOINT") and sum(a * b for a, b in zip(census["N"], w3)) <= 1_500_000:
            G = {i: rl[i] for i in selfs}
            try:
                cl, calls_at, nv, _ = RS.expand(defs0, T + 3, G)
                rec["joint_sat"] = RS.solve(cl, nv, calls_at, {t: ("le", b) for t, b in zip(range(T, T + 3), w3)})
                rec["below_sat"] = [RS.solve(cl, nv, calls_at, {t: ("le", b - 1)}) for t, b in zip(range(T, T + 3), w3)]
            except OverflowError:
                pass
    return rec


def run(worker, workers):
    fams = RS.families()
    census = {}
    for name in glob.glob(str(CENSUS / "runs_*.jsonl")):
        for x in open(name):
            r = json.loads(x)
            if "idx" in r:
                census[r["idx"]] = r
    prefix = "dp" if os.environ.get("WC_NOJOINT") else "result"
    with open(HERE / f"{prefix}_{worker}.jsonl", "w") as f:
        for idx, defs in enumerate(fams):
            if idx % workers == worker:
                r = read(defs, census.get(idx))
                r["idx"] = idx
                r["census_joint"] = census.get(idx, {}).get("joint")
                r["census_read"] = "w" in census.get(idx, {})
                f.write(json.dumps(r) + "\n")
                f.flush()


def summarize():
    rows = [json.loads(x) for name in sorted(HERE.glob("dp_*.jsonl")) for x in open(name)]
    joint = {}
    for name in sorted(HERE.glob("result_*.jsonl")):
        if name.stem == "result_summary":
            continue
        for x in open(name):
            r = json.loads(x)
            if "joint_sat" in r:
                joint[r["idx"]] = r
    for r in rows:
        if r["idx"] in joint:
            r["joint_sat"], r["below_sat"] = joint[r["idx"]]["joint_sat"], joint[r["idx"]]["below_sat"]
    g = [r for r in rows if r["genuine"]]
    S = dict(genuine=len(g), read_by_table=sum("w_dp" in r for r in g))
    cm = [r for r in g if "census_match" in r]
    S["census_compared"] = len(cm)
    S["w_match"] = sum(r["census_match"]["w"] for r in cm)
    S["N_match"] = sum(r["census_match"]["N"] for r in cm)
    S["B_match_one_definition"] = [sum(r["census_match"]["B"] for r in cm if r["census_match"]["B"] is not None),
                                   sum(r["census_match"]["B"] is not None for r in cm)]
    js = [r for r in cm if "joint_sat" in r]
    S["joint_checked"] = len(js)
    S["joint_match"] = sum(r["joint_sat"] == bool(r["census_joint"]) for r in js)
    S["joint_true"] = [sum(r["joint_sat"] for r in js), len(js)]
    S["below_least_count_feasible"] = sum(any(r["below_sat"]) for r in js)
    one = [r for r in cm if r["ndefs"] == 1]
    mult = [r for r in one if r["w_dp"][1:3] == r["B_dp"][1:3]]
    S["one_definition"] = len(one)
    S["multiplicative"] = len(mult)
    S["multiplicative_with_constant_fT"] = sum(len(r["fT_values"]) == 1 for r in mult)
    nonm = [r for r in one if r["w_dp"][1:3] != r["B_dp"][1:3]]
    S["non_multiplicative_with_constant_fT"] = sum(len(r["fT_values"]) == 1 for r in nonm)
    S["non_multiplicative_fT_varies"] = sum(len(r["fT_values"]) > 1 for r in nonm)
    S["excess_at_T+1"] = sum(r["w_dp"][1] > r["B_dp"][1] for r in nonm)
    S["fT_all_equal_cheapest"] = dict(Counter(("all-equal ends cheapest" if 0 in r["fT_min_states"] else "not-all-equal ends cheapest")
                                              for r in one))
    # growth to T+6 by the table
    br = [r for r in g if "w_dp" in r and max(r["N_dp"][:3]) >= 2]
    S["share_w_over_N_median_T_to_T+6"] = [round(float(np.median([r["w_dp"][j] / r["N_dp"][j] for r in br])), 4) for j in range(EXTRA_DP)]
    S["share_ratio_T+6_over_T"] = dict(Counter(("<0.5" if q < 0.5 else ("0.5-2" if q <= 2 else ">2"))
                                               for q in [(r["w_dp"][6] / r["N_dp"][6]) / (r["w_dp"][0] / r["N_dp"][0]) for r in br]))
    S["not_read_by_census_read_by_table"] = sum(not r["census_read"] and "w_dp" in r for r in g)
    json.dump(S, open(HERE / "result_summary.json", "w"), indent=1)
    print(json.dumps(S, indent=1))


if __name__ == "__main__":
    if sys.argv[1] == "run":
        run(int(sys.argv[2]), int(sys.argv[3]))
    else:
        summarize()
