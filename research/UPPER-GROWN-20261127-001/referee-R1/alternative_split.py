"""Test disjoint splits and shortenings of the four-place-carrier witness."""

import argparse
from collections import Counter
from functools import lru_cache, reduce
from itertools import combinations, islice, product
import json
from operator import and_

import alternative_growth as base


def read_cells(whole, readings):
    groups = [whole]
    for mask in readings:
        groups = [w for x in groups for w in (x & ~mask, x & mask)]
    return groups


def has_knot_image(present):
    return (0 < len(present) < 8 and
            all(len({w & mask for w in present}) == 4 for mask in (3, 5, 6)))


@lru_cache(None)
def virtual(n):
    whole, values = base.columns(range(n))
    subsets = {}
    all_indices = tuple(range(n))
    for r in range(3, n + 1):
        for parts in combinations(all_indices, r):
            subsets[parts] = read_cells(whole, [values[k] for k in parts])
    upper_choices = []
    signed_masks = {}
    pairs_or_triples = [s for size in (2, 3) for s in combinations(all_indices, size)]
    for s in pairs_or_triples:
        choices = [0] if len(s) == 2 else range(4)
        words = read_cells(whole, [values[k] for k in s])
        signed_masks[s] = [(code, words[code] | words[-1-code]) for code in choices]
    for p, q, r in combinations(pairs_or_triples, 3):
        if len(set(p + q + r)) != len(p + q + r):
            continue
        for readings in product(signed_masks[p], signed_masks[q], signed_masks[r]):
            signs, masks = zip(*readings)
            upper_choices.append(((p, q, r), signs, masks, read_cells(whole, masks)))
    return whole, values, subsets, upper_choices


def virtual_word_mask(rows, lower):
    # The local binary place at i is 2**i, the opposite display order
    # to read_cells, which prints its first reading first.
    masks = read_cells(rows, lower[::-1])
    return sum(1 << i for i, states in enumerate(masks) if states)


def candidates(joint, deleted, n, tally):
    whole, _, subset_masks, upper_choices = virtual(n)
    small_nonfull = []
    # Discard any putative first knot with a constrained pair or singleton.
    for size in (1, 2):
        for s in combinations(range(n), size):
            fibres = read_cells(whole, [virtual(n)[1][x] for x in s])
            if any(not (mask & joint) for mask in fibres):
                small_nonfull.append(s)
    knots = []
    for s, parts in subset_masks.items():
        if any(set(t).issubset(s) for t in small_nonfull):
            continue
        forbidden = [part for part in parts if not (joint & part)]
        if forbidden:
            small_nonfull.append(s)
            knots.append((s, whole ^ sum(forbidden)))
    examples = []
    for raw_carriers, signs, outputs, upper_rows in upper_choices:
        kind = "all_agreement" if signs == (0, 0, 0) else "at_least_one_signed_agreement"
        tally[kind + "_upper_choices"] += 1
        present = [i for i, rows in enumerate(upper_rows) if joint & rows]
        if not has_knot_image(present):
            continue
        tally[kind + "_joint_upper_knot"] += 1
        restored = [i for i, rows in enumerate(upper_rows) if i not in present and deleted & rows]
        if not restored:
            continue
        tally[kind + "_with_a_restored_word_on_birth_deletion"] += 1
        usable = []
        for s, law in knots:
            fibres = subset_masks[s]
            if all(any((joint & f & col) and (joint & f & ~col) for f in fibres) for col in outputs):
                usable.append((s, law))
        conjunction = reduce(and_, (law for _, law in usable), whole)
        for target in restored:
            if conjunction & upper_rows[target]:
                continue
            tally[kind + "_birth_essential_word_forced_by_lower_knots"] += 1
            # Reduce to one inclusion-minimal explanatory family for this word.
            minimal = usable.copy()
            for rule in usable:
                rest = [other for other in minimal if other != rule]
                if not (upper_rows[target] & reduce(and_, (law for _, law in rest), whole)):
                    minimal = rest
            supports = [s for s, _ in minimal]
            reached = {0}
            while True:
                more = reached | {i for i, s in enumerate(supports) if any(set(s) & set(supports[j]) for j in reached)}
                if more == reached:
                    break
                reached = more
            examples.append({"upper_carriers": raw_carriers, "upper_signs": signs,
                             "upper_image": present, "restored_word": target,
                             "essential_lower_supports": supports, "connected": len(reached) == len(supports)})
    return examples


def configurations(carriers, permitted):
    # Split precisely the four-place carrier into two disjoint agreement
    # pairs. Each other carrier may retain two or three of its members.
    a, b, c, d = carriers[0]
    splits = [((a, b), (c, d)), ((a, c), (b, d)), ((a, d), (b, c))]
    choice = [[s for size in (2, 3) for s in combinations(parts, size) if permitted(s)] for parts in carriers[1:]]
    for first, second in splits:
        if permitted(first) and permitted(second):
            for others in product(*choice):
                yield (first, second, *others)


def run(limit):
    _, laws, carriers, _ = base.stage_and_readings(False)
    _, whole, cols, rules, allowed, original, _ = base.source_data(laws)
    relaxed = reduce(and_, rules[:-1], whole)
    @lru_cache(None)
    def reading(s):
        return base.agreement(s, cols, whole)

    @lru_cache(None)
    def permitted(s):
        return all(base.mixed(allowed, [cols[x] for x in law], [reading(s)])[0] for law in laws)

    control_tally = Counter()
    controls = candidates(virtual_word_mask(allowed, original), virtual_word_mask(relaxed, original), 6, control_tally)
    assert any(x["connected"] and len(x["essential_lower_supports"]) == 8 for x in controls)
    all_configs = list(configurations(carriers, permitted))
    tally = Counter()
    witnesses = []
    actual = 0
    for selected in islice(all_configs, limit):
        actual += 1
        lower = [reading(x) for x in selected]
        j = virtual_word_mask(allowed, lower)
        other = virtual_word_mask(relaxed, lower)
        if j == other:
            tally["same_entire_lower_joint_image_on_birth_deletion"] += 1
        for evidence in candidates(j, other, len(lower), tally):
            witnesses.append({"lower_raw_carriers": selected, **evidence})
    return {"qualified_seven_reading_configurations_available": len(all_configs), "read": actual,
            "counts": tally, "witnesses": witnesses, "positive_control_on_unsplit_carrier": controls}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limit", type=int)
    print(json.dumps(run(parser.parse_args().limit), indent=2))
