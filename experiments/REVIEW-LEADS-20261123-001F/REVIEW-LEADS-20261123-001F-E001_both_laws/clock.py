"""Structure 1: the five-founder clock with the enrolled receiver, to six returns
(30 parent steps, 155 knots), all three arms (rule, parity alone, not-all-equal
alone).

Counts every whole history exactly (every lawful completion and every allocation
of loose distinctions to children, up to renaming) by dynamic programming over
carried-count states of the five live knots; the abstract ring is checked against
the engine's real births and against the counting engine in gate.py.
"""

import json
import math
import sys
import time
from collections import Counter, defaultdict
from fractions import Fraction
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import both_laws as B

OUT = B.OUT
OUT.mkdir(parents=True, exist_ok=True)
NULL_FILE = B.HERE / "counting_null.md"


def summarize(vals):
    vals = sorted(vals)
    n = len(vals)
    return {"n": n, "min": str(vals[0]), "median": str(vals[n // 2]), "max": str(vals[-1]),
            "distinct": len(set(vals)), "unique_history_starts": sum(1 for v in vals if v == 1)}


def run_arm(arm, five, order, S, live, ring_returns):
    R = B.Ring(arm, 30)
    n, mode, vals, raw = S.draw(arm)
    rows = []
    t0 = time.time()
    for v in vals:
        c = S.carried(v, live)
        cp = tuple(c[live.index(order[p])] for p in range(5))
        by_k = R.future_counts(0, cp)
        total = sum(by_k.values())
        fac = math.prod(math.factorial(x) * math.factorial(2 - x) for x in cp)
        rows.append({"start": v, "carried_by_phase": cp, "C0": sum(cp),
                     "alive_depth": R.alive_depth(cp), "histories": total,
                     "histories_labelled_founders": total * fac,
                     "by_signal_count": {k: by_k[k] for k in sorted(by_k)}})
    # survivors by step
    survivors = [sum(1 for r in rows if r["alive_depth"] >= t) for t in range(31)]
    # carried count by stage over all histories of all drawn starts
    reach = R.reach({r["carried_by_phase"] for r in rows})
    carried_by_stage = [sorted({sum(c) for c in layer}) for layer in reach]
    # universal statement for every state
    universal_alternation = None
    if arm == "rule":
        universal_alternation = all(sum(c2) == 10 - sum(c) for c, tr in R.trans.items()
                                    for (c2, _) in tr)
    # per carried count
    by_c0 = {}
    for r in rows:
        d = by_c0.setdefault(r["C0"], {"starts": 0, "unique": 0, "fraction_sets": Counter(),
                                       "histories_min": None, "histories_max": None,
                                       "pooled": Counter(), "share_sum": defaultdict(Fraction)})
        d["starts"] += 1
        for k, m in r["by_signal_count"].items():
            d["pooled"][k] += m
            d["share_sum"][k] += Fraction(m, r["histories"])
        d["unique"] += int(r["histories"] == 1)
        ks = tuple(k for k, m in r["by_signal_count"].items() if m)
        d["fraction_sets"][ks] += 1
        h = r["histories"]
        d["histories_min"] = h if d["histories_min"] is None else min(d["histories_min"], h)
        d["histories_max"] = h if d["histories_max"] is None else max(d["histories_max"], h)
    sets = Counter(tuple(k for k, m in r["by_signal_count"].items() if m) for r in rows)
    union = sorted({k for r in rows for k, m in r["by_signal_count"].items() if m})
    per_start_min = sorted({min(k for k, m in r["by_signal_count"].items() if m) for r in rows})
    per_start_max = sorted({max(k for k, m in r["by_signal_count"].items() if m) for r in rows})
    single_valued = sum(1 for r in rows if sum(1 for m in r["by_signal_count"].values() if m) == 1)
    verdict = {
        "P1_some_start_without_survivor_at_30": survivors[30] < len(rows),
        "P2_every_surviving_start_has_one_fraction": single_valued == survivors[30] and survivors[30] > 0,
        "P2_starts_with_one_fraction": single_valued,
        "P2_starts_with_several_fractions": len(rows) - single_valued,
        "P3_union_of_fractions_over_all_histories": [f"{k}/6" for k in union],
        "P3_at_most_two_values": len(union) <= 2,
        "P3_alt_values_of_per_start_unique_fraction": sorted(
            {next(k for k, m in r['by_signal_count'].items() if m) for r in rows
             if sum(1 for m in r['by_signal_count'].values() if m) == 1}),
    }
    out = {
        "lawful_valued_starts": n, "selection": mode, "starts_used": len(vals),
        "raw_draws_for_selection": raw, "starts_sha256": B.start_digest(vals),
        "distinct_carried_vectors": len({r["carried_by_phase"] for r in rows}),
        "survivors_by_step": survivors,
        "prefix_removal": {"carried_vectors_in_the_whole_space": len(R.trans),
                           "of_which_with_no_lawful_next_step": sum(1 for c in R.trans if not R.trans[c])},
        "histories_per_start": summarize([r["histories"] for r in rows]),
        "histories_labelled_founders_per_start": summarize([r["histories_labelled_founders"] for r in rows]),
        "carried_count_by_stage_over_all_histories": carried_by_stage,
        "carried_alternates_C0_10_minus_C0_universal": universal_alternation,
        "fraction_sets_per_start": {",".join(f"{k}/6" for k in ks): m for ks, m in sets.items()},
        "by_C0": {str(c): {"starts": d["starts"], "unique_history_starts": d["unique"],
                           "histories_min": str(d["histories_min"]), "histories_max": str(d["histories_max"]),
                           "histories_by_signal_count_pooled_each_whole_history_once":
                               {str(k): str(m) for k, m in sorted(d["pooled"].items())},
                           "mean_share_of_histories_by_signal_count_each_start_once":
                               {str(k): round(float(v / d["starts"]), 6) for k, v in sorted(d["share_sum"].items())},
                           "fraction_sets": {",".join(f"{k}/6" for k in ks): m
                                             for ks, m in sorted(d["fraction_sets"].items())}}
                  for c, d in sorted(by_c0.items())},
        "predictions": verdict,
        "seconds": round(time.time() - t0, 1),
    }
    return out, rows, R


def compare_with_null(rule_rows, R):
    """The hand-derived null of counting_null.md against the run, rule arm."""
    res = {"C0_0_or_10": {"starts": 0, "unique_and_fraction_zero": 0},
           "C0_1_or_9": {"starts": 0, "histories_equal_2^30": 0, "signal_histogram_equals_hand_walk": 0,
                         "all_seven_fractions": 0},
           "C0_2_to_8": {"starts": 0, "at_least_two_histories": 0, "all_seven_fractions": 0}}
    for r in rule_rows:
        c0, cp, byk = r["C0"], r["carried_by_phase"], r["by_signal_count"]
        if c0 in (0, 10):
            d = res["C0_0_or_10"]
            d["starts"] += 1
            d["unique_and_fraction_zero"] += int(r["histories"] == 1 and {k for k, m in byk.items() if m} == {0})
        elif c0 in (1, 9):
            d = res["C0_1_or_9"]
            d["starts"] += 1
            d["histories_equal_2^30"] += int(r["histories"] == 2 ** 30)
            p0 = cp.index(1)
            nul = B.null_single_position(p0)
            d["signal_histogram_equals_hand_walk"] += int({k: m for k, m in byk.items() if m} == dict(nul))
            d["all_seven_fractions"] += int(sorted(k for k, m in byk.items() if m) == list(range(7)))
        else:
            d = res["C0_2_to_8"]
            d["starts"] += 1
            d["at_least_two_histories"] += int(r["histories"] >= 2)
            d["all_seven_fractions"] += int(sorted(k for k, m in byk.items() if m) == list(range(7)))
    return res


def main():
    t0 = time.time()
    five = B.build_structure("five", B.five_source(), 30, 300)
    order, marker, ring, words, returns = B.clock_phases(five)
    assert returns == [5, 10, 15, 20, 25, 30] and five.horizon == 30
    S = B.Starts(five.stars)
    live = [u for u in range(five.n0) if five.loose(u) > 0]
    founders, born = five.arities()
    result = {
        "structure": "five-founder clock, enrolled receiver, six returns",
        "sources": B.source_hashes(),
        "counting_null_sha256": B.sha(NULL_FILE),
        "horizon_parent_steps": five.horizon, "knots_by_step": five.knots_by_step,
        "knots_at_horizon": five.knots_by_step[five.horizon],
        "stalls": five.stalled_at, "both_laws_same_births": five.both_laws_agree,
        "phase_order": order, "returns_at_cuts": returns,
        "arities_met": {"founders": {str(k): v for k, v in sorted(founders.items())},
                        "newborns": {str(k): v for k, v in sorted(born.items())}},
        "allowed_ones_by_arity": {str(n): {arm: [k for k in range(n + 1) if B.lawful(arm, n, k)]
                                           for arm in B.ARMS} for n in sorted(set(founders) | set(born))},
        "arms": {},
    }
    rows_by_arm = {}
    for arm in B.ARMS:
        out, rows, R = run_arm(arm, five, order, S, live, returns)
        result["arms"][arm] = out
        rows_by_arm[arm] = rows
        print(arm, "starts", out["lawful_valued_starts"], out["selection"], "used", out["starts_used"],
              "survivors@30", out["survivors_by_step"][30], "histories", out["histories_per_start"]["min"],
              out["histories_per_start"]["max"], out["predictions"], round(time.time() - t0, 1), flush=True)
        if arm == "rule":
            result["null_comparison_rule_arm"] = compare_with_null(rows, R)
    result["seconds"] = round(time.time() - t0, 1)
    (OUT / "clock.json").write_text(json.dumps(result, indent=1) + "\n")
    with (OUT / "clock_starts.jsonl").open("w") as f:
        for arm, rows in rows_by_arm.items():
            for r in rows:
                f.write(json.dumps({"arm": arm, **{k: (str(v) if k.startswith("histories") else v)
                                                   for k, v in r.items() if k != "by_signal_count"},
                                    "by_signal_count": {str(k): str(m) for k, m in r["by_signal_count"].items()}}) + "\n")
    print("done", result["seconds"])


if __name__ == "__main__":
    main()
