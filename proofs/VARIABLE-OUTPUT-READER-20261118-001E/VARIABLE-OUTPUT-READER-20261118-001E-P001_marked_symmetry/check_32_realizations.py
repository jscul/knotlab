"""Classify every allowed-state relation realizable over one complete scalar table."""

from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
PRIOR = (
    HERE.parents[1] / "VARIABLE-OUTPUT-READER-20261118-001D"
    / "VARIABLE-OUTPUT-READER-20261118-001D-P001_separator_inverse"
)
DIGESTS = {
    "active_part.json": "48a711f1fa5b6eca0aa05d47eba9011bb129af985f29f8fd3ea959981ee09ed3",
    "check_continuation.py": "86ccf507575d635a2348ca9287bf9cdc2a752a9ae78f5d079a071c8f3387d524",
    "check_scalar_span.py": "19d293fe62d76eb910ebe606ed3afda97b69ff0b700eb7beab433c0cbb47c05c",
    "check_span_controls.py": "ece53f8c0aa3f71c6be5984de374992d11c15bd3f4a20e9ff979d4c57e7cd6a2",
}
for filename, digest in DIGESTS.items():
    assert sha256((PRIOR / filename).read_bytes()).hexdigest() == digest
sys.path.insert(0, str(PRIOR))
import check_continuation as graphic
import check_scalar_span as short
import check_span_controls as linear


WIDTH = 32
PAIRS = tuple(combinations(range(WIDTH), 2))
TRIPLES = tuple(combinations(range(WIDTH), 3))


def physical_verdicts(stars):
    """Check all marks directly from the incidence, independently of their table."""
    sites = [set(star) for star in stars]
    holders = [tuple(i for i, site in enumerate(sites) if bit in site) for bit in range(WIDTH)]
    assert all(1 <= len(group) <= 2 for group in holders)
    neighbors = [set() for site in sites]
    for group in holders:
        if len(group) == 2:
            a, b = group
            neighbors[a].add(b)
            neighbors[b].add(a)
    legal = set()
    for triple in TRIPLES:
        if any(len(holders[bit]) != 1 for bit in triple):
            continue
        a, b, c = (holders[bit][0] for bit in triple)
        if len({a, b, c}) != 3:
            continue
        na, nb, nc = neighbors[a], neighbors[b], neighbors[c]
        if na & nb and na & nc and nb & nc and not na & nb & nc:
            legal.add(triple)
    return legal


def enumerate_models(table):
    """Input here is solely the full scalar matrix on named bits."""
    known, unresolved, passes = short.infer(table, WIDTH)
    forced_rank = len(known).bit_length() - 1
    rank_cap = (WIDTH - 1) // 2
    assert (forced_rank, rank_cap) == (14, 15)
    representatives = {}
    for support in sorted(unresolved):
        coset = min(support ^ word for word in known)
        representatives.setdefault(coset, support)

    matching = set()
    tested = []
    for coset, support in [(0, 0), *sorted(representatives.items())]:
        model = frozenset(known | {word ^ support for word in known})
        measured = linear.measure_every_pair(model, WIDTH)
        different = [(a, b) for a, b in PAIRS if measured[a][b] != table[a, b]]
        tested.append({
            "additional_short_support": list(short.names(support)),
            "coset_minimum_integer": coset,
            "rank": len(model).bit_length() - 1,
            "different_scalar_entries": len(different),
            "first_different_pair": different[0] if different else None,
        })
        if not different:
            matching.add(model)
    return matching, {
        "forced_rank": forced_rank,
        "rank_upper_bound": rank_cap,
        "inference_passes": passes,
        "unresolved_short_supports": len(unresolved),
        "distinct_nonzero_cosets": len(representatives),
        "tested_spaces": tested,
        "pair_entries_checked_for_each_space": len(PAIRS),
    }


def run():
    fixture = json.loads((PRIOR / "active_part.json").read_text())["completions"][0]
    stars = tuple(tuple(star) for star in fixture["junction_supports"])
    swap = list(range(WIDTH))
    swap[13], swap[14] = 14, 13
    renamed = tuple(tuple(sorted(swap[bit] for bit in star)) for star in stars)
    bridge = short.bridge
    bridge.replay(stars)
    bridge.replay(renamed)
    table = bridge.scalar_table(graphic.cut_supports(bridge, stars), WIDTH)
    alternate = bridge.scalar_table(graphic.cut_supports(bridge, renamed), WIDTH)
    assert table == alternate and all(value is not None for value in table.values())
    assert set(table) == set(PAIRS)
    matching, proof = enumerate_models(table)

    concrete_spaces = {
        frozenset(short.span(short.as_mask(star) for star in presentation))
        for presentation in (stars, renamed)
    }
    assert len(concrete_spaces) == 2 and matching == concrete_spaces
    legal = physical_verdicts(stars)
    assert legal == physical_verdicts(renamed)
    assert legal == {tuple(row) for row in fixture["true_triples"]} and len(legal) == 8
    assert all(15 not in triple for triple in legal)
    assert sum(15 in star for star in stars) == sum(15 in star for star in renamed) == 1
    return {
        "input": "First completion in the predecessor's active_part.json.",
        "input_sha256": DIGESTS["active_part.json"],
        "width": WIDTH,
        "scalar_table_sha256": sha256(bytes(table[pair] for pair in PAIRS)).hexdigest(),
        "table_only_code_exhaustion": proof,
        "two_surviving_spaces_equal_the_replayed_original_and_13_14_swap": True,
        "ordered_pair_of_swapped_bits": [13, 14],
        "distinct_named_codes": len(matching),
        "unordered_marks_checked_per_reachable_witness": len(TRIPLES),
        "legal_unordered_triples_in_both": sorted(legal),
        "different_mark_verdicts": 0,
        "ungrafted_loose_bit_outside_all_eight_choices": 15,
    }


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))
