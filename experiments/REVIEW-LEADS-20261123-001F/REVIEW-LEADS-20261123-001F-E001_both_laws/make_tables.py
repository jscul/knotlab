"""Print the tables of the draft result note from the four result files."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import both_laws as B

A = B.OUT


def sci(x):
    x = int(x)
    if x < 10 ** 7:
        return f"{x:,}"
    s = f"{x:.3e}"
    mant, exp = s.split("e")
    return f"{mant}e{int(exp)}"


def main():
    g = json.load(open(A / "gate.json"))
    c = json.load(open(A / "clock.json"))
    lines = []
    w = lines.append
    w("## Gate row G")
    w("")
    w("| Part | Result |")
    w("| --- | --- |")
    for r in g["G1"]["rows"]:
        if r["arm"] == "rule" and r["places"] in (3, 4):
            w(f"| G1 rule, {r['places']} places | K1 {r['K1']}, K2 {r['K2']}, K3 {r['K3']}, knot {r['is_knot']} "
              f"(command line agrees) |")
    for r in g["G1"]["rows"]:
        if r["arm"] != "rule" and r["places"] in (3, 4):
            w(f"| G1 control {r['arm']}, {r['places']} places | K1 {r['K1']}, K2 {r['K2']}, K3 {r['K3']}, knot {r['is_knot']} |")
    for arm, d in g["G23"]["G2"].items():
        w(f"| G2 {arm} alone from the quiet start | {d['patterns_of_six']} of 64 six-bit patterns, "
          f"signal counts {d['signal_counts']} |")
    d = g["G23"]["G3"]
    w(f"| G3 rule from the quiet start | histories {d['histories']}, patterns {d['patterns']}, "
      f"carried count by stage {[x for x in d['carried_count_by_stage'][:4]]}..., engine count at depth 4 {d['engine_count_depth4']} |")
    w("")
    w("## Five-founder clock, all arms")
    w("")
    w("| Arm | lawful valued starts | used | survivors at step 0 / 30 | histories per start: min / median / max | starts with exactly one history | signal fractions over the histories of a start |")
    w("| --- | --- | --- | --- | --- | --- | --- |")
    for arm, a in c["arms"].items():
        h = a["histories_per_start"]
        fs = "; ".join(f"{m} starts: {k}" for k, m in a["fraction_sets_per_start"].items())
        w(f"| {arm} | {a['lawful_valued_starts']:,} | {a['starts_used']:,} ({a['selection']}) | "
          f"{a['survivors_by_step'][0]:,} / {a['survivors_by_step'][30]:,} | "
          f"{sci(h['min'])} / {sci(h['median'])} / {sci(h['max'])} | {h['unique_history_starts']} | {fs} |")
    w("")
    w("## Clock, rule arm, by carried count of the start, with the hand null")
    w("")
    w("| C0 | starts | with one history | histories min .. max | fractions with a history | mean share of a start's histories at signal count 0,1,...,6 |")
    w("| --- | --- | --- | --- | --- | --- |")
    for k, d in c["arms"]["rule"]["by_C0"].items():
        shares = d["mean_share_of_histories_by_signal_count_each_start_once"]
        sh = ", ".join(f"{shares.get(str(i), 0):.4f}" for i in range(7))
        fr = "; ".join(f"{m}: {s}" for s, m in d["fraction_sets"].items())
        w(f"| {k} | {d['starts']} | {d['unique_history_starts']} | {sci(d['histories_min'])} .. {sci(d['histories_max'])} | {fr} | {sh} |")
    w("")
    nc = c["null_comparison_rule_arm"]
    w(f"Hand null against the run: {json.dumps(nc)}")
    w("")
    w("## Carried count by stage on the clock")
    w("")
    for arm, a in c["arms"].items():
        cs = a["carried_count_by_stage_over_all_histories"]
        w(f"- {arm}: stage 0 {cs[0]}; stage 1 {cs[1]}; stage 2 {cs[2]}; stage 29 {cs[29]}; stage 30 {cs[30]}; "
          f"universal alternation C0, 10-C0 (rule): {a['carried_alternates_C0_10_minus_C0_universal']}; "
          f"carried vectors with no lawful next step: {a['prefix_removal']['of_which_with_no_lawful_next_step']} of "
          f"{a['prefix_removal']['carried_vectors_in_the_whole_space']}")
    w("")
    for name in ("seven", "nine"):
        s = json.load(open(A / f"{name}.json"))
        w(f"## {name}-knot source")
        w("")
        w(f"{s['founders']} founders, {s['distinctions']} distinctions ({s['shared_distinctions']} shared), "
          f"loose per founder {s['loose_per_founder']}, founder arities {s['founder_arities']}; horizon "
          f"{s['horizon_parent_steps']} parent steps; knots by step {s['knots_by_step_through_first_step_over_cap']}; "
          f"stalls {s['stalls_through_horizon']}; both laws give the same births {s['both_laws_give_same_births']}.")
        w("")
        w(f"Arities met: founders {s['arities_met']['founders']}, newborns {s['arities_met']['newborns']}.")
        w("")
        w("| Arm | lawful valued starts | used | survivors by step (drawn) | lawful starts with no survivor at the horizon | to the horizon: no history / one / two or more (drawn) | counted through | histories per start at the deepest counted step: min / median / max |")
        w("| --- | --- | --- | --- | --- | --- | --- | --- |")
        for arm, a in s["arms"].items():
            d = a["counted_through_depth"]
            h = a["histories_per_start_by_depth"][str(d)]["value_flow"]
            u = a["horizon_history_uniqueness_over_drawn_starts"]
            w(f"| {arm} | {a['lawful_valued_starts']:,} | {a['starts_used']:,} | {a['survivors_by_step']} | "
              f"{a['lawful_starts_without_survivor_at_horizon']} | {u['no_history']} / {u['exactly_one_history']} / {u['at_least_two_histories']} | "
              f"{d} | {sci(h['min'])} / {sci(h['median'])} / {sci(h['max'])} |")
        w("")
        for arm, a in s["arms"].items():
            w(f"- {arm}: all lawful starts surviving by step {a['all_lawful_starts_surviving_by_step']}; "
              f"uniqueness over all lawful starts {a.get('horizon_history_uniqueness_over_all_lawful_starts')}; "
              f"prefix removal at step 2 {a['prefix_removal_at_step_2_over_all_step_1_budgets']}; "
              f"counting stopped at depth {a.get('counting_stopped_at_depth')} ({a.get('counting_stop_reason')}), "
              f"distinct vectors finished {a.get('distinct_carried_vectors_finished_at_stop_depth')} of "
              f"{a['distinct_carried_vectors_among_starts']}; carried count values reached by stage "
              f"{ {k: (v['values_reached'][0], v['values_reached'][-1]) for k, v in a['carried_count_by_stage'].items() if 'values_reached' in v} }")
        w("")
    text = "\n".join(lines) + "\n"
    (A / "tables.md").write_text(text)
    print(text)


if __name__ == "__main__":
    main()
