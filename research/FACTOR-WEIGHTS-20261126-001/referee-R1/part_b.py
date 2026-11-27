"""Rebuild the parity growth, restrictions, and shared-pair counts in Part B."""

import argparse
from collections import Counter, defaultdict
import gzip
from itertools import chain, combinations, count
import json
from pathlib import Path
import resource
from time import perf_counter


HERE = Path(__file__).resolve().parent
FROZEN_ROUNDS = (1, 4, 5, 6)
TREATMENTS = ("unread", "values", "changes")
FACT_NAMES = ("R", "S", "T", "P", "Q")
MEMORY_LIMIT = 2560 * 1024**2


def mask(names):
    return sum(1 << name for name in set(names))


def bits(form):
    while form:
        bit = form & -form
        yield bit
        form ^= bit


def pivots_and_remainders(forms, coordinates=None):
    """Eliminate on chosen coordinates, retaining the other coordinates."""
    pivots = {}
    remainders = []
    for form in forms:
        restricted = form if coordinates is None else form & coordinates
        while restricted:
            pivot = restricted & -restricted
            if pivot not in pivots:
                pivots[pivot] = form
                break
            form ^= pivots[pivot]
            restricted = form if coordinates is None else form & coordinates
        else:
            remainders.append(form)
    return pivots, remainders


def rank(forms):
    return len(pivots_and_remainders(forms)[0])


def remainder(form, pivots):
    unmatched = 0
    while form:
        pivot = form & -form
        if pivot in pivots:
            form ^= pivots[pivot]
        else:
            unmatched |= pivot
            form ^= pivot
    return unmatched


def ring_start(linked):
    """Three four-knot rings with linked connectors or loose connector ends."""
    rings = tuple(tuple(range(i, i + 4)) for i in (0, 4, 8))
    knots = [[] for _ in range(18)]
    names = count()

    def add(*holders):
        name = next(names)
        for holder in holders:
            knots[holder].append(name)
        return name

    for ring in rings:
        for pos, knot in enumerate(ring):
            add(knot, ring[(pos + 1) % 4])
    loose = tuple(tuple(add(knot) for knot in ring for _ in range(2)) for ring in rings)
    attachments = []
    used = [0] * len(rings)
    for connector, pair in enumerate(combinations(range(len(rings)), 2)):
        mids = (12 + 2 * connector, 13 + 2 * connector)
        for ring_number, middle in zip(pair, mids, strict=True):
            pos = used[ring_number]
            used[ring_number] += 1
            first, second = rings[ring_number][pos], rings[ring_number][pos + 2]
            attachments.append((pair, (add(first, middle), add(second, middle))))
        if linked:
            add(*mids)
            add(*mids)
        else:
            for middle in mids:
                add(middle)
                add(middle)
    return knots, rings, loose, attachments


def holdings(knots):
    owners = defaultdict(list)
    for name, distinctions in enumerate(knots):
        for distinction in distinctions:
            owners[distinction].append(name)

    meets, loose = [set() for _ in knots], defaultdict(list)
    for distinction, holders in owners.items():
        if len(holders) == 1:
            loose[holders[0]].append(distinction)
        else:
            left, right = holders
            meets[left].add(right)
            meets[right].add(left)
    return meets, loose, max(owners) + 1


def groups(meets, eligible):
    pair_set = {pair for neighbors in meets for pair in combinations(sorted(neighbors & eligible), 2)}
    joined = {knot: set() for knot in eligible}
    for left, right in pair_set:
        joined[left].add(right)
        joined[right].add(left)

    def maximal(current, open_knots, used_knots):
        if not (open_knots or used_knots):
            if len(current) >= 3 and not set.intersection(*(meets[knot] for knot in current)):
                yield tuple(sorted(current))
            return
        for knot in sorted(open_knots):
            yield from maximal(current + (knot,), open_knots & joined[knot], used_knots & joined[knot])
            open_knots.remove(knot)
            used_knots.add(knot)

    large = sorted(maximal((), set(eligible), set()))
    covered = {pair for group in large for pair in combinations(group, 2)}
    return large + sorted(pair_set - covered)


