"""Compare the two prescribed pulse/first-growth orders on the archived five-ring."""

import argparse
import json
import sys
from collections import Counter, defaultdict
from hashlib import sha256
from itertools import combinations
from math import comb, gcd
from pathlib import Path
from runpy import run_path


ROOT = Path(__file__).resolve().parents[3]
MOTION_TICKET = "READS-HOLDERS-SOURCES-20261120-001A"
GROWTH_TICKET = "FREEDOM-CLOCKS-AND-BIRTHS-20261120-001A"


def archives():
    motion_path = ROOT / "experiments" / MOTION_TICKET / f"{MOTION_TICKET}-E001_reads_changes"
    motion = run_path(str(motion_path / "motion.py"))
    growth_path = ROOT / "experiments" / GROWTH_TICKET / f"{GROWTH_TICKET}-E001_freedom"
    sys.path.insert(0, str(growth_path))
    try:
        from ordinary import advance
    finally:
        sys.path.remove(str(growth_path))
    record = motion["motion_stage"].load_case_record("R0")
    return motion, advance, record


def star_rows(rows):
    return tuple(tuple(sorted(row)) for row in rows)


def parity(word, readout):
    return (word & readout).bit_count() % 2


def fair_offer(counts, move):
    updated = counts.copy()
    updated.update({word ^ move: weight for word, weight in counts.items()})
    return updated


def fair_offers(counts, menu):
    for move in menu:
        counts = fair_offer(counts, move)
    return counts


def spectrum(counts, readout):
    return [sum(weight for word, weight in counts.items() if parity(word, readout) == wanted)
            for wanted in (0, 1)]


