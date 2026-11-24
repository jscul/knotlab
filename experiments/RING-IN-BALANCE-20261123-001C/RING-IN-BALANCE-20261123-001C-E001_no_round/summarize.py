"""Verdict lines for G(b), G(c), P1-P6 and the R items, with the numbers behind each.

Usage: python -B summarize.py   -> prints, and writes summary.json
"""

import json
import os
from collections import Counter, defaultdict
from statistics import mean

from selfcheck import ART

P4_PRIOS = ["UNIFORM", "BY-MEMBERS", "ALL-IN-TURN", "LEAST-TIME"]
ALL_PRIOS = ["ALL-IN-TURN", "UNIFORM", "BY-MEMBERS", "LARGEST", "SMALLEST", "MOST-LOOSE", "LEAST-TIME"]
STARTS1 = ["D2(4,3)", "D2(5,3)", "Ring(5,3)"]


def load(name):
    with open(os.path.join(ART, name)) as f:
        return json.load(f)


def window(r, lo, hi):
    return [x["births_since"] for x in r["returns"] if lo <= x["k"] <= hi]


def ratio_stats(runs):
    """Mean over seeds of each seed's mean over returns 7-12, against the same over returns 2-6; the
    pooled means (over every (seed, return)) are given as well."""
    a = [mean(window(r, 2, 6)) for r in runs if window(r, 2, 6)]
    b = [mean(window(r, 7, 12)) for r in runs if window(r, 7, 12)]
    pa = [v for r in runs for v in window(r, 2, 6)]
    pb = [v for r in runs for v in window(r, 7, 12)]
    out = {"seeds": len(runs), "seeds_with_returns_7_12": len(b),
           "seeds_with_all_12": sum(1 for r in runs if len(r["returns"]) >= 12),
           "mean_2_6": round(mean(a), 2) if a else None, "mean_7_12": round(mean(b), 2) if b else None,
           "pooled_mean_2_6": round(mean(pa), 2) if pa else None, "pooled_mean_7_12": round(mean(pb), 2) if pb else None}
    out["ratio"] = round(out["mean_7_12"] / out["mean_2_6"], 3) if a and b else None
    out["pooled_ratio"] = round(out["pooled_mean_7_12"] / out["pooled_mean_2_6"], 3) if pa and pb else None
    return out


