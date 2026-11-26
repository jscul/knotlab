"""Recount the live-roster comparisons from the recorded member-pair integers.

Run in the repository with .venv/bin/python -B PATH/end_recount.py. A positive
--limit reads that many starts per input file, using the same calculations.
"""

import argparse
import gzip
import itertools
import json
import math
import resource
import time
from collections import Counter, defaultdict
from fractions import Fraction
from pathlib import Path


HERE = Path(__file__).resolve().parent
EPIC = HERE.parent.name
ROOT = HERE.parents[2]
TICKET = f"{EPIC}A"
FAMILY = ROOT / "artifacts" / TICKET / f"{TICKET}-E001_knots_within_reach"
LAWS = ("L0", "L1", "L3", "L6", "L7")
LEVELS = ("i-1", "i-2", "i-3")
KEYS = ("delta", "ws", "hs")
READINGS = ("kappa", "gamma", "rho")


def ratio(n, d):
    return str(Fraction(n, d)) if d else None


def add3(total, current):
    for i, value in enumerate(current):
        total[i] += value


def counts(records):
    """Outcomes in each weighted bin, without independence assumptions."""
    bins = Counter(records)
    rows = list(bins.items())
    total = sum(bins.values())
    concordant = discordant = 0
    for i, ((a, x), left) in enumerate(rows):
        for (b, y), right in rows[:i]:
            product = (a - b) * (x - y)
            if product < 0:
                concordant += left * right
            elif product > 0:
                discordant += left * right
    return [concordant, discordant, math.comb(total, 2) - concordant - discordant]


def grouped(records, key):
    groups = defaultdict(list)
    for record in records:
        groups[record[key]].append(record)
    return groups.values()


def order(groups, reading, key):
    out = [0, 0, 0]
    for group in groups:
        add3(out, counts((p[reading], p[key]) for p in group))
    return out


def unequal_values(pairs, field):
    n = len(pairs)
    return math.comb(n, 2) - sum(math.comb(v, 2) for v in Counter(
        p[field] for p in pairs).values())


def verify(issues, key, condition, identity):
    if not condition:
        row = issues.setdefault(key, {"count": 0, "first": identity})
        row["count"] += 1


def pair_readings(stage, issues, identity):
    z = int(stage["Z"])
    result = []
    for p in stage["pairs"]:
        if "N" not in p:
            continue
        n_disagree = int(p["N"])
        signed = z - 2 * n_disagree
        gamma_z = int(p["gZ"])
        profile = tuple(sorted(zip(p["lam"], p["sig"], strict=True)))
        loose = tuple(sorted(p["lam"]))
        shared = tuple(sorted(p["sig"]))
        scale = math.prod(2 ** q - 1 for q in loose)
        verify(issues, "gamma scaling", signed * scale == gamma_z, identity)
        verify(issues, "joint bound", abs(gamma_z) <= z, identity)
        result.append(dict(p, kappa=abs(signed), signed=signed, gamma=abs(gamma_z),
                           rho=-n_disagree, loose=loose, loose_shared=(loose, shared),
                           profile=profile, same_profile_part=(profile, p["part"]),
                           loose_bound=-scale))
    return result


def stratum(p, past):
    if p["part"] is None:
        return "ii" if past else "vi"
    if isinstance(p["delta"], int):
        return "i"
    return {"never": "iii", "undecided": "iv", "ancestor": "v"}[p["delta"]]


def between(parts, measured):
    lookup = {(p["u"], p["v"]): p for p in measured}
    tested = failing = 0
    for part in parts:
        for u, v, w in itertools.combinations(sorted(part), 3):
            a, b, c = lookup[u, v], lookup[u, w], lookup[v, w]
            for side, first, second in ((a, b, c), (b, a, c), (c, a, b)):
                if side["ws"] == first["ws"] + second["ws"]:
                    tested += 1
                    failing += side["gamma"] > min(first["gamma"], second["gamma"])
    return tested, failing


def record_minima(out, criterion, stage, run, summary, discordance):
    if not discordance:
        return
    size = [stage["knots"], stage["distinctions"], stage["round"]]
    if criterion not in out or size < out[criterion]["size"]:
        out[criterion] = {"size": size, "examples": []}
    if size == out[criterion]["size"]:
        out[criterion]["examples"].append({"start_index": run["index"], "S_all": summary})


