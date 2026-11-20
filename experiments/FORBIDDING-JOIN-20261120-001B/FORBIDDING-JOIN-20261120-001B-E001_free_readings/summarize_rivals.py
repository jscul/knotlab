"""Summaries preserve each law, rule, reference stage and reader denominator."""

from collections import Counter, defaultdict
from fractions import Fraction


def ratio(value):
    return None if value is None else [value.numerator, value.denominator]


def span(values):
    return [ratio(min(values, default=None)), ratio(max(values, default=None))]


def update_scores(scores, source, law, arm, stage, family, slot):
    placement = slot["placement"]
    keys = [(law, arm, stage["age"], family, basis, weighting, protocol)
            for basis in ("reader_only", "all_supports_lawful")
            if basis == "reader_only" or stage["every_displayed_support_lawful"]
            for weighting in ("U", "L", "T", "L_survival") for protocol in ("I", "II")]
    for key in keys:
        _, _, _, _, _, weighting, protocol = key
        row = scores[key]
        if placement is None:
            row["absent_placement"] += 1
            continue
        mass = slot["result"]["weightings"].get(weighting)
        if mass is None or "undefined" in mass:
            row["undefined_weight"] += 1
            continue
        maximum = Fraction(*mass["readings"][protocol]["maximum"])
        witness = {"source": source, "band": slot["band"], "origin": slot["origin"],
                   "marks": slot["result"]["mark_order"]}
        row["placements"] += 1
        row["positive_contexts"] += sum(context["weight"] > 0 for context in mass["readings"]["contexts"])
        row["same_outcome_and_pair_marginals"] += 1
        row["signed_sums"].append(Fraction(*mass["readings"][protocol]["signed_s"]))
        if row["maximum"] is None or maximum > row["maximum"]:
            row["maximum"] = maximum
            row["witness"] = witness
        row["minmax"].append(maximum)


def summarize(records, metadata):
    group_sizes = Counter(source["group"] for source in records)
    reached = defaultdict(Counter)
    coverage = defaultdict(Counter)
    loss_range = defaultdict(list)
    scores = defaultdict(lambda: {"placements": 0, "absent_placement": 0, "undefined_weight": 0, "positive_contexts": 0,
                                  "same_outcome_and_pair_marginals": 0, "maximum": None, "witness": None,
                                  "signed_sums": [], "minmax": []})
    cohorts = defaultdict(Counter)
    controls = []
    first_differences = Counter()
    matched_readings = defaultdict(Counter)
    different_example = None
    for source in records:
        group = source["group"]
        for law, variants in source["laws"].items():
            cuts = [variants[arm][1]["transition"].get("births", []) for arm in ("one_fewer", "arity_floor")]
            for first, last in zip(*cuts, strict=True):
                assert all(first[key] == last[key] for key in ("p", "D", "q", "inputs"))
                if first["f"] != last["f"]:
                    key = law, first["p"], first["D"], first["q"], first["f"], last["f"]
                    first_differences[key] += 1
                    if different_example is None:
                        different_example = {"source": source["name"], "law": law, "one_fewer": first, "arity_floor": last}
            for arm, stages in variants.items():
                for stage in stages:
                    age = stage["age"]
                    key = law, arm, age
                    status = stage["status"]
                    stat = reached[key]
                    cohort = cohorts[(group, *key)]
                    stat[status] += 1
                    cohort[status] += 1
                    for family, rows in stage.get("matched_predecessor_marks", {}).items():
                        tally = matched_readings[law, arm, family]
                        for row in rows:
                            tally[row.get("undefined", "eligible")] += 1
                    if source["name"].startswith("closure_"):
                        relevant = {key: stage[key] for key in ("status", "complete_states", "every_displayed_support_lawful",
                                                                "previous_stage_states", "surviving_previous_states", "lost_previous_states",
                                                                "initial_states", "surviving_initial_states", "literal_L", "L_reference_age")
                                    if key in stage}
                        controls.append({"source": source["name"], "law": law, "arm": arm, "age": age,
                                         **relevant, "transition": stage.get("transition")})
                    if "complete_states" not in stage:
                        stat["terminal_nonempty"] += int(stage["stage_persists"])
                        continue
                    if stage["every_displayed_support_lawful"]:
                        stat["all_supports_lawful"] += 1
                        cohort["all_supports_lawful"] += 1
                    if age:
                        following = stage["transition"]["following_funding"]["status"]
                        stat[f"next_{following}"] += 1
                        stat["reduced_births"] += sum(row["q"] != row["f"] for row in stage["transition"]["births"])
                        stat["nonimplied_zero_fresh_births"] += sum(row["f"] == 0 and not row["old_inputs_already_imply_law"]
                                                                   for row in stage["transition"]["births"])
                        stat["state_loss"] += int(stage["lost_previous_states"] > 0)
                        cohort["state_loss"] += int(stage["lost_previous_states"] > 0)
                        fraction = Fraction(stage["surviving_previous_states"], stage["previous_stage_states"])
                        loss_range[key].append(fraction)
                    if status != "reached":
                        continue
                    for family in ("external_pairs", "six_marks"):
                        roster = stage[family]
                        for slot in roster["slots"]:
                            scope = (*key, family, slot["band"], slot["origin"])
                            group_count = coverage[scope]
                            present = int(slot["placement"] is not None)
                            group_count["eligible_markings"] += slot["eligible"]
                            group_count["retained_placements"] += present
                            group_count["retained_with_all_supports_lawful"] += present * stage["every_displayed_support_lawful"]
                            group_count["missing_placements"] += 1 - present
                            update_scores(scores, source["name"], law, arm, stage, family, slot)

    def score_row(key, row):
        law, arm, age, family, basis, weighting, reading = key
        return {"law": law, "arm": arm, "age": age, "reading_family": family, "eligibility": basis,
                "weighting": weighting, "reading": reading,
                **{key: row[key] for key in ("placements", "absent_placement", "undefined_weight", "positive_contexts",
                                             "same_outcome_and_pair_marginals", "witness")},
                "maximum": ratio(row["maximum"]), "max_score_range": span(row["minmax"]),
                "signed_score_range": span(row["signed_sums"])}

    return {"metadata": metadata, "sources": len(records), "source_denominators": group_sizes,
            "stages": [{"law": law, "arm": arm, "age": age, "denominator": sum(s["horizon"] >= age for s in records),
                        "previous_state_retention_range": span(loss_range[(law, arm, age)]), **row}
                       for (law, arm, age), row in sorted(reached.items())],
            "cohorts": [{"source_group": group, "law": law, "arm": arm, "age": age, **row}
                        for (group, law, arm, age), row in sorted(cohorts.items())],
            "marking": [{"law": law, "arm": arm, "age": age, "reading_family": family, "band": band, "origin": origin, **row}
                        for (law, arm, age, family, band, origin), row in sorted(coverage.items())],
            "scores": [score_row(key, row) for key, row in sorted(scores.items())],
            "closure_controls": controls,
            "different_cutoffs_on_first_shared_prefix": [{"law": law, "p": p, "D": demand, "q": q,
                                                           "one_fewer_f": first, "arity_floor_f": last, "count": count}
                                                          for (law, p, demand, q, first, last), count in sorted(first_differences.items())],
            "matched_predecessor_marks": [{"law": law, "arm": arm, "reading_family": family, **row}
                                          for (law, arm, family), row in sorted(matched_readings.items())],
            "first_different_cutoff": different_example}
