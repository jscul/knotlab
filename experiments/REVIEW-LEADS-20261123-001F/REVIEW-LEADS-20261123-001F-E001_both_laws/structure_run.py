"""Driver shared by seven.py and nine.py (one script per structure calls it).

For one source and the three arms (rule, parity alone, not-all-equal alone):
  * the structure by ordinary growth to the horizon (the smaller of the step cap
    and the last step with at most 300 knots), arities met, stalls;
  * lawful valued starts: exact number, all of them if at most 4,096, otherwise
    1,024 drawn by seed 2026112306; the carried-count vector of each start is all
    that a continuation can depend on;
  * survivors by step: whether a start has at least one whole lawful history of
    t parent steps, decided by a SAT instance over the edge bits of the growth
    graph for t = 1..horizon, for the drawn starts and for every lawful carried
    vector (hence every lawful start);
  * whether a surviving start has one whole history or several, to the horizon;
  * the number of whole histories per start, exactly, for as many parent steps as
    fit in the time and memory allowance, with the carried count by stage.
"""

import itertools
import json
import math
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import both_laws as B

OUT = B.OUT
COUNT_SECONDS_PER_ARM = 110.0
CAP_STATES = 3_000_000


def lawful_cvector_weights(S, arm, live):
    """Exact number of lawful valued starts with each carried-count vector of the
    live founders, summed over every lawful valuation (sum over the shared
    distinctions of a product of independent founder factors)."""
    import numpy as np
    shape = tuple(len(S.loose_bits[u]) + 1 for u in live)
    total = np.zeros(shape, dtype=np.int64)
    for bits in itertools.product((0, 1), repeat=len(S.shared)):
        val = dict(zip(S.shared, bits))
        scalar = 1
        vecs = []
        for u, row in enumerate(S.stars):
            s = sum(val[d] for d in row if d in val)
            h = len(S.loose_bits[u])
            vec = np.array([math.comb(h, k) if B.lawful(arm, S.arity[u], s + k) else 0
                            for k in range(h + 1)], dtype=np.int64)
            if u in live:
                vecs.append(vec)
            else:
                scalar *= int(vec[0])
        if not scalar:
            continue
        t = vecs[0]
        for v in vecs[1:]:
            t = np.multiply.outer(t, v)
        total += scalar * t
    weights = {tuple(int(i) for i in idx): int(total[tuple(idx)]) for idx in np.argwhere(total > 0)}
    return Counter(weights)


