"""Coverage, ranges and extrema of the fixed measured placements."""

from collections import Counter, defaultdict
from fractions import Fraction

from readings import ratio


def maximum(values):
    return max((Fraction(*value) for value in values if value is not None), default=None)


def observe(source, law, stage, reading_class, slot):
    for weighting, weighted in slot["result"]["weightings"].items():
        for arm, tables in weighted["arms"].items():
            for reading in ("I", "II"):
                contexts = tables["contexts"]
                allowed = tables[reading]["maximum"]
                marginal = maximum(value for side in tables[reading]["outcome_marginal_remote_tv"] for value in side)
                pair_marginal = maximum(value for side in tables["pair_marginal_remote_tv"] for value in side)
                place = {"source": source, "law": law, "age": stage, "reading_class": reading_class,
                         "band": slot["band"], "origin": slot["origin"], "weighting": weighting,
                         "arm": arm, "reading": reading}
                yield place, {
                    "maximum": Fraction(*allowed) if allowed is not None else None,
                    "outcome_marginal_remote_tv": marginal,
                    "pair_marginal_remote_tv": pair_marginal,
                    "joint_tv_from_product": maximum(row[reading]["joint_tv_from_product"] for row in contexts),
                    "joint_pairs_tv_from_common": maximum(row["joint_pairs_tv_from_common"] for row in contexts),
                    "all_marks_tv_from_common": maximum(row["all_marks_tv_from_common"] for row in contexts),
                    "missing_contexts": sum(not row["weight"] for row in contexts),
                }


def aggregate(coverage, sample):
    observed = [(place, row) for place, row in sample if row["maximum"] is not None]
    values = [row["maximum"] for _, row in observed]
    highest = max(values, default=None)
    witnesses = (place for place, row in observed if row["maximum"] == highest)
    scores = {"measured_placements": len(sample), "defined_placements": len(observed),
              "missing_contexts": sum(row["missing_contexts"] for _, row in sample),
              "score_range": [ratio(min(values, default=None)), ratio(highest)],
              "score_mean_equal_weight_of_defined_placements": ratio(sum(values, Fraction()) / len(values)) if values else None,
              "first_maximizer": next(witnesses, None),
              "above_two": sum(value > 2 for value in values),
              "above_two_and_no_outcome_marginal_change": sum(
                  row["maximum"] > 2 and row["outcome_marginal_remote_tv"] == 0 for _, row in observed),
              "above_two_and_no_pair_marginal_change": sum(
                  row["maximum"] > 2 and row["pair_marginal_remote_tv"] == 0 for _, row in observed)}
    for field in ("outcome_marginal_remote_tv", "pair_marginal_remote_tv", "joint_tv_from_product",
                  "joint_pairs_tv_from_common", "all_marks_tv_from_common"):
        found = [row[field] for _, row in sample if row[field] is not None]
        scores[f"{field}_range"] = [ratio(min(found, default=None)), ratio(max(found, default=None))]
    return {**coverage, **scores}


def summarize(cohort):
    source_groups = Counter(source["group"] for source in cohort)
    stages = Counter()
    stage_agreement = Counter()
    coverage = defaultdict(Counter)
    per_band = defaultdict(list)
    by_law = defaultdict(list)
    examples_with_pair_only_dependence = []
    direct_newborn = Counter()
    support_failures = Counter()
    old_weight_tv = defaultdict(list)
    retained = 0
    for source in cohort:
        group = source["group"]
        parity, nae = (source["laws"][law][1] for law in ("parity", "nae"))
        if parity["status"] != "measured_stage" or nae["status"] != "measured_stage":
            stage_agreement["paired_growth_unavailable"] += 1
        elif parity["supports"] == nae["supports"]:
            stage_agreement["same_complete_growth"] += 1
        else:
            stage_agreement["parity_closing_top"] += 1
        for law, history in source["laws"].items():
            for stage in history:
                age = stage["age"]
                statuses = stages[(group, law, age, stage["status"])]
                stages[(group, law, age, stage["status"])] = statuses + 1
                for certificate in stage.get("support_certificates", []):
                    if not certificate["eligible"]:
                        support_failures[(law, age)] += 1
                if stage["status"] != "measured_stage":
                    continue
                for reading_class in ("external_pairs", "six_marks"):
                    for slot in stage[reading_class]["slots"]:
                        key = (group, law, age, reading_class, slot["band"], slot["origin"])
                        entry = coverage[key]
                        entry["stages_available"] += 1
                        entry["retained_source_stages"] += int(slot["eligible"] > 0)
                        entry["eligible_placements"] += slot["eligible"]
                        if slot["placement"] is None:
                            continue
                        retained += 1
                        if slot["origin"] == "newborn":
                            direct_newborn[(law, reading_class)] += 1
                        for weighting, row in slot["result"]["weightings"].items():
                            if row.get("old_mark_check"):
                                old_weight_tv[(law, weighting)].append(Fraction(*row["old_mark_check"]["mass_tv_from_start_u"]))
                            ext = row["arms"]["external"]["contexts"]
                            if (all(context["I"]["joint_tv_from_product"] == [0, 1] for context in ext)
                                    and any(context["II"]["joint_tv_from_product"] != [0, 1] for context in ext)):
                                examples_with_pair_only_dependence.append({"source": source["name"], "law": law, "age": age,
                                                                           "reading_class": reading_class, "band": slot["band"],
                                                                           "origin": slot["origin"], "weighting": weighting})
                        for place, result in observe(source["name"], law, age, reading_class, slot):
                            suffix = tuple(place[k] for k in ("weighting", "arm", "reading"))
                            per_band[key + suffix].append((place, result))
                            by_law[(law,) + suffix].append((place, result))
    return {
        "sources": len(cohort), "source_group_denominators": source_groups,
        "source_stages": [{"group": group, "law": law, "age": age, "status": status, "count": count}
                          for (group, law, age, status), count in sorted(stages.items())],
        "growth_agreement": stage_agreement,
        "excluded_supports": [{"law": law, "age": age, "count": count}
                              for (law, age), count in sorted(support_failures.items())],
        "placement_count": retained,
        "direct_newborn_placement_count": [{"law": law, "reading_class": reads, "count": count}
                                           for (law, reads), count in sorted(direct_newborn.items())],
        "placement_coverage": [{"group": group, "law": law, "age": age, "reading_class": reads,
                                "band": band, "origin": origin, "predeclared_sources": source_groups[group], **counts}
                               for (group, law, age, reads, band, origin), counts in sorted(coverage.items())],
        "scores_by_law": [{"law": law, "weighting": weighting, "arm": arm, "reading": reading,
                          **aggregate({}, found)} for (law, weighting, arm, reading), found in sorted(by_law.items())],
        "scores_by_source_group_and_band": [
            {"group": key[0], "law": key[1], "age": key[2], "reading_class": key[3], "band": key[4],
             "origin": key[5], "weighting": weighting, "arm": arm, "reading": reading,
             **aggregate({"predeclared_sources": source_groups[key[0]], **coverage[key]}, found)}
            for combined, found in sorted(per_band.items())
            for key, (weighting, arm, reading) in [(combined[:-3], combined[-3:])]],
        "pair_only_dependence": examples_with_pair_only_dependence,
        "old_marks_probability_change": [{"law": law, "weighting": weighting, "measured": len(values),
                                          "changed": sum(value > 0 for value in values),
                                          "tv_range": [ratio(min(values)), ratio(max(values))]}
                                         for (law, weighting), values in sorted(old_weight_tv.items())],
    }
