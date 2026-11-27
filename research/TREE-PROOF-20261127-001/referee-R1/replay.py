"""Remeasure the frozen pair and set costs from the ordinary stage parity rows.

For pair costs, connect the loose distinctions of each family to its own
auxiliary terminal. An allowed change of the prescribed family parities has
odd incidence precisely at the two specified terminals. They must lie in
one connected part of the change, so a shortest route is an exact minimum.
This computation uses the actual stage distinctions and their holders.
The family-chain comparison is run only after this measurement.
"""

import argparse
import hashlib
import json
import resource
import time
from collections import Counter, deque
from itertools import combinations
from pathlib import Path

from growth import (
    components,
    families,
    family_facts,
    family_step_counts,
    meeting_pattern,
    name_mask,
    parity_basis,
    reduce_mask,
    stages,
)
from growth_roster import ARCHIVE, SETS, load_starts


HERE = Path(__file__).resolve().parent
SCALES = (8, 12)


def extend_lineages(lineages, births):
    for birth in births:
        parent_families = {lineages[parent] for parent in birth.parents}
        if len(parent_families) != 1:
            raise ValueError(f"Birth {birth.knot} has parents in multiple families")
        lineages[birth.knot] = parent_families.pop()


def stage_family_facts(supports, lineages, count):
    _, _, loose = meeting_pattern(supports)
    facts = [[] for _ in range(count)]
    for knot, names in loose.items():
        facts[lineages[knot]].extend(names)
    return tuple(map(tuple, facts))


def _incidence(holders, count, loose_end):
    adjacency = [[] for _ in range(count)]
    for name, held in holders.items():
        a, b = held if len(held) == 2 else (held[0], loose_end[name])
        adjacency[a].append((b, name))
        adjacency[b].append((a, name))
    return adjacency


def _walk(adjacency, source, omit=-1, stop=-1, with_routes=False):
    distance = [-1] * len(adjacency)
    route = [0] * len(adjacency) if with_routes else None
    todo = deque([source])
    distance[source] = 0
    while todo:
        a = todo.popleft()
        if a == stop:
            break
        step = distance[a] + 1
        for b, name in adjacency[a]:
            if name != omit and distance[b] < 0:
                todo.append(b)
                distance[b] = step
                if with_routes:
                    route[b] = route[a] ^ (1 << name)
    return distance, route


def pair_minima(supports, facts):
    """Return exact two-family minima and one attaining change per pair."""
    holders, _, loose = meeting_pattern(supports)
    count, family_count = len(supports), len(facts)
    loose_end = {name: count + index for index, fact in enumerate(facts) for name in fact}
    names = tuple(name for row in loose.values() for name in row)
    if sorted(loose_end) != sorted(names) or sum(map(len, facts)) != len(names):
        raise ValueError("The stage family facts must partition the loose distinctions")
    adjacency = _incidence(holders, count + family_count, loose_end)
    costs, attaining = {}, {}
    for i in range(family_count - 1):
        steps, routes = _walk(adjacency, count + i, with_routes=True)
        for j in range(i + 1, family_count):
            cost = steps[count + j]
            costs[i, j] = cost if cost >= 0 else None
            attaining[i, j] = routes[count + j]
    return costs, attaining


def _set_minimum(shared, loose, owner, mask):
    # Split the auxiliary exterior in two by the parity being flipped. A
    # shortest route between the two parts uses one loose distinction at
    # its beginning and one at its end.
    from_side = {owner[name] for name, family in loose.items() if mask & (1 << family)}
    to_side = {owner[name] for name, family in loose.items() if not mask & (1 << family)}
    if from_side & to_side:
        return 2
    todo = deque((knot, 2) for knot in from_side)
    seen = set(from_side)
    while todo:
        knot, cost = todo.popleft()
        for other in shared[knot] - seen:
            if other in to_side:
                return cost + 1
            seen.add(other)
            todo.append((other, cost + 1))
    return None


