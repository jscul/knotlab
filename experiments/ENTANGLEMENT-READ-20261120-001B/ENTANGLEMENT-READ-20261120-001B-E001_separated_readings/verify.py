"""Check stored scores and re-count the minimum and archived controls independently."""

import argparse
from collections import Counter, deque
from fractions import Fraction
import gzip
from itertools import combinations, product
import json
from math import prod
from pathlib import Path


HERE = Path(__file__).resolve().parent
DEFAULT = HERE.parents[2] / "artifacts" / HERE.parent.name / HERE.name
SETTINGS = tuple(product((0, 1), repeat=2))


def pack(values):
    index = 0
    for value in values:
        index = 2 * index + value
    return index


def as_fraction(value):
    return None if value is None else Fraction(*value)


def probability(counts):
    total = sum(counts)
    return [Fraction(n, total) for n in counts] if total else None


def variation(left, right):
    left, right = probability(left), probability(right)
    if left is None or right is None:
        return None
    return sum((abs(a - b) for a, b in zip(left, right, strict=True)), Fraction()) / 2


def product_counts(rows, columns):
    return [a * b for a, b in product(rows, columns)]


def independent_contexts(counts, embodied, width):
    states = tuple(product((0, 1), repeat=2 * width))
    all_pairs = [0] * 16
    for state, weight in zip(states, counts, strict=True):
        a, b = state[:2], state[width:width + 2]
        all_pairs[pack(a + b)] += weight
    for x, y in SETTINGS:
        pair_joint = [0] * 16
        outcome_joint = {"I": [0] * 4, "II": [0] * 4}
        filtered = [0] * len(states)
        for i, (state, weight) in enumerate(zip(states, counts, strict=True)):
            left, right = state[:width], state[width:]
            if embodied and (left[-1], right[-1]) != (x, y):
                continue
            filtered[i] = weight
            pair_joint[pack(left[:2] + right[:2])] += weight
            outcome_joint["I"][pack((left[x], right[y]))] += weight
            outcome_joint["II"][pack((left[:2] == (x, x), right[:2] == (y, y)))] += weight
        yield filtered, pair_joint, all_pairs, outcome_joint


def marginals(joint, size):
    return [[sum(joint[i:i + size]) for i in range(0, len(joint), size)],
            [sum(joint[i::size]) for i in range(size)]]


def check_context(counts, context, direct, arm, band):
    filtered, pair_joint, all_pairs, outcome_joint = direct
    weight = sum(filtered)
    assert context["weight"] == weight
    assert context["pair_joint"] == pair_joint
    pairs = marginals(pair_joint, 4)
    assert context["pair_marginals"] == pairs
    assert as_fraction(context["mass"]) == (Fraction(1, 4) if arm == "external" else Fraction(weight, sum(counts)))
    assert as_fraction(context["all_marks_tv_from_common"]) == variation(filtered, counts)
    assert as_fraction(context["joint_pairs_tv_from_common"]) == variation(pair_joint, all_pairs)
    joint_tv = variation(pair_joint, product_counts(*pairs))
    assert as_fraction(context["joint_pairs_tv_from_product"]) == joint_tv
    if band == "no_chain":
        assert joint_tv in (None, 0)
    for reading, joint in outcome_joint.items():
        assert context[reading]["joint"] == joint
        expected = sum((-1) ** (a + b) * mass for (a, b), mass in zip(SETTINGS, joint, strict=True))
        assert as_fraction(context[reading]["correlation"]) == (Fraction(expected, weight) if weight else None)
        outputs = marginals(joint, 2)
        assert context[reading]["outcome_marginals"] == outputs
        assert as_fraction(context[reading]["joint_tv_from_product"]) == variation(joint, product_counts(*outputs))


def check_remotes(tables, contexts, field):
    for side in (0, 1):
        for own in (0, 1):
            before, after = (2 * own, 2 * own + 1) if side == 0 else (own, own + 2)
            assert as_fraction(tables[side][own]) == variation(field(contexts[before])[side], field(contexts[after])[side])


