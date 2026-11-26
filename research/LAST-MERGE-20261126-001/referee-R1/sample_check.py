"""Reconstruct the six-knot sample and check its two law populations."""

import argparse
from collections import Counter
from fractions import Fraction
import gzip
from hashlib import sha256
from itertools import combinations, islice, permutations, product
import json
from math import comb, prod
from pathlib import Path
from random import Random
from resource import RUSAGE_SELF, getrusage
from time import perf_counter

from networkx.generators.atlas import graph_atlas_g


HERE = Path(__file__).resolve().parent
STUDY = HERE.parent
ROOT = STUDY.parents[1]
SETTLING = STUDY.parent / "SETTLE-BOUND-20261126-001"
BALANCE = (ROOT / "artifacts" / "RING-IN-BALANCE-20261123-001B"
           / "RING-IN-BALANCE-20261123-001B-E001_reference" / "census")
DESCENT = (ROOT / "artifacts" / "DESCENT-HELD-20261125-001A"
           / "DESCENT-HELD-20261125-001A-E001_order_in_own_places" / "part1_runs.json.gz")
EARLIER_TWO_LAWS = (STUDY.parent / "NAE-GROWTH-20261119-001" / "referee-R1" / "referee_nae_growth.json")
KNOTS = 6
PAIRS = tuple(combinations(range(KNOTS), 2))
PAIR_BITS = {pair: 1 << bit for bit, pair in enumerate(PAIRS)}
HORIZON = 24
CAP = 30_000
PILOT_SIZE = 64
READINGS = {"sig0": (5, 3), "sig1": (7, 5)}


def signature(value):
    return sha256(json.dumps(value, separators=(",", ":")).encode()).hexdigest()


def json_lines(path):
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "rt") as rows:
        for row in rows:
            yield json.loads(row)


def neighbours(pairs):
    adjacent = [0] * KNOTS
    for first, second in pairs:
        adjacent[first] |= 1 << second
        adjacent[second] |= 1 << first
    return adjacent


def connected(adjacent):
    reached = 1
    for _ in range(KNOTS - 1):
        for knot, links in enumerate(adjacent):
            if reached & (1 << knot):
                reached |= links
    return reached == (1 << KNOTS) - 1


def loose_domains(adjacent):
    return [range(max(0, 3 - links.bit_count()), 4) for links in adjacent]


def shared_holdings(pairs):
    holdings = [[] for _ in range(KNOTS)]
    for distinction, (first, second) in enumerate(pairs):
        holdings[first].append(distinction)
        holdings[second].append(distinction)
    return holdings


def all_holdings(shared, loose):
    next_distinction = 1 + max(max(row) for row in shared)
    holdings = []
    for row, count in zip(shared, loose, strict=True):
        holdings.append(row + list(range(next_distinction, next_distinction + count)))
        next_distinction += count
    return holdings


def numbered_meetings(pairs, numbering):
    return sum(PAIR_BITS[tuple(sorted((numbering[a], numbering[b])))] for a, b in pairs)


