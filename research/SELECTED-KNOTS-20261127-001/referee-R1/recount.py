"""Recount the frozen records and enumerate both readings on their family trees."""

import argparse
import hashlib
import json
from collections import Counter, defaultdict, deque
from itertools import combinations
from pathlib import Path

from cost_check import Stage, grow, stage_costs, starting_families


HERE = Path(__file__).resolve().parent
STUDY = HERE.parent
ROSTERS = ("census", "heldout", "sampled", "built")
SCALES = (8, 12)


def indices(mask):
    return tuple(i for i in range(mask.bit_length()) if mask & (1 << i))


def dot(left, right):
    return (left & right).bit_count() % 2


def span(vectors):
    result = {0}
    for vector in vectors:
        if vector not in result:
            result |= {word ^ vector for word in result}
    return result


def canonical(mask, universe):
    return min(mask, mask ^ universe)


def partition(size, costs, limit):
    """Return the family groups joined by any chain of affordable pairs."""
    groups = [1 << i for i in range(size)]
    for (i, j), cost in costs.items():
        if cost <= limit and groups[i] != groups[j]:
            joined = groups[i] | groups[j]
            for member in indices(joined):
                groups[member] = joined
    return frozenset(groups)


def partition_facts(groups, universe):
    return {canonical(mask, universe) for mask in span(sorted(groups))} - {0}


def dendrogram(size, distances):
    """Merge all equal holder-step counts at once and retain every distinct group."""
    universe = (1 << size) - 1
    previous = frozenset(1 << i for i in range(size))
    children = {}
    merge_thresholds = {}
    for threshold in sorted(set(distances.values())):
        current = partition(size, distances, threshold)
        for group in current - previous:
            children[group] = tuple(sorted(child for child in previous if child & group))
            assert all(child & group == child for child in children[group])
            assert sum(children[group]) == group and len(children[group]) >= 2
            merge_thresholds[group] = threshold
        previous = current
    assert previous == {universe}
    places = sorted((set(children) | {1 << i for i in range(size)}) - {universe},
                    key=lambda group: (group.bit_count(), indices(group)))
    place_index = {place: i for i, place in enumerate(places)}
    laws = []
    for parent, kids in children.items():
        support = kids if parent == universe else (parent,) + kids
        laws.append(tuple(sorted(place_index[place] for place in support)))
    return places, sorted(laws), children, merge_thresholds


def layer_three(size, places, laws):
    """Use literal family assignments and enumerate facts modulo the root relation."""
    universe = (1 << size) - 1
    signatures = [word for word in range(1 << size) if not word.bit_count() % 2]
    codewords = {word: sum(dot(place, word) << i for i, place in enumerate(places))
                 for word in signatures}
    assert len(set(codewords.values())) == len(signatures)
    costs = {word: code.bit_count() for word, code in codewords.items() if word}
    minimum = min(costs.values())
    global_shortest = {word for word, cost in costs.items() if cost == minimum}
    shortest_through_places = set()
    for place in places:
        through = {word: cost for word, cost in costs.items() if dot(word, place)}
        bound = min(through.values())
        shortest_through_places.update(word for word, cost in through.items() if cost == bound)

    def kept_by(changes):
        return {word for word in range(1, 1 << (size - 1))
                if all(not dot(word, change) for change in changes)}

    locals_by_knot = [{canonical(word, universe) for word in span(places[i] for i in law)}
                      for law in laws]
    kept = kept_by(global_shortest)
    locally_read = kept & set.union(*locals_by_knot)
    readers_of_arity_three_or_more = [local for law, local in zip(laws, locals_by_knot) if len(law) >= 3]
    kept_with_no_equalities = kept & set().union(*readers_of_arity_three_or_more)
    span_of_locals = span(sorted(locally_read)) - {0}
    assert span_of_locals <= kept

    # Read the lattice of allowed values directly for every proposed law support.
    for law in laws:
        tuples = {tuple((code >> i) & 1 for i in law) for code in codewords.values()}
        assert len(tuples) == 1 << (len(law) - 1)
        assert all(not sum(values) % 2 for values in tuples)
    relation_span = span(sum(1 << i for i in law) for law in laws)
    assert len(relation_span) == 1 << (len(places) - size + 1)

    return {
        "least": minimum, "least signatures": global_shortest, "facts": kept,
        "read by one knot": locally_read, "outside local span": kept - span_of_locals,
        "read by one law of at least three places": kept_with_no_equalities,
        "shortest-through-each-place signatures": shortest_through_places,
        "shortest-through-each-place facts": kept_by(shortest_through_places),
        "local functions": locals_by_knot,
    }


def crossing(costs, cut):
    return min(cost for (i, j), cost in costs.items() if ((cut >> i) ^ (cut >> j)) & 1)