def check_shuffle(shuffle, orders, stat, issues, identity):
    for x, row in shuffle.items():
        a, d, _ = orders[x, "delta", "i-1"]
        verify(issues, "shuffle S matches actual pairs", row["S"] == a - d, identity)
        tally = stat["shuffle"][x]
        tally["stages"] += 1
        tally["exact"] += row["exact"]
        tally["positive_variance"] += row["var"] > 0
        tally["permutations"] += row["perms"]
        tally["actual_sum"] += a - d
        tally["saved_mean_sum"] += row["mean"]
        tally["saved_variance_sum"] += row["var"]
        tally["saved_pair_variance_sum"] += float(Fraction(row["pair_shuffle_var"]))


def empty_stat():
    return dict(runs=0, stages=Counter(), strata=Counter(), knot_test=Counter(),
                totals=defaultdict(lambda: [0, 0, 0]), minima={}, eligible=defaultdict(Counter),
                comparison_opportunities=Counter(), counts_as_explanation=Counter(),
                L_W=Counter(), betweenness=Counter(),
                sign_by_ws=defaultdict(Counter), same_part_sign_by_ws=defaultdict(Counter),
                small=Counter(), history_orders=defaultdict(lambda: [0, 0, 0]),
                shuffle=defaultdict(Counter), exact_key_histograms=defaultdict(Counter),
                comparisons_within_parts=defaultdict(lambda: [0, 0, 0]),
                course=Counter(), small_starts_rounds_1_to_3=Counter(),
                stronger_condition=defaultdict(lambda: [0, 0, 0]), issues={})


