"""Post-score analysis of group ambiguity using independent exact enumeration."""

from collections import Counter, defaultdict
from dataclasses import dataclass
from fractions import Fraction
from itertools import combinations, product
from operator import index


BIN_COUNT = 16
PATCH_COUNT = 81
FULL_MASK = (1 << BIN_COUNT) - 1
OMITTED_BIN = 1 << (BIN_COUNT - 1)
PRIOR_TURN_CLOSED_GROUP = sum(1 << bin_id for bin_id in (7, 11, 13, 14))
ARMS = ("narrow", "varied")
BACKENDS = ("parity", "nae", "integer")
SCHEDULES = ("ordinary", "opposite")
COMPARISONS = (
    "supports_strict_majority", "opposes_strict_majority", "abstains",
    "supports_emitted_default", "disagrees_with_emitted_default",
)


@dataclass(frozen=True)
class _Fit:
    rows: tuple
    class_positions: tuple
    scores: dict
    ranks: dict
    maximal: tuple
    retained: tuple


def _bitmap_counts(pixels):
    pixels = tuple(map(int if isinstance(pixels, str) else index, pixels))
    if len(pixels) != 64 or any(pixel not in (0, 1) for pixel in pixels):
        raise ValueError("expected a bitmap of 64 bits")
    counts = [0] * BIN_COUNT
    for row, col in product(range(-1, 8), repeat=2):
        word = 0
        for down, right in ((0, 0), (0, 1), (1, 0), (1, 1)):
            y, x = row + down, col + right
            word *= 2
            if 0 <= y < 8 and 0 <= x < 8:
                word += pixels[8 * y + x]
        counts[word] += 1
    return tuple(counts)


def _counts(row):
    counts = _bitmap_counts(row["pixels"]) if "pixels" in row else tuple(map(index, row["counts"]))
    if len(counts) != BIN_COUNT or min(counts) < 0 or sum(counts) != PATCH_COUNT:
        raise ValueError("expected 16 counts summing to 81")
    if "pixels" in row and "counts" in row and tuple(row["counts"]) != counts:
        raise ValueError("supplied counts are inconsistent with the raw bitmap")
    return counts


def _earned(receipt):
    guess, correct = receipt["guess"], receipt["correct"]
    if (type(guess) not in (int, bool) or guess not in (0, 1)
            or type(correct) not in (int, bool) or correct not in (0, 1)):
        raise ValueError("invalid emitted action or feedback bit")
    return int(guess) ^ int(not correct)


def training_from_receipts(raw_rows, receipts, arm):
    """Replay earned actions on raw training rows in the recorded presentation order."""
    if arm not in ARMS:
        raise ValueError(f"unregistered training arm {arm}")
    selected = sorted((row for row in receipts if row["arm"] == arm), key=lambda row: row["presentation"])
    result = []
    for presentation, (raw, receipt) in enumerate(zip(raw_rows, selected, strict=True), 1):
        slot = receipt["slot"]
        if (receipt["presentation"] != presentation or type(slot) is not int or slot != presentation - 1
                or raw["id"] != receipt["id"] or raw.get("slot", slot) != slot):
            raise ValueError("training bitmap and receipt do not match by presentation and slot")
        earned = {
            _earned(receipt["arms"][f"{arm}-{backend}-{schedule}"]) ^ int(schedule == "opposite")
            for backend, schedule in product(BACKENDS, SCHEDULES)
        }
        if len(earned) != 1:
            raise ValueError("laws or opposite schedule disagree on the replayed training action")
        result.append({"id": raw["id"], "slot": slot, "action": earned.pop(), "counts": _counts(raw)})
    return result


def _canonical(mask):
    mask = index(mask)
    if not 0 < mask < FULL_MASK:
        raise ValueError("expected a nontrivial bin bipartition")
    return FULL_MASK ^ mask if mask & OMITTED_BIN else mask


def _members(mask):
    return tuple(bin_id for bin_id in range(BIN_COUNT) if mask & (1 << bin_id))


def _size(mask):
    cardinality = mask.bit_count()
    return min(cardinality, BIN_COUNT - cardinality)


def _quarter_turn(mask):
    rotated = 0
    for word in _members(mask):
        top_left, top_right, bottom_left, bottom_right = ((word >> shift) & 1 for shift in (3, 2, 1, 0))
        rotated |= 1 << (8 * bottom_left + 4 * top_left + 2 * bottom_right + top_right)
    return _canonical(rotated)