def possible_larger_competitor(cut, size):
    # An even family change of weight >=4 crosses oddly only if we can take
    # three families on one side and at least one family on the other.
    return max(cut.bit_count(), size - cut.bit_count()) >= 3


def recount_roster(path, pilot):
    output = defaultdict(Counter)
    count = output["coverage"]
    stop_counts = output["terminal records by reason"]
    denominators = output["family counts by start"]
    seen = set()
    differences = defaultdict(list)
    raw = path.read_bytes()
    for n, line in enumerate(raw.splitlines()):
        if pilot and n >= 40:
            break
        entry = json.loads(line)
        size = entry["families"]
        name = entry["start"]
        assert name not in seen
        seen.add(name)
        count["start records"] += 1
        denominators[size] += 1
        if size < 2:
            assert not entry["rounds"] and "SK4" not in entry
            continue
        count["starts with at least two families"] += 1
        distances = {tuple(map(int, pair.split("-"))): value
                     for pair, value in entry["distances"].items()}
        assert set(distances) == set(combinations(range(size), 2))
        assert min(distances.values()) > 0
        universe = (1 << size) - 1
        places, laws, children, _ = dendrogram(size, distances)
        tree = layer_three(size, places, laws)
        archived = entry["SK4"]
        assert archived["places"] == len(places)
        assert sorted(tuple(sorted(law)) for law in archived["second-layer knots"]) == laws
        assert archived["least layer-two change"] == tree["least"] == 2
        sibling_pairs = {a | b for kids in children.values()
                         for a, b in combinations((k for k in kids if k.bit_count() == 1), 2)}
        assert tree["least signatures"] == sibling_pairs
        assert len(tree["facts"]) == (1 << archived["layer-three dimension"]) - 1
        assert len(tree["outside local span"]) == (
            (1 << archived["layer-three dimension"])
            - (1 << (archived["layer-three dimension"] -
                     archived["layer-three facts read by no single second-layer knot (dimension)"])))
        place_laws = output["SK4"]
        place_laws["starts checked"] += 1
        place_laws["places"] += len(places)
        place_laws["relations checked by literal projection"] += len(laws)
        for law in laws:
            output["SK4 relation arities"][len(law)] += 1
        two_place = sum(len(law) == 2 for law in laws)
        assert two_place == (len(children[universe]) == 2)
        place_laws["starts with root equality"] += bool(two_place)
        place_laws["starts with nonzero class facts"] += bool(tree["facts"])
        place_laws["nonzero class facts modulo the laws"] += len(tree["facts"])
        place_laws["nonzero facts lacking a single reader"] += len(tree["facts"] - tree["read by one knot"])
        place_laws["nonzero facts lacking a single reader of arity at least three"] += len(
            tree["facts"] - tree["read by one law of at least three places"])
        place_laws["nonzero facts outside the span of single-knot class facts"] += len(tree["outside local span"])
        place_laws["starts with nonzero facts under shortest-through-each-place ties"] += bool(
            tree["shortest-through-each-place facts"])
        output["SK4 class fact counts by start"][len(tree["facts"])] += 1

        scale_blocks = set()
        kept_by_round = {}
        scale_partitions = {}
        for t, row in enumerate(entry["rounds"]):
            assert t == row["round"]
            if "end" in row:
                assert row is entry["rounds"][-1]
                stop_counts[row["end"]] += 1
                break
            count["read rounds"] += 1
            predicted = {pair: d + 2 + 2 * t for pair, d in distances.items()}
            recorded = predicted.copy()
            for i, j, d, observed in row["SK1 failures"]:
                pair = (i, j)
                assert d == distances[pair] and observed != predicted[pair]
                assert isinstance(observed, int)
                recorded[pair] = observed
                differences["SK1 recorded pair failures"].append({
                    "start": name, "round": t, "families": pair,
                    "holder steps": d, "predicted cost": predicted[pair], "recorded cost": observed,
                })
            checked = output["SK1"]
            checked["pair comparisons"] += len(predicted)
            checked["round-zero pair comparisons"] += len(predicted) if t == 0 else 0
            checked["positive-round pair comparisons"] += len(predicted) if t > 0 else 0
            checked["pair discrepancies"] += len(row["SK1 failures"])
            checked["positive-round pair discrepancies"] += len(row["SK1 failures"]) if t > 0 else 0

            if size > 6:
                assert not row["SK2 failures"] and all(f"SK3 k={k}" not in row for k in SCALES)
                assert "shortest reading: kept sums" not in row
                count["rounds omitted for family sums above six families"] += 1
                continue
            count["rounds reading family sums"] += 1
            cuts = range(1, 1 << (size - 1))
            pred_cuts = {cut: crossing(predicted, cut) for cut in cuts}
            recorded_cuts = {cut: crossing(recorded, cut) for cut in cuts}
            set_costs = pred_cuts.copy()
            for families, forecast, observed in row["SK2 failures"]:
                cut = canonical(sum(1 << i for i in families), universe)
                assert forecast == pred_cuts[cut] and forecast != observed
                set_costs[cut] = observed
            cut_summary = output["SK2"]
            cut_summary["sum comparisons"] += len(cuts)
            cut_summary["rows with at least four families"] += size >= 4
            cut_summary["sum comparisons allowing an odd larger-support competitor"] += sum(
                possible_larger_competitor(cut, size) for cut in cuts)
            cut_summary["reported failures against the formula"] += len(row["SK2 failures"])
            cut_summary["cuts with different formula and recorded-pair minima"] += sum(
                pred_cuts[cut] != recorded_cuts[cut] for cut in cuts)
            cut_summary["sum discrepancies against the recorded-pair minima"] += sum(
                set_costs[cut] != recorded_cuts[cut] for cut in cuts)

            for k in SCALES:
                cells = output[f"SK3 at {k}"]
                clusters = partition(size, predicted, k)
                actual_clusters = partition(size, recorded, k)
                scale_partitions[t, k] = clusters
                scale_blocks.update(clusters - {universe})
                predicted_facts = partition_facts(clusters, universe)
                kept = {cut for cut, cost in set_costs.items() if not isinstance(cost, int) or cost > k}
                assert predicted_facts == {cut for cut, cost in pred_cuts.items() if cost > k}
                record = row[f"SK3 k={k}"]
                assert record["predicted"] == len(clusters) - 1
                assert record["kept sums"] == len(kept)
                assert len(kept) == (1 << record["dimension"]) - 1
                cells["rows"] += 1
                cells["zero fact rows"] += not kept
                cells["all family sum rows"] += len(kept) == len(cuts)
                cells["proper nonzero rows"] += 0 < len(kept) < len(cuts)
                cells["mismatches against the reconstructed family-sum memberships"] += kept != predicted_facts
                cells["rows where one group has an unaffordable direct pair"] += any(
                    cost > k and any(group & (1 << i) and group & (1 << j) for group in clusters)
                    for (i, j), cost in predicted.items())
                cells["rows whose threshold partition differs using recorded pair costs"] += actual_clusters != clusters

            shortest = row["shortest reading: kept sums"]
            assert 0 <= shortest <= len(cuts) and not (shortest & (shortest + 1))
            kept_by_round[t] = shortest
            counts = output[f"shortest reading round {t}"]
            counts["rounds"] += 1
            counts["nonzero"] += shortest > 0
            counts["proper nonzero"] += 0 < shortest < len(cuts)
            counts["all family sums"] += shortest == len(cuts)
            if t:
                totals = output["shortest reading rounds 1 to 4"]
                totals.update({"rounds": 1, "nonzero": shortest > 0,
                               "proper nonzero": 0 < shortest < len(cuts),
                               "all family sums": shortest == len(cuts)})

        if kept_by_round:
            place_laws["starts with scale rows"] += 1
            place_laws["starts showing every nonroot place at the two recorded scales"] += set(places) <= scale_blocks
            internal_places = {place for place in places if place.bit_count() > 1}
            place_laws["starts with a nonroot internal place"] += bool(internal_places)
            place_laws["starts missing a nonroot internal place at both scales across all read rounds"] += bool(
                internal_places - scale_blocks)
            place_laws["nonroot internal places across starts with scale rows"] += len(internal_places)
            place_laws["nonroot internal places seen at either scale"] += len(internal_places & scale_blocks)
            positive_rounds = [kept for t, kept in kept_by_round.items() if t > 0]
            output["shortest reading rounds 1 to 4"]["starts with a read positive round"] += bool(positive_rounds)
            output["shortest reading rounds 1 to 4"]["starts with any nonzero round"] += any(positive_rounds)
        shift = output["scale shift k=8 at t versus k=12 at t+2"]
        for t in range(3):
            if (t, 8) in scale_partitions and (t + 2, 12) in scale_partitions:
                shift["row pairs"] += 1
                shift["unequal partitions"] += scale_partitions[t, 8] != scale_partitions[t + 2, 12]

    return {"sha256": hashlib.sha256(raw).hexdigest(), "counts": dict(output),
            "discrepancies": dict(differences)}