def explicit_law(counts):
    denominator = sum(counts.values())
    factor = gcd(denominator, *counts.values())
    return {
        "probability_denominator": denominator // factor,
        "numerators_by_word_mask": [[word, counts[word] // factor] for word in sorted(counts)],
    }


def uniform_law(counts):
    assert len(set(counts.values())) == 1
    literal = "\n".join(map(str, sorted(counts))) + "\n"
    return {
        "probability_per_supported_word": [1, len(counts)],
        "word_mask_support_sha256": sha256(literal.encode()).hexdigest(),
        "support_digest_encoding": "ascending decimal masks, each followed by a newline",
    }


def holding_differences(holdings, representatives, mask, number_of_holders):
    seen = []
    for selected in combinations(range(len(holdings)), number_of_holders):
        observed = mask(set().union(*(holdings[i] for i in selected)))
        if any(readout & observed == readout for readout in representatives):
            seen.append(selected)
    return seen


def marginal(counts, observed):
    result = Counter()
    for word, weight in counts.items():
        result[word & observed] += weight
    return result


def readout_receipt(holdings, left, right, readout, motion):
    mask, bits = motion["mask"], motion["bits"]
    dual = motion["all_words"](motion["basis"](map(mask, holdings)))
    characters = {readout ^ equivalent for equivalent in dual}
    assert not dual & characters
    by_size = Counter(readout.bit_count() for readout in characters)
    minimum = min(by_size)
    smallest = sorted(readout for readout in characters if readout.bit_count() == minimum)
    assert minimum == 5 and len(smallest) == 16
    assert not holding_differences(holdings, characters, mask, 1)
    for row in holdings:
        l = marginal(left, mask(row))
        r = marginal(right, mask(row))
        assert explicit_law(l) == explicit_law(r)
        assert len(l) == 2 ** (len(row) - 1) and len(set(l.values())) == 1
    width = max(max(row) for row in holdings) + 1
    return {
        "equivalent_parity_mask_count": len(characters),
        "equivalent_parity_masks_by_size": by_size,
        "minimum_ordinary_read_distinctions": minimum,
        "minimum_readout_supports": [list(bits(r)) for r in smallest],
        "identical_marginals_for_all_subsets_smaller_than_minimum": sum(
            comb(width, i) for i in range(minimum)
        ),
        "one_holder_projections_tested": len(holdings),
        "two_holders_with_different_joint_marginals": holding_differences(
            holdings, characters, mask, 2
        ),
    }


def addressed_pulses(stage, mark, mask):
    minimum = stage.minimum_response(mark, pinned_loose=False)
    assert minimum.listed_all_supports
    pulses = sorted(map(mask, minimum.supports))
    assert len(pulses) == minimum.count
    return pulses


def prepare(extensions, old_pulses, new_pulses):
    before = Counter(word for move in old_pulses for word in extensions[move])
    after = Counter(word ^ move for move in new_pulses for word in extensions[0])
    per_old_count = len(extensions[0])
    assert sum(before.values()) == len(old_pulses) * per_old_count
    assert sum(after.values()) == len(new_pulses) * per_old_count
    return before, after


def raw_comparison(before, after, holdings, mask):
    def differs(observed):
        return explicit_law(marginal(before, observed)) != explicit_law(marginal(after, observed))

    return {
        "one_distinction_queries_with_different_marginals": [
            i for i in sorted(set().union(*map(set, holdings))) if differs(1 << i)
        ],
        "one_holder_queries_with_different_marginals": [
            i for i, row in enumerate(holdings) if differs(mask(row))
        ],
    }


def results():
    motion, advance, record = archives()
    mask, bits = motion["mask"], motion["bits"]
    basis, span = motion["basis"], motion["all_words"]
    source = star_rows(record["stages"]["0"]["stars"])
    event, grown = advance(source, "parity")
    assert event["status"] == "grown"
    assert star_rows(grown) == star_rows(record["stages"]["1"]["stars"])
    assert all(len(row) == 4 for row in source + star_rows(grown))
    make_stage = motion["motion_stage"].MotionStage
    old_stage, new_stage = make_stage(source), make_stage(grown)
    readout = mask(record["input"]["roles"]["ring_edges"][0])
    named_mark = min(bits(readout))
    old_names, old_basis, old_menu, _ = motion["ring_generators"](old_stage, pinned=False)
    _, full_basis, menu, _ = motion["ring_generators"](new_stage, pinned=False)
    menu = sorted(menu)
    assert all(new_stage.allowed_change(bits(move)) for move in menu)
    full = span(full_basis)
    assert len(full) == (1 << (event["distinctions"] - len(basis(map(mask, grown)))))
    assert all(new_stage.allowed_change(bits(word)) for word in full)
    even = span(basis(menu))
    assert even == {word for word in full if parity(word, readout) == 0}
    assert new_stage.allowed_change(bits(readout)) and readout not in even
    odd = {word ^ readout for word in even}
    assert odd == full - even

    old_mask = mask(old_names)
    extensions = defaultdict(list)
    for word in sorted(full):
        extensions[word & old_mask].append(word)
    assert set(extensions) == span(old_basis)
    per_old_count = len(extensions[0])
    assert all(len(lifts) == per_old_count for lifts in extensions.values())
    addresses = {}
    for mark in bits(readout):
        earlier = addressed_pulses(old_stage, mark, mask)
        later = addressed_pulses(new_stage, mark, mask)
        assert all(parity(move, readout) == 1 for move in earlier)
        assert all(parity(move, readout) == 0 for move in later)
        assert set(earlier) <= old_menu and set(later) <= set(menu)
        # The common initial word is zero. Each tie and each allowed extension
        # receives equal weight. Test the full product for every address.
        raw_earlier, raw_later = prepare(extensions, earlier, later)
        assert raw_earlier.keys() <= odd and raw_later.keys() <= even
        addresses[mark] = {
            "before_growth_pulse_supports": [list(bits(move)) for move in earlier],
            "after_growth_pulse_supports": [list(bits(move)) for move in later],
            "before_growth_even_odd_trial_counts": spectrum(raw_earlier, readout),
            "after_growth_even_odd_trial_counts": spectrum(raw_later, readout),
        }

    old_pulses = addressed_pulses(old_stage, named_mark, mask)
    new_pulses = addressed_pulses(new_stage, named_mark, mask)
    before, after = prepare(extensions, old_pulses, new_pulses)
    before_mixed = fair_offers(before, menu)
    after_mixed = fair_offers(after, menu)
    assert before_mixed.keys() == odd and after_mixed.keys() == even

    def arm(raw, mixed, favored_parity):
        mixed_record = uniform_law(mixed)
        raw_parity = spectrum(raw, readout)
        assert raw_parity[favored_parity] == sum(raw.values())
        return {
            "raw": explicit_law(raw),
            "raw_even_odd_trial_counts": raw_parity,
            "after_fair_shortest_offers": mixed_record,
            "after_fair_shortest_offers_sign": (-1) ** favored_parity,
            "support_condition": f"grown parity equations and old shared parity {favored_parity}",
        }

    erased_before = fair_offer(before_mixed, readout)
    erased_after = fair_offer(after_mixed, readout)
    assert erased_before.keys() == erased_after.keys() == full
    erased = uniform_law(erased_before)
    assert erased == uniform_law(erased_after)

    uniform_source_before = Counter(word for w in extensions for move in old_pulses
                                    for word in extensions[w ^ move])
    uniform_source_after = Counter(word ^ move for word in full for move in new_pulses)
    assert uniform_law(uniform_source_before) == uniform_law(uniform_source_after) == erased
    unaddressed_before, unaddressed_after = prepare(extensions, sorted(old_menu), menu)
    return {
        "archive_fixture": "R0",
        "mask_encoding": "bit i represents the literal distinction numbered i",
        "named_pulse_distinction": named_mark,
        "old_shared_sign_readout": list(bits(readout)),
        "source_holdings": source,
        "first_growth_event": event,
        "grown_holdings": grown,
        "allowed_source_words": len(extensions),
        "allowed_grown_words": len(full),
        "uniform_extensions_per_source_word": per_old_count,
        "pulse_offers_before_growth": [list(bits(move)) for move in old_pulses],
        "pulse_offers_after_growth": [list(bits(move)) for move in new_pulses],
        "all_old_shared_pulse_addresses": addresses,
        "fair_shortest_offer_traversal": [list(bits(move)) for move in menu],
        "fair_shortest_rank": len(basis(menu)),
        "pulse_then_grow": arm(before, before_mixed, 1),
        "grow_then_pulse": arm(after, after_mixed, 0),
        "readout_comparison": readout_receipt(grown, before_mixed, after_mixed, readout, motion),
        "no_mixing_control": raw_comparison(before, after, grown, mask),
        "uniform_unaddressed_pulse_control": {
            "before_growth_menu_size": len(old_menu),
            "after_growth_menu_size": len(menu),
            "before_growth_even_odd_trial_counts": spectrum(unaddressed_before, readout),
            "after_growth_even_odd_trial_counts": spectrum(unaddressed_after, readout),
        },
        "erase_by_one_independent_fair_old_ring_offer": erased,
        "uniform_source_control": erased,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="compare with results.json")
    args = parser.parse_args()
    rendered = json.dumps(results(), indent=2, sort_keys=True) + "\n"
    if args.check:
        recorded = Path(__file__).with_name("results.json").read_text(encoding="utf-8")
        if recorded != rendered:
            raise SystemExit("results.json differs from the replay")
        print("results.json matches the exact replay")
    else:
        print(rendered, end="")


if __name__ == "__main__":
    main()