def _ratio(value):
    return [value.numerator, value.denominator]


def _moments(values):
    mean = Fraction(sum(values), len(values))
    variance = Fraction(sum(value ** 2 for value in values), len(values)) - mean ** 2
    return mean, variance


def _enumerate(training_rows):
    rows, slots = [], set()
    for row in training_rows:
        identity, slot, action = row["id"], row["slot"], row["action"]
        if not isinstance(identity, str) or slot in slots or type(action) is not int or action not in (0, 1):
            raise ValueError("invalid training receipt")
        rows.append({"id": identity, "slot": slot, "action": action, "counts": _counts(row)})
        slots.add(slot)
    classes = tuple(tuple(pos for pos, row in enumerate(rows) if row["action"] == action) for action in (0, 1))
    if not all(classes):
        raise ValueError("independent rank comparison requires training receipts for both actions")
    columns = [tuple(zip(*(rows[pos]["counts"] for pos in positions))) for positions in classes]

    # Take raw scalar sums afresh for every representative, with ordinary rational arithmetic.
    scores = {}
    for size in range(1, BIN_COUNT):
        for members in combinations(range(BIN_COUNT - 1), size):
            first, second = (_moments(tuple(map(sum, zip(*(side[j] for j in members))))) for side in columns)
            separation = first[0] - second[0]
            if separation:
                variance = first[1] + second[1]
                mask = sum(1 << j for j in members)
                scores[mask] = (False, separation ** 2 / variance) if variance else (True, Fraction(0))

    tier_sizes = Counter(scores.values())
    ranks, partitions_above = {}, 0
    for tier, score in enumerate(sorted(tier_sizes, reverse=True), 1):
        tier_size = tier_sizes[score]
        ranks[score] = {"score_tier": tier, "partitions_above": partitions_above, "partitions_with_score": tier_size}
        partitions_above += tier_size
    if not ranks:
        return _Fit(tuple(rows), classes, scores, ranks, (), ())
    best_score = next(iter(ranks))
    maximal = tuple(sorted(mask for mask, score in scores.items() if score == best_score))
    min_size = min(map(_size, maximal))
    retained = tuple(mask for mask in maximal if _size(mask) == min_size)
    return _Fit(tuple(rows), classes, scores, ranks, maximal, retained)


def _score_record(fit, mask):
    score = fit.scores.get(mask)
    if score is None:
        return {"kind": "equal_means", "ratio": None, "score_tier": None,
                "partitions_above": len(fit.scores), "partitions_with_score": None}
    infinite, value = score
    return {"kind": "infinite" if infinite else "finite", "ratio": [1, 0] if infinite else _ratio(value),
            **fit.ranks[score]}


def _group_stats(fit, mask):
    members = _members(mask)
    values = tuple(sum(row["counts"][bin_id] for bin_id in members) for row in fit.rows)
    by_class = [tuple(values[pos] for pos in positions) for positions in fit.class_positions]
    mean_variances = list(map(_moments, by_class))
    means = tuple(pair[0] for pair in mean_variances)
    rotated = _quarter_turn(mask)
    group = {
        "mask": mask,
        "bins": list(members),
        "smaller_side_size": _size(mask),
        "score": _score_record(fit, mask),
        "classes": [
            {"action": action, "mean": _ratio(mean), "population_variance": _ratio(variance),
             "minimum": min(observed), "maximum": max(observed)}
            for action, ((mean, variance), observed) in enumerate(zip(mean_variances, by_class))
        ],
        "quarter_turn_mask": rotated,
        "quarter_turn_closed": rotated == mask,
    }
    return group, means, values


def _vote(value, means):
    left, right = (abs(value - mean) for mean in means)
    return None if left == right else int(right < left)


def _equivalence(fit, stats):
    oriented_counts, votes = defaultdict(list), defaultdict(list)
    for mask in fit.maximal:
        _, means, values = stats[mask]
        oriented = values if means[0] < means[1] else tuple(PATCH_COUNT - value for value in values)
        oriented_counts[oriented].append(mask)
        votes[tuple(_vote(value, means) for value in values)].append(mask)

    def classes(by_signature):
        return [{"masks": masks, "signature": list(signature)} for signature, masks in by_signature.items()]

    return {"receipt_order": [{key: row[key] for key in ("id", "slot", "action")} for row in fit.rows],
            "mean_oriented_count_classes": classes(oriented_counts), "rule_vote_classes": classes(votes)}