def grow(knots, lineages):
    meets, loose, next_name = holdings(knots)
    planned = []
    for parents in groups(meets, set(loose)):
        inputs = tuple(min(loose[parent]) for parent in parents)
        for parent, name in zip(parents, inputs, strict=True):
            loose[parent].remove(name)
        planned.append((parents, sorted(inputs)))
    planned.extend(((knot,), [name]) for knot in sorted(loose) for name in sorted(loose[knot]))

    provisional = knots + [inputs for _, inputs in planned]
    newborn = range(len(knots), len(provisional))
    future_meets, _, _ = holdings(provisional)
    demand = Counter(chain.from_iterable(groups(future_meets, set(newborn))))
    old_laws = pivots_and_remainders(map(mask, knots))[0]
    births = []
    for birth, (parents, inputs) in zip(newborn, planned, strict=True):
        implied = remainder(mask(inputs), old_laws) == 0
        count_fresh = demand[birth] if implied else max(demand[birth], 3 - len(inputs), 1)
        fresh = list(range(next_name, next_name + count_fresh))
        next_name += count_fresh
        origin = {lineages[parent] for parent in parents}
        assert len(origin) == 1 and None not in origin
        lineages.append(origin.pop())
        knots.append(inputs + fresh)
        births.append((parents, fresh))
    return births


def shared_pairs(laws, a, b, all_names):
    """Take ranks after restricting the certainty spaces to each middle treatment."""
    assert a and b and not (a & b)
    pair = a | b
    middle = all_names ^ pair
    joint_values = pivots_and_remainders(laws, middle)[1]
    pair_laws = [row & pair for row in laws]
    rank_pair = rank(pair_laws)
    rank_all = rank(laws)

    # A restricted value functional acts on ker H through its class modulo row H.
    # The change space is ker H on the pair if middle changes are prohibited.
    unread = rank(chain(pair_laws, (row & a for row in joint_values))) - rank_pair
    values = rank(chain(pair_laws, (row & a for row in laws))) - rank_pair
    changes = rank(chain(laws, (row & a for row in joint_values))) - rank_all

    # A second computation uses dimensions of the laws or changes supported on each reader.
    assert values == rank(row & a for row in laws) + rank(row & b for row in laws) - rank_pair
    assert changes == (rank(row & (a | middle) for row in laws)
                       + rank(row & (b | middle) for row in laws)
                       - rank(row & middle for row in laws) - rank_all)
    return [unread, values, changes]


def local_witness(row, ring, local_laws):
    """Find an allowed change on one ring on which the given functional is odd."""
    witness_pivots = {**local_laws}
    reduced = remainder(row & ring, local_laws)
    if reduced == 0:
        return []
    new_pivot = reduced & -reduced
    witness_pivots[new_pivot] = reduced
    witness = new_pivot
    for pivot, rule in sorted(witness_pivots.items(), reverse=True):
        if pivot != new_pivot and (rule & witness).bit_count() % 2:
            witness |= pivot
    assert (witness & row).bit_count() % 2 == 1
    assert all((rule & witness).bit_count() % 2 == 0 for rule in local_laws.values())
    return [bit.bit_length() - 1 for bit in bits(witness)]


