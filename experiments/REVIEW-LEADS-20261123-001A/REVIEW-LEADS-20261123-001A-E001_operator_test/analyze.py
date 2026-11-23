"""Tables and verdicts from the census files.  Reads artifacts/<ticket>/<experiment>/*.jsonl, gates.json, knotside.json and writes
summary.json beside them and the tables to stdout (the draft note research/REVIEW-LEADS-20261123-001A/results_draft.md is made
from this output).

Run from the repo root:  timeout 600 prlimit --as=12884901888 .venv/bin/python -B <this file>
"""
import glob
import json
import math
import statistics
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import lib  # noqa: E402

OUT = lib.OUT
INF = math.inf


def read(pattern):
    rows = []
    for path in sorted(glob.glob(str(OUT / pattern))):
        with open(path) as f:
            rows += [json.loads(l) for l in f]
    return rows


def pct(a, b):
    return f"{a}/{b}" + (f" ({100 * a / b:.1f}%)" if b else "")


def median_two_middle(values):
    v = sorted(values)
    n = len(v)
    return (v[n // 2 - 1] + v[n // 2]) / 2 if n % 2 == 0 else v[n // 2]


def p3_share(starts, mode):
    """The share of qualifying P3 starts whose first failing step is no earlier than the median of its rewirings'.
    mode 'primary': no failure within the horizon is +infinity, median = mean of the two middle values of the eight;
    'lower': the 4th smallest value (lower median); 'censored': no failure is coded horizon+1 (the last stage reached + 1)."""
    qualifying = good = 0
    for s in starts:
        ff = [r["first_failing_step"] for r in s["rewired"]]
        own = s["first_failing_step"]
        if own is None and all(x is None for x in ff):
            continue
        last = s["steps"]
        if mode == "censored":
            code = lambda x: last + 1 if x is None else x  # noqa: E731
        else:
            code = lambda x: INF if x is None else x  # noqa: E731
        vals = sorted(code(x) for x in ff)
        med = vals[3] if mode == "lower" else median_two_middle(vals)
        qualifying += 1
        good += code(own) >= med
    return good, qualifying


def main():
    summary = {}
    md = []
    gates = json.loads((OUT / "gates.json").read_text())
    knotside = json.loads((OUT / "knotside.json").read_text())
    p1 = read("p1_census.jsonl")
    p2 = read("p2_*.jsonl")
    p3 = read("p3_*_arm*_*.jsonl")

    # ------------------------------------------------------------------ gates
    md.append("## Gate row G")
    g = gates
    md.append("| Gate | Result |\n| --- | --- |")
    md.append(f"| G1: 173 recorded simple sharing patterns, fail verdict equals recorded admit verdict | "
              f"{g['G1']['patterns']} patterns, {g['G1']['recorded_admit']} admit; every verdict equal: {g['G1']['fail_equals_admit_everywhere']} |")
    c = g["G2"]["checked"]
    md.append(f"| G2: planarity routine against brute-force minor search (K5 or K3,3 minor), patterns of at most six knots | "
              f"{c['census_at_most_six_knots']} recorded patterns of at most six knots, {c['atlas_simple_graphs_up_to_six_knots']} simple graphs on 1 to 6 knots, "
              f"plus (beyond the requirement) {c['census_seven_knots']} recorded seven-knot patterns, {c['atlas_simple_graphs_seven_knots']} simple graphs on 7 knots, "
              f"{c['hypergraph_incidence']} small incidence patterns with a distinction of three or more holders; disagreements: {len(g['G2']['disagreements'])} |")
    m3 = g["G3"]
    md.append(f"| G3: mutant unlinking the second holder of every shared distinction | passes {m3['recorded_patterns']['mutant_passes']}/{m3['recorded_patterns']['of']} recorded patterns "
              f"({m3['recorded_patterns']['real_fail']} of them fail unmutated), {m3['engine_stages']['mutant_passes']}/{m3['engine_stages']['of']} engine stages "
              f"({m3['engine_stages']['real_fail']} fail unmutated), every benchmark construction with at most two holders per distinction; "
              f"literal mutant passes the bounded-bond windows 1: {m3['benchmark']['bounded_bond:1']['mutant_passes']}, 2: {m3['benchmark']['bounded_bond:2']['mutant_passes']}, "
              f"3: {m3['benchmark']['bounded_bond:3']['mutant_passes']}, 4: {m3['benchmark']['bounded_bond:4']['mutant_passes']} (distinctions of up to six holders) |")
    k2 = g["G4_first_two"]
    md.append("| G4: knot-side check, five structures | " + "; ".join(
        f"{n}: {v['knots']} knots, {v['distinctions']} distinctions, {v['answer_words']} answer words, agree {v['agree']}"
        for n, v in k2.items() if n != "pass") + "; " + "; ".join(
        f"P3 part {i + 1} (arm {s['arm']}, draw {s['draw']}, stage {s['t']}): {s['knots']} knots, {s['distinctions']} distinctions, {s['answer_words']} answer words, agree {s['agree']}"
        for i, s in enumerate(knotside["structures"])) + " |")
    md.append(f"| Supporting: Euler shortcut equals networkx on | {g['S2_census']['patterns']} recorded patterns, {g['S2_p1']['patterns']} benchmark patterns, {g['S2_stages']['stages']} engine stages (disagreements {g['S2_census']['euler_shortcut_disagreements'] + g['S2_p1']['disagreements'] + g['S2_stages']['disagreements']}) |")
    md.append(f"| Supporting: growth driver equals the other recorded engine (naelib) on counts per parent step | {g['S3']['same']}/{g['S3']['compared']} |")
    md.append(f"| Supporting: archived starts 00, 04, 13 reproduce recorded supports and birth counts | {all(g['S1'][n]['supports_equal_recorded_literal_supports'] and g['S1'][n]['counts_equal'] for n in ('start-00', 'start-04', 'start-13'))} |")
    summary["gates"] = {"G1": g["G1"]["pass"], "G2": g["G2"]["pass"], "G3_two_holder": g["G3"]["pass"],
                        "G3_literal_all_patterns": g["G3"]["literal_mutant_passes_every_pattern_including_bounded_bond"],
                        "G4": k2["pass"] and knotside["pass"]}

    # ------------------------------------------------------------------ P1
    md.append("\n## P1: shape benchmark")
    md.append("| Construction | Depth or window | Knots | Distinctions | Loop rank | T | Lower bound | Upper bound at first failure | Most holders of a distinction |\n| --- | ---: | ---: | ---: | ---: | --- | ---: | --- | ---: |")
    for r in p1:
        if r["kind"] != "stage":
            continue
        ub = r.get("upper_bound")
        note = r.get("upper_bound_note")
        shown = "" if r["T"] == "pass" else (ub if "upper_bound" in r and ub is not None else
                                            ("only computed at the first failing stage" if "upper_bound" not in r else "not computed: " + str(note)))
        md.append(f"| {r['construction']} | {r['depth']} | {r['knots']} | {r['distinctions']} | {r['loop_rank']} | {r['T']} | {r['lower_bound']} | "
                  f"{shown} | {r['max_holders_of_a_distinction']} |")
    cons = {r["construction"]: r for r in p1 if r["kind"] == "construction"}
    v = {k: {int(d): t for d, t in c["verdicts"].items()} for k, c in cons.items()}
    p1_checks = {
        "cubic passes to depth 3 and fails from depth 4": all(v["cubic"][d] == "pass" for d in (0, 1, 2, 3)) and all(t == "fail" for d, t in v["cubic"].items() if d >= 4) and cons["cubic"]["first_failing_depth"] == 4,
        "pinwheel passes at every depth": all(t == "pass" for t in v["pinwheel"].values()) and sorted(v["pinwheel"]) == [1, 2, 3, 4, 5],
        "polygonal control passes at every depth": all(t == "pass" for t in v["periodic"].values()) and sorted(v["periodic"]) == list(range(1, 9)),
        "bounded-bond fails from window 2": v["bounded_bond"][1] == "pass" and all(v["bounded_bond"][w] == "fail" for w in (2, 3, 4)),
    }
    md.append("\nP1 verdicts: " + "; ".join(f"{k}: **{'holds' if ok else 'DIFFERS'}**" for k, ok in p1_checks.items()))
    summary["P1"] = {"checks": p1_checks, "depths_reached": {k: c["depths_reached"] for k, c in cons.items()}}

    # ------------------------------------------------------------------ stage rows
    stages = {"P1": [], "P2": [], "P3": []}
    for r in p1:
        if r["kind"] == "stage":
            stages["P1"].append(dict(r, law="-", source=r["construction"], t=r["depth"]))
    for r in p2:
        if r["kind"] == "stage":
            stages["P2"].append(r)
    for r in p3:
        if r["kind"] == "stage":
            stages["P3"].append(dict(r, source="P3"))
    histories = {"P2": [r for r in p2 if r["kind"] == "history"], "P3": [r for r in p3 if r["kind"] == "history"]}
    summary["counts"] = {"P2_histories": len(histories["P2"]), "P3_histories": len(histories["P3"]),
                         "stage_rows": {k: len(x) for k, x in stages.items()}}

    # ------------------------------------------------------------------ settled by construction (checked here)
    low_rank_fail = sum(1 for pop in stages.values() for r in pop if r["loop_rank"] < 4 and r["T"] == "fail")
    low_rank_total = sum(1 for pop in stages.values() for r in pop if r["loop_rank"] < 4)
    monotone_bad = sum(1 for h in histories["P3"] if h.get("monotone_violation"))
    for h in histories["P2"]:
        rows = sorted((r for r in stages["P2"] if r["source"] == h["source"] and r["law"] == h["law"]), key=lambda r: r["t"])
        monotone_bad += any(a["T"] == "fail" and b["T"] == "pass" for a, b in zip(rows, rows[1:]))
    one_only = [h for pop in histories.values() for h in pop if h["births"] and h["one_parent_births"] == h["births"]]
    summary["settled_by_construction"] = {"stages_with_loop_rank_below_4": low_rank_total, "of_which_failing": low_rank_fail,
                                          "histories_with_a_failure_followed_by_a_pass": monotone_bad,
                                          "histories_with_only_one_parent_births": len(one_only),
                                          "of_which_fail": sum(1 for h in one_only if h["first_failing_step"] is not None)}
    md.append("\n## Settled by construction, checked on the data")
    md.append(f"Stages with loop rank below 4: {low_rank_total}, failing: {low_rank_fail}. Histories in which a failing stage is followed by a passing one: {monotone_bad}. "
              f"Histories whose births are all one-parent: {len(one_only)}, of which fail: {summary['settled_by_construction']['of_which_fail']}.")

    # ------------------------------------------------------------------ P2 (loop rank)
    md.append("\n## P2: T against loop rank")
    by_rank = defaultdict(lambda: {"pass": 0, "fail": 0})
    example = {}
    for pop, rows in stages.items():
        for r in rows:
            by_rank[r["loop_rank"]][r["T"]] += 1
            example.setdefault((r["loop_rank"], r["T"]), (pop, r["source"], r.get("draw"), r.get("arm"), r["law"], r["t"], r["knots"]))
    mixed = sorted(k for k, c in by_rank.items() if c["pass"] and c["fail"])
    mixed_within = {}
    for pop, rows in stages.items():
        br = defaultdict(set)
        for r in rows:
            br[r["loop_rank"]].add(r["T"])
        mixed_within[pop] = sorted(k for k, v in br.items() if len(v) == 2)
    md.append("Loop ranks with both a passing and a failing reached stage, within one population: " + "; ".join(f"{p}: {len(v)} ranks" + (f" (least {v[0]})" if v else "") for p, v in mixed_within.items()) + ".")
    md.append(f"Loop ranks that have at least one passing and at least one failing reached stage: {len(mixed)} of {len(by_rank)} ranks seen; least: {mixed[0] if mixed else None}; "
              f"first example pair at rank {mixed[0] if mixed else None}: pass {example.get((mixed[0], 'pass')) if mixed else None}, fail {example.get((mixed[0], 'fail')) if mixed else None}.")
    ranks_pop = {}
    md.append("\n| Population | Law | Reached stages | Failing stages | Least loop rank of a failing stage | Smallest failing stage (knots, distinctions, loop rank; where) |\n| --- | --- | ---: | ---: | ---: | --- |")
    for pop in ("P1", "P2", "P3"):
        for law in (("-",) if pop == "P1" else lib.LAWS):
            rows = [r for r in stages[pop] if r["law"] == law]
            fails = [r for r in rows if r["T"] == "fail"]
            if fails:
                least = min(r["loop_rank"] for r in fails)
                small = min(fails, key=lambda r: (r["knots"], r["distinctions"], r["loop_rank"]))
                where = f"{small['source']} t={small['t']}" + (f" arm {small['arm']} draw {small['draw']}" if pop == "P3" else "")
                small_txt = f"{small['knots']}, {small['distinctions']}, {small['loop_rank']}; {where}"
            else:
                least, small_txt = None, "none"
            ranks_pop[f"{pop}/{law}"] = least
            md.append(f"| {pop} | {law} | {len(rows)} | {len(fails)} | {least} | {small_txt} |")
    summary["P2_loop_rank"] = {"mixed_ranks": mixed, "least_failing_rank": ranks_pop,
                               "prediction_holds": bool(mixed)}
    md.append("\nPass/fail counts by loop rank, P3 stages, both laws pooled (ranks seen in P3; every stage is a row, so a start counts once per stage):")
    p3rank = defaultdict(lambda: [0, 0])
    for r in stages["P3"]:
        p3rank[r["loop_rank"]][r["T"] == "fail"] += 1
    md.append("| Loop rank | Passing stages | Failing stages |\n| ---: | ---: | ---: |")
    for k in sorted(p3rank)[:16]:
        md.append(f"| {k} | {p3rank[k][0]} | {p3rank[k][1]} |")
    if len(p3rank) > 16:
        md.append(f"| (ranks above {sorted(p3rank)[15]}) | {sum(p3rank[k][0] for k in sorted(p3rank)[16:])} | {sum(p3rank[k][1] for k in sorted(p3rank)[16:])} |")

    # ------------------------------------------------------------------ growth kind and T, bounded starts
    md.append("\n## Growth kind against the test (starts; fails = some stage within the horizon fails T)")
    md.append("| Population | Law | Growth kind | Starts | Fail within horizon | Pass throughout | Median share of one-parent births (starts with births) |\n| --- | --- | --- | ---: | ---: | ---: | --- |")
    cross = {}
    for pop in ("P2", "P3"):
        for law in lib.LAWS:
            hs = [h for h in histories[pop] if h["law"] == law]
            for kind in ("stalled", "bounded", "growing"):
                sel = [h for h in hs if h["growth_kind"] == kind]
                fail = sum(1 for h in sel if h["first_failing_step"] is not None)
                shares = [h["one_parent_share"] for h in sel if h["one_parent_share"] is not None]
                cross[f"{pop}/{law}/{kind}"] = [len(sel), fail]
                md.append(f"| {pop} | {law} | {kind} | {len(sel)} | {fail} | {len(sel) - fail} | {statistics.median(shares):.3f} |" if shares else
                          f"| {pop} | {law} | {kind} | {len(sel)} | {fail} | {len(sel) - fail} | n/a |")
    summary["cross_table"] = cross
    for pop in ("P2", "P3"):
        for law in lib.LAWS:
            st = Counter(h["outcome"] for h in histories[pop] if h["law"] == law and h["growth_kind"] == "stalled")
            md.append(f"Stalled kind, {pop}/{law}: by outcome {dict(st)} (outcome closed with no births = no live knot at the source).")
    bounded_fail = [(h["population"], h["law"], h["source"] if "source" in h else (h["arm"], h["draw"]), h["first_failing_step"])
                    for pop in histories.values() for h in pop if h["growth_kind"] == "bounded" and h["first_failing_step"] is not None]
    bounded_total = sum(1 for pop in histories.values() for h in pop if h["growth_kind"] == "bounded")
    summary["bounded_that_fail"] = {"bounded_histories": bounded_total, "failing": len(bounded_fail), "examples": bounded_fail[:10]}
    md.append(f"\nStarts of bounded kind that fail within the horizon: {len(bounded_fail)} of {bounded_total} bounded histories (P2 and P3, both laws): {bounded_fail[:10]}.")
    out_counts = Counter((h["population"], h["law"], h["outcome"]) for pop in histories.values() for h in pop)
    md.append("\nOutcomes of the histories (horizon = alive after the horizon; closed = a closing birth or no live knot; stall; cap = the next step would exceed the knot cap; time = wall-clock budget): "
              + "; ".join(f"{k[0]}/{k[1]}/{k[2]}: {v}" for k, v in sorted(out_counts.items())))

    # ------------------------------------------------------------------ P2 history table
    md.append("\n## P2 histories (recorded sources)")
    md.append("| Source | Law | Outcome | Knots at each stage | Growth kind | One-parent births / births | First failing step | Lower / upper removal bound at it |\n| --- | --- | --- | --- | --- | --- | ---: | --- |")
    for h in histories["P2"]:
        md.append(f"| {h['source']} | {h['law']}{' (history shared with parity)' if h['history_shared_with_parity'] else ''} | {h['outcome']} | {h['n_at']} | {h['growth_kind']} | {h['one_parent_births']}/{h['births']} | "
                  f"{h['first_failing_step']} | {h.get('lower_bound_at_first_failing_stage')} / {h.get('upper_bound_at_first_failing_stage')} ({h.get('upper_bound_note')}) |")

    # ------------------------------------------------------------------ removal bounds in P3
    md.append("\n## Removal bounds at the first failing stage (P3 starts that fail)")
    fails3 = [h for h in histories["P3"] if h["first_failing_step"] is not None]
    comp = Counter()
    for h in fails3:
        lo, up = h["lower_bound_at_first_failing_stage"], h["upper_bound_at_first_failing_stage"]
        comp["upper not computed" if up is None else ("lower<=upper" if lo <= up else "lower>upper")] += 1
        if up is not None:
            comp["lower==upper" if lo == up else "lower<upper"] += (lo <= up)
    ups = [h["upper_bound_at_first_failing_stage"] for h in fails3 if h["upper_bound_at_first_failing_stage"] is not None]
    los = [h["lower_bound_at_first_failing_stage"] for h in fails3]
    md.append(f"{len(fails3)} failing P3 histories; upper bound computed for {len(ups)} (min {min(ups) if ups else None}, median {statistics.median(ups) if ups else None}, max {max(ups) if ups else None}); "
              f"lower bound min {min(los) if los else None}, max {max(los) if los else None}; comparison {dict(comp)}. First failing step distribution: "
              + str(dict(sorted(Counter(h['first_failing_step'] for h in fails3).items()))))
    summary["removal_bounds_P3"] = {"failing": len(fails3), "comparison": dict(comp), "upper_min": min(ups) if ups else None,
                                   "upper_max": max(ups) if ups else None}

    # ------------------------------------------------------------------ P3
    md.append("\n## P3: ordinary growth against its rewiring")
    md.append("| Law | Arm (extra meetings) | Starts | Funded (at least one step) | Start or a rewiring fails | First failing step of the start no earlier than the median of its rewirings' | Fail within horizon: start | Fail: at least one rewiring |\n| --- | --- | ---: | ---: | ---: | --- | ---: | ---: |")
    p3rows = {}
    allgood = allq = 0
    for law in lib.LAWS + ("both",):
        for arm in (0, 1, 2, 3, "all"):
            hs = [h for h in histories["P3"] if (law == "both" or h["law"] == law) and (arm == "all" or h["arm"] == arm)]
            good, q = p3_share(hs, "primary")
            funded = sum(1 for h in hs if h["steps"] >= 1)
            own = sum(1 for h in hs if h["first_failing_step"] is not None)
            anyrw = sum(1 for h in hs if any(r["first_failing_step"] is not None for r in h["rewired"]))
            p3rows[f"{law}/{arm}"] = [good, q]
            md.append(f"| {law} | {arm} | {len(hs)} | {funded} | {q} | {pct(good, q)} | {own} | {anyrw} |")
    both = p3rows["both/all"]
    share = both[0] / both[1] if both[1] else None
    lower = p3_share(histories["P3"], "lower")
    cens = p3_share(histories["P3"], "censored")
    md.append(f"\nPrimary reading (no failure = +infinity; median = mean of the 4th and 5th smallest of eight): {pct(*both)}; lower median: {pct(*lower)}; no failure coded last stage + 1: {pct(*cens)}. Prediction P3 holds when the share is at least 3/4.")
    summary["P3"] = {"primary": both, "share": share, "lower_median": list(lower), "censored_code": list(cens), "by_cell": p3rows,
                     "holds": bool(share is not None and share >= 0.75)}
    # direction of the disagreements
    earlier = Counter()
    for h in histories["P3"]:
        ff = [r["first_failing_step"] for r in h["rewired"]]
        own = h["first_failing_step"]
        if own is None and all(x is None for x in ff):
            continue
        vals = sorted(INF if x is None else x for x in ff)
        med = median_two_middle(vals)
        o = INF if own is None else own
        earlier["start later than median" if o > med else ("equal" if o == med else "start earlier than median")] += 1
    md.append(f"Starts compared with the median of their rewirings (primary reading): {dict(earlier)}.")
    cats = Counter()
    medians = Counter()
    exceptions = []
    for h in histories["P3"]:
        ff = [r["first_failing_step"] for r in h["rewired"]]
        own = h["first_failing_step"]
        if own is None and all(x is None for x in ff):
            continue
        vals = sorted(INF if x is None else x for x in ff)
        med = median_two_middle(vals)
        nfail = sum(x is not None for x in ff)
        key = ("start passes" if own is None else "start fails") + f"; {nfail} of 8 rewirings fail"
        cats[key] += 1
        medians[("inf" if med == INF else med)] += 1
        if (INF if own is None else own) < med:
            exceptions.append({"law": h["law"], "arm": h["arm"], "draw": h["draw"], "start_first_failing_step": own,
                               "rewirings_first_failing_step": ff, "steps": h["steps"], "n_at": h["n_at"]})
    md.append("\nQualifying starts by whether the start passes and how many of its eight rewirings fail (within the horizon): " + str(dict(sorted(cats.items()))))
    md.append("Median first failing step of the rewirings (inf = at least five of eight rewirings pass throughout): " + str(dict(sorted(medians.items(), key=str))))
    md.append("Starts whose first failing step is earlier than the rewiring median (the exceptions to P3): " + json.dumps(exceptions))
    summary["P3"]["exceptions"] = exceptions
    summary["P3"]["qualifying_categories"] = dict(cats)
    short = [(r["shortfall"], r["births_with_shortfall"]) for h in histories["P3"] for r in h["rewired"] if h["steps"] >= 1]
    md.append(f"Rewirings of funded starts: {len(short)}; with any shortfall: {sum(1 for s in short if s[0])}; total parents missing: {sum(s[0] for s in short)}; births with a shortfall: {sum(s[1] for s in short)}.")
    summary["P3"]["rewirings_of_funded"] = len(short)
    summary["P3"]["rewirings_with_shortfall"] = sum(1 for s in short if s[0])
    summary["P3"]["earlier_than_median"] = dict(earlier)
    # funded fractions
    md.append("\nFirst step funded (starts with at least one parent step): " + "; ".join(
        f"{law} arm {arm}: {sum(1 for h in histories['P3'] if h['law'] == law and h['arm'] == arm and h['steps'] >= 1)}/256" for law in lib.LAWS for arm in range(4)))

    # ------------------------------------------------------------------ P4
    md.append("\n## P4: closed parity parts met")
    parts = [r for r in p2 + p3 if r["kind"] == "closed_part" and r["law"] == "parity"]
    checked = [r for r in parts if r["admits"] is not None]
    disagree = [r for r in checked if (r["T"] == "fail") != bool(r["admits"])]
    md.append(f"Closed parity parts met (P2 and P3, parity law): {len(parts)}; checked by the independent signed-operator solver: {len(checked)}; not checked: {len(parts) - len(checked)} "
              f"({Counter(r['admits_note'] for r in parts if r['admits'] is None)}); admits and fails T: {sum(1 for r in checked if r['admits'] and r['T'] == 'fail')}; "
              f"neither: {sum(1 for r in checked if not r['admits'] and r['T'] == 'pass')}; disagreements: {len(disagree)}.")
    by_pop = Counter((r["population"], r["T"], r["admits"]) for r in parts)
    md.append("Breakdown (population, T, admits): " + "; ".join(f"{k}: {v}" for k, v in sorted(by_pop.items(), key=str)))
    summary["P4"] = {"closed_parts": len(parts), "checked": len(checked), "disagreements": len(disagree),
                     "holds": not disagree and len(checked) == len(parts),
                     "admit_and_fail": sum(1 for r in checked if r["admits"] and r["T"] == "fail")}
    if disagree:
        md.append("Disagreements: " + json.dumps([{k: r[k] for k in ("population", "arm", "draw", "source", "t", "knots", "distinctions") if k in r} for r in disagree][:10]))
    sizes = Counter((r["knots"], r["distinctions"]) for r in parts)
    md.append("Closed parts by (knots, distinctions): " + str(dict(sorted(sizes.items()))))

    (OUT / "summary.json").write_text(json.dumps(summary, indent=1, sort_keys=True, default=str) + "\n")
    print("\n".join(md))


if __name__ == "__main__":
    main()
