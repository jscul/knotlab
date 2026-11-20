"""Uniform queries of one five-knot growth through 48 parent steps."""

from argparse import ArgumentParser
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
from itertools import combinations
import json
from math import comb
from pathlib import Path
from random import Random
import sys
from typing import NamedTuple


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
RESEARCH = ROOT / "research" / HERE.parent.name
LITERAL_FIXTURE = ROOT / ("experiments/GENERATORS-20261120-001A/"
                          "GENERATORS-20261120-001A-E001_generators/fixtures.py")
LITERAL_OPERATOR = ROOT / ("experiments/ORDINARY-DYNAMICS-20261120-001A/"
                           "ORDINARY-DYNAMICS-20261120-001A-E001_ordinary/end_operator.py")
PERIOD = 5
ANCHOR_SIZE = 33
HORIZON = 16
DRAWS = 96
SEED = 20261120404
LAWS = ("parity", "nae")


class Cluster(NamedTuple):
    """One cluster modulo complete turns, indexed only for scoring."""

    phase: int
    run_length: int
    spare_offsets: tuple[int, ...]


def count_at_size(size):
    return PERIOD * sum(comb(length, size - length)
                        for length in range((size + 1) // 2, size + 1))


def unrank_subset(length, count, rank):
    offsets = []
    cursor = 0
    for remaining in range(count, 0, -1):
        for candidate in range(cursor, length - remaining + 1):
            block = comb(length - candidate - 1, remaining - 1)
            if rank < block:
                offsets.append(candidate)
                cursor = candidate + 1
                break
            rank -= block
        else:
            raise ValueError("subset rank is outside its population")
    assert not rank
    return tuple(offsets)


def unrank_cluster(size, rank):
    population = count_at_size(size)
    if not 0 <= rank < population:
        raise ValueError("cluster rank is outside its population")
    phase, rank = divmod(rank, population // PERIOD)
    for length in range((size + 1) // 2, size + 1):
        count = size - length
        block = comb(length, count)
        if rank < block:
            return Cluster(phase, length, unrank_subset(length, count, rank))
        rank -= block
    raise AssertionError("length blocks do not account for the population")


def parents(cluster):
    phase, length, spares = cluster
    result = [Cluster(phase, length, tuple(p for p in spares if p != removed))
              for removed in spares]
    if length > 1 and 0 not in spares:
        result.append(Cluster((phase + 1) % PERIOD, length - 1, tuple(p - 1 for p in spares)))
    if length > 1 and length - 1 not in spares:
        result.append(Cluster(phase, length - 1, spares))
    return tuple(result)


def extensions(cluster):
    phase, length, spares = cluster
    return (
        Cluster((phase - 1) % PERIOD, length + 1, tuple(p + 1 for p in spares)),
        Cluster(phase, length + 1, spares),
        *(Cluster(phase, length, tuple(sorted((*spares, p))))
          for p in range(length) if p not in spares),
    )


def holding_count(cluster):
    if cluster.run_length == 1 and not cluster.spare_offsets:
        return 5
    return len(parents(cluster)) + len(extensions(cluster))


def reflected(cluster):
    phase, length, spares = cluster
    return Cluster((-phase - length + 1) % PERIOD, length,
                   tuple(length - p - 1 for p in reversed(spares)))


def read_observations(cluster):
    """Recover the pointed facts without passing the score labels to either read."""
    incoming = parents(cluster)
    forward = extensions(cluster)
    assert len(forward) == len(set(forward))
    co_children = set()
    witness_counts = []
    for parent in incoming:
        witnesses = set(extensions(parent))
        assert cluster in witnesses
        witnesses.remove(cluster)
        # Two distinct parent rosters have no second child in common.
        assert not co_children.intersection(witnesses)
        co_children.update(witnesses)
        witness_counts.append(len(witnesses) + 1)
    return {
        "full_current": {
            "input_count": len(incoming),
            "previous_holder_arities": sorted(holding_count(p) for p in incoming),
        },
        "growing_end": {
            "loose": len(forward),
            "witnessed_degree": len(co_children),
            "witness_child_counts": sorted(witness_counts),
        },
    }


def blind_checks():
    """Small complete roster and literal-holdings comparisons."""
    spec = spec_from_file_location("generators_literal_fixture", LITERAL_FIXTURE)
    fixture = module_from_spec(spec)
    sys.modules[spec.name] = fixture
    spec.loader.exec_module(fixture)

    literal_checks = {}
    unranking_size = 8
    literal_size = 7
    source = fixture.source_from([(i, (i + 1) % PERIOD) for i in range(PERIOD)], [3] * PERIOD)
    small_cohorts = {}
    for size in range(1, unranking_size + 1):
        exhaustive = {
            Cluster(phase, length, offsets)
            for phase in range(PERIOD)
            for length in range((size + 1) // 2, size + 1)
            for offsets in combinations(range(length), size - length)
        }
        ranks = range(count_at_size(size))
        assert {unrank_cluster(size, rank) for rank in ranks} == exhaustive
        small_cohorts[size] = exhaustive

    for law in LAWS:
        fixture.certify_source(source, law)
        frames, layers = fixture.trajectory(source, law, literal_size - 1)
        assert len(frames) == literal_size
        previous = {Cluster(phase, 1, ()): (2 * phase) % PERIOD for phase in range(PERIOD)}
        births_checked = 0
        for size, (stars, (births, _)) in enumerate(zip(frames[1:], layers, strict=True), 2):
            by_parents = {frozenset(birth.parents): birth for birth in births}
            assert len(by_parents) == len(births) == count_at_size(size)
            assert len(births) <= 128
            _, ordinary, loose = fixture.incidence(stars)
            blocks, witnessed = fixture.witnessed_end(ordinary, loose)
            current = {}
            for cluster in small_cohorts[size]:
                actual = by_parents[frozenset(previous[p] for p in parents(cluster))]
                current[cluster] = actual.knot
                assert len(actual.fresh) == len(loose[actual.knot])
                readings = read_observations(cluster)
                assert readings["full_current"] == {
                    "input_count": len(ordinary[actual.knot]),
                    "previous_holder_arities": sorted(len(stars[p]) for p in ordinary[actual.knot]),
                }
                assert readings["growing_end"] == {
                    "loose": len(loose[actual.knot]),
                    "witnessed_degree": witnessed.degree(actual.knot),
                    "witness_child_counts": sorted(len(block) for block in blocks if actual.knot in block),
                }
            assert set(current.values()) == set(loose)
            previous = current
            births_checked += len(current)
        literal_checks[law] = {
            "start_k1_k3": PERIOD,
            "through_cluster_size": literal_size,
            "actual_births_with_roster_and_both_reads_checked": births_checked,
        }
    return {"exact_unranking_through_cluster_size": unranking_size,
            "literal_replay_by_law": literal_checks}


def follow(cluster, extension_index, initial):
    observations = [initial]
    for _ in range(HORIZON):
        child = extensions(cluster)[extension_index]
        assert cluster in parents(child)
        cluster = child
        observations.append(read_observations(cluster))
    return observations


def draw_receipt(rank):
    cluster = unrank_cluster(ANCHOR_SIZE, rank)
    initial = read_observations(cluster)
    assert initial == read_observations(reflected(cluster))
    assert initial == read_observations(cluster._replace(phase=(cluster.phase + 1) % PERIOD))
    traces = [follow(cluster, extension_index, initial) for extension_index in range(2)]
    seen = [row for trace in traces for row in trace]
    funded = all(row["growing_end"]["loose"] >= 2 for row in seen)
    assert funded
    assert all(row["full_current"]["input_count"] >= 2 for row in seen)
    assert all(row["growing_end"]["witnessed_degree"] >= 2 for row in seen)
    # The zero outcomes use the obstructions in deep_method.md. The traces
    # check pointed holdings through the horizon; they are not a cohort search.
    events = {
        "funded": funded,
        "at_least_one_recognized_release": False,
        "one_recognized_release": False,
        "two_or_more_recognized_releases": False,
        "both_persist_direct": False,
        "both_persist_indirect": False,
        "recurrent_source": False,
    }
    return {
        "scorer_rank": rank,
        "scorer_cluster": cluster._asdict(),
        "starting_readings": initial,
        "continuations_in_both_index_directions": [trace[1:] for trace in traces],
        "events_by_reader": {reader: events for reader in initial},
    }


def rates(yes, no, unknown):
    """Exact binomial endpoints when every vote has the same classification."""
    assert sum((yes, no, unknown)) == DRAWS
    assert set((yes, no, unknown)) == {0, DRAWS}
    tail = 0.025 ** (1 / DRAWS)
    result = {
        "counts": {"yes": yes, "no": no, "unknown": unknown},
        "identification_interval": [yes / DRAWS, (yes + unknown) / DRAWS],
        "marginal_binomial_95": [tail if yes else 0.0, 1.0 - tail if no else 1.0],
    }
    if no == DRAWS:
        result["zero_detection_one_sided_binomial_95_upper"] = 1.0 - 0.05 ** (1 / DRAWS)
    return result


def result(checks):
    population = count_at_size(ANCHOR_SIZE)
    rng = Random(SEED)
    draws = [draw_receipt(rng.randrange(population)) for _ in range(DRAWS)]
    summaries = {}
    for reader in draws[0]["events_by_reader"]:
        counts = {
            event: sum(draw["events_by_reader"][reader][event] for draw in draws)
            for event in draws[0]["events_by_reader"][reader]
        }
        recognized = {event: rates(count, DRAWS - count, 0) for event, count in counts.items()}
        broader = recognized | {
            "at_least_one_recognized_release": rates(0, 0, DRAWS),
            "one_recognized_release": rates(0, 0, DRAWS),
        }
        summaries[reader] = {
            "denominator_per_law": DRAWS,
            "lawful_denominator_per_law": DRAWS,
            "funded_denominator_per_law": DRAWS,
            "observed_counts_per_law": counts,
            "frozen_reader": recognized,
            "broader_existence": broader,
        }
    return {
        "host": {"original_knots": PERIOD, "shared_distinctions": PERIOD,
                 "loose_distinctions_per_knot": 3,
                 "description": "five-knot cycle with one spare per holder"},
        "design": {"laws": LAWS, "paired_across_laws_and_readings": True, "seed": SEED,
                   "sample_unit": "uniform individual birth with replacement",
                   "anchor_parent_steps": ANCHOR_SIZE - 1,
                   "followup_parent_steps": HORIZON,
                   "population_at_anchor": population,
                   "population_at_followup_end": count_at_size(ANCHOR_SIZE + HORIZON)},
        "checks": checks,
        "sha256": {
            str(path.relative_to(ROOT)): sha256(path.read_bytes()).hexdigest()
            for path in (Path(__file__).resolve(), RESEARCH / "preregistration.md", HERE / "contract.json",
                         LITERAL_FIXTURE, LITERAL_OPERATOR)
        },
        "summary_by_reader": summaries,
        "draws": draws,
    }


def main():
    cli = ArgumentParser(description=__doc__)
    cli.add_argument("--check-only", action="store_true", help="Run only the small literal controls.")
    cli.add_argument("--output", type=Path, help="Write a new receipt at this path.")
    args = cli.parse_args()
    checks = blind_checks()
    payload = checks if args.check_only else result(checks)
    # Compact rows keep the thousands of exact pointed observations replayable.
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n"
    if args.output:
        with args.output.open("x", encoding="utf-8") as receipt:
            receipt.write(raw)
    else:
        print(raw, end="")


if __name__ == "__main__":
    main()