def process(run, stage, stat, weight, primary_lookup):
    status = stage["status"]
    stat["stages"][status] += 1
    identity = [run["index"], run["law"], stage["round"], run["label"]]
    issues = stat["issues"]
    mcap, scap = run["cap"]
    in_cap = stage["members"] <= mcap and stage["shared"] <= scap
    verify(issues, "cap matches status", in_cap == (status != "not run (stage cap)"), identity)
    if status != "computed":
        return
    measured = pair_readings(stage, issues, identity)
    stratum_counts = Counter(stratum(p, stage["past_its_start"]) for p in stage["pairs"])
    for p in stage["pairs"]:
        verify(issues, "pair labels follow recorded delay and parts",
               p["stratum"] == stratum(p, stage["past_its_start"]), identity)
    verify(issues, "six pair strata agree", all(stratum_counts[k] == n
           for k, n in stage["strata"].items()), identity)
    verify(issues, "all member pairs recorded", sum(stratum_counts.values()) ==
           math.comb(stage["members"], 2), identity)
    stat["strata"].update(stratum_counts)
    pairs = [p for p in measured if p["stratum"] == "i"]
    groups = [[pairs], list(grouped(pairs, "loose")), list(grouped(pairs, "loose_shared"))]
    table = {(x, y, l): order(g, x, y)
             for g, l in zip(groups, LEVELS, strict=True) for x in READINGS for y in KEYS}
    saved = stage["orders"]
    for field, tally in table.items():
        name = "|".join(field)
        add3(stat["totals"][name], tally)
        verify(issues, "recorded order tallies", saved.get(name, [0, 0, 0]) == tally, identity)
    for p in measured:
        sign = "+" if p["signed"] > 0 else "-" if p["signed"] < 0 else "0"
        stat["same_part_sign_by_ws"][p["ws"]][sign] += 1
        if p["stratum"] == "i":
            stat["sign_by_ws"][p["ws"]][sign] += 1
            for key in KEYS:
                stat["exact_key_histograms"][key][p[key]] += 1
            stat["course"]["delta_eq_ws_pairs"] += p["delta"] == p["ws"]
            stat["course"]["decided_pairs"] += 1
    for field in KEYS:
        stat["comparison_opportunities"][f"different_{field}"] += unequal_values(pairs, field)
    for k in ("kappa", "gamma"):
        stat["comparison_opportunities"][f"different_{k}"] += unequal_values(pairs, k)
    stat["comparison_opportunities"]["comparisons"] += math.comb(len(pairs), 2)
    if len(pairs) == 1:
        stat["comparison_opportunities"]["one_pair_stages_excluded_by_saved_sign_table"] += 1
    for x in ("kappa", "gamma"):
        add3(stat["comparisons_within_parts"][x], order(grouped(pairs, "part"), x, "delta"))
    for key in KEYS:
        tally = order(grouped(pairs, "same_profile_part"), "kappa", key)
        name = f"linked_profiles_same_part|{key}"
        add3(stat["stronger_condition"][name], tally)
        all_cmp = table["kappa", key, "i-1"]
        record_minima(stat["minima"], name, stage, run, all_cmp[0]-all_cmp[1], tally[1])
    add3(stat["stronger_condition"]["loose_bound_only|delta"], order([pairs], "loose_bound", "delta"))
    any_disc = table["kappa", "delta", "i-1"][1]
    loose_cmp = table["kappa", "delta", "i-2"]
    shared_cmp = table["kappa", "delta", "i-3"]
    diagnostic = stat["counts_as_explanation"]
    if any_disc and not loose_cmp[1]:
        diagnostic["reversal_only_before_matching_loose_counts"] += 1
        diagnostic["of_these_no_comparison_after_matching_loose_counts"] += not sum(loose_cmp)
        diagnostic["of_these_no_untied_comparison_after_matching_loose_counts"] += not sum(loose_cmp[:2])
    if loose_cmp[1] and not shared_cmp[1]:
        diagnostic["reversal_survives_loose_only"] += 1
        diagnostic["of_these_no_untied_comparison_after_matching_both_counts"] += not sum(shared_cmp[:2])
    for y in KEYS:
        for level in LEVELS:
            a, d, t = table["kappa", y, level]
            e = stat["eligible"][f"{y}|{level}"]
            e["computed_stages"] += 1
            e["all_stage_weight"] += weight
            e["with_comparisons"] += bool(a+d+t)
            e["with_different_strength_and_key"] += bool(a+d)
            e["discordant_stages"] += d > 0
            e["weight_discordant_stages"] += weight * (d > 0)
            source = table["kappa", y, "i-1"]
            record_minima(stat["minima"], f"{y}|{level}", stage, run,
                          source[0]-source[1], d)
    if run["n"] <= 4 and stage["round"] <= 3:
        sub = stat["small_starts_rounds_1_to_3"]
        c, d, t = table["kappa", "delta", "i-1"]
        sub.update(dict(stages=1, pairs=len(pairs), comparisons=c+d+t, concordant=c,
                        discordant=d, tied=t, stages_with_comparisons=bool(c+d+t),
                        stages_with_unequal_delta=bool(unequal_values(pairs, "delta")),
                        unequal_delta=unequal_values(pairs, "delta"),
                        unequal_kappa=unequal_values(pairs, "kappa")))
        for p in pairs:
            sub[f"delay_{p['delta']}"] += 1
    a, d, _ = table["gamma", "ws", "i-1"]
    unequal_ws = unequal_values(pairs, "ws")
    tally = stat["L_W"]
    tally["stages_with_unequal_ws"] += bool(unequal_ws)
    tally["stages_with_both_unequal"] += bool(a+d)
    tally["comparisons_with_unequal_ws"] += unequal_ws
    tally["strict_failures"] += d
    tally["equal_strength_failures"] += unequal_ws - a - d
    tally["failing_stages"] += unequal_ws > a
    tally["strict_failure_stages"] += bool(d)
    saved_lw = stage["LW"]
    verify(issues, "L-W stage tests", saved_lw["tests"] == bool(unequal_ws), identity)
    if unequal_ws:
        verify(issues, "L-W failures", saved_lw["failing_comparisons"] == unequal_ws-a
               and saved_lw["strict_reversals"] == d, identity)
    bt, bf = between(stage["parts"], measured)
    stat["betweenness"].update(dict(tested_triples=bt, failing_triples=bf,
                                   tested_stages=int(bt > 0), failing_stages=int(bf > 0)))
    verify(issues, "betweenness", bt == stage["betweenness"]["tested"] and
           bf == stage["betweenness"]["failing"], identity)
    check_shuffle(stage["shuffle"], table, stat, issues, identity)
    if "small" in stage:
        s = stage["small"]
        small = stat["small"]
        small["checked"] += 1
        small["pairs"] += s["pairs"]
        small["I_bad"] += s["I_bad"]
        small["N_bad"] += s["N_bad"]
        small["Z_bad"] += not s["Z_ok"]
        for p in pairs:
            frac = Fraction(s["history_rho"][f"{p['u']},{p['v']}"])
            p["history"] = abs(1 - 2*frac)
        for l, g in zip(LEVELS, groups, strict=True):
            hist = order(g, "history", "delta")
            add3(stat["history_orders"][l], hist)
            verify(issues, "history-order tallies",
                   hist == s.get("history_orders", {}).get(l, [0,0,0]), identity)
            sd, hd = table["kappa", "delta", l][1], hist[1]
            small[f"history_stages_with_discordance|{l}"] += hd > 0
            small[f"stage_stages_with_discordance|{l}"] += sd > 0
            small[f"history_only_stages|{l}"] += hd > 0 and sd == 0
            small[f"stage_only_stages|{l}"] += sd > 0 and hd == 0
            for gp in g:
                for p, q in itertools.combinations(gp, 2):
                    delta = p["delta"] - q["delta"]
                    hist_dis = (p["history"]-q["history"])*delta > 0
                    stage_dis = (p["kappa"]-q["kappa"])*delta > 0
                    small[f"history_only_comparisons|{l}"] += hist_dis and not stage_dis
                    small[f"stage_only_comparisons|{l}"] += stage_dis and not hist_dis
        small["stages_with_comparisons"] += len(pairs) > 1
    pair_key = (run["law"],run["index"],stage["round"])
    if run["n"] <= 4:
        if run["label"] == "primary":
            primary_lookup[pair_key] = tuple(table["kappa","delta",level] for level in LEVELS)
        elif run["label"] == "swap horizon 10" and pair_key in primary_lookup:
            registered = primary_lookup[pair_key]
            stat["course"]["stages_matching_primary"] += 1
            stat["course"]["one_or_more_levels_changed"] += tuple(table["kappa","delta",l] for l in LEVELS) != registered
            stat["course"]["primary_failure_removed"] += any(
                baseline[1] and not table["kappa","delta",l][1]
                for l,baseline in zip(LEVELS,registered,strict=True))


