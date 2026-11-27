"""Audit the ordinary growth selection and projections from raw inputs."""

import argparse
from collections import Counter, defaultdict
from dataclasses import asdict
import gzip
from itertools import combinations, product
import json
from pathlib import Path
from random import Random
from time import perf_counter

from pysat.solvers import MapleChrono

from growth_rule import GrowthLimit, advance, holders, loose, supports_of


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CENSUS_INPUT = ROOT / "research/FORBID-EDITS-20261126-001/starts.json"
CENSUS_RECORD = HERE.parent / "census.jsonl"
T7_RECORD = HERE.parent / "t7.json"
OLDER_RECORD = ROOT / (
    "artifacts/ENTANGLEMENT-READ-20261120-001B/"
    "ENTANGLEMENT-READ-20261120-001B-E001_separated_readings/exact_readings.json.gz"
)
T7 = ((0, 1, 2), (0, 3, 6), (1, 4, 7), (2, 5, 8), (3, 9, 10), (4, 11, 12), (5, 13, 14))
FUNDED_T7 = tuple(support + (14 + i,) if i in (1, 2, 3) else support for i, support in enumerate(T7))


def component_profiles(supports):
    """Connected components of the mathematical knot multigraph."""
    parent = list(range(len(supports)))

    def root(knot):
        while parent[knot] != knot:
            parent[knot] = parent[parent[knot]]
            knot = parent[knot]
        return knot

    occurrences = holders(supports)
    for owners in occurrences.values():
        if len(owners) == 2:
            first, second = owners
            parent[root(first)] = root(second)
    counts = defaultdict(Counter)
    for knot in range(len(supports)):
        counts[root(knot)]["knots"] += 1
    for owners in occurrences.values():
        kind = "shared" if len(owners) == 2 else "loose"
        counts[root(owners[0])][kind] += 1
    return [
        {"knots": row["knots"], "loose": row["loose"], "cyclic": row["shared"] >= row["knots"]}
        for row in counts.values()
    ]


def structural_count(profiles):
    count = 1
    for component in profiles:
        count *= (1 << component["loose"]) - (0 if component["cyclic"] else 2)
    return count


def clauses(supports):
    return [tuple(sign * (distinction + 1) for distinction in support) for support in supports for sign in (-1, 1)]


def direct_projection(supports, kept, pilot=False, save_missing=False):
    """Check all complementary pairs of patterns with an incremental solver."""
    possibilities = 1 << len(kept)
    pair_count = 1 << max(0, len(kept) - 1)
    checks = min(pair_count, 128) if pilot else pair_count
    missing = []
    with MapleChrono(bootstrap_with=clauses(supports)) as solver:
        for word in range(checks):
            assumptions = [(distinction + 1) * (1 if word & (1 << i) else -1)
                           for i, distinction in enumerate(kept)]
            if not solver.solve(assumptions=assumptions):
                missing.append(word)
    multiplier = 2 if kept else 1
    result = {"checks": checks, "checked_patterns": checks * multiplier,
              "allowed_among_checked": (checks - len(missing)) * multiplier,
              "possible_patterns": possibilities, "complete": checks == pair_count}
    if save_missing and kept:
        result["missing_masks_among_checked"] = sorted(missing + [possibilities - 1 - mask for mask in missing])
    return result


def literal_states(supports):
    distinctions = sorted(holders(supports))
    index = {distinction: i for i, distinction in enumerate(distinctions)}
    masks = [sum(1 << index[distinction] for distinction in support) for support in supports]
    for assignment in range(1 << len(index)):
        if all((assignment & mask) not in (0, mask) for mask in masks):
            yield assignment, index


def source_profile(supports):
    kept = loose(supports)
    patterns = set()
    count = 0
    for assignment, index in literal_states(supports):
        count += 1
        patterns.add(tuple((assignment >> index[distinction]) & 1 for distinction in kept))
    return {"allowed_states": count, "allowed_loose_patterns": len(patterns), "possible_loose_patterns": 1 << len(kept)}


def certificate(supports, checks=False, pilot=False, detail=False):
    kept = loose(supports)
    profiles = component_profiles(supports)
    result = {
        "knot_count": len(supports), "distinction_count": len(holders(supports)), "loose_count": len(kept),
        "cyclic_components": sum(component["cyclic"] for component in profiles), "components": len(profiles),
        "possible_loose_patterns": 1 << len(kept), "structural_loose_count": structural_count(profiles),
    }
    if detail:
        result["supports"] = supports
        result["loose"] = kept
    if checks:
        result["direct_projection"] = direct_projection(supports, kept, pilot, detail)
        direct = result["direct_projection"]
        if direct["complete"]:
            assert direct["allowed_among_checked"] == result["structural_loose_count"]
    return result