def check_scores(cells, width, band):
    counts = cells["counts"]
    assert cells["total"] == sum(counts) > 0
    assert all(count >= 0 for count in counts)
    assert set(cells["arms"]) == ({"external", "embodied"} if width == 3 else {"external"})
    if band == "no_chain":
        assert variation(counts, product_counts(*marginals(counts, 1 << width))) == 0
    for arm, arms in cells["arms"].items():
        contexts = arms["contexts"]
        assert [tuple(row["settings"]) for row in contexts] == list(SETTINGS)
        for context, direct in zip(contexts, independent_contexts(counts, arm == "embodied", width), strict=True):
            check_context(counts, context, direct, arm, band)
        check_remotes(arms["pair_marginal_remote_tv"], contexts, lambda context: context["pair_marginals"])
        for reading in ("I", "II"):
            check_remotes(arms[reading]["outcome_marginal_remote_tv"], contexts,
                          lambda context: context[reading]["outcome_marginals"])
            scores = arms[reading]["chsh_sign_scores"]
            assert len({tuple(row["signs"]) for row in scores}) == 8
            corrs = [as_fraction(context[reading]["correlation"]) for context in contexts]
            if None in corrs:
                assert arm == "embodied"
                assert arms[reading]["signed_s"] is None and arms[reading]["maximum"] is None
                assert all(row["value"] is None for row in scores)
                continue
            assert as_fraction(arms[reading]["signed_s"]) == sum(corrs[:3]) - corrs[3]
            for row in scores:
                assert set(row["signs"]) <= {-1, 1} and prod(row["signs"]) == -1
                assert as_fraction(row["value"]) == sum(a * b for a, b in zip(corrs, row["signs"], strict=True))
            best = as_fraction(arms[reading]["maximum"])
            assert best == max(as_fraction(row["value"]) for row in scores)
            if arm == "external" or band == "no_chain":
                assert best <= 2
                assert arms["pair_marginal_remote_tv"] == [[[0, 1]] * 2] * 2
                assert arms[reading]["outcome_marginal_remote_tv"] == [[[0, 1]] * 2] * 2


def adjacency_of(supports):
    adjacency = {bit: set() for bit in set().union(*map(set, supports))}
    for support in supports:
        for a, b in combinations(support, 2):
            adjacency[a].add(b)
            adjacency[b].add(a)
    return adjacency


def steps_between(graph, left, right):
    pending = deque((value, 0) for value in left)
    seen = set(left)
    while pending:
        bit, distance = pending.popleft()
        if bit in right:
            return distance
        following = graph[bit] - seen
        seen.update(following)
        pending.extend((other, distance + 1) for other in following)
    return None


def check_placement_enumeration(source, stage, graph, counts):
    supports = stage["supports"]
    support_ids = sorted((i for i, row in enumerate(stage["support_certificates"]) if row["eligible"]),
                         key=lambda i: (supports[i], i))
    old = source["old_distinctions"]
    infinity = len(graph) + 1
    distance = {}
    for a, b in product(graph, repeat=2):
        steps = steps_between(graph, (a,), (b,))
        distance[a, b] = infinity if steps is None else steps
    for family, width in (("external_pairs", 2), ("six_marks", 3)):
        side = {i: sorted(tuple(pair) + tuple(selector) for pair in combinations(supports[i], 2)
                          for selector in combinations(set(supports[i]) - set(pair), width - 2)) for i in support_ids}
        expected = Counter()
        first = {}
        for left, right in combinations(support_ids, 2):
            for alice in side[left]:
                nearest = {bit: min(distance[a, bit] for a in alice) for bit in supports[right]}
                alice_new = max(alice) >= old
                for bob in side[right]:
                    cross = min(map(nearest.__getitem__, bob))
                    if cross < 2:
                        expected["repeated_mark" if cross == 0 else "cross_step_one"] += 1
                        continue
                    band = "no_chain" if cross == infinity else "2" if cross == 2 else "finite_3_or_more"
                    key = band, "newborn" if alice_new or max(bob) >= old else "old_only"
                    expected[key] += 1
                    first.setdefault(key, ([left, right], list(alice), list(bob)))
        roster = stage[family]
        assert roster["candidate_count"] == sum(expected.values())
        counts["placement_candidates"] += roster["candidate_count"]
        assert all(expected[key] == total for key, total in roster["excluded"].items())
        for slot in roster["slots"]:
            key = slot["band"], slot["origin"]
            assert expected[key] == slot["eligible"]
            fixed = (source["name"] == "two_sharing_one" and key == ("2", "old_only") and width == 2
                     or source["name"] == "two_disjoint" and key == ("no_chain", "old_only"))
            if slot["eligible"] and not fixed:
                placement = slot["placement"]
                assert first[key] == (placement["supports"], placement["alice"], placement["bob"])