def _choose_alternatives(fit, equivalent, stats):
    retained = set(fit.retained)
    alternatives = sorted(set(fit.maximal) - retained)
    selected = defaultdict(list)
    if alternatives:
        selected[alternatives[0]].append("first_maximal_mask_omitted_by_size")
    for name in ("mean_oriented_count_classes", "rule_vote_classes"):
        candidates = {mask for group in equivalent[name] if retained.intersection(group["masks"])
                      for mask in group["masks"]}
        same_signature = sorted(candidates.intersection(alternatives))
        if same_signature:
            selected[same_signature[0]].append(f"first_omitted_mask_in_retained_{name}")
    closed = [mask for mask in alternatives if stats[mask][0]["quarter_turn_closed"]]
    if closed:
        selected[closed[0]].append("first_omitted_quarter_turn_closed_mask")
    selected[PRIOR_TURN_CLOSED_GROUP].append("prior_training_only_turn_closed_group")
    return selected


def _held_rows(held_rows):
    result = {}
    for row in held_rows:
        identity = row["id"]
        if not isinstance(identity, str) or identity in result or ("q" in row and row["q"] not in (2, 3)):
            raise ValueError("held query IDs must be unique and any declared turns must be 2 or 3")
        if "label" in row and (row["label"] not in ("L", "T") or "q" not in row):
            raise ValueError("a held true letter requires L or T and a declared held turn")
        result[identity] = {"id": identity, "counts": _counts(row),
                            **{key: row[key] for key in ("q", "label") if key in row}}
    return [result[identity] for identity in sorted(result)]


def _committee(retained, votes):
    cast = {action: [mask for mask in retained if votes[mask] == action] for action in (0, 1)}
    zeros, ones = map(len, cast.values())
    if zeros != ones:
        kind = "strict_majority"
    elif zeros:
        kind = "split_tie"
    else:
        kind = "all_abstain" if retained else "no_rules"
    return {"kind": kind, "action": int(ones > zeros), "votes": [zeros, ones],
            "abstentions": len(retained) - zeros - ones, "example_voting_masks": {str(a): m[0] for a, m in cast.items() if m}}


def _comparison(vote, committee):
    if vote is None:
        return "abstains"
    if committee["kind"] == "strict_majority":
        return "supports_strict_majority" if vote == committee["action"] else "opposes_strict_majority"
    return "supports_emitted_default" if vote == committee["action"] else "disagrees_with_emitted_default"


def _held_disagreements(fit, stats, selected_examples, queries):
    all_masks = tuple(dict.fromkeys((*fit.maximal, *selected_examples)))
    memberships = {mask: _members(mask) for mask in all_masks}
    alternatives = sorted(set(fit.maximal) - set(fit.retained))
    reported = {mask: {"training_selection_reasons": reasons, "group": stats[mask][0],
                       "comparisons": dict.fromkeys(COMPARISONS, 0), "examples": {}}
                for mask, reasons in selected_examples.items()}
    committee_counts = Counter(dict.fromkeys(("strict_majority", "split_tie", "all_abstain", "no_rules",
                                               "both_actions_received_retained_votes"), 0))
    possible_comparisons = Counter(dict.fromkeys(COMPARISONS, 0))
    witnesses = {}
    for query in queries:
        totals = {mask: sum(query["counts"][bin_id] for bin_id in members)
                  for mask, members in memberships.items()}
        votes = {mask: _vote(total, stats[mask][1]) for mask, total in totals.items()}
        committee = _committee(fit.retained, votes)
        committee_counts[committee["kind"]] += 1
        case = {key: query[key] for key in ("id", "q") if key in query}
        case["committee"] = committee
        if all(committee["votes"]):
            committee_counts["both_actions_received_retained_votes"] += 1
            witnesses.setdefault("retained_rule_disagreement", case)

        comparisons = {mask: _comparison(votes[mask], committee) for mask in (*alternatives, *reported)}
        example_masks = {}
        for mask in alternatives:
            example_masks.setdefault(comparisons[mask], mask)
        for relation, mask in example_masks.items():
            possible_comparisons[relation] += 1
            witnesses.setdefault(relation, {**case, "alternative_mask": mask,
                                            "alternative_vote": votes[mask], "observed_count": totals[mask]})
        for mask, record in reported.items():
            relation = comparisons[mask]
            record["comparisons"][relation] += 1
            record["examples"].setdefault(relation, {**case, "vote": votes[mask], "observed_count": totals[mask]})

    return {"cases": len(queries), "committee": dict(committee_counts), "omitted_maximal_masks": len(alternatives),
            "cases_where_any_omitted_maximal_mask": dict(possible_comparisons), "witnesses": witnesses,
            "concrete_groups": list(reported.values())}