def summarize(values):
    values = sorted(values)
    n = len(values)
    if not n:
        return {"n": 0}
    return {"n": n, "min": str(values[0]), "median": str(values[n // 2]), "max": str(values[-1]),
            "distinct": len(set(values)), "unique_history_starts": sum(1 for v in values if v == 1)}


def layer_budget_removals(st, arm, base=1, limit=2_000_000):
    """Prefix-level removal. Over every vector of numbers of ones that the knots born
    at parent step ``base`` could carry (whether or not reachable), those from which
    no whole lawful history reaches the horizon. Empty means no old word of
    ``base`` parent steps is ever removed later. Skipped when the space is large."""
    layer = st.layers[base - 1]
    live = [b for b in layer if len(b.fresh) > 0]
    size = math.prod(len(b.fresh) + 1 for b in live)
    if st.horizon <= base:
        return {"space": size, "skipped": "no later step inside the horizon"}
    if size > limit:
        return {"space": size, "skipped": "space too large to enumerate"}
    sv = B.SurvivalFrom(st, arm, st.horizon, base)
    dead = [f for f in itertools.product(*(range(len(b.fresh) + 1) for b in live)) if not sv.alive(f)]
    sv.close()
    return {"space": size, "dead_vectors": len(dead), "examples": [list(f) for f in dead[:3]]}


def structure_table(st):
    rows = []
    knots = st.n0
    for step, layer in enumerate(st.layers, 1):
        knots += len(layer)
        rows.append({"parent_step": step, "births": len(layer), "knots": knots,
                     "parents": dict(sorted(Counter(len(b.parents) for b in layer).items())),
                     "fresh": dict(sorted(Counter(len(b.fresh) for b in layer).items())),
                     "arity": dict(sorted(Counter(len(b.support) for b in layer).items()))})
    return rows


def run(name, stars, max_steps, cap):
    t0 = time.time()
    st = B.build_structure(name, stars, max_steps, cap)
    S = B.Starts(st.stars)
    live = [u for u in range(st.n0) if st.loose(u) > 0]
    founders, born = st.arities()
    result = {
        "structure": name, "sources": B.source_hashes(),
        "counting_null_sha256": B.sha(B.HERE / "counting_null.md"),
        "founders": st.n0, "distinctions": S.D, "shared_distinctions": len(S.shared),
        "loose_per_founder": [len(S.loose_bits[u]) for u in range(st.n0)],
        "founder_arities": [S.arity[u] for u in range(st.n0)],
        "step_cap": max_steps, "knot_cap": cap, "horizon_parent_steps": st.horizon,
        "knots_by_step_through_first_step_over_cap": st.knots_by_step,
        "stalls_through_horizon": None if st.stalled_at is None else st.stalled_at,
        "both_laws_give_same_births": st.both_laws_agree,
        "layers": structure_table(st),
        "arities_met": {"founders": {str(k): v for k, v in sorted(founders.items())},
                        "newborns": {str(k): v for k, v in sorted(born.items())}},
        "allowed_ones_by_arity": {str(n): {arm: [k for k in range(n + 1) if B.lawful(arm, n, k)]
                                           for arm in B.ARMS}
                                  for n in sorted(set(founders) | set(born))},
        "arms": {},
    }
    jsonl = []
    for arm in B.ARMS:
        ta = time.time()
        n, mode, vals, raw = S.draw(arm)
        weights = lawful_cvector_weights(S, arm, live)
        assert sum(weights.values()) == n, (sum(weights.values()), n)
        cvec = {v: S.carried(v, live) for v in vals}
        distinct = sorted(set(cvec.values()))
        arm_out = {"lawful_valued_starts": n, "selection": mode, "starts_used": len(vals),
                   "raw_draws_for_selection": raw, "starts_sha256": B.start_digest(vals),
                   "distinct_carried_vectors_among_starts": len(distinct),
                   "lawful_carried_vectors": len(weights)}
        # survivors by step: SAT, drawn starts at every depth, all lawful vectors at every depth
        alive_depth = {c: 0 for c in distinct}
        alive_depth_all = {c: 0 for c in weights}
        sat_info = []
        for depth in range(st.horizon, 0, -1):
            sv = B.Survival(st, arm, depth)
            sat_info.append({"depth": depth, "variables": sv.nvars, "clauses": sv.nclauses})
            for c in distinct:
                if alive_depth[c] == 0 and sv.alive(c):
                    alive_depth[c] = depth
            for c in weights:
                if alive_depth_all[c] == 0 and sv.alive(c):
                    alive_depth_all[c] = depth
            sv.solver.delete()
        # a start that survives to a depth survives to every smaller depth
        sat_info.sort(key=lambda r: r["depth"])
        arm_out["sat_instances"] = sat_info
        arm_out["survivors_by_step"] = [len(vals)] + [
            sum(1 for v in vals if alive_depth[cvec[v]] >= t) for t in range(1, st.horizon + 1)]
        arm_out["all_lawful_starts_surviving_by_step"] = [n] + [
            sum(w for c, w in weights.items() if alive_depth_all[c] >= t) for t in range(1, st.horizon + 1)]
        arm_out["lawful_starts_without_survivor_at_horizon"] = n - arm_out["all_lawful_starts_surviving_by_step"][-1]
        # one whole history or several, to the horizon
        sv = B.Survival(st, arm, st.horizon)
        uniq = {}
        for c in distinct:
            uniq[c] = sv.unique(c)
        arm_out["horizon_history_uniqueness_over_drawn_starts"] = {
            "no_history": sum(1 for v in vals if uniq[cvec[v]] is None),
            "exactly_one_history": sum(1 for v in vals if uniq[cvec[v]] is True),
            "at_least_two_histories": sum(1 for v in vals if uniq[cvec[v]] is False)}
        if arm == "rule":
            uniq_all = Counter()
            stop = time.time() + 120
            for c, w in weights.items():
                u = sv.unique(c) if time.time() < stop else "not_checked"
                uniq_all[str(u)] += w
            arm_out["horizon_history_uniqueness_over_all_lawful_starts"] = dict(uniq_all)
        sv.solver.delete()
        # exact history counts, as deep as fits
        counts = {}
        deadline = time.time() + COUNT_SECONDS_PER_ARM
        depth_done = 0
        for depth in range(1, st.horizon + 1):
            hc = B.HistoryCounter(st, arm, depth, cap_states=CAP_STATES, deadline=deadline)
            per = {}
            try:
                for c in distinct:
                    per[c] = hc.count(c)
            except B.Overflow:
                arm_out["counting_stopped_at_depth"] = depth
                arm_out["counting_stop_reason"] = ("state cap" if len(hc.memo) > CAP_STATES
                                                   else "time allowance")
                arm_out["distinct_carried_vectors_finished_at_stop_depth"] = len(per)
                arm_out["memo_states_at_stop"] = len(hc.memo)
                arm_out["max_frontier_knots_at_stop_depth"] = hc.max_frontier
                break
            counts[depth] = per
            depth_done = depth
            arm_out.setdefault("max_frontier_knots_by_depth", {})[depth] = hc.max_frontier
        arm_out["counted_through_depth"] = depth_done
        arm_out["prefix_removal_at_step_2_over_all_step_1_budgets"] = layer_budget_removals(st, arm, 1)
        arm_out["histories_per_start_by_depth"] = {}
        for depth, per in counts.items():
            hs = [per[cvec[v]] for v in vals]
            fac = {c: math.prod(math.factorial(x) * math.factorial(st.loose(u) - x)
                                for u, x in zip(live, c)) for c in distinct}
            arm_out["histories_per_start_by_depth"][str(depth)] = {
                "starts_with_a_history": sum(1 for h in hs if h > 0),
                "value_flow": summarize([h for h in hs if h > 0]),
                "labelled_founder_distinctions": summarize([per[cvec[v]] * fac[cvec[v]] for v in vals
                                                            if per[cvec[v]] > 0])}
            # agreement of the SAT decisions with the counts
            assert all((per[c] > 0) == (alive_depth[c] >= depth) for c in distinct)
        # carried count by stage, over all histories of the drawn starts, to the counted depth
        carried = {}
        if depth_done:
            deadline = time.time() + 40
            hc = B.HistoryCounter(st, arm, depth_done, cap_states=CAP_STATES, deadline=deadline)
            try:
                for stage in range(1, depth_done + 1):
                    pooled = Counter()
                    values = set()
                    for v in vals:
                        by = hc.count_by_carried(cvec[v], stage)
                        for k, m in by.items():
                            pooled[k] += m
                            values.add(k)
                    carried[str(stage)] = {"values_reached": sorted(values),
                                           "histories_by_carried_count": {str(k): str(m) for k, m in sorted(pooled.items())}}
            except B.Overflow:
                carried["stopped"] = True
        c0 = Counter(sum(cvec[v]) for v in vals)
        carried["0"] = {"values_reached": sorted(c0), "starts_by_carried_count": {str(k): m for k, m in sorted(c0.items())}}
        arm_out["carried_count_by_stage"] = carried
        arm_out["seconds"] = round(time.time() - ta, 1)
        result["arms"][arm] = arm_out
        for v in vals:
            c = cvec[v]
            jsonl.append({"arm": arm, "start": v, "carried": c, "alive_depth": alive_depth[c],
                          "unique_to_horizon": uniq[c],
                          "histories_by_depth": {str(d): str(counts[d][c]) for d in counts}})
        print(name, arm, "lawful", n, mode, "survivors", arm_out["survivors_by_step"],
              "counted depth", depth_done, "unique/>=2", arm_out["horizon_history_uniqueness_over_drawn_starts"],
              "t", round(time.time() - t0, 1), flush=True)
    result["seconds"] = round(time.time() - t0, 1)
    (OUT / f"{name}.json").write_text(json.dumps(result, indent=1) + "\n")
    with (OUT / f"{name}_starts.jsonl").open("w") as f:
        for row in jsonl:
            f.write(json.dumps(row) + "\n")
    print("done", result["seconds"])
    return result
