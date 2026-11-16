"""Small synthetic witnesses and split-block CPU traces; no experiment data."""

from itertools import combinations
import json
from random import Random

from oracle_plans import (
    MENUS, PRICES, balanced_folds, build_plan_maps, crossfit_envelope, describe_plans,
    favorable_width_routing, fit_timing_choices, make_plans, materialize_choices,
    same_return_floor, structural_bounds,
)


def synthetic_task(m, outputs):
    groups = list(combinations(range(m), 3))
    pairs = []
    for i, j in combinations(range(m), 2):
        values, masks = [], []
        for base in range(1 << m):
            if base & ((1 << i) | (1 << j)):
                continue
            rows = [base | (((c >> 0) & 1) << i) | (((c >> 1) & 1) << j) for c in range(4)]
            labels = [tuple((t >> row) & 1 for t in outputs) for row in rows]
            valid = [mask for mask in (7, 11, 13, 14)
                     if len({value for c, value in enumerate(labels) if mask & (1 << c)}) == 3]
            if valid:
                values.append(base)
                masks.append(valid)
        if values:
            pairs.append({"test": [i, j, values[0]], "bases": values, "corner_masks": masks,
                          "covers": [g for g, triple in enumerate(groups) if i in triple and j in triple]})
    universe = set().union(*(set(x["covers"]) for x in pairs))
    frontier = []
    for k in range(len(pairs) + 1):
        best, chosen = -1, None
        for subset in combinations(pairs, k):
            coverage = len(set().union(*(set(row["covers"]) for row in subset)))
            if coverage > best:
                best, chosen = coverage, subset
        frontier.append({"k": k, "covered": best, "tests": [d["test"] for d in chosen]})
        if best == len(universe):
            break
    return {"m": m, "available": pairs, "eligible": list(range(len(groups))),
            "width": 2, "min_full": frontier[-1]["k"], "frontier": frontier}


def replay(m, outputs, actions):
    known, covered = set(), set()
    requests = 0
    for action in actions:
        i, j, base = action[:3]
        mask = action[3] if len(action) == 4 else 15
        rows = {base | (((q >> 0) & 1) << i) | (((q >> 1) & 1) << j) for q in range(4) if mask & (1 << q)}
        responses = {tuple((t >> r) & 1 for t in outputs) for r in rows}
        assert len(responses) >= 3
        known.update(rows)
        requests += len(rows)
        covered.update(g for g, t in enumerate(combinations(range(m), 3)) if i in t and j in t)
    return len(known), len(covered), requests


def check_menus():
    rng = Random(194001)
    for m in (4, 5):
        for _ in range(3):
            outputs = tuple(rng.getrandbits(1 << m) for _ in range(2))
            t = synthetic_task(m, outputs)
            all_menus = make_plans(t)
            counts = describe_plans(t, all_menus)
            assert tuple(all_menus) == MENUS and json.loads(json.dumps(all_menus)) == all_menus
            for name, requests in all_menus.items():
                st = counts[name]
                assert replay(m, outputs, requests) == (st["distinct_cited_stage_rows"], st["covered_groups"],
                                                         st["cited_stage_row_requests"])
                assert st["geometry_row_lower_bound"] <= st["distinct_cited_stage_rows"]
            for name, cap in (("one", 1), ("two", 2), ("four", 4)):
                assert counts[name]["covered_groups"] == t["frontier"][min(cap, t["min_full"])]["covered"]
            for name, prices in PRICES.items():
                st = counts[name]
                utility = 4 * st["covered_groups"] - prices[0] * st["requests"] - prices[1] * st["distinct_cited_stage_rows"]
                assert 0 <= utility <= structural_bounds(t, *prices)["max_coverage_proxy_utility_upper"]
            coverage = {"tasks": {"par": {"edit": t}}}
            full = {"parents": {"par": {"edit": all_menus["full"]}}}
            corpus = build_plan_maps(coverage, full)
            assert {n: data["par"]["edit"] for n, data in corpus.items()} == all_menus
            assert favorable_width_routing(coverage, corpus["one"])["par"]["edit"] == all_menus["one"]
            coverage["tasks"]["par"]["edit"] = dict(t, width=1)
            assert favorable_width_routing(coverage, corpus["one"])["par"]["edit"] == []
    empty = synthetic_task(4, (0, 0))
    assert all(not x for x in make_plans(empty).values())


def check_clocks():
    records, totals = [], {}
    for block in range(8):
        totals[block] = {}
        for arm in ("skip", "one", "two", "ordinary"):
            by_edit = []
            for e in ("A", "B", "C"):
                base = 1000 + 8 * block
                delta = {"one": {"A": -50, "B": 25, "C": 8},
                         "two": {"A": 25, "B": -70, "C": 5},
                         "skip": {"A": 0, "B": 0, "C": 0},
                         "ordinary": {"A": -20, "B": -30, "C": -10}}[arm][e]
                records.append(dict(panel="toy", parent="P", edit=e, block=block, arm=arm, cpu_ns=base+delta))
                by_edit.append(base + delta)
            totals[block][arm] = 100 + sum(by_edit)
    arms = ("skip", "one", "two")
    split = balanced_folds(range(8))
    fit = fit_timing_choices(records, split[0][0], arms=arms)
    assert fit["choices"]["P"] == {"A": "one", "B": "two", "C": "skip"}
    result = crossfit_envelope(records, arms=arms, comparators=("skip", "ordinary"), block_totals=totals)
    assert result["wins"] == 8 and result["median_saved_vs_control_ns"] == 60
    for f in result["folds"]:
        assert not set(f["calibration_blocks"]) & set(f["evaluation_blocks"])
        assert f["control"] == "ordinary" and f["choices"] == fit["choices"]
    # Changing only evaluation timings cannot alter a frozen choice.
    changed = [dict(r, cpu_ns=10**6) if r["block"] in split[0][1] and r["arm"] == "one" else r for r in records]
    assert fit_timing_choices(changed, split[0][0], arms=arms) == fit
    maps = {a: {"P": {e: [] if a == "skip" else [[0, 1, 0, 7]] for e in ("A", "B", "C")}} for a in arms}
    materialized = materialize_choices(maps, fit["choices"])
    assert materialized["P"]["C"] == []
    materialized["P"]["A"][0][0] = 99
    assert maps["one"]["P"]["A"][0][0] == 0
    try:
        crossfit_envelope(records[:-1], arms=arms, comparators=("ordinary",))
    except ValueError:
        pass
    else:
        raise AssertionError("incomplete timing matrix accepted")
    child = {"cpu_ns": 1100, "phases": {"solve": 400, "verify": 500},
             "work": {"minimum_selection_cpu_ns": 175},
             "check": {"alternative_checks_cpu_ns": 225, "pair_proof_verification_cpu_ns": 100}}
    floor = same_return_floor(child)
    assert floor["free_selection_and_alternative_checks_ns"] == 700
    assert floor["free_whole_solve_and_alternative_checks_ns"] == 475
    assert floor["remaining_verification_ns"] == 275


if __name__ == "__main__":
    check_menus()
    check_clocks()
    print("Synthetic probe replay, price/row bounds, separate clock folds and retained physical phase checks passed.")
