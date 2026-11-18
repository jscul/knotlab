"""Enumerate the physical width-19 population and its actual serial menus."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from collections import Counter, defaultdict
from functools import cache
from itertools import combinations
from math import prod
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
PARENT = (
    ROOT / "proofs/VARIABLE-OUTPUT-READER-20261118-001A"
    / "VARIABLE-OUTPUT-READER-20261118-001A-P001_width_eighteen"
)
SOURCE = PARENT / "check_width.py"
SOURCE_SHA256 = "dc1bdeaea873653d027b07dcad78f0735716bce7604f2bb62a179da1bbd6d163"
CONTROL_SHA256 = "03fddd9dd1989ffacb3e4209c8225cb08e4e1504762ba9361b987f8c16184ae1"
WIDTH = 19
SEED_WIDTH = 3
FRESH_COUNTS = (2, 3)
PARENT_COUNTS = (1, 2, 3)


def width_quotas(target_width):
    available = target_width - SEED_WIDTH
    quotas = {}
    for additions in range(available // 2 + 1):
        threes = available - 2 * additions
        twos = additions - threes
        if twos >= 0 and threes >= 0:
            quotas[additions + 1] = {2: twos, 3: threes}
    return quotas


@cache
def producer(target_width):
    """Configure the verified producer in a private module instance."""
    assert target_width in (18, WIDTH)
    assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == SOURCE_SHA256
    private_name = f"variable_output_population_producer_{target_width}"
    spec = importlib.util.spec_from_file_location(private_name, SOURCE)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    assert module.WIDTH == 18 and module.MAX_JUNCTIONS == 8 and module.FRESH_COUNTS == FRESH_COUNTS
    if target_width != 18:
        module.WIDTH = target_width
        module.MAX_JUNCTIONS = max(width_quotas(target_width))
        module.PAIRS = tuple(combinations(range(target_width), 2))
        # Reuse one scout object across both private producers. Parent tests,
        # exact graph-isomorphism deduplication and the scalar oracle stay fixed.
        module.inherited = producer(18).inherited
    return module


def inherited():
    """Return the archived scout, scalar reader and rules used by this population."""
    return producer(WIDTH).inherited()


def width_fixtures():
    """Return the unique physical fixtures, sorted by junction count and history."""
    return producer(WIDTH).width_fixtures()


def width_records():
    """Yield archived Measured records, including actual menus and all 171 pairs."""
    yield from producer(WIDTH).width_records()


def menu_counts(scout, rules, fixture):
    """Count actual operand sets using the number of loose identities at each parent."""
    counts = Counter()
    for parents, available in scout.legal_parent_sets(rules, fixture.checks()):
        # Every selection from distinct parents has those owners. The loose
        # sets of distinct owners are disjoint, so no operand set is repeated.
        counts[len(parents)] += prod(map(len, available))
    return counts


def triple_grade(checks, operands, rules):
    users, neighbors = rules.incidence(checks)
    loose = all(len(users[bit]) == 1 for bit in operands)
    distinct_parents = ()
    pair_witnesses = {}
    common = set()
    if loose:
        distinct_parents = tuple(sorted({users[bit][0] for bit in operands}))
        if len(distinct_parents) == 3:
            pair_witnesses = {
                (i, j): neighbors[i] & neighbors[j] for i, j in combinations(distinct_parents, 2)
            }
            common = set.intersection(*(neighbors[parent] for parent in distinct_parents))
    legal = loose and len(distinct_parents) == 3 and all(pair_witnesses.values()) and not common
    assert legal == rules.legal_local_move(checks, operands, (19, 20, 21))
    return {
        "operands": operands,
        "legal": legal,
        "all_operands_loose": loose,
        "parents_if_all_loose": distinct_parents,
        "pair_witnesses": [
            {"parents": pair, "common_neighbors": sorted(witnesses)}
            for pair, witnesses in pair_witnesses.items()
        ],
        "neighbors_common_to_all_three": sorted(common),
    }


def example(fixture, counts):
    scout, _, rules = inherited()
    # Replay the retained parent choices before grading the present identities.
    assert producer(WIDTH).replay(fixture.history) == fixture
    checks = fixture.checks()
    menu = scout.actual_menu(rules, checks)
    assert Counter(map(len, menu)) == counts
    triples = sorted(tuple(sorted(item)) for item in menu if len(item) == 3)
    assert triples
    good = triples[0]
    users, _ = rules.incidence(checks)
    loose = sorted(bit for bit, owners in users.items() if len(owners) == 1)
    # Prefer a forbidden input on loose identities at distinct parents.
    bad = next((
        operands for operands in combinations(loose, 3)
        if len({users[bit][0] for bit in operands}) == 3 and frozenset(operands) not in menu
    ), None)
    if bad is None:
        bad = next(operands for operands in combinations(range(WIDTH), 3)
                   if frozenset(operands) not in menu)
    positive = triple_grade(checks, good, rules)
    negative = triple_grade(checks, bad, rules)
    assert positive["legal"] and not negative["legal"]
    return {
        "history": fixture.history,
        "junction_supports": tuple(checks.values()),
        "loose_counts": fixture.loose_counts,
        "legal_triples": triples,
        "legal_example": positive,
        "forbidden_example": negative,
        "fresh_output_counts_at_the_legal_example": FRESH_COUNTS,
    }


def population(fixtures, quotas):
    scout, _, rules = inherited()
    histograms = {depth: Counter() for depth in quotas}
    serial = defaultdict(Counter)
    examples = {}
    for fixture in fixtures:
        depth = len(fixture.loose_counts)
        assert len(fixture.history) == depth - 1
        assert Counter(fresh for _, fresh in fixture.history) == Counter(quotas[depth])
        counts = menu_counts(scout, rules, fixture)
        histograms[depth][counts[3]] += 1
        serial[depth].update(counts)
        if counts[3] and depth not in examples:
            examples[depth] = example(fixture, counts)

    rows = {}
    for depth, histogram in histograms.items():
        total = sum(histogram.values())
        triple_total = sum(menu_size * multiplicity for menu_size, multiplicity in histogram.items())
        assert triple_total == serial[depth][3]
        rows[str(depth)] = {
            "incidence_types": total,
            "fresh_output_quota_for_history": quotas[depth],
            "types_with_legal_triples": total - histogram[0],
            "legal_triples_sum_over_types": triple_total,
            "triple_menu_size_distribution": dict(sorted(histogram.items())),
            "serial_operand_sets_sum_over_types_by_parent_count": {
                count: serial[depth][count] for count in PARENT_COUNTS
            },
            "example": examples.get(depth),
        }
    return rows


def archived_width_control():
    path = PARENT / "width.json"
    assert hashlib.sha256(path.read_bytes()).hexdigest() == CONTROL_SHA256
    reference = json.loads(path.read_text())
    assert reference["width"] == 18
    expected = {key: count for key, count in reference["population"].items() if key != "total"}
    original = producer(18)
    assert original.WIDTH == 18 and original.MAX_JUNCTIONS == 8
    actual = Counter(str(len(fixture.loose_counts)) for fixture in original.width_fixtures())
    assert actual == expected
    assert original.WIDTH == 18 and original is not producer(WIDTH)
    return dict(actual)


def run():
    quotas = width_quotas(WIDTH)
    assert tuple(quotas) == (7, 8, 9)
    adapter = producer(WIDTH)
    fixtures, generation = adapter.generate_width_fixtures()
    assert {len(fixture.loose_counts) for fixture in fixtures} == set(quotas)
    assert all(adapter.width(fixture) == WIDTH for fixture in fixtures)
    by_depth = population(fixtures, quotas)
    assert sum(row["incidence_types"] for row in by_depth.values()) == len(fixtures)
    audit = [
        {
            **{key: value for key, value in row.items() if key != "width_eighteen_types"},
            "width_nineteen_types": row["width_eighteen_types"],
        }
        for row in generation
    ]
    return {
        "width": WIDTH,
        "seed_width": SEED_WIDTH,
        "admitted_existing_junction_counts": tuple(quotas),
        "fresh_output_counts_per_legal_operand_set": FRESH_COUNTS,
        "parent_counts": PARENT_COUNTS,
        "producer_sha256": SOURCE_SHA256,
        "width_eighteen_record_sha256": CONTROL_SHA256,
        "physical_types": len(fixtures),
        "types_with_legal_triples": sum(row["types_with_legal_triples"] for row in by_depth.values()),
        "legal_triples_sum_over_types": sum(row["legal_triples_sum_over_types"] for row in by_depth.values()),
        "by_existing_junction_count": by_depth,
        "generation": audit,
        "unchanged_width_eighteen_control": archived_width_control(),
    }


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))