def census():
    # The atlas gives the historical numbering. Independently account for all
    # connected numbered meeting patterns and all ways of adding loose places.
    numbered = set()
    labelled_starts = 0
    for mask in range(1 << len(PAIRS)):
        if mask.bit_count() < KNOTS - 1:
            continue
        adjacent = neighbours(pair for pair, bit in PAIR_BITS.items() if mask & bit)
        if connected(adjacent):
            numbered.add(mask)
            domains = loose_domains(adjacent)
            labelled_starts += prod(map(len, domains)) - all(0 in domain for domain in domains)

    roster, weights, shared, covered = [], [], {}, set()
    relabellings = list(permutations(range(KNOTS)))
    for number, pattern in enumerate(graph_atlas_g()):
        if pattern.number_of_nodes() != KNOTS:
            continue
        pairs = sorted(tuple(sorted(pair)) for pair in pattern.edges)
        adjacent = neighbours(pairs)
        if not connected(adjacent):
            continue
        base = sum(PAIR_BITS[pair] for pair in pairs)
        images, symmetries = set(), []
        for permutation in relabellings:
            image = numbered_meetings(pairs, permutation)
            images.add(image)
            if image == base:
                symmetries.append(permutation)
        assert not covered.intersection(images), number
        covered.update(images)
        shared[number] = shared_holdings(pairs)
        seen = set()
        for loose in product(*loose_domains(adjacent)):
            if loose in seen or not any(loose):
                continue
            orbit = {tuple(loose[knot] for knot in symmetry) for symmetry in symmetries}
            assert loose == min(orbit), (number, loose)
            seen.update(orbit)
            roster.append((number, loose))
            weights.append(len(images) * len(orbit))
    assert covered == numbered and sum(weights) == labelled_starts
    stats = {
        "connected_meeting_patterns_up_to_renaming": len(shared),
        "connected_numbered_meeting_patterns": len(numbered),
        "numbered_meeting_patterns_checked": 1 << len(PAIRS),
        "starts_up_to_renaming": len(roster),
        "starts_with_knots_numbered": labelled_starts,
        "ordered_starts_sha256": signature(roster),
    }
    return roster, weights, shared, stats


def parity_test(holdings):
    # A proper, nonzero row combination supported within this rule obstructs
    # forgetting. The rule itself supplies K1, and the zero state supplies K3.
    rows = tuple(sum(1 << place for place in row) for row in holdings)
    span = {0}
    for row in rows:
        span |= {row ^ other for other in span}
    return {
        knot: min(restrictions, key=lambda mask: (mask.bit_count(), mask))
        for knot, row in enumerate(rows)
        if (restrictions := [mask for mask in span if mask and mask != row and mask & row == mask])
    }


def nae_shared_states(shared):
    # One bit per assignment of the shared distinctions. A live knot can
    # satisfy its rule for any assignment of its shared distinctions.
    state_count = 1 << (max(max(row) for row in shared) + 1)
    full = (1 << state_count) - 1
    high = []
    for place in range(state_count.bit_length() - 1):
        run = 1 << place
        repeats = full // ((1 << (2 * run)) - 1)
        high.append(repeats * (((1 << run) - 1) << run))
    local = []
    for row in shared:
        assignments = [full]
        for place in row:
            assignments = ([mask & (full ^ high[place]) for mask in assignments]
                           + [mask & high[place] for mask in assignments])
        local.append(assignments)
    return full, local


def nae_projections(loose_mask, shared_states):
    full, local = shared_states
    valid = full
    for knot, masks in enumerate(local):
        if not loose_mask & (1 << knot):
            valid &= full ^ (masks[0] | masks[-1])
    return tuple(tuple(state for state, mask in enumerate(masks) if valid & mask)
                 for masks in local)