def witness_start():
    """Use two shared distinctions per consecutive pair and five singleton live families."""
    rows = [[] for _ in range(17)]
    for first in range(16):
        shared = (2 * first, 2 * first + 1)
        rows[first].extend(shared)
        rows[first + 1].extend(shared)
    for i, knot in enumerate((0, 1, 4, 9, 16)):
        rows[knot].append(32 + i)
    return rows


def shared_steps(neighbors, starts):
    queue = deque(starts)
    steps = dict.fromkeys(starts, 0)
    while queue:
        knot = queue.popleft()
        for child in neighbors[knot] - steps.keys():
            steps[child] = steps[knot] + 1
            queue.append(child)
    return steps


def five_family_witness():
    start = witness_start()
    stage = Stage(start)
    families, labels = starting_families(stage)
    assert families == [[0], [1], [4], [9], [16]]
    assert all(len(row) >= 3 for row in start)
    assert sum(len(owners) == 1 for owners in stage.owners) == 5
    assert len(shared_steps(stage.near, [0])) == len(start)
    distances = {(i, j): shared_steps(stage.near, families[i])[families[j][0]]
                 for i, j in combinations(range(len(families)), 2)}
    places, laws, _, thresholds = dendrogram(len(families), distances)
    result = layer_three(len(families), places, laws)
    assert result["least signatures"] == {0b00011}
    assert result["facts"] - result["read by one knot"] == {0b01011, 0b01100}
    assert not result["outside local span"] and not result["shortest-through-each-place facts"]

    # A simple allowed change that reaches loose distinctions in two different
    # families costs their minimum shared-holder route plus its two loose ends.
    # Larger allowed changes decompose into simple cycles with at most two loose
    # ends each. The minimum exact-pair cost is the cheapest sum along any
    # route of such family pairs, found by shortest additive closure below.
    rounds = []
    universe = (1 << len(families)) - 1
    for t in range(5):
        if t:
            stage, labels, state, _ = grow(stage, labels)
            assert state == "funded" and len(stage.owners) <= 300
        live = [{knot for knot in stage.live() if labels[knot] == i} for i in range(len(families))]
        by_family = [shared_steps(stage.near, source) for source in live]
        simple_pairs = {(i, j): min(by_family[i][knot] for knot in live[j]) + 2
                        for i, j in distances}
        pairs = [[0 if a == b else simple_pairs[tuple(sorted((a, b)))] for b in range(len(families))]
                 for a in range(len(families))]
        for k in range(len(families)):
            for i, j in distances:
                pairs[i][j] = pairs[j][i] = min(pairs[i][j], pairs[i][k] + pairs[k][j])
        exact = {(i, j): pairs[i][j] for i, j in distances}
        _, comparison_simple, comparison_exact, _ = stage_costs(stage, labels, len(families), do_short=False)
        assert simple_pairs == comparison_simple and exact == comparison_exact
        assert all(cost == distances[pair] + 2 + 2 * t for pair, cost in exact.items())
        rounds.append({"round": t, "distinctions": len(stage.owners), "knots": len(stage.rows),
                       "least pair costs": {f"{i}-{j}": cost for (i, j), cost in exact.items()},
                       "scale facts": {scale: sorted(partition_facts(partition(len(families), exact, scale), universe))
                                       for scale in SCALES},
                       "scale partitions": {scale: sorted(partition(len(families), exact, scale)) for scale in SCALES}})

    return {
        "start knot holdings": start,
        "family live knot indices": families,
        "initial loose distinctions": [[32 + i] for i in range(len(families))],
        "family pair holder steps": {f"{i}-{j}": d for (i, j), d in distances.items()},
        "places as family masks": places, "laws as place indices": laws,
        "cluster appearance thresholds by family mask": thresholds,
        "global least cost": result["least"], "global least signatures": sorted(result["least signatures"]),
        "locally kept facts and their reading laws": {
            fact: [i for i, local in enumerate(result["local functions"]) if fact in local]
            for fact in sorted(result["facts"])
        },
        "facts lacking a single reader of arity at least three": sorted(
            result["facts"] - result["read by one law of at least three places"]),
        "facts outside local span": sorted(result["outside local span"]),
        "shortest-through-each-place signatures": sorted(result["shortest-through-each-place signatures"]),
        "facts under shortest-through-each-place ties": sorted(result["shortest-through-each-place facts"]),
        "grown rounds": rounds,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot", action="store_true", help="Use the first forty starts of each roster and the witness")
    args = parser.parse_args()
    result = {
        "rosters": {label: recount_roster(STUDY / f"frozen_{label}.jsonl", args.pilot) for label in ROSTERS},
        "five-family start": five_family_witness(),
    }
    print("Start records checked:", sum(row["counts"]["coverage"]["start records"]
                                        for row in result["rosters"].values()))
    print("Five-family witness checked through rounds:", len(result["five-family start"]["grown rounds"]))
    if not args.pilot:
        HERE.joinpath("recount.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