def _shortest_pair_flips(holders, facts, count):
    # Here there is a single exterior, as in the frozen shortest reading.
    # A minimal change through a named distinction is a shortest cycle
    # through it. The cycle has a nonzero family parity only if it enters
    # and leaves the exterior on loose distinctions of different families.
    labels = {name: family for family, fact in enumerate(facts) for name in fact}
    exterior = count
    adjacency = _incidence(holders, count + 1, dict.fromkeys(labels, exterior))
    flips = set()

    def closest_labels(distance, omit):
        steps = distance[exterior]
        if steps < 0:
            return set()
        return {
            labels[name]
            for knot, name in adjacency[exterior]
            if name != omit and distance[knot] == steps - 1
        }

    for name, held in holders.items():
        a = held[0]
        if len(held) == 1:
            steps, _ = _walk(adjacency, a, omit=name, stop=exterior)
            flip = labels[name]
            flips.update(tuple(sorted((flip, other))) for other in closest_labels(steps, name) if flip != other)
            continue
        b = held[1]
        if any(other == b and link != name for other, link in adjacency[a]):
            continue  # A parallel shared distinction gives a change of two.
        from_a, _ = _walk(adjacency, a, omit=name)
        direct, via_exterior = from_a[b], from_a[exterior]
        if via_exterior < 0 or direct <= via_exterior:
            continue
        from_b, _ = _walk(adjacency, b, omit=name)
        if via_exterior + from_b[exterior] != direct:
            continue
        # Equality means that any two shortest routes to the exterior meet
        # only there. An earlier meeting would give a shorter route to b.
        flips.update(
            tuple(sorted((i, j)))
            for i in closest_labels(from_a, name)
            for j in closest_labels(from_b, name)
            if i != j
        )
    return flips


def _measure_sums(supports, facts):
    holders, shared, _ = meeting_pattern(supports)
    loose = {name: family for family, fact in enumerate(facts) for name in fact}
    owner = {name: holders[name][0] for name in loose}
    sums = {mask: _set_minimum(shared, loose, owner, mask) for mask in range(1, (1 << len(facts)) - 1, 2)}
    split = tuple((1 << i) | (1 << j) for i, j in _shortest_pair_flips(holders, facts, len(supports)))
    kept = sum(not any((mask & change).bit_count() & 1 for change in split) for mask in sums)
    return sums, kept


def chain_costs(count, starting_steps, round_number):
    """Compute the proof's prediction on the start after measuring the stage."""
    costs = [[0] * count for _ in range(count)]
    for (i, j), value in starting_steps.items():
        costs[i][j] = costs[j][i] = value + 2 * round_number + 2
    for middle in range(count):
        for a in range(count):
            for b in range(a + 1, count):
                route = costs[a][middle] + costs[middle][b]
                if route < costs[a][b]:
                    costs[a][b] = costs[b][a] = route
    return {(i, j): costs[i][j] for i, j in starting_steps}


def maximum_triangle_defect(count, starting_steps):
    """The smallest nonnegative toll per step that makes every direct weight metric."""
    steps = [[0] * count for _ in range(count)]
    for (i, j), value in starting_steps.items():
        steps[i][j] = steps[j][i] = value
    return max(
        (d - steps[i][k] - steps[k][j] for (i, j), d in starting_steps.items() for k in range(count)),
        default=0,
    )


def _label_set(mask, count):
    return [index for index in range(count) if mask & (1 << index)]


def _stage_record(supports, round_number, start_facts, current_facts, starting_steps):
    count = len(start_facts)
    rows = [name_mask(support) for support in supports]
    start_masks, current_masks = tuple(map(name_mask, start_facts)), tuple(map(name_mask, current_facts))
    basis = parity_basis(supports)
    for old, new in zip(start_masks, current_masks, strict=True):
        if reduce_mask(old ^ new, basis):
            raise ValueError("Starting and current loose family parities disagree on allowed states")

    pair, attaining = pair_minima(supports, current_facts)
    direct = {key: value + 2 * round_number + 2 for key, value in starting_steps.items()}
    chain = chain_costs(count, starting_steps, round_number)
    sk1 = []
    witness_records = []
    for (i, j), min_cost in pair.items():
        change = attaining[i, j]
        if min_cost is not None:
            if change.bit_count() != min_cost or any((row & change).bit_count() & 1 for row in rows):
                raise ValueError("An attaining change violates an actual stage parity or its reported size")
            if any(((mask & change).bit_count() & 1) != (index in (i, j))
                   for index, mask in enumerate(start_masks)):
                raise ValueError("An attaining change has the wrong starting family parities")
        if min_cost != direct[i, j]:
            sk1.append([i, j, starting_steps[i, j], min_cost])
            witness_records.append({
                "families": (i, j),
                "least change distinctions": _label_set(change, change.bit_length()),
                "loose distinctions in least change": [
                    name for fact in current_facts for name in fact if change & (1 << name)
                ],
                "direct prediction": direct[i, j],
                "chain prediction": chain[i, j],
            })

    observed = {"round": round_number, "SK1 failures": sk1, "SK2 failures": []}
    raw = {
        "round": round_number,
        "knots": len(supports),
        "distinctions": len({name for row in supports for name in row}),
        "pair costs": tuple(pair.values()),
    }
    if witness_records:
        raw["direct discrepancies"] = witness_records
    tally = Counter({
        "rounds read": 1,
        "pair rows": len(pair),
        "chain matches": sum(pair[key] == chain[key] for key in pair),
        "pair rows with a third family present": len(pair) if count > 2 else 0,
        "chain shorter than direct prediction": sum(chain[key] < direct[key] for key in pair),
        "direct predictions missed": len(sk1),
    })
    differences = [[i, j, pair[i, j], value] for (i, j), value in chain.items() if pair[i, j] != value]
    if differences:
        raw["chain discrepancies"] = differences
    if count <= 6:
        sums, kept_shortest = _measure_sums(supports, current_facts)
        tally["set costs read"] = len(sums)
        for mask, cost in sums.items():
            cutting = [
                (i, j) for i, j in pair
                if ((mask >> i) & 1) != ((mask >> j) & 1)
            ]
            prediction = min(direct[key] for key in cutting)
            measured_crossing = min((pair[key] for key in cutting if pair[key] is not None), default=None)
            if cost != prediction:
                observed["SK2 failures"].append([_label_set(mask, count), prediction, cost])
            tally["SK2 direct crossing matches"] += cost == prediction
            tally["SK2 measured crossing matches"] += cost == measured_crossing
        for k in SCALES:
            kept = sum(cost is None or cost > k for cost in sums.values())
            dim = kept.bit_length() if not kept & (kept + 1) else None
            neighbors = {index: set() for index in range(count)}
            for (i, j), weight in direct.items():
                if weight <= k:
                    neighbors[i].add(j)
                    neighbors[j].add(i)
            clusters = tuple(name_mask(group) for group in components(neighbors))
            predicted = len(clusters) - 1
            agreeing_sums = sum(
                (cost is None or cost > k) == all(mask & group in (0, group) for group in clusters)
                for mask, cost in sums.items()
            )
            observed[f"SK3 k={k}"] = {"kept sums": kept, "dimension": dim, "predicted": predicted}
            tally[f"SK3 rounds at {k}"] = 1
            tally[f"SK3 dimension matches at {k}"] = dim == predicted
            tally[f"SK3 individual sum classifications matched at {k}"] = agreeing_sums
        observed["shortest reading: kept sums"] = kept_shortest
        tally["shortest reading rounds"] = 1
        tally["shortest reading keeps a sum"] = kept_shortest > 0
        raw["proper set costs"] = tuple(sums.values())
        raw["shortest reading kept sums"] = kept_shortest
    return observed, raw, tally