def nae_test(shared_projection, shared_count, loose_count):
    arity = shared_count + loose_count
    full = 1 << arity
    allowed = {state | (loose << shared_count) for state in shared_projection
               for loose in range(1 << loose_count)} - {0, full - 1}
    # The two locally forbidden states give K1. Test K2 and K3 from the
    # complete projection of the global relation onto this rule.
    dropping = [len({state & ~(1 << place) for state in allowed}) for place in range(arity)]
    return bool(allowed), all(count == full // 2 for count in dropping), len(allowed)


def admissions(roster, shared, indices):
    tables = {number: nae_shared_states(holds) for number, holds in shared.items()}
    shared_projections, nae_cache = {}, {}
    issues = {"nae": {}, "parity": {}}
    for index in indices:
        number, loose = roster[index]
        shared_stars = shared[number]
        holds = all_holdings(shared_stars, loose)
        parity = parity_test(holds)
        if parity:
            issues["parity"][index] = {knot: [place for place in holds[knot] if mask & (1 << place)]
                                       for knot, mask in parity.items()}
        loose_mask = sum(1 << knot for knot, count in enumerate(loose) if count)
        key = (number, loose_mask)
        if key not in shared_projections:
            shared_projections[key] = nae_projections(loose_mask, tables[number])
        failed = {}
        for knot, count in enumerate(loose):
            key = (number, loose_mask, knot, count)
            if key not in nae_cache:
                nae_cache[key] = nae_test(shared_projections[number, loose_mask][knot],
                                          len(shared_stars[knot]), count)
            coexistence, forgetting, allowed_count = nae_cache[key]
            if not (coexistence and forgetting):
                failed[knot] = {"K2": forgetting, "K3": coexistence, "allowed_states": allowed_count}
        if failed:
            issues["nae"][index] = failed
    return issues


def canonical_control(roster, shared, indices, issues):
    from knotlab.knots import check_knot
    from knotlab.relations import Relation

    def distinction_count(index):
        number, loose = roster[index]
        return sum(map(len, shared[number])) // 2 + sum(loose)

    possible = sorted(indices, key=distinction_count)
    valid = next(index for index in possible if index not in issues["parity"])
    invalid = [index for index in possible if index in issues["parity"]]
    controls = []
    for index in [valid, *invalid]:
        number, loose = roster[index]
        holdings = all_holdings(shared[number], loose)
        names = [f"x{place}" for place in range(distinction_count(index))]
        for law in issues:
            forbidden_clauses = []
            for row in holdings:
                for states in product((False, True), repeat=len(row)):
                    forbidden = sum(states) % 2 if law == "parity" else len(set(states)) == 1
                    if forbidden:
                        forbidden_clauses.append(tuple((names[place], not value)
                                                       for place, value in zip(row, states)))
            relation = Relation.from_cnf(forbidden_clauses, names)
            verdicts = []
            for knot, row in enumerate(holdings):
                target = [names[place] for place in row]
                projection = relation.project(target)
                verdict = check_knot(projection, target[:-1], target[-1])
                assert verdict.is_knot == (knot not in issues[law].get(index, {})), (index, law, knot)
                verdicts.append({"K1": verdict.binding, "K2": verdict.loss_on_erasure,
                                 "K3": verdict.coexistence, "allowed_states": len(projection.rows)})
            controls.append({"index": index, "meeting_pattern": number, "loose": loose,
                             "law": law, "holdings": holdings, "verdicts_in_start_order": verdicts})
    return controls


def saved_kind(counts, ending):
    if ending.startswith(("stalls", "closes")):
        return ending.split()[0]
    if len(counts) < 10:
        return "unread"
    differences = counts[-8:]
    for dimension in range(1, 5):
        if differences[0] > 0 and len(set(differences)) == 1:
            return f"dim {dimension}"
        differences = [b - a for a, b in zip(differences, differences[1:])]
    ratios = [Fraction(b, a) for a, b in zip(counts[-5:], counts[-4:])]
    if min(ratios) > Fraction(105, 100) and max(ratios) - min(ratios) < Fraction(1, 100):
        return f"rate {float(ratios[-1]):.2f}"
    return "unread"


def read_case(raw, index, law, roster, shared):
    number, loose = roster[index]
    assert (raw["index"], raw["graph"], tuple(raw["loose"])) == (index, number, loose), index
    assert raw["stars"] == all_holdings(shared[number], loose), index
    assert (raw["n knots"], raw["knot law"]) == (KNOTS, law), index
    counts = [row["n"] for row in raw["rows"]]
    ending = raw["end"]
    knots = KNOTS + sum(counts)
    assert all(count > 0 for count in counts) and len(counts) <= HORIZON and raw["knots"] == knots, index
    if ending == "rounds":
        assert len(counts) == HORIZON and knots <= CAP, index
    elif ending == "bound":
        assert knots > CAP >= knots - counts[-1], index
    else:
        assert ending in {f"stalls at round {len(counts) + 1}", f"closes at round {len(counts) + 1}",
                          "guard"}, index
        assert knots <= CAP and len(counts) < HORIZON, index
    assert saved_kind(counts, ending) == raw["kind"], index
    return raw


def archive(path, order, law, roster, shared, pilot):
    source = json_lines(path)
    if pilot:
        source = islice(source, len(order))
    return {index: read_case(row, index, law, roster, shared)
            for row, index in zip(source, order, strict=True)}


def immutable(value):
    if isinstance(value, list):
        return tuple(map(immutable, value))
    return value


def read_cut(rows, dimension, reading):
    counts = [{immutable(kind): count for kind, count in row[reading]} for row in rows]
    assert all(sum(row.values()) == raw["n"] for row, raw in zip(counts, rows, strict=True))
    coefficients = [(-1) ** (dimension - step) * comb(dimension, step)
                    for step in range(dimension + 1)]
    for end in range(len(counts), dimension, -1):
        window = counts[end - dimension - 1:end]
        kinds = set().union(*window)
        if any(sum(coef * row.get(kind, 0) for coef, row in zip(coefficients, window)) for kind in kinds):
            return max(3, dimension, end)
    return max(3, dimension)


def classify_by_saved_rounds(run_by_index):
    classifications = {}
    for index, run in run_by_index.items():
        label = run["kind"]
        readings = {}
        if label.startswith("dim "):
            dimension = int(label.split()[1])
            rows = run["rows"]
            totals = [row["n"] for row in rows]
            trough = max((r for r, (a, b) in enumerate(zip(totals, totals[1:]), 2) if b < a), default=1)
            for reading, (m_offset, t_offset) in READINGS.items():
                cut = read_cut(rows, dimension, reading)
                checkable = len(rows) == HORIZON and cut <= HORIZON - max(2, dimension)
                late = checkable and cut > run["M"] + m_offset
                upper = max(run["M"] + m_offset, trough + t_offset)
                readings[reading] = {"checkable": checkable, "late": late, "K": cut,
                                     "point_miss": late and cut != trough + t_offset,
                                     "bound_miss": checkable and cut > upper,
                                     "bound_tight": checkable and cut == upper}
        classifications[index] = readings
    return classifications


def denominator(classifications, admitted, weights):
    counts = {reading: Counter() for reading in READINGS}
    numbered = {reading: Counter() for reading in READINGS}
    for index in admitted:
        for reading, items in classifications[index].items():
            outcomes = {"dimension": True, "censored": not items["checkable"],
                        "checkable": items["checkable"], "late": items["late"],
                        "point_miss": items["point_miss"], "bound_miss": items["bound_miss"],
                        "bound_tight": items["bound_tight"]}
            for outcome, flag in outcomes.items():
                counts[reading][outcome] += flag
                numbered[reading][outcome] += weights[index] * flag
    return {"census_weights": counts, "numbered_knot_weights": numbered}


def paired_denominators(classifications, eligible):
    denominators = {}
    for reading in READINGS:
        denominators[reading] = {}
        for outcome in ("checkable", "late", "point_miss", "bound_miss"):
            qualifying = [{index for index in eligible[law]
                           if classifications[law][index].get(reading, {}).get(outcome, False)}
                          for law in ("nae", "parity")]
            first, second = qualifying
            denominators[reading][outcome] = {"both": len(first & second), "nae_only": len(first - second),
                                              "parity_only": len(second - first), "distinct": len(first | second)}
    return denominators


def cross_law(runs, classifications, admitted):
    nae, parity = (runs[law] for law in ("nae", "parity"))
    pairs = Counter()
    exact, prior_to_closure = 0, 0
    for index, first in nae.items():
        second = parity[index]
        pairs[first["kind"], second["kind"]] += 1
        exact += all(first[key] == second[key] for key in ("rows", "M", "end", "knots"))
        if second["kind"] == "closes":
            before = len(second["rows"]) - 1
            prior_to_closure += first["rows"][:before] == second["rows"][:before]
    return {"paired_kinds_nae_then_parity": {f"{a} / {b}": count for (a, b), count in sorted(pairs.items())},
            "same_views_M_and_run_ending": exact, "same_views_before_parity_closing_birth": prior_to_closure,
            "paired_denominators": paired_denominators(classifications, runs),
            "paired_denominators_among_admitted_starts": paired_denominators(classifications, admitted)}


def earlier_balance(roster, current, issues, pilot):
    seen, compared, mismatch = set(), Counter(), []
    status_at_index = {}
    blocks = 0
    for path in (BALANCE / "results.jsonl.gz", BALANCE / "extra_blocks.jsonl"):
        for block in json_lines(path):
            if block["status"] != "ok" or not block["case"].startswith("n6-"):
                continue
            blocks += 1
            if pilot and blocks > 8:
                break
            result = block["result"]
            assert (result["rounds"], result["cap"]) == (10, 1_500)
            offset = 200 * result["block"] + block.get("start_range", [0])[0]
            for index, case in enumerate(result["starts"], offset):
                assert roster[index] == (case["g"], tuple(case["loose"])) and index not in seen, index
                seen.add(index)
                if not pilot or index in current:
                    failed = set(issues["parity"].get(index, {}))
                    assert case["set_aside"] == bool(failed), index
                    assert failed == set(case["kt"]["rank_fail"]) == set(case["kt"]["cut_fail"]), index
                if case["set_aside"]:
                    status_at_index[index] = "set aside at starting parity knot test"
                    continue
                old = case["laws"]["ordinary"]
                if old.get("not_completed"):
                    status_at_index[index] = "ordinary parity run incomplete"
                    continue
                status_at_index[index] = "ordinary parity run completed"
                if index in current:
                    total = KNOTS
                    for row in current[index]["rows"][:old["rounds"]]:
                        total += row["n"]
                        if total > result["cap"]:
                            break
                    compared["total at earlier stop compared"] += 1
                    if (old["knots"], old["cut"]) != (total, total > result["cap"]):
                        mismatch.append({"index": index, "earlier_total": old["knots"], "current_prefix": total})
    if not pilot:
        assert len(seen) == len(roster)
    compared["total at earlier stop agreed"] = compared["total at earlier stop compared"] - len(mismatch)
    return {"census": Counter(status_at_index.values()),
            "current_sample": Counter(status_at_index[i] for i in current if i in seen),
            "current_indices_with_earlier_completed_ordinary_parity_run": sorted(
                i for i in current if status_at_index.get(i) == "ordinary parity run completed"
            ), "prior_stop_comparison": compared, "prior_stop_disagreements": mismatch}


def earlier_descent(roster, current, previous, issues, pilot):
    with gzip.open(DESCENT, "rt") as source:
        records = json.load(source)["six_rows"]
    if pilot:
        records = records[:PILOT_SIZE]
    observed = [row["idx6"] for row in records]
    assert len(set(observed)) == len(observed)
    if not pilot:
        order = list(range(len(roster)))
        Random("DESCENT-HELD-20261125-001|six|v2").shuffle(order)
        expected = [index for index in order if index not in issues["parity"]][:3_000]
        assert observed == expected[:len(observed)]
    overlap = sorted(set(observed).intersection(current))
    return {"earlier_sample_records_read": len(observed), "overlap_with_current": len(overlap),
            "overlap_with_predecessor": len(set(observed).intersection(previous)),
            "overlap_with_current_indices": overlap}


def old_two_law_start(seed):
    # The earlier not-all-equal growth referee used this sampler from the
    # cluster-rule referee. Recreate the draws without importing either study.
    draw = Random(seed)
    while True:
        places = [draw.randint(3, 5) for _ in range(KNOTS)]
        loose = places.copy()
        meetings = Counter()
        for _ in range(draw.randint(5, 12)):
            first, second = draw.choice(PAIRS)
            if loose[first] and loose[second]:
                loose[first] -= 1
                loose[second] -= 1
                meetings[first, second] += 1
        if connected(neighbours(meetings)):
            return meetings, loose


def earlier_two_laws(roster, shared, current, previous, pilot):
    numberings, symmetries = {}, {}
    relabellings = list(permutations(range(KNOTS)))
    for number, holdings in shared.items():
        pairs = [(a, b) for a, b in PAIRS if set(holdings[a]).intersection(holdings[b])]
        base = sum(PAIR_BITS[pair] for pair in pairs)
        symmetries[number] = []
        for order in relabellings:
            mask = numbered_meetings(pairs, order)
            numberings[mask] = (number, order)
            if mask == base:
                symmetries[number].append(order)

    prior_count = json.loads(EARLIER_TWO_LAWS.read_text())["six"]["starts"]
    seeds = range(80_000, 80_000 + (PILOT_SIZE if pilot else prior_count))
    index_by_start = {start: index for index, start in enumerate(roster)}
    frame_matches = []
    for seed in seeds:
        meetings, loose = old_two_law_start(seed)
        if max(meetings.values()) > 1 or max(loose) > 3 or not any(loose):
            continue
        number, order = numberings[sum(PAIR_BITS[pair] for pair in meetings)]
        atlas_loose = tuple(loose[knot] for knot in order)
        representative = min(tuple(atlas_loose[knot] for knot in symmetry) for symmetry in symmetries[number])
        index = index_by_start[number, representative]
        frame_matches.append((seed, index))

    matched_indices = {index for _, index in frame_matches}
    current_set, previous_set = set(current), set(previous)
    overlaps = matched_indices.intersection(current_set)
    return {
        "method": "Regenerated the earlier sample from its seeds and compared starts up to renaming. "
                  "The older result keeps totals for those seeds, with no trace for individual starts.",
        "comparison_sample": "The not-all-equal growth referee's six-knot sample under both laws, "
                             "through 14 rounds or 3,000 knots.",
        "prior_sample_draws_recreated": len(seeds),
        "earlier_draws_in_current_census_frame": len(frame_matches),
        "distinct_earlier_draws_in_current_census_frame": len(matched_indices),
        "overlap_with_current": len(overlaps),
        "overlap_with_predecessor": len(matched_indices.intersection(previous_set)),
        "overlap_with_current_indices": sorted(overlaps),
        "overlap_source_seeds_and_indices": [(seed, index) for seed, index in frame_matches if index in overlaps],
    }


def main(pilot):
    start = before = perf_counter()
    timing = {}
    roster, weights, shared, frame = census()
    old_seed, new_seed = 20261126, 20261127
    previous = Random(old_seed).sample(range(len(roster)), 1_000)
    previous_set = set(previous)
    remaining = [i for i in range(len(roster)) if i not in previous_set]
    current = Random(new_seed).sample(remaining, 2_000)
    assert len(set(current)) == len(current) and not set(current).intersection(previous)
    if pilot:
        current, previous = current[:PILOT_SIZE], previous[:PILOT_SIZE]
    timing["census_and_sampling"] = round(perf_counter() - before, 4)

    before = perf_counter()
    issues = admissions(roster, shared, current if pilot else range(len(roster)))
    controls = canonical_control(roster, shared, current, issues)
    timing["admission_and_direct_control"] = round(perf_counter() - before, 4)

    before = perf_counter()
    kinds, runs, reviews, classifications, admitted = {}, {}, {}, {}, {}
    for law, suffix in (("nae", "nae"), ("parity", "par")):
        archive(SETTLING / f"grown_g6_{suffix}.jsonl.gz", previous, law, roster, shared, pilot)
        runs[law] = archive(STUDY / f"grown_fresh_{law}.jsonl.gz", current, law, roster, shared, pilot)
        kinds[law] = Counter(row["kind"] for row in runs[law].values())
        admitted[law] = set(current) - issues[law].keys()
        classifications[law] = classify_by_saved_rounds(runs[law])
        baseline = denominator(classifications[law], current, weights)
        reviewed = denominator(classifications[law], admitted[law], weights)
        reviews[law] = {"archive_kind_counts": kinds[law], "admitted_start_count": len(admitted[law]),
                        "structural_archive_denominators": baseline, "admitted_denominators": reviewed,
                        "not_admitted": [{"index": i, "meeting_pattern": roster[i][0], "loose": roster[i][1],
                                          "claimed_kind": runs[law][i]["kind"], "knot_test": issues[law][i],
                                          "readings": classifications[law][i]}
                                         for i in current if i in issues[law]]}
    pair_counts = cross_law(runs, classifications, admitted)
    timing["archive_identity_and_law_denominators"] = round(perf_counter() - before, 4)

    before = perf_counter()
    balance = earlier_balance(roster, runs["parity"], issues, pilot)
    descent = earlier_descent(roster, current, previous, issues, pilot)
    earlier_dual = earlier_two_laws(roster, shared, current, previous, pilot)
    overlaps = {"earlier_ordinary_parity": set(balance["current_indices_with_earlier_completed_ordinary_parity_run"]),
                "earlier_waiting_law_sample": set(descent["overlap_with_current_indices"]),
                "earlier_two_law_sample": set(earlier_dual["overlap_with_current_indices"])}
    prior_late = {source: {law: {reading: len({i for i in indices
                                             if classifications[law][i].get(reading, {}).get("late")})
                                for reading in READINGS} for law in runs}
                  for source, indices in overlaps.items()}
    timing["earlier_run_overlap"] = round(perf_counter() - before, 4)
    return {
        "scope": "timing pilot over archive and admission prefixes" if pilot else "full recorded sample and initial census admission",
        "census_source": "The shared graph atlas supplies the historical numbering and order. This script independently "
                         "enumerates connected numbered meeting patterns and loose-count renamings, and checks coverage.",
        "source_archive_method": "No growth or reading program was imported. The two historical sample archives and the "
                                 "two current archives were compared against the generated identities in order. Cut checks "
                                 "use integer differences on the saved views and the saved value of M.",
        "frame": frame,
        "sampling": {"old_seed": old_seed, "new_seed": new_seed, "sampled_without_replacement": True,
                     "eligible_after_excluding_predecessor": len(remaining), "current_archive_records_per_law": len(current),
                     "verified_overlap_with_predecessor": 0, "previous_archive_records_per_law": len(previous),
                     "current_identity_order_sha256": signature([roster[i] for i in current]),
                     "current_indices_in_order": current, "current_weight_if_knots_were_numbered": sum(weights[i] for i in current)},
        "frame_failures_of_start_admission": {law: {"starts": len(by_index), "starting_rules": sum(map(len, by_index.values()))}
                                              for law, by_index in issues.items()},
        "starts_tested_for_admission_under_each_law": len(current) if pilot else len(roster),
        "canonical_direct_controls": controls,
        "current_laws": reviews,
        "law_overlap": pair_counts,
        "earlier_ordinary_parity_census": balance,
        "earlier_waiting_law_six_knot_sample": descent,
        "earlier_six_knot_sample_under_both_laws": earlier_dual,
        "earlier_runs_among_current_late_starts": prior_late,
        "seconds_by_stage": timing,
        "seconds": round(perf_counter() - start, 4),
        "peak_rss_kib": getrusage(RUSAGE_SELF).ru_maxrss,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot", action="store_true")
    result = main(parser.parse_args().pilot)
    destination = HERE / ("sample_check_pilot.json" if result["scope"].startswith("timing") else "sample_check.json")
    destination.write_text(json.dumps(result, indent=2) + "\n")
    print(destination.name, result["seconds"], result["peak_rss_kib"])
