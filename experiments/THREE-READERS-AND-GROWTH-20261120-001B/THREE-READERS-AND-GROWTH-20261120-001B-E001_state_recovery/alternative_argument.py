"""Check the single-flip and forcing proofs against complete state tables."""

from collections import Counter
from itertools import combinations
from pathlib import Path
import gzip
import json


ROOT = Path(__file__).resolve().parents[3]
TICKET = "THREE-READERS-AND-GROWTH-20261120-001B"
EARLIER = "READS-HOLDERS-SOURCES-20261120-001B"


def read_cases(ticket, family):
    path = ROOT / "artifacts" / ticket / f"{ticket}-E001_{family}" / "census_cases.json.gz"
    with gzip.open(path, "rt") as stream:
        return json.load(stream)


def support_mask(names):
    return sum(1 << name for name in names)


def allowed_words(width, holders):
    return [
        word for word in range(1 << width)
        if all(0 < word & holder < holder for holder in holders)
    ]


def full_local_law(words, holder):
    observed = {word & holder for word in words}
    return 0 not in observed and holder not in observed and len(observed) == 2 ** holder.bit_count() - 2


def pairwise_candidates(width, words, neighbours):
    # A set can be all ones exactly when it is inside an allowed word.
    can_be_one = [False] * (1 << width)
    for word in words:
        can_be_one[word] = True
    for variable in range(width):
        bit = 1 << variable
        for mask in range(1 << width):
            if mask & bit == 0 and can_be_one[mask | bit]:
                can_be_one[mask] = True
    found = set()
    for mask in range(1 << width):
        if mask.bit_count() < 3 or can_be_one[mask]:
            continue
        names = [name for name in range(width) if mask >> name & 1]
        if not all(can_be_one[mask ^ (1 << name)] for name in names):
            continue
        if all(mask & ~neighbours[name] == 0 for name in names) and full_local_law(words, mask):
            found.add(mask)
    return found


def classify_candidates(width, holders):
    predicted = set(holders)
    if len(holders) != 4:
        return predicted
    if not all(sum((holder >> name) & 1 for holder in holders) == 2 for name in range(width)):
        return predicted
    if not all(first & second for first, second in combinations(holders, 2)):
        return predicted
    all_names = (1 << width) - 1
    for centre in holders:
        if all((centre & other).bit_count() == 1 for other in holders if other != centre):
            predicted.add(all_names ^ centre)
    return predicted


def check_presentation(width, state_bits, holders):
    words = [word for word in range(1 << width) if state_bits >> word & 1]
    all_names = (1 << width) - 1
    assert words == allowed_words(width, holders)
    assert all(full_local_law(words, holder) for holder in holders)
    # Locate a third completion of the two positions with the very same exterior.
    zero_at = [
        sum(1 << word for word in range(1 << width) if not word >> name & 1)
        for name in range(width)
    ]
    observed = [1 << name for name in range(width)]
    for first, second in combinations(range(width), 2):
        x, y = 1 << first, 1 << second
        exterior = zero_at[first] & zero_at[second]
        witnesses = exterior & ~state_bits & (state_bits >> x) & (state_bits >> y) & (state_bits >> (x+y))
        if witnesses:
            observed[first] |= y
            observed[second] |= x

    # Independently gather all repairs of each forbidden word by literal flips.
    repairs = [0] * width
    for word in range(1 << width):
        if state_bits >> word & 1:
            continue
        changes = [
            name for name in range(width)
            if state_bits >> (word ^ (1 << name)) & 1
        ]
        changed_names = support_mask(changes)
        for name in changes:
            repairs[name] |= changed_names

    assert observed == repairs
    loose = []
    for name in range(width):
        holders_here = [holder for holder in holders if holder >> name & 1]
        expected = 0
        for holder in holders_here:
            expected |= holder
        assert observed[name] == expected
        assert full_local_law(words, repairs[name]) == (len(holders_here) == 1)
        if len(holders_here) == 1:
            loose.append(name)

    candidates = pairwise_candidates(width, words, observed)
    assert candidates == classify_candidates(width, holders)
    assert all(mask & ~all_names == 0 for mask in candidates)
    return {
        "words": len(words),
        "loose": loose,
        "pairs_that_share_a_holder": sum(mask.bit_count() - 1 for mask in observed) // 2,
        "extra_pairwise_candidates": sorted(candidates - set(holders)),
    }