def run_start(name, start):
    groups = families(start)
    result = {"start": name, "families": groups, "rounds": []}
    observed = {"start": name, "families": len(groups), "rounds": []}
    totals = Counter({"starts": 1, f"starts with {len(groups)} families": 1})
    by_round = {}
    if len(groups) < 2:
        return observed, result, totals, by_round
    totals["eligible starts"] = 1
    start_facts = family_facts(start, groups)
    starting_steps = family_step_counts(start, groups)
    observed["distances"] = {f"{i}-{j}": value for (i, j), value in starting_steps.items()}
    result["starting steps"] = observed["distances"]
    result["maximum triangle defect"] = maximum_triangle_defect(len(groups), starting_steps)
    totals[f"starts with maximum triangle defect {result['maximum triangle defect']}"] = 1
    lineages = {knot: index for index, group in enumerate(groups) for knot in group}
    prev = start
    for round_number, supports, status, births in stages(start):
        if round_number and births:
            holders, meetings, loose = meeting_pattern(prev)
            allocated = Counter(name for birth in births for name in birth.inputs)
            if allocated != Counter(name for row in loose.values() for name in row):
                raise ValueError("A funded transition did not spend each loose distinction once")
            totals["funded transitions"] += 1
            totals["births"] += len(births)
            for birth in births:
                if len(birth.parents) != len(birth.inputs) or len(birth.parents) != len(set(birth.parents)):
                    raise ValueError("A birth did not take one distinction per parent")
                if {holders[name][0] for name in birth.inputs} != set(birth.parents):
                    raise ValueError("A paid distinction did not come from the corresponding parent")
                if any(not (meetings[a] & meetings[b]) for a, b in combinations(birth.parents, 2)):
                    raise ValueError("Two parents of a birth have no common meeting knot")
            extend_lineages(lineages, births)
            if any(not birth.fresh for birth in births) and len(births) != 1:
                raise ValueError("A connected start closed in more than one birth")
            totals["zero-fresh births"] += sum(not birth.fresh for birth in births)
        if status != "stage":
            row = {"round": round_number, "end": status}
            observed["rounds"].append(row)
            result["rounds"].append(row)
            totals[f"end: {status}"] += 1
            break
        prev = supports
        current_facts = stage_family_facts(supports, lineages, len(groups))
        stage, raw, tally = _stage_record(supports, round_number, start_facts, current_facts, starting_steps)
        tally["rounds with a strictly cheaper family chain possible"] = (
            result["maximum triangle defect"] > 2 * round_number + 2
        )
        observed["rounds"].append(stage)
        result["rounds"].append(raw)
        totals.update(tally)
        by_round[round_number] = tally
    return observed, result, totals, by_round