def _collision_summary(queries, *, masks=None):
    grouped = defaultdict(lambda: {"L": [], "T": []})
    members = [_members(mask) for mask in masks] if masks is not None else None
    for row in queries:
        counts = row["counts"]
        signature = counts if members is None else tuple(sum(counts[j] for j in group) for group in members)
        grouped[signature][row["label"]].append(row["id"])

    collision_count = affected_rows = conflicting_pairs = unavoidable_errors = 0
    first = None
    for signature, by_letter in sorted(grouped.items()):
        left, right = (len(by_letter[letter]) for letter in ("L", "T"))
        if left and right:
            collision_count += 1
            affected_rows += left + right
            conflicting_pairs += left * right
            unavoidable_errors += min(left, right)
            if first is None:
                first = {"signature": list(signature), "letter_counts": {"L": left, "T": right},
                         "example_ids": {letter: ids[0] for letter, ids in by_letter.items()}}

    total = len(queries)
    return {"total": total, "distinct_signatures": len(grouped), "cross_label_signatures": collision_count,
            "rows_in_cross_label_signatures": affected_rows, "cross_label_pairs": conflicting_pairs,
            "unavoidable_errors": unavoidable_errors,
            "equal_weight_accuracy_ceiling": [total - unavoidable_errors, total] if total else None,
            "witness": first}


def _collision_bounds(queries, fits):
    if not any("label" in row for row in queries):
        return None
    if not all("label" in row for row in queries):
        raise ValueError("signature collisions require a true letter on every held query")
    subsets = {"held_turns": queries}
    subsets.update({f"q{turn}": [row for row in queries if row["q"] == turn] for turn in (2, 3)})
    return {
        "full_sensor": {name: _collision_summary(rows) for name, rows in subsets.items()},
        "retained_group_counts": {
            arm: {"mask_order": list(fit.retained),
                  "by_turn": {name: _collision_summary(rows, masks=fit.retained) for name, rows in subsets.items()}}
            for arm, fit in fits.items()
        },
    }


def _marginals(fit):
    bins = [[sum(fit.rows[pos]["counts"][bin_id] for pos in members) for bin_id in range(BIN_COUNT)]
            for members in fit.class_positions]
    return list(map(len, fit.class_positions)), bins


def _check_checkpoints(arm, fit, fitted):
    counts, bins = _marginals(fit)
    best_ratio = _score_record(fit, fit.maximal[0])["ratio"] if fit.maximal else None
    checkpoint_checks = {}
    for backend, schedule in product(BACKENDS, SCHEDULES):
        name = f"{arm}-{backend}-{schedule}"
        snapshot = fitted[name]
        masks = sorted(_canonical(mask) for mask in snapshot["masks"])
        if backend == "integer":
            fitted_counts, fitted_bins, rank = snapshot["class_totals"], snapshot["class_bin_totals"], snapshot["score"]
        else:
            fitted_counts, fitted_bins = snapshot["class_counts"], snapshot["class_totals"]
            rank = [snapshot["rank_numerator"], snapshot["rank_denominator"]] if masks else None
        expected_counts, expected_bins = (counts[::-1], bins[::-1]) if schedule == "opposite" else (counts, bins)
        checkpoint_checks[name] = {"retained_masks_match": masks == list(fit.retained),
                                  "class_counts_match": fitted_counts == expected_counts,
                                  "bin_marginals_match": fitted_bins == expected_bins, "rank_matches": rank == best_ratio}
    return checkpoint_checks


def _overlap(fit, reference):
    shared = set(fit.maximal).intersection(reference)
    return {"reference_count": len(reference), "shared_count": len(shared), "shared_masks": sorted(shared),
            "reference_only_count": len(reference) - len(shared), "fit_only_count": len(fit.maximal) - len(shared)}