def built_controls():
    result = {}
    for copies in (1, 2, 3, 6):
        pairs = [(0, 1)] * copies + list(combinations(range(4), 2))[1:]
        width = len(pairs)
        stars = [
            support_mask(i for i, pair in enumerate(pairs) if holder in pair)
            for holder in range(4)
        ]
        complements = [((1 << width) - 1) ^ holder for holder in stars]
        words = allowed_words(width, stars)
        other_words = allowed_words(width, complements)
        diagnostics = check_presentation(width, sum(1 << word for word in words), stars)
        # Each displayed family separately has the full local law and essential rules.
        for family, own_words in ((stars, words), (complements, other_words)):
            assert all(full_local_law(own_words, holder) for holder in family)
            for index in range(len(family)):
                reduced = family[:index] + family[index + 1:]
                assert len(allowed_words(width, reduced)) > len(own_words)
        lost = sorted(set(words) - set(other_words))
        gained = sorted(set(other_words) - set(words))
        assert bool(lost) == bool(gained) == (copies > 1)
        result[f"four_mutually_meeting_holders_{copies}_at_first_meeting"] = {
            **diagnostics,
            "variable_order": pairs,
            "all_complements_words": len(other_words),
            "words_lost": len(lost),
            "words_gained": len(gained),
            "first_all_complements_only_word": gained[0] if gained else None,
        }
    live = [support_mask(row) for row in ((0, 1, 2, 3), (0, 1, 4), (2, 4, 5))]
    live_words = allowed_words(6, live)
    assert all(len(allowed_words(6, live[:i] + live[i+1:])) > len(live_words) for i in range(3))
    result["three_pairwise_meeting_holders_one_repeated_meeting"] = check_presentation(
        6, sum(1 << word for word in live_words), live
    )
    common = [support_mask(row) for row in ((0, 1, 2), (3, 4, 5), (0, 3, 6))]
    narrow = support_mask((1, 2, 4, 5))
    wide = narrow | (1 << 6)
    base_words = allowed_words(7, common + [narrow])
    assert base_words == allowed_words(7, common + [wide])
    assert len(base_words) == 52 and len(allowed_words(7, common)) == 54
    observed_wide = len({word & wide for word in base_words})
    assert full_local_law(base_words, narrow) and observed_wide == 28
    result["previous_seven_name_five_place_control"] = {
        "words_in_each": len(base_words),
        "words_after_erasing_last_rule": len(allowed_words(7, common)),
        "observed_five_place_words": observed_wide,
        "required_five_place_words": 2 ** wide.bit_count() - 2,
    }
    # Three unshortened ternaries with their individual loose names pinned to zero.
    binary_pairs = [support_mask(row) for row in ((0, 1), (1, 2), (0, 2))]
    pinned = [
        word for word in range(8) if all(word & holder for holder in binary_pairs)
    ]
    assert pinned == [3, 5, 6, 7]
    assert allowed_words(3, binary_pairs) == []
    result["odd_residual_with_three_one_sided_rules"] = pinned
    result["odd_residual_with_three_full_binary_rules_outside_gate"] = []
    return result


def main():
    cases = read_cases(EARLIER, "irredundant")
    cases["10"] = read_cases(TICKET, "state_recovery")
    totals = {}
    for width_string, by_law in cases.items():
        width = int(width_string)
        counts = Counter()
        for case in by_law["nae"]:
            state_bits = int(case["state_words_hex"], 16)
            for presentation in case["presentations"]:
                holders = [support_mask(row) for row in presentation["supports"]]
                result = check_presentation(width, state_bits, holders)
                counts["presentation_representatives"] += 1
                counts["distinctions"] += width
                counts["loose_distinctions"] += len(result["loose"])
                counts["pairs_tested"] += width * (width - 1) // 2
                counts["pairs_that_share_a_holder"] += result["pairs_that_share_a_holder"]
                counts["extra_pairwise_candidates"] += len(result["extra_pairwise_candidates"])
        totals[width] = dict(counts)
    output = {
        "evidence": "Literal comparisons on one representative per physical presentation type.",
        "census": totals,
        "built_controls": built_controls(),
    }
    destination = ROOT / "artifacts" / TICKET / f"{TICKET}-E001_state_recovery" / "alternative_argument.json"
    destination.write_text(json.dumps(output, indent=2) + "\n")
    print(json.dumps(totals, sort_keys=True))


if __name__ == "__main__":
    main()