def audit_census(pilot):
    raw_starts = json.loads(CENSUS_INPUT.read_text())
    *archived, final_tally = [json.loads(line) for line in CENSUS_RECORD.read_text().splitlines()]
    assert len(raw_starts) == len(archived) == final_tally["tally"]["starts"]
    archived_indices = [i for i, row in enumerate(archived) if "C4 after one round" in row]
    assert len(archived_indices) == 500
    widest = max(archived_indices, key=lambda i: archived[i]["C4 after one round"][1])
    requested = ({0, 1, widest, archived_indices[len(archived_indices) // 2], archived_indices[-1], 900, len(archived) - 1}
                 if pilot else range(len(archived)))
    strata = defaultdict(Counter)
    selection = []
    eligible_indices = []
    checks = {"selected": Counter(), "outside selection": Counter()}
    begin = perf_counter()
    for i in sorted(requested):
        row = archived[i]
        assert row["start"] == f"census {i}"
        start = supports_of(raw_starts[i])
        source_component = component_profiles(start)
        assert len(source_component) == 1 and row["tree-shaped"] == (not source_component[0]["cyclic"])
        shape = "cyclic" if source_component[0]["cyclic"] else "tree"
        by_size = strata[(len(start), shape)]
        step = advance(start)
        by_size[step.status] += 1
        if step.status != "funded":
            assert i not in archived_indices
            continue
        loose_after = loose(step.supports)
        assert certificate(step.supports)["cyclic_components"] == 1
        if len(loose_after) > 14:
            assert i not in archived_indices
            by_size["above loose count cap"] += 1
            continue
        eligible_indices.append(i)
        by_size["eligible"] += 1
        chosen = (i in archived_indices) if pilot else len(selection) < 500
        direct = direct_projection(step.supports, loose_after, pilot)
        group_checks = checks["selected" if chosen else "outside selection"]
        group_checks.update({"solver checks": direct["checks"], "patterns represented": direct["checked_patterns"],
                             "allowed patterns": direct["allowed_among_checked"], "complete projections": direct["complete"]})
        assert direct["allowed_among_checked"] == direct["checked_patterns"]
        if not chosen:
            continue
        expected = row["C4 after one round"]
        assert direct["possible_patterns"] == expected[1]
        if direct["complete"]:
            assert direct["allowed_among_checked"] == expected[0]
        by_size["selected"] += 1
        selection.append({"index": i, "source_shape": shape, "start_knots": len(start),
                          "births": len(step.births), "new_loose_count": len(loose_after),
                          "archived": expected, "direct": direct})
    if not pilot:
        assert [row["index"] for row in selection] == eligible_indices[:500] == archived_indices
    return {"strata": {f"{size} knots, {shape}": dict(count) for (size, shape), count in sorted(strata.items())},
            "starts_reconstructed": len(requested), "eligibles": eligible_indices,
            "selected": selection, "eligible_not_selected": len(eligible_indices) - len(selection),
            "direct_total": checks, "seconds": perf_counter() - begin}


def audit_archive(pilot):
    with gzip.open(OLDER_RECORD, "rt") as source:
        raw = json.load(source)["sources"]
    if pilot:
        raw = raw[:3]
    rows = []
    begin = perf_counter()
    for case in raw:
        initial, next_round = case["laws"]["nae"]
        assert initial["status"] == "measured_stage"
        step = advance(initial["supports"], max_births=400, search_limit=100_000)
        expected_status = {"measured_stage": "funded", "stalled": "stalled", "closed": "closed"}[next_round["status"]]
        assert step.status == expected_status
        births = 0
        if step.status == "funded":
            assert step.supports == tuple(map(tuple, next_round["supports"]))
            expected_births = next_round["growth"]["births"]
            assert len(expected_births) == len(step.births)
            for actual, expected in zip(step.births, expected_births, strict=True):
                assert actual.knot == expected["knot"] and actual.parents == tuple(expected["parents"])
                assert actual.inputs == tuple(expected["consumed"]) and actual.fresh == tuple(expected["fresh"])
                assert actual.demand == expected["lookahead_demand"]
                births += 1
        else:
            assert step.shortages == {int(knot): amount for knot, amount in next_round["growth"].get("shortages", {}).items()}
        rows.append({"source": case["name"], "status": expected_status, "births_compared": births,
                     "supports_compared": len(step.supports) if step.status == "funded" else 0})
    return {"source": str(OLDER_RECORD.relative_to(ROOT)), "cases": rows,
            "births_compared": sum(row["births_compared"] for row in rows),
            "supports_compared": sum(row["supports_compared"] for row in rows), "seconds": perf_counter() - begin}


def rounds(supports, maximum_round, *, direct_cap=None, pilot=False, detail=False):
    source = certificate(supports, direct_enabled(direct_cap, supports), pilot, detail)
    source.update({"round": 0, "status": "source"})
    stages = [source]
    for round_index in range(1, maximum_round + 1):
        try:
            result = advance(supports, max_births=180, search_limit=50_000)
        except GrowthLimit as limit:
            stages.append({"round": round_index, "status": "not run", "why": str(limit)})
            break
        if result.status != "funded":
            stages.append({"round": round_index, "status": result.status, "shortages": result.shortages})
            break
        supports = result.supports
        stage = certificate(supports, direct_enabled(direct_cap, supports), pilot, detail)
        stage.update({"round": round_index, "status": "funded", "birth_count": len(result.births),
                      "multi_parent_births": sum(len(birth.parents) > 1 for birth in result.births)})
        if detail:
            stage["births"] = [asdict(birth) for birth in result.births]
        stages.append(stage)
    return stages


def direct_enabled(direct_cap, supports):
    return direct_cap is not None and len(loose(supports)) <= direct_cap


def offshoot_readout(supports, carriers):
    signatures = set()
    for assignment, index in literal_states(supports):
        values = []
        for left, right in carriers:
            pair = ((assignment >> index[left]) & 1, (assignment >> index[right]) & 1)
            values.append("+" if pair == (0, 0) else "-" if pair == (1, 1) else "0")
        signatures.add(tuple(values))
    binary = {tuple(value == "+" for value in signature) for signature in signatures}
    return {"carriers": carriers, "ternary_count": len(signatures),
            "ternary_missing": sorted(set(product("+-0", repeat=3)) - signatures),
            "ternary_pair_counts": [len({(row[i], row[j]) for row in signatures}) for i, j in combinations(range(3), 2)],
            "binary_count": len(binary), "binary_missing": sorted(set(product((False, True), repeat=3)) - binary),
            "binary_pair_counts": [len({(row[i], row[j]) for row in binary}) for i, j in combinations(range(3), 2)]}


def audit_built(pilot):
    wanted = json.loads(T7_RECORD.read_text())
    begin = perf_counter()
    initial = advance(T7)
    assert initial.status == wanted["N5 T7 round 1"]
    funded_source = source_profile(FUNDED_T7)
    assert funded_source["allowed_states"] == wanted["N5 T7 with 15, 16, 17: states"]
    assert [funded_source["allowed_loose_patterns"], funded_source["possible_loose_patterns"]] == wanted[
        "N5 T7 with 15, 16, 17: loose patterns"]
    funded_stages = rounds(FUNDED_T7, 2 if pilot else 4, direct_cap=19, pilot=pilot, detail=True)
    first = funded_stages[1]
    assert first["status"] == wanted["N5 its round 1"] and first["knot_count"] == wanted["N5 stage after one round: knots"]
    if first["direct_projection"]["complete"]:
        assert [first["direct_projection"]["allowed_among_checked"], first["possible_loose_patterns"]] == wanted[
            "N5 loose patterns after one round"]
    lone = rounds(((0, 1, 2),), 2 if pilot else 4, direct_cap=16, pilot=pilot, detail=True)
    two = rounds(((0, 1, 2), (0, 3, 4)), 2 if pilot else 4, direct_cap=16, pilot=pilot, detail=True)
    for stages in (lone, two):
        assert stages[1]["multi_parent_births"] == 0 and stages[1]["structural_loose_count"] + 2 == stages[1]["possible_loose_patterns"]
        assert stages[2]["multi_parent_births"] > 0 and stages[2]["structural_loose_count"] == stages[2]["possible_loose_patterns"]
    marks = tuple(tuple(birth["fresh"]) for birth in lone[1]["births"])
    readouts = [offshoot_readout(lone[round_index]["supports"], marks) for round_index in (1, 2)]
    assert readouts[0] == readouts[1] and readouts[0]["ternary_count"] == 25 and readouts[0]["binary_count"] == 7
    return {"T7 initial round": {"status": initial.status, "shortages": initial.shortages},
            "funded T7 source profile": funded_source, "funded T7 stages": funded_stages,
            "lone ternary knot": lone, "two ternary knots sharing one distinction": two,
            "offshoot readouts at rounds 1 and 2": readouts, "seconds": perf_counter() - begin}


def extension_draws(size, count, seed):
    """Labelled draws accepted under connectivity, minimum arity, and width limits."""
    rng = Random(seed)
    pairs = tuple(combinations(range(size), 2))
    accepted = 0
    while accepted < count:
        present = [pair for pair in pairs if rng.random() < 1 / 3]
        shared = [(left, right, rng.choice((1, 2))) for left, right in present]
        loose_counts = tuple(rng.choice((0, 1, 2)) for _ in range(size))
        shared_counts = Counter(knot for left, right, multiplicity in shared for knot in (left, right)
                                for _ in range(multiplicity))
        if any(shared_counts[knot] + loose_counts[knot] < 3 for knot in range(size)):
            continue
        if sum(row[2] for row in shared) + sum(loose_counts) > 18:
            continue
        supports = supports_of((size, shared, loose_counts))
        if len(component_profiles(supports)) != 1:
            continue
        accepted += 1
        yield supports


def audit_larger(pilot):
    begin = perf_counter()
    inputs = [
        ("six-knot ternary chain", supports_of((6, [(i, i + 1, 1) for i in range(5)], (2, 1, 1, 1, 1, 2)))),
        ("seven-knot ternary ring", supports_of((7, [(i, (i + 1) % 7, 1) for i in range(7)], (1,) * 7))),
        ("funded eight-knot ring", supports_of((8, [(i, (i + 1) % 8, 1) for i in range(8)], (2,) * 8))),
    ]
    built = [{"name": name, "initial_supports": source, "stages": rounds(source, 2 if pilot else 4, direct_cap=16, pilot=pilot)}
             for name, source in inputs]
    funded_chain = supports_of((6, [(i, i + 1, 1) for i in range(5)], (2, 1, 2, 2, 1, 2)))
    chain_stages = rounds(funded_chain, 2 if pilot else 4, direct_cap=16, pilot=pilot, detail=True)
    old_loose = loose(funded_chain)
    for stage in chain_stages:
        assert stage["status"] in ("source", "funded")
        stage["fixed_source_loose_projection"] = direct_projection(stage["supports"], old_loose, pilot=pilot,
                                                                   save_missing=True)
        assert stage["fixed_source_loose_projection"] == chain_stages[0]["fixed_source_loose_projection"]
    built.append({"name": "funded six-knot chain", "initial_supports": funded_chain, "stages": chain_stages})
    samples = {}
    reach = defaultdict(Counter)
    for size in (6, 7, 8):
        seed = 20261127 + size
        samples[size] = {"seed": seed, "draws": []}
        for draw, support in enumerate(extension_draws(size, 2 if pilot else 30, seed)):
            stages = rounds(support, 4, direct_cap=16, pilot=pilot)
            for stage in stages[1:]:
                index = stage["round"]
                reach[index][stage["status"]] += 1
                if stage["status"] == "funded":
                    assert stage["structural_loose_count"] == stage["possible_loose_patterns"]
                    if "direct_projection" in stage and stage["direct_projection"]["complete"]:
                        reach[index]["direct"] += 1
            samples[size]["draws"].append({"index": draw, "initial_supports": support, "stages": stages})
    return {"built": built, "labelled_draws": samples, "reach": reach, "seconds": perf_counter() - begin}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot", action="store_true")
    parser.add_argument("--part", choices=("all", "census", "archive", "built", "larger"), default="all")
    args = parser.parse_args()
    jobs = {"census": audit_census, "archive": audit_archive, "built": audit_built, "larger": audit_larger}
    result = {name: job(args.pilot) for name, job in jobs.items() if args.part in ("all", name)}
    if args.pilot:
        pilot_fields = {"census": ("starts_reconstructed", "direct_total"),
                        "archive": ("births_compared", "supports_compared"),
                        "built": ("funded T7 source profile",), "larger": ("reach",)}
        result = {name: {field: data[field] for field in (*pilot_fields[name], "seconds")} for name, data in result.items()}
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