def _read_frozen(which):
    source = ARCHIVE / f"frozen_{which}.jsonl"
    data = source.read_bytes()
    return list(map(json.loads, data.splitlines())), hashlib.sha256(data).hexdigest()


def _check_record(computed, archived):
    expected = {key: archived[key] for key in ("start", "families", "rounds")}
    if "distances" in archived:
        expected["distances"] = archived["distances"]
    return None if computed == expected else {"recomputed": computed, "recorded": expected}


def _pilot_roster(roster):
    positions = {0, len(roster) - 1, len(roster) // 3, len(roster) * 2 // 3}
    positions.update(range(0, len(roster), max(1, len(roster) // 20)))
    shortcuts = {"held out 8-50", "sampled 12-35", "sampled 12-56"}
    return [row for i, row in enumerate(roster) if i in positions or row[0] in shortcuts]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot", action="store_true", help="Run a fixed sample and the three exceptions")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--raw", type=Path, help="Write all independently measured pair costs by start")
    args = parser.parse_args()
    begin = time.monotonic()
    coverage = {}
    raw_lines = []
    for which in SETS:
        started = time.monotonic()
        records, digest = _read_frozen(which)
        full = list(load_starts(which))
        if [name for name, _ in full] != [r["start"] for r in records]:
            raise ValueError(f"Start names or order disagree in the {which} roster")
        by_name = {r["start"]: r for r in records}
        if len(by_name) != len(records):
            raise ValueError(f"Duplicate start names in the {which} roster")
        chosen = _pilot_roster(full) if args.pilot else full
        tallies, rounds = Counter(), {}
        exceptions = []
        differences = []
        chain_differences = []
        for name, start in chosen:
            computed, raw, tally, by_round = run_start(name, start)
            diff = _check_record(computed, by_name[name])
            if diff:
                differences.append(diff)
            tallies.update(tally)
            for round_number, counter in by_round.items():
                rounds.setdefault(round_number, Counter()).update(counter)
            for round_row in raw["rounds"]:
                if "direct discrepancies" in round_row:
                    exceptions.append({
                        "start": name,
                        "start supports": start,
                        "families": raw["families"],
                        "starting steps": raw["starting steps"],
                        "round": round_row["round"],
                        "witnesses": round_row["direct discrepancies"],
                    })
                if "chain discrepancies" in round_row:
                    chain_differences.append({
                        "start": name,
                        "round": round_row["round"],
                        "discrepancies": round_row["chain discrepancies"],
                    })
            if args.raw:
                raw_lines.append(json.dumps({"roster": which, **raw}, separators=(",", ":")))
        coverage[which] = {
            "archive sha256": digest,
            "population": len(full),
            "counts": tallies,
            "counts by round": rounds,
            "direct exceptions": exceptions,
            "chain discrepancies": chain_differences,
            "archive discrepancies": differences,
            "seconds including roster generation": round(time.monotonic() - started, 4),
        }
    if args.raw:
        args.raw.write_text("[\n" + ",\n".join(raw_lines) + "\n]\n")
    totals = sum((record["counts"] for record in coverage.values()), Counter())
    for key in ("zero-fresh births", "end: closed", "end: stalled", "end: not read"):
        totals.setdefault(key, 0)
    result = {
        "method": "Exact least changes measured from the independently rebuilt stage parity constraints. Pair minima come from split-terminal shortest routes. Set minima are separately measured by splitting the exterior in two. Shortest reading projects every tied shortest cycle through each distinction.",
        "scope": "Frozen starts with at least two families, rounds zero through four, 300-distinction ceiling, and at most six families for set costs and both readings. Start order checked against the archives.",
        "raw ordering": "Pair costs follow the family pairs in lexicographic order. Proper-set costs follow ascending binary masks for sets containing family zero, omitting the whole set.",
        "triangle defect": "The largest d(A,B) minus d(A,C) minus d(C,B), floored at zero. The direct weights satisfy all triangles exactly when 2t+2 is at least this defect. Any smaller toll admits a strictly cheaper chain on some pair.",
        "run": "pilot" if args.pilot else "full",
        "totals": totals,
        "set details": coverage,
        "seconds": round(time.monotonic() - begin, 4),
        "peak RSS KiB": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
    }
    if args.output:
        args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({
        "totals": totals,
        "seconds": result["seconds"],
        "peak RSS KiB": result["peak RSS KiB"],
        "archive discrepancy counts": {which: len(row["archive discrepancies"]) for which, row in coverage.items()},
        "chain discrepancy counts": {which: len(row["chain discrepancies"]) for which, row in coverage.items()},
    }, indent=2))


if __name__ == "__main__":
    main()