def run_recount(limit):
    census = json.loads((ROOT/"research"/TICKET/"census_starts.json").read_text())
    stats = defaultdict(empty_stat)
    primary_lookup = {}
    for arm in (*LAWS, "swaps"):
        with gzip.open(FAMILY / f"run5_{arm}.jsonl.gz", "rt") as records:
            for raw in itertools.islice(records, limit):
                row = json.loads(raw)
                stat = stats[f"{row['label']} {row['law']}"]
                stat["runs"] += 1
                for k,v in row.get("knot_test", {}).items():
                    stat["knot_test"][k] += len(v) if k == "fails" else v
                for stage in row["stages"]:
                    process(row, stage, stat, census[row["index"]]["w_labelled"], primary_lookup)
    for stat in stats.values():
        for e in stat["eligible"].values():
            e["discordant_share_all_stages"] = ratio(e["discordant_stages"], e["computed_stages"])
            e["discordant_share_labelled_stages"] = ratio(e["weight_discordant_stages"], e["all_stage_weight"])
            e["discordant_share_eligible_stages"] = ratio(e["discordant_stages"], e["with_different_strength_and_key"])
    return stats


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limit", type=int)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    resource.setrlimit(resource.RLIMIT_AS, (2_300_000_000, 2_300_000_000))
    start = time.monotonic()
    stats = run_recount(args.limit)
    result = {"limit_per_file": args.limit, "counts_in_order": ["concordant", "discordant", "tied"],
              "from": "Raw disagreements N, count Z and between-knots numerator gZ. The same stage has one denominator.",
              "laws": stats, "seconds": time.monotonic()-start,
              "peak_rss_KiB": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}
    if args.limit:
        result["laws"] = {k: dict(runs=v["runs"], stages=v["stages"], issues=v["issues"])
                          for k, v in stats.items()}
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True)+"\n")