def read_stage(round_number, knots, lineage, supports, attachments, trial_masks):
    laws = list(map(mask, knots))
    all_names = mask(chain.from_iterable(knots))
    ring_masks = [mask(chain.from_iterable(knot for knot, label in zip(knots, lineage, strict=True)
                                         if label == ring)) for ring in range(3)]
    pairs = list(combinations(range(3), 2))
    for i, j in pairs:
        assert not (ring_masks[i] & ring_masks[j])
        assert not any(row & ring_masks[i] and row & ring_masks[j] for row in laws)

    forms = [0]
    for support in supports:
        forms += [row ^ mask(support) for row in forms]
    law_basis = pivots_and_remainders(laws)[0]
    classes = {}
    for index, form in enumerate(forms):
        classes.setdefault(remainder(form, law_basis), []).append(index)
    index_to_class = {index: group[0] for group in classes.values() for index in group}

    local_laws = [pivots_and_remainders(row & ring for row in laws)[0] for ring in ring_masks]
    outside_laws = [pivots_and_remainders(row & (all_names ^ ring) for row in laws)[0] for ring in ring_masks]
    results = [[], [], []]
    flip_counts = [0, 0, 0]
    single_ring_count = 0
    witnesses = [{name: local_witness(mask(support), ring, local)
                  for name, support in zip(FACT_NAMES, supports, strict=True)}
                 for ring, local in zip(ring_masks, local_laws, strict=True)]
    for index in trial_masks:
        form = forms[index]
        local_flips = [ring for ring in range(3) if remainder(form & ring_masks[ring], local_laws[ring])]
        single_reps = [ring for ring in range(3)
                       if not remainder(form & (all_names ^ ring_masks[ring]), outside_laws[ring])]
        for ring in local_flips:
            flip_counts[ring] += 1
        single_ring_count += bool(single_reps) and index != 0
        class_id = index_to_class[index]
        for pair_number, (i, j) in enumerate(pairs):
            # The zero outcome is always allowed. For a nonzero class, the one
            # outcome is a translation with the same certainty supports and rank.
            restricted = laws + [form] if index else laws
            e = shared_pairs(restricted, ring_masks[i], ring_masks[j], all_names)
            results[pair_number].append({"restriction_mask": index, "class_mask": class_id,
                                         "allowed_outcomes": [0, 1] if class_id else [0],
                                         "local_flip_rings": local_flips, "single_ring_representatives": single_reps,
                                         "can_avoid_readers": [ring for ring in (i, j) if ring not in local_flips],
                                         "e": e})

    attachment_controls = []
    for (i, j), support in attachments:
        fixed = shared_pairs(laws + [mask(support)], ring_masks[i], ring_masks[j], all_names)
        attachment_controls.append({"readers": [i, j], "fixed_attachment_parity": support, "e": fixed})
    return {"round": round_number, "frozen_round": round_number in FROZEN_ROUNDS,
            "knots": len(knots), "distinctions": all_names.bit_count(), "ring_sizes": [a.bit_count() for a in ring_masks],
            "fact_supports": supports, "classes": list(classes.values()),
            "local_change_rank": [ring.bit_count() - len(basis)
                                  for ring, basis in zip(ring_masks, local_laws, strict=True)],
            "local_flip_count": flip_counts, "single_ring_representative_count": single_ring_count,
            "local_flip_witnesses": witnesses, "pairs": [{"readers": pair, "results": rows}
                                                          for pair, rows in zip(pairs, results, strict=True)],
            "attachment_controls": attachment_controls}


def disconnected_controls():
    knots, rings, loose, _ = ring_start(linked=False)
    laws = list(map(mask, knots))
    a, b, m = (ring[0] for ring in loose)
    left, right, _ = (mask(chain.from_iterable(knots[knot] for knot in ring)) for ring in rings)
    all_names = mask(chain.from_iterable(knots))
    assert not any(row & left and row & right for row in laws)
    cases = (("unrestricted", [], left, right),
             ("a + b fixed (one loose distinction of each ring)", [a, b], left, right),
             ("a + b + m fixed (m a loose distinction of the third ring)", [a, b, m], left, right),
             ("ring 0's own fact fixed", loose[0], left, right),
             ("readers holding only a and b, a + b + m fixed", [a, b, m], mask([a]), mask([b])))
    return [{"control": name, "fixed_support": support, "e": shared_pairs(laws + [mask(support)], x, y, all_names)}
            for name, support, x, y in cases]