def selected(stage):
    for family, width in (("external_pairs", 2), ("six_marks", 3)):
        roster = stage[family]
        eligible = sum(slot["eligible"] for slot in roster["slots"])
        assert roster["candidate_count"] == eligible + sum(roster["excluded"].values())
        for slot in roster["slots"]:
            assert bool(slot["eligible"]) == (slot["placement"] is not None)
            if slot["eligible"]:
                yield slot, width


def check_record(source, law, counts):
    history = source["laws"][law]
    start_total = history[0]["complete_assignments"]
    for stage in history:
        assert stage["status"] == "measured_stage"
        supports = stage["supports"]
        graph = adjacency_of(supports)
        check_placement_enumeration(source, stage, graph, counts)
        counts["stage_laws"] += 1
        for slot, width in selected(stage):
            counts["placements"] += 1
            placement = slot["placement"]
            marks = placement["alice"] + placement["bob"]
            assert len(set(marks)) == 2 * width
            assert (max(marks) >= source["old_distinctions"]) == (slot["origin"] == "newborn")
            assert marks == slot["result"]["mark_order"]
            for index, marks_here in zip(placement["supports"], (placement["alice"], placement["bob"]), strict=True):
                support = set(supports[index])
                certificate = stage["support_certificates"][index]
                assert set(marks_here) <= support and certificate["eligible"] and certificate["full_law"]
            steps = steps_between(graph, placement["alice"], placement["bob"])
            assert steps == placement["cross_steps"]
            assert steps is None or steps >= 2
            assert slot["band"] == ("no_chain" if steps is None else "2" if steps == 2 else "finite_3_or_more")
            weighted = slot["result"]["weightings"]
            assert set(weighted) == {"U", "L", "T"}
            assert weighted["U"]["total"] == stage["complete_assignments"]
            external = weighted["U"]["arms"]["external"]["contexts"]
            assert all(all(side) for side in external[0]["pair_marginals"])
            assert weighted["L"]["total"] == start_total * weighted["L"]["integer_units_per_unscaled_mass"]
            raw = weighted["U"]["counts"]
            tilted = weighted["T"]["counts"]
            assert tilted == raw[:len(raw) // 2] + [2 * value for value in raw[len(raw) // 2:]]
            assert [n > 0 for n in raw] == [n > 0 for n in weighted["L"]["counts"]]
            if law == "parity" or stage["age"] == 0:
                assert raw == weighted["L"]["counts"]
            for name, cells in weighted.items():
                counts["weighted_tables"] += 1
                check_scores(cells, width, slot["band"])
                if stage["age"]:
                    prior = cells["old_mark_check"]
                    assert prior["same_support"]
                    assert as_fraction(prior["mass_tv_from_start_u"]) == variation(prior["start_counts"], prior["grown_counts"])
                    if name == "L":
                        assert as_fraction(prior["mass_tv_from_start_u"]) == 0


def brute_counts(supports, law):
    rows = [sum(1 << bit for bit in support) for support in supports]
    width = max(map(max, supports)) + 1
    if law == "parity":
        return [assignment for assignment in range(1 << width)
                if all((assignment & row).bit_count() % 2 == 0 for row in rows)]
    return [assignment for assignment in range(1 << width) if all(assignment & row not in (0, row) for row in rows)]


def check_minimum(source, law, counts):
    history = source["laws"][law]
    old = (1 << source["old_distinctions"]) - 1
    for stage in history:
        assignments = brute_counts(stage["supports"], law)
        extensions = Counter(state & old for state in assignments)
        assert len(assignments) == stage["complete_assignments"]
        assert len(extensions) == history[0]["complete_assignments"]
        for support, certificate in zip(stage["supports"], stage["support_certificates"], strict=True):
            support_mask = sum(1 << bit for bit in support)
            assert len({state & support_mask for state in assignments}) == certificate["projected_count"]
        for slot, _ in selected(stage):
            result = slot["result"]
            marks = result["mark_order"]
            uniform = [0] * (1 << len(marks))
            lifted = [Fraction()] * (1 << len(marks))
            for assignment in assignments:
                at = pack((assignment >> bit) & 1 for bit in marks)
                uniform[at] += 1
                lifted[at] += Fraction(1, extensions[assignment & old])
            counts["brute_verified_placements"] += 1
            weightings = result["weightings"]
            assert uniform == weightings["U"]["counts"]
            unit = weightings["L"]["integer_units_per_unscaled_mass"]
            assert lifted == [Fraction(count, unit) for count in weightings["L"]["counts"]]
            if source["name"] == "two_sharing_one" and law == "parity" and stage["age"] == 0:
                contexts = weightings["U"]["arms"]["external"]["contexts"]
                assert all(row["I"]["joint"] == [2, 2, 2, 2] and row["II"]["joint"] == [5, 1, 1, 1] for row in contexts)


def inclusion_exclusion_terms(old_supports):
    """Expand the old not-all-equal rows as one minus each monochrome event."""
    old_masks = [sum(1 << bit for bit in support) for support in old_supports]
    for failures in product((None, 0, 1), repeat=len(old_supports)):
        forced = [0, 0]
        for index, value in enumerate(failures):
            if value is not None:
                forced[value] |= old_masks[index]
        if not forced[0] & forced[1]:
            yield *forced, (-1) ** sum(value is not None for value in failures)


def archive_recount(old_supports, stage, marks, weighting, scale):
    """Use inclusion-exclusion only on old rows, then count within disjoint births."""
    births = stage.get("growth", {}).get("births", [])
    birth_masks = [(sum(1 << d for d in birth["consumed"]), sum(1 << d for d in birth["fresh"])) for birth in births]
    all_bits = sum(1 << d for d in set().union(*map(set, stage["supports"])))
    unused = all_bits ^ sum(consumed + fresh for consumed, fresh in birth_masks)
    terms = list(inclusion_exclusion_terms(old_supports))
    answer = []
    for values in product((0, 1), repeat=len(marks)):
        pins = [sum(1 << d for d, value in zip(marks, values, strict=True) if value == color) for color in (0, 1)]
        query_mask = pins[0] | pins[1]
        total = 0
        for old_zeros, old_ones, sign in terms:
            if old_zeros & pins[1] or old_ones & pins[0]:
                continue
            zeros, ones = old_zeros | pins[0], old_ones | pins[1]
            fixed = zeros | ones
            weight = sign * (1 << (unused & ~fixed).bit_count())
            units = 1
            for consumed, fresh in birth_masks:
                if weighting == "U":
                    support = consumed | fresh
                    weight *= (1 << (support & ~fixed).bit_count()) - int(not support & zeros) - int(not support & ones)
                else:
                    old_choices = 1 << (consumed & ~fixed).bit_count()
                    if not fresh & query_mask:
                        weight *= old_choices
                        continue
                    all_zero = int(not consumed & ones)
                    all_one = int(not consumed & zeros)
                    grown_choices = 1 << (fresh & ~fixed).bit_count()
                    full_choices = 1 << fresh.bit_count()
                    units *= full_choices * (full_choices - 1)
                    nonconstant = old_choices - all_zero - all_one
                    weight *= (nonconstant * grown_choices * (full_choices - 1)
                               + full_choices * (all_zero * (grown_choices - int(not fresh & ones))
                                                 + all_one * (grown_choices - int(not fresh & zeros))))
            assert units == scale
            total += weight
        answer.append(total)
    return answer


def check_archive(source, counts):
    history = source["laws"]["nae"]
    old = history[0]["supports"]
    for stage in history:
        assert archive_recount(old, stage, (), "U", 1) == [stage["complete_assignments"]]
        eligible = list(selected(stage))
        # Fixed order from the frozen report. Prefer a newborn and use the six-mark table when present.
        preferred = max(eligible, key=lambda row: (row[0]["origin"] == "newborn", row[1]))[0]
        result = preferred["result"]
        for weighting in ("U", "L"):
            cell = result["weightings"][weighting]
            actual = archive_recount(old, stage, result["mark_order"], weighting, cell["integer_units_per_unscaled_mass"])
            assert actual == cell["counts"]
            counts["archive_verified_histograms"] += 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifacts", type=Path, default=DEFAULT)
    args = parser.parse_args()
    data = json.loads(gzip.decompress((args.artifacts / "exact_readings.json.gz").read_bytes()))
    counts = Counter()
    for source in data["sources"]:
        for law in source["laws"]:
            check_record(source, law, counts)
            if source["group"] == "controls":
                check_minimum(source, law, counts)
        if source["group"] == "archive":
            check_archive(source, counts)
    print(json.dumps(dict(sorted(counts.items()))))


if __name__ == "__main__":
    main()