def main():
    S = {}
    lines = []

    def say(s):
        lines.append(s)
        print(s)

    # ------------------------------------------------------------------ gate
    c0 = load("c0_results.json")
    gb = c0["G(b)"]
    tt, lf = gb["results"]["TWO-THREE"], gb["results"]["LONE-FOUR"]
    say(f"G(a): c0_trace.json written; this ticket's part-round ALL-IN-TURN equals its own complete rounds on all "
        f"{len(load('c0_trace.json')['own_complete_round_check'])} start/law pairs through 8 rounds; the comparison with "
        f"ticket A is the coordinator's.")
    say(f"G(b): {'PASS' if gb['pass'] else 'FAIL'} - two three-place knots sharing one distinction: {tt['stopped']} of 40 "
        f"seeds stop, {tt['reached_300']} reach 300 moves, {tt['other']} other; lone four-place knot: {lf['reached_300']} "
        f"of 40 reach 300 moves ({lf['stopped']} stop).")
    gc = c0["G(c)"]
    say(f"G(c): {'PASS' if gc['pass'] else 'FAIL'} - structures: " + "; ".join(
        f"{r['structure']}: renamed {r['renamed_accepted']}/{r['renamed_trials']} accepted, moved "
        f"{r['moved_rejected']}/{r['moved_trials']} rejected" for r in gc["structures"]) +
        " | rosters: " + "; ".join(f"{r['roster']}: renamed {r['renamed_accepted']}/5, changed h rejected "
                                    f"{r['changed_h_rejected']}" for r in gc["rosters"]))
    S["G"] = {"b": gb["pass"], "c": gc["pass"]}

    # ------------------------------------------------------------------ C1
    c1 = load("c1_results.json")["runs"]
    by = defaultdict(list)
    for r in c1:
        by[(r["start"], r["law"], r["priority"])].append(r)

    # P2
    bad = [r for r in c1 if not r["p2"]["same"]]
    Rs = Counter(r["p2"]["R"] for r in c1)
    say(f"P2: {'PASS' if not bad else 'FAIL'} - {len(c1) - len(bad)} of {len(c1)} C1 runs: the knots of own time at most R "
        f"are the same structure as {len(c1)} complete-round references (hash equal and exact isomorphism with "
        f"rounds as colours); R ranges {min(Rs)}..{max(Rs)}; largest comparison "
        f"{max(r['p2'].get('knots_compared', 0) for r in c1)} knots.")
    if bad:
        for r in bad[:5]:
            say(f"    differs: {r['start']} {r['law']} {r['priority']} seed {r['seed']} R {r['p2']['R']} {r['p2']}")
    S["P2"] = {"pass": not bad, "differs": len(bad)}

    # P3
    ends = Counter(r["end"] for r in c1)
    knot_bound = [r for r in c1 if r["end"] == "knots"]
    other = [r for r in c1 if r["end"] not in ("returns", "knots")]
    say(f"P3: {'PASS' if not other else 'FAIL'} - ends {dict(ends)}; the 20,000-knot bound met first in "
        f"{len(knot_bound)} runs: " + ", ".join(f"{k}: {v}" for k, v in sorted(Counter(
            f"{r['start']} {r['law']} {r['priority']}" for r in knot_bound).items())) +
        (f"; returns reached in those runs {sorted(Counter(len(r['returns']) for r in knot_bound).items())}" if knot_bound else ""))
    for r in other[:10]:
        say(f"    stops returning otherwise: {r['start']} {r['law']} {r['priority']} seed {r['seed']} end {r['end']} "
            f"returns {len(r['returns'])} moves {r['moves']} knots {r['knots']}")
    S["P3"] = {"pass": not other, "ends": dict(ends), "knot_bound_runs": len(knot_bound)}

    # P4
    p4 = {}
    ok4 = True
    for prio in P4_PRIOS:
        for st in STARTS1:
            rs = ratio_stats(by[(st, "two", prio)])
            p4[f"{st} {prio}"] = rs
            if rs["ratio"] is None or rs["ratio"] <= 1.5:
                ok4 = False
    say(f"P4: {'PASS' if ok4 else 'FAIL'} - two added rules, ratio of mean births between returns 7-12 to 2-6 "
        f"(must exceed 1.5): " + "; ".join(f"{k} {v['ratio']} ({v['mean_2_6']} -> {v['mean_7_12']}, "
                                           f"{v['seeds_with_all_12']}/{v['seeds']} seeds with 12 returns)" for k, v in p4.items()))
    S["P4"] = {"pass": ok4, "cases": p4}

    # P5
    p5 = {}
    ok5_lit = True
    ok5_alt = True
    for prio in ["LARGEST", "MOST-LOOSE"]:
        for st in STARTS1:
            rs = by[(st, "two", prio)]
            ca = sum(r.get("come_apart_moves", 0) for r in rs)
            counts = sorted({x["births_since"] for r in rs for x in r["returns"]})
            nY = sorted({r["Y0"]["members"] for r in rs})
            nS = rs[0]["n_start"]
            lit = ca == 0 and counts == [4 * nY[0]] and len(nY) == 1
            alt = ca == 0 and counts == [4 * nS]
            ok5_lit &= lit
            ok5_alt &= alt
            p5[f"{st} {prio}"] = {"come_apart_moves": ca, "births_between_returns": counts,
                                  "members_of_part_that_returns": nY, "4n_literal": [4 * x for x in nY],
                                  "4n_start_n": 4 * nS, "literal_ok": lit, "start_n_ok": alt}
    say(f"P5: {'PASS' if ok5_lit else 'FAIL'} under the literal reading (n = members of the part that returns); "
        f"{'PASS' if ok5_alt else 'FAIL'} with n = the start's n - " + "; ".join(
            f"{k}: parts that came apart moved {v['come_apart_moves']} times, births between returns {v['births_between_returns']}, "
            f"part that returns has {v['members_of_part_that_returns']} members (4n = {v['4n_literal']}; start n gives {v['4n_start_n']})"
            for k, v in p5.items()))
    S["P5"] = {"pass_literal": ok5_lit, "pass_start_n": ok5_alt, "cases": p5}

    # P6
    p6 = {}
    ok6 = True
    for prio in ALL_PRIOS:
        for st in STARTS1:
            rs = ratio_stats(by[(st, "three", prio)])
            p6[f"{st} {prio}"] = rs
            if rs["ratio"] is None or rs["ratio"] > 1.2:
                ok6 = False
    worst = max(p6.items(), key=lambda kv: kv[1]["ratio"] or 99)
    say(f"P6: {'PASS' if ok6 else 'FAIL'} - three added rules, ratio 7-12 / 2-6 at most 1.2 on every start and "
        f"priority; largest {worst[0]} {worst[1]['ratio']}; all: " +
        "; ".join(f"{k} {v['ratio']}" for k, v in p6.items()))
    S["P6"] = {"pass": ok6, "cases": p6}

    # R (C1): SMALLEST under both laws
    rr = {}
    for law in ("two", "three"):
        for st in STARTS1:
            rs = by[(st, law, "SMALLEST")]
            rr[f"{st} {law}"] = dict(ratio_stats(rs), ends=dict(Counter(r["end"] for r in rs)),
                                     come_apart_moves_mean=round(mean(r.get("come_apart_moves", 0) for r in rs), 1))
    say("R (SMALLEST, part-round law): " + "; ".join(
        f"{k}: births between returns {v['mean_2_6']} (2-6) -> {v['mean_7_12']} (7-12), ratio {v['ratio']}, ends {v['ends']}"
        for k, v in rr.items()))
    S["R_smallest"] = rr

    # ------------------------------------------------------------------ C2 and C3
    c2 = []
    with open(os.path.join(ART, "c2_runs.jsonl")) as f:
        for line in f:
            c2.append(json.loads(line))
    c3 = load("c3_results.json")
    nn = {"D2(4,3)": 4, "D2(5,3)": 5, "DW(5,3)": 5, "D2(6,3)": 6}
    fails = []
    for r in c2:
        if r["start"] not in nn or r["order"] == "UNIFORM":
            continue
        n = nn[r["start"]]
        j1 = r["jam_first"].get("1")
        g1 = r["made_by_gen"].get("1", {})
        problems = []
        if j1 is None:
            problems.append("no jam at generation 1")
        else:
            if j1["made_O"] != 2 * n or j1["made_J"] != 0:
                problems.append(f"at the jam: {j1['made_O']} offshoots and {j1['made_J']} joins of generation 1 (expected {2 * n} and 0)")
        if g1.get("J", 0):
            problems.append(f"{g1['J']} joins of generation 1 made")
        if problems:
            fails.append((n, r["seed"], r, problems))
    fails.sort(key=lambda x: (x[0], x[1]))
    p1_runs = sum(1 for r in c2 if r["start"] in nn and r["order"] != "UNIFORM")
    jam0 = sum(1 for r in c2 if r["start"] in nn and r["order"] != "UNIFORM" and "0" in r["jam_first"])
    say(f"    (observation: BY-GENERATION runs on these starts that were ever jammed at generation 0: {jam0})")
    p1ok = not fails and c3["registered"]["pass_P1"]
    say(f"P1: {'PASS' if p1ok else 'FAIL'} - {p1_runs - len(fails)} of {p1_runs} BY-GENERATION runs (4 starts x ANY/DEAD x 3 tie "
        f"rules x 100 seeds) jam at generation 1 with exactly 2n offshoots and no join of generation 1, and no join of "
        f"generation 1 is made later in the run; C3: {c3['registered']['distinct_states']} distinct states, "
        f"{c3['registered']['terminal_states']} distinct end, {c3['registered']['orders_total']} orders, all ending in "
        f"{list(c3['registered']['terminal_outcomes'])}.")
    for n, seed, r, pb in fails[:5]:
        say(f"    counterexample: {r['start']} {r['rule']} {r['order']} seed {seed}: {pb}")
    gen1_counts = Counter((r["start"], json.dumps(r["made_by_gen"].get("1", {}), sort_keys=True))
                          for r in c2 if r["start"] in nn and r["order"] != "UNIFORM")
    S["P1"] = {"pass": p1ok, "fails": len(fails), "runs": p1_runs, "c3": c3["registered"],
               "gen1_moves_whole_run": {f"{a} {b}": v for (a, b), v in gen1_counts.items()}}

    # R (C2): UNIFORM, and the rings
    ru = {}
    for r in c2:
        if r["order"] != "UNIFORM":
            continue
        k = f"{r['start']} {r['rule']}"
        d = ru.setdefault(k, {"seeds": 0, "join_gen1": 0, "jam": 0, "jam_gen1": 0, "start_copy": 0,
                              "start_copy_any_reading": 0, "ends": Counter()})
        d["seeds"] += 1
        d["join_gen1"] += bool(r["made_by_gen"].get("1", {}).get("J", 0))
        d["jam"] += bool(r["jam_first"])
        d["jam_gen1"] += "1" in r["jam_first"]
        d["start_copy"] += bool(r["start_copies_n"])
        d["start_copy_any_reading"] += bool(r["start_copies_any_reading_n"])
        d["ends"][r["end"]] += 1
    for d in ru.values():
        d["ends"] = dict(d["ends"])
    say("R (UNIFORM, birth-by-birth law; seeds of 100): " + "; ".join(
        f"{k}: join of generation 1 in {v['join_gen1']}, a jam in {v['jam']} (at generation 1 in {v['jam_gen1']}), copy of the "
        f"start's roster in {v['start_copy']} (start read with ANY: {v['start_copy_any_reading']}), ends {v['ends']}"
        for k, v in ru.items()))
    S["R_uniform_bbb"] = ru
    rings = {}
    for r in c2:
        if not r["start"].startswith("Ring"):
            continue
        k = f"{r['start']} {r['rule']} {r['order']}"
        d = rings.setdefault(k, {"seeds": 0, "ends": Counter(), "first_jam_gen": Counter(), "join_gen1": 0,
                                 "start_copy": 0, "start_copy_any_reading": 0, "moves_mean": []})
        d["seeds"] += 1
        d["ends"][r["end"]] += 1
        fj = min((int(x) for x in r["jam_first"]), default=None)
        d["first_jam_gen"][str(fj)] += 1
        d["join_gen1"] += bool(r["made_by_gen"].get("1", {}).get("J", 0))
        d["start_copy"] += bool(r["start_copies_n"])
        d["start_copy_any_reading"] += bool(r["start_copies_any_reading_n"])
        d["moves_mean"].append(r["moves"])
    for d in rings.values():
        d["ends"] = dict(d["ends"])
        d["first_jam_gen"] = dict(d["first_jam_gen"])
        d["moves_mean"] = round(mean(d["moves_mean"]), 1)
    say("R (rings, birth-by-birth law): " + "; ".join(
        f"{k}: ends {v['ends']}, least jam generation {v['first_jam_gen']}, join of generation 1 in {v['join_gen1']}, "
        f"copy of start's roster {v['start_copy']} (ANY reading {v['start_copy_any_reading']}), mean moves {v['moves_mean']}"
        for k, v in rings.items()))
    S["R_rings_bbb"] = rings
    copies_total = sum(1 for r in c2 if r["start_copies_n"])
    say(f"C2 overall: {len(c2)} runs; runs showing a part the same as the start's roster (run's rule): {copies_total}; "
        f"ends {dict(Counter(r['end'] for r in c2))}.")
    S["C2_ends"] = dict(Counter(r["end"] for r in c2))
    with open(os.path.join(ART, "summary.json"), "w") as f:
        json.dump(S, f, indent=1)
    with open(os.path.join(ART, "summary.txt"), "w") as f:
        f.write("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