def match_saved_fields(result):
    """Compare saved summaries after rebuilding the cases without archived inputs."""
    with gzip.open(HERE.parent / "bound_facts_out.jsonl.gz", "rt") as handle:
        *rows, saved_controls = [json.loads(line) for line in handle]
    predecessor = HERE.parents[1] / "THIRD-LAYER-20261126-001/referee-R1/ring_overlap_counts.json"
    certificate = json.loads(predecessor.read_text())
    inspected = [stage for stage in result["stages"] if stage["frozen_round"]]
    matched_stage_fields = 0
    for stage, saved, certified in zip(inspected, rows, certificate["stages"], strict=True):
        assert stage["round"] == certified["round"]
        assert [list(support) for support in stage["fact_supports"]] == certified["supports"]
        assert {tuple(int(bool(index & (1 << bit))) for bit in range(len(FACT_NAMES)))
                for index in stage["classes"][0]} == set(map(tuple, certified["relations including zero"]))
        fields = {key: stage[key] for key in ("round", "knots", "distinctions")}
        for ring in range(3):
            fields[f"ring {ring}: local changes (rank)"] = stage["local_change_rank"][ring]
            fields[f"ring {ring}: sums of the five facts flipped by a local change"] = stage["local_flip_count"][ring]
        summaries = {}
        for pair in stage["pairs"]:
            i, j = pair["readers"]
            for index, treatment in enumerate(TREATMENTS):
                scores = [row["e"][index] for row in pair["results"]]
                summaries[f"rings {i} and {j}, middle {treatment}"] = {
                    "unrestricted": scores[0],
                    **{f"{name} fixed": scores[1 << bit] for bit, name in enumerate(FACT_NAMES)},
                    "largest over the 31 sums": max(scores[1:]),
                    "smallest over the 31 sums": min(scores[1:]),
                }
        fields["e"] = summaries
        assert fields == saved, stage["round"]
        matched_stage_fields += len(fields) - 1 + sum(map(len, summaries.values()))

    controls = {"separated": True}
    for index, treatment in enumerate(TREATMENTS):
        controls[f"middle {treatment}"] = {row["control"]: row["e"][index] for row in result["controls"]}
    assert controls == saved_controls["controls: three rings joined by nothing"]
    return {"matched_stage_fields": matched_stage_fields, "matched_control_fields": 1 + 5 * len(TREATMENTS),
            "matched_supports_and_relations_on_rounds": FROZEN_ROUNDS}


def run(pilot):
    started = perf_counter()
    knots, rings, loose, attachments = ring_start(linked=True)
    lineage = [ring for ring, members in enumerate(rings) for _ in members] + [None] * 6
    trial_masks = (0, 1, 2, 4, 8, 16) if pilot else range(32)
    stages = []
    for round_number in range(1, 2 if pilot else 8):
        births = grow(knots, lineage)
        if round_number == 1:
            halves = (set(rings[0][::2]), set(rings[0][1::2]))
            supports = loose + tuple(tuple(chain.from_iterable(fresh for parents, fresh in births
                                                               if set(parents) <= half)) for half in halves)
            assert len(set(chain.from_iterable(supports))) == sum(map(len, supports))
        stages.append(read_stage(round_number, knots, lineage, supports, attachments, trial_masks))

    return {"pilot": pilot, "treatments": TREATMENTS, "fact_order": FACT_NAMES,
            "stage_computation_seconds": perf_counter() - started,
            "workers": 1, "address_space_limit_bytes": MEMORY_LIMIT,
            "controls": disconnected_controls(), "stages": stages}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot", action="store_true")
    args = parser.parse_args()
    resource.setrlimit(resource.RLIMIT_AS, (MEMORY_LIMIT, MEMORY_LIMIT))
    started = perf_counter()
    result = run(args.pilot)
    if not args.pilot:
        result["saved_field_comparison"] = match_saved_fields(result)
    result["elapsed_seconds"] = perf_counter() - started
    result["peak_rss_kib"] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    path = HERE / ("part_b_pilot.json" if args.pilot else "part_b_results.json")
    path.write_text(json.dumps(result, indent=2) + "\n")
    score_rows = sum(len(pair["results"]) for stage in result["stages"] for pair in stage["pairs"])
    print(f"{len(result['stages'])} rounds, {score_rows} reader-pair rows, "
          f"{result['elapsed_seconds']:.3f} seconds and {result['peak_rss_kib']} KiB peak RSS")


if __name__ == "__main__":
    main()