def _arm_summary(fit, reference, queries):
    stats = {mask: _group_stats(fit, mask) for mask in (*fit.maximal, PRIOR_TURN_CLOSED_GROUP)}
    equivalent = _equivalence(fit, stats)
    examples = _choose_alternatives(fit, equivalent, stats)
    class_counts, bin_marginals = _marginals(fit)
    return {
        "class_counts": class_counts, "class_bin_totals": bin_marginals,
        "partitions_examined": OMITTED_BIN - 1, "partitions_with_separation": len(fit.scores),
        "maximal_score": _score_record(fit, fit.maximal[0]) if fit.maximal else None,
        "maximal_masks": list(fit.maximal),
        "maximal_smaller_side_sizes": dict(sorted(Counter(str(_size(mask)) for mask in fit.maximal).items())),
        "retained_masks": list(fit.retained), "retained_groups": [stats[mask][0] for mask in fit.retained],
        "retained_family_quarter_turn_closed": (bool(fit.retained) and
                                               set(map(_quarter_turn, fit.retained)) == set(fit.retained)),
        "prior_maximal_overlap": _overlap(fit, reference), "training_equivalence": equivalent,
        "held_disagreements": _held_disagreements(fit, stats, examples, queries),
    }


def _broken_constants(narrow, varied, varied_fit, values):
    examples = []
    for action, (before, after) in enumerate(zip(narrow["classes"], varied["classes"])):
        if before["minimum"] != before["maximum"] or after["minimum"] == after["maximum"]:
            continue
        positions = varied_fit.class_positions[action]
        first = positions[0]
        second = next(pos for pos in positions if values[pos] != values[first])
        examples.append({"action": action, "narrow_constant": before["minimum"],
                         "varied_receipts": [{"id": varied_fit.rows[pos]["id"], "slot": varied_fit.rows[pos]["slot"],
                                              "count": values[pos]} for pos in (first, second)]})
    return examples


def _changes(narrow, varied):
    groups, surviving, displaced = [], [], []
    varied_maximal = set(varied.maximal)
    for mask in narrow.maximal:
        before, _, _ = _group_stats(narrow, mask)
        after, _, values = _group_stats(varied, mask)
        survives = mask in varied_maximal
        row = {"mask": mask, "narrow": before, "varied": after, "still_maximal": survives,
               "broken_constants": _broken_constants(before, after, varied, values)}
        groups.append(row)
        (surviving if survives else displaced).append(mask)
    return {"surviving_masks": surviving, "displaced_masks": displaced, "groups": groups,
            "first_surviving_tie": next((row for row in groups if row["still_maximal"]), None),
            "first_broken_constant": next((row for row in groups if row["broken_constants"]), None)}


def maximal_groups(training_rows):
    """Return all highest-scoring masks before size preference on an admitted training roster."""
    return list(_enumerate(training_rows).maximal)


def analyze(training_by_arm, held_rows, fitted_by_checkpoint=None, *, prior_maximal_masks=None):
    """Measure fitted-group ambiguity and exact signature bounds after scoring.

    Training rows have id, unique slot, earned action and either pixels or counts.
    Held rows have id and either pixels or counts, with optional q for a witness.
    If every held row carries a true letter and q, report collision bounds too.
    Checkpoints, if supplied, are the per-checkpoint fit snapshots from the producer.
    """
    if training_by_arm.keys() != set(ARMS):
        raise ValueError("post-score analysis requires both training arms")
    fits = {arm: _enumerate(training_by_arm[arm]) for arm in ARMS}
    queries = _held_rows(held_rows)
    narrow, varied = (fits[arm] for arm in ARMS)
    reference = set(narrow.maximal) if prior_maximal_masks is None else set(map(_canonical, prior_maximal_masks))
    return {
        "prior_reference": {"source": "recomputed_narrow_fit" if prior_maximal_masks is None else "provided_prior_fit",
                            "mask_count": len(reference), "matches_narrow": reference == set(narrow.maximal)},
        "arms": {arm: _arm_summary(fits[arm], reference, queries) for arm in ARMS},
        "checkpoint_checks": ({name: result for arm in ARMS
                               for name, result in _check_checkpoints(arm, fits[arm], fitted_by_checkpoint).items()}
                              if fitted_by_checkpoint is not None else None),
        "narrow_maximal_rank_changes": _changes(narrow, varied),
        "signature_collision_bounds": _collision_bounds(queries, fits),
    }
