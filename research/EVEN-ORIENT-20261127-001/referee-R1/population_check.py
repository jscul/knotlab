"""Replay the three grown populations and audit their choice listings.

The archived forbid wrapper supplies only start support labels, relabelling,
and ordinary parity growth. The earlier cross-pair referee supplies the
strict-choice enumerator, direct balanced-order test, and occurrence-pairing
analysis. The start rosters, choice eligibility, and archive comparisons are
rebuilt here.
"""

import argparse
from collections import Counter, defaultdict
from itertools import combinations, permutations, product
import json
from pathlib import Path
from random import Random
import sys
from time import monotonic

import networkx as nx

HERE = Path(__file__).resolve().parent
STUDY = HERE.parent
RESEARCH = STUDY.parent
ENGINE = RESEARCH / "FORBID-EDITS-20261126-001"
PRIOR = RESEARCH / "CELL-SIGN-20261127-001" / "referee-R1"
REBUILT = RESEARCH / "READER-SPLIT-20261127-001" / "referee-R1" / "rebuilt_inputs.jsonl"
sys.path[:0] = [str(ENGINE), str(PRIOR)]
import forbid
from minimal_attachment import analyse_choice, analyse_attachment
from minimal_measure import measure_cycles, occurrences, separated_cycles
from scope_check import can_orient, strict_words


def read_json(name):
    return json.loads(name.read_text())


def plain(value):
    return json.loads(json.dumps(value))


def census():
    """Enumerate connected simple meeting patterns first, then refine them."""
    archive = [
        (n, tuple(map(tuple, meetings)), tuple(loose))
        for n, meetings, loose in read_json(ENGINE / "starts.json")
    ]
    generated = set()
    for graph in nx.graph_atlas_g():
        n = len(graph)
        if not 3 <= n <= 5 or not nx.is_connected(graph):
            continue
        meetings = sorted(tuple(sorted(e)) for e in graph.edges)
        index = {pair: i for i, pair in enumerate(meetings)}
        automorphisms = []
        for order in permutations(range(n)):
            image = [tuple(sorted((order[a], order[b]))) for a, b in meetings]
            if set(image) == index.keys():
                automorphisms.append((tuple(index[pair] for pair in image), order))
        for multiplicities in product((1, 2), repeat=len(meetings)):
            spare = 12 - sum(multiplicities)
            if spare < 0:
                continue
            shared = Counter()
            for (a, b), m in zip(meetings, multiplicities):
                shared[a] += m
                shared[b] += m
            ranges = [range(max(0, 3 - shared[i]), 3) for i in range(n)]
            for loose in product(*ranges):
                if sum(loose) > spare:
                    continue
                key = multiplicities, loose
                if any(
                    (tuple(multiplicities[i] for i in perm),
                     tuple(loose[i] for i in order)) < key
                    for perm, order in automorphisms
                ):
                    continue
                canonical = forbid.canonical(n, dict(zip(meetings, multiplicities)), loose)
                entry = (n, *canonical)
                assert entry not in generated, entry
                generated.add(entry)
    assert len(archive) == len(generated) and set(archive) == generated
    return archive


def sample(n, count, seed):
    """One vote per accepted labelled sample, with replacement."""
    rng = Random(seed)
    pairs = list(combinations(range(n), 2))
    accepted = []
    proposals = 0
    while len(accepted) < count:
        proposals += 1
        meetings = [pair for pair in pairs if rng.random() < 1 / 3]
        multiplicities = [rng.choice((1, 2)) for _ in meetings]
        loose = tuple(rng.choice((0, 1, 2)) for _ in range(n))
        if sum(multiplicities) + sum(loose) > 18:
            continue
        places = list(loose)
        neighbours = [0] * n
        for (a, b), m in zip(meetings, multiplicities):
            places[a] += m
            places[b] += m
            neighbours[a] |= 1 << b
            neighbours[b] |= 1 << a
        if min(places) < 3:
            continue
        reached = 0
        pending = 1
        while pending:
            knot = pending & -pending
            pending ^= knot
            reached |= knot
            pending |= neighbours[knot.bit_length() - 1] & ~reached
        if reached.bit_count() == n:
            accepted.append((n, tuple((*p, m) for p, m in zip(meetings, multiplicities)), loose))
    check_count = min(100, count)
    assert accepted[:check_count] == forbid.sampled(n, check_count, seed)
    return accepted, {
        "starting knots": n,
        "seed": seed,
        "proposals": proposals,
        "accepted samples": count,
        "accepted-prefix rows matched to the archived sampler": check_count,
        "distinct labelled starts": len(set(accepted)),
        "accepted with more than three places at a knot": sum(
            max(len(row) for row in forbid.supports_of(start)) > 3 for start in accepted
        ),
    }


def history(start, rounds, cap):
    stage = forbid.supports_of(start)
    dates = [0] * len(stage)
    births = []
    for round_number in range(1, rounds + 2):
        counts = Counter(value for knot in stage for value in knot)
        if set(counts.values()) == {2}:
            return ("grown closed" if births else "initially closed"), stage, dates, births
        grown, status, records = forbid.grown(stage, "parity", "ordinary")
        if status == "stalled":
            return "stalled", stage, dates, births
        assert status == "funded"
        if round_number > rounds:
            return "growing", stage, dates, births
        if len(grown) > cap:
            return "cut", stage, dates, births
        assert grown[:len(stage)] == stage
        assert sorted(b["knot"] for b in records) == list(range(len(stage), len(grown)))
        for birth in records:
            parents = birth["parents"]
            assert len(parents) == len(set(parents))
            births.append([round_number, birth["knot"], list(parents)])
        dates.extend([round_number] * (len(grown) - len(stage)))
        stage = grown
    raise AssertionError("unreachable growth horizon")


def choices(supports, dates):
    where = defaultdict(list)
    for knot, distinctions in enumerate(supports):
        for distinction in distinctions:
            where[distinction].append(knot)
    assert all(len(knots) == 2 for knots in where.values())
    birth, whole = [], []
    for x, y in combinations(sorted(where), 2):
        a, b = where[x]
        c, d = where[y]
        if len({a, b, c, d}) != 4:
            continue
        whole.append((x, y))
        if dates[b] <= dates[c] or dates[d] <= dates[a]:
            birth.append((x, y))
    return where, birth, whole


def fingerprint(cycles):
    """Class under knot relabelling, order of failing pairs and cycle reversal."""
    knots = sorted({x for cycle in cycles for x in cycle})
    by_type = set()
    for order in permutations(range(len(knots))):
        table = dict(zip(knots, order))
        cycles_by_holdings = []
        for a, c, b, d in cycles:
            holdings = tuple(sorted((table[u], table[v])) for u, v in ((a, b), (c, d)))
            cycles_by_holdings.append(tuple(sorted(holdings)))
        by_type.add(tuple(sorted(cycles_by_holdings)))
    return min(by_type)


def check_word(cycles, pairs, where, dates):
    measured = measure_cycles(cycles)
    visits = occurrences(cycles)
    oriented = can_orient(cycles)
    assert oriented == measured["orientable"]
    assert measured["sign"] == measured["reference_order_count"]
    assert not measured["sign"] or not oriented
    shares = Counter(tuple(where[value]) for pair in pairs for value in pair)
    doubled = sorted(pair for pair, count in shares.items() if count >= 2)
    knots = {knot for cycle in cycles for knot in cycle}
    knots_on_doubled = {knot for pair in doubled for knot in pair}
    held_new = sum(any(dates[knot] for knot in where[value]) for pair in pairs for value in pair)
    first_held_new = sum(all(dates[knot] for knot in where[value]) for pair in pairs for value in pair)
    covered_twice = measured["covered_twice"]
    result = {
        "pairs": len(pairs), "sign": measured["sign"], "orientable": oriented,
        "covered twice": covered_twice, "coverage": max(map(len, visits.values())),
        "knots": len(knots), "Euler count": measured["euler"],
        "separated Euler count": measured["separated_euler"],
        "one cycle at every knot": bool(measured["one_cycle_per_knot"]),
        "two-colourable": measured["two_colourable"],
        "doubled pairs": len(doubled), "knots on a doubled pair": len(knots_on_doubled),
        "every knot on a doubled pair": knots <= knots_on_doubled,
        "start knots": sum(dates[knot] == 0 for knot in knots),
        "newborns": sum(dates[knot] > 0 for knot in knots),
        "birth value": bool(held_new),
    }
    separation = None
    if covered_twice:
        assigned = list((cross_pair, (tuple(paired),)) for cross_pair, paired in visits.items())
        agreement = analyse_attachment(assigned)
        assert agreement == (oriented, measured["separated_euler"],
                             measured["separated_two_colourable"], True, measured["sign"])
        assert measured["sign"] == measured["same_order_parity"]
        result["same-order parity"] = measured["same_order_parity"]
        separation = separated_cycles(cycles)
    return result, measured, doubled, held_new, first_held_new, separation


def check_arm(eligible, supports, where, dates):
    matrix = Counter()
    coverage = Counter()
    separated = Counter()
    attachment_counts = Counter()
    variation_counts = Counter()
    by_word, found = {}, {}
    for cycles, pairs, minimal in strict_words({"supports": supports, "pairs": eligible}, minimal_only=True):
        assert minimal
        word = tuple(pairs)
        assert word not in by_word
        result, measured, doubled, held_new, first_held_new, separation = check_word(cycles, pairs, where, dates)
        label = "odd" if result["sign"] else "even"
        size, oriented, maximum = len(pairs), result["orientable"], result["coverage"]
        category = size, label, oriented
        matrix[category] += 1
        coverage[(*category, maximum)] += 1
        if maximum == 2:
            attached = examples = None
            separated[(*category, measured["euler"], measured["separated_euler"],
                       measured["two_colourable"], measured["separated_two_colourable"])] += 1
        else:
            attached, examples = analyse_choice(cycles, measured["sign"])
            assert oriented == any(result[0] for result in attached)
            changes = tuple(len({row[i] for row in attached}) > 1 for i in range(3))
            for (o, e, colour), count in attached.items():
                attachment_counts[(*category, maximum, o, e, colour)] += count
            variation_counts[(*category, maximum, sum(attached.values()), *changes)] += 1
        by_word[word] = category
        if not oriented and label == "even":
            found[word] = {
                "saved fields": {"failing pairs": pairs, "cycles": cycles, "kind": None, **result},
                "distinctions held by a newborn": held_new,
                "distinctions first held by a newborn": first_held_new,
                "doubled meetings": doubled,
                "coverage by cross pair": [[*pair, len(items)] for pair, items in sorted(occurrences(cycles).items())],
                "separated cycles": separation,
                "two-colourable after separation": measured["separated_two_colourable"],
                "pairings above coverage two": None if attached is None else [
                    [o, e, colour, count, examples[o, e, colour]]
                    for (o, e, colour), count in sorted(attached.items())
                ],
            }
    record = {
        "candidates": len(eligible),
        "words": len(by_word),
        "capped": False,
        "tally": [[*key, value] for key, value in sorted(matrix.items(), key=lambda item: str(item[0]))],
    }
    assert len(by_word) < 200_000
    return record, by_word, found, (matrix, coverage, separated, attachment_counts, variation_counts)


TABLES = (
    ("choices", "pairs, sign, orientable, labelled choices"),
    ("coverage", "pairs, sign, orientable, maximum coverage, labelled choices"),
    ("separation at coverage two",
     "pairs, sign, orientable, Euler count before and after, two-colourable before and after, labelled choices"),
    ("pairings at higher coverage",
     "pairs, sign, balanced orders, maximum coverage, pairing orientable, pairing Euler count, "
     "pairing two-colourable, pairings"),
    ("pairing dependence",
     "pairs, sign, balanced orders, maximum coverage, pairings per choice, whether orientability varies, "
     "whether Euler count varies, whether two-colourability varies, labelled choices"),
)


def rows_of(counter):
    return [[*key, count] for key, count in sorted(counter.items())]


def audit(name, starts, rounds, cap, limit=None):
    candidate_rows = [json.loads(line) for line in (STUDY / f"{name}.jsonl").open()]
    old_found = read_json(STUDY / f"{name}_nonorientable_even.json")
    old_found_by_key = {
        (item["index"], "whole" if item["whole"] else "birth", tuple(sorted(map(tuple, item["failing pairs"])))): item
        for item in old_found
    }
    assert len(starts) == len(candidate_rows)
    assert len(old_found) == len(old_found_by_key)
    precedent = read_json(PRIOR / "grown_scope.json") if name == "census_starts" else None
    precedent_by_index = {} if precedent is None else {row["start"]: row for row in precedent["rows"]}
    if precedent is not None:
        older_inputs = {row["key"]: row for row in map(json.loads, REBUILT.open()) if row["population"] == "birth"}
        older_inputs_total = len(older_inputs)
    rows, found, additions, discrepancies = [], [], [], []
    statuses, stages, large_census_even = Counter(), Counter(), Counter()
    stats_by_n = defaultdict(Counter)
    arm_tables = {arm: [Counter() for _ in TABLES] for arm in ("birth", "whole")}
    coverage_hits = defaultdict(set)
    unique_shapes = {}
    higher_coverage_hits = set()
    prior_even_sizes = Counter()
    for index, (start, archived) in enumerate(zip(starts[:limit], candidate_rows)):
        n = start[0]
        state, supports, dates, births = history(start, rounds, cap)
        status = {
            "outcome": state, "rounds": max(dates), "start knots": n, "index": index,
        }
        statuses[state] += 1
        stats_by_n[n]["starts"] += 1
        stats_by_n[n][state] += 1
        if state != "grown closed":
            if status != archived:
                discrepancies.append({"index": index, "archived": archived, "replay": status})
            continue
        where, birth_candidates, whole_candidates = choices(supports, dates)
        doubled = Counter(map(tuple, where.values()))
        assert all(dates[b] == 0 for (a, b), count in doubled.items() if count >= 2)
        status.update({"knots": len(supports), "distinctions": len(where), "doubled only between start knots": True})
        stages[n, max(dates), len(supports), sum(count >= 2 for count in doubled.values())] += 1
        birth = check_arm(birth_candidates, supports, where, dates)
        whole = birth if birth_candidates == whole_candidates else check_arm(whole_candidates, supports, where, dates)
        assert birth[1].items() <= whole[1].items()
        if len(whole[1]) > len(birth[1]):
            new_only = Counter(whole[1][word] for word in whole[1].keys() - birth[1].keys())
            additions.append({"index": index, "start knots": n, "growth rounds": max(dates),
                              "closure knots": len(supports), "new whole choices": rows_of(new_only)})
        for arm, (record, words, hits, measurements) in (("birth", birth), ("whole", whole)):
            if arm in archived:
                status[arm] = record
            if hits:
                coverage_hits[n, arm, "all"].add(index)
                for hit in hits.values():
                    maximum = hit["saved fields"]["coverage"]
                    coverage_hits[n, arm, "exactly two" if maximum == 2 else "above two"].add(index)
            for total, detail in zip(arm_tables[arm], measurements):
                total.update(detail)
            for word, hit in hits.items():
                hit_record = hit["saved fields"]
                if len(word) == 6:
                    key = fingerprint(hit_record["cycles"])
                    unique_shapes.setdefault(key, hit_record["cycles"])
                    hit_record["kind"] = "UNCLASSIFIED SIX-PAIR HIT"
                if hit_record["coverage"] > 2:
                    higher_coverage_hits.add((index, word))
                row_key = index, arm, word
                record_compared = arm in archived
                expected = old_found_by_key.pop(row_key, None) if record_compared else None
                reproduced = plain({"index": index, "whole": arm == "whole", **hit_record})
                if record_compared and reproduced != expected:
                    discrepancies.append({"index": index, "archived choice": expected, "replay choice": reproduced})
                found.append({
                    "birth or whole": arm, "index": index,
                    **{k: v for k, v in hit.items() if k != "saved fields"},
                    **hit_record,
                })
        if precedent is not None:
            old_row = precedent_by_index.pop(index)
            assert old_row["rounds"] == status["rounds"]
            assert old_row["birth_choices_attain_odd"] == (index in older_inputs)
            if index in older_inputs:
                older = older_inputs.pop(index)
                assert plain(supports) == older["supports"]
                assert plain(birth_candidates) == older["pairs"]
            prior_counts = {
                "minimal, odd, nonorientable": sum(k[1] == "odd" and not k[2] for k in birth[1].values()),
                "minimal, even, orientable": sum(k[1] == "even" and k[2] for k in birth[1].values()),
                "minimal, even, nonorientable": sum(k[1] == "even" and not k[2] for k in birth[1].values()),
                "minimal, odd, orientable": sum(k[1] == "odd" and k[2] for k in birth[1].values()),
            }
            assert all(old_row["counts"].get(key, 0) == count for key, count in prior_counts.items())
            prior_even_sizes.update(pairs for pairs, label, _ in birth[1].values() if label == "even")
        if name == "census_starts" and len(supports) >= 7:
            large_census_even.update((len(supports), pairs) for pairs, label, _ in whole[1].values() if label == "even")
        if status != archived:
            discrepancies.append({"index": index, "archived": archived, "replay": status})
        rows.append({
            "index": index,
            "birth choices": birth[0]["words"],
            "whole choices": whole[0]["words"],
            "closure knots": len(supports),
            "start knots": n,
        })
        if hits or birth[2]:
            rows[-1].update({"start": start, "births": births, "supports": supports})
    if limit is None:
        assert not old_found_by_key, old_found_by_key.keys()
        if precedent is not None:
            assert not precedent_by_index and not older_inputs
            assert dict(statuses) == precedent["outcomes"]
            assert {str(k): v for k, v in prior_even_sizes.items()} == precedent["minimal_even_by_size"]
    rates = []
    for n, counts in sorted(stats_by_n.items()):
        for arm in arm_tables:
            for coverage in ("all", "exactly two", "above two"):
                hits = len(coverage_hits[n, arm, coverage])
                rates.append([n, arm, coverage, hits, counts["starts"], counts["grown closed"]])
    return {
        "scope": {"rounds": rounds, "knot cap": cap, "starts compared with archive": sum(statuses.values()),
                  "grown closures": len(rows), "choice modes": list(arm_tables),
                  "whole mode is a referee extension": name == "second_sample"},
        "outcomes": statuses,
        "outcomes by start size": dict(stats_by_n),
        "hit rates by start size": {
            "fields": "start knots, choice mode, coverage, hit closures, starts or accepted samples, grown closures",
            "rows": rates,
        },
        "closed by start size, round, closure knots, doubled meetings": rows_of(stages),
        "choice totals": {
            arm: {label: {"fields": fields, "rows": rows_of(counter)}
                  for (label, fields), counter in zip(TABLES, tables)}
            for arm, tables in arm_tables.items()
        },
        "whole mode additions": additions,
        "non-orientable even choices": found,
        "non-orientable even hit closures": [r for r in rows if "births" in r],
        "unique labelled non-orientable even choices above coverage two, across modes": len(higher_coverage_hits),
        "non-orientable even six-pair shapes": list(unique_shapes.values()),
        "large census closure whole even choices by closure knots and pairs": rows_of(large_census_even),
        "prior census referee agreed by closure, sign and orientation": precedent is not None and limit is None,
        "census closure holdings and eligible birth list agreed with earlier referee": (
            older_inputs_total - len(older_inputs) if precedent is not None else None
        ),
        "saved rows and listings discrepancies": discrepancies,
    }


def write_overview():
    populations = {}
    for name in ("census_starts", "extension", "second_sample"):
        replay = read_json(HERE / f"population_counts_{name}.json")
        assert not replay["saved rows and listings discrepancies"]
        saved_rows = [json.loads(line) for line in (STUDY / f"{name}.jsonl").open()]
        grown = [row for row in saved_rows if row["outcome"] == "grown closed"]
        extra = {
            row["index"]: sum(choice[-1] for choice in row["new whole choices"])
            for row in replay["whole mode additions"]
        }
        overview = {}
        for mode in ("birth", "whole"):
            coverage_counts = replay["choice totals"][mode]["coverage"]["rows"]
            counts = Counter()
            for _, sign, orientable, coverage, number in coverage_counts:
                if sign != "even":
                    continue
                band = "twice" if coverage == 2 else "above twice"
                counts[band, "all"] += number
                if not orientable:
                    counts[band, "non-orientable"] += number
            sizes = {
                row["index"]: (row[mode]["words"] if mode in row
                               else row["birth"]["words"] + extra.get(row["index"], 0))
                for row in grown
            }
            largest = max(sizes.values())
            overview[mode] = {
                "largest listing": largest,
                "sample or census indices with largest listing": [index for index, size in sizes.items() if size == largest],
                "even choices by coverage": {
                    band: {orientability: counts[band, orientability]
                           for orientability in ("all", "non-orientable")}
                    for band in ("twice", "above twice")
                },
            }
        populations[name] = overview
    result = {
        "scope": "Lists at positive-round closures. The second sample's whole mode is the additional referee listing.",
        "weighting": "One per accepted labelled sample or census start. One per labelled choice at its closure, within each mode.",
        "reported cap per listing": 200_000,
        "populations": populations,
    }
    (HERE / "population_counts_overview.json").write_text(json.dumps(result, indent=2) + "\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--population", choices=("census_starts", "extension", "second_sample"))
    parser.add_argument("--probe", type=int, metavar="STARTS_PER_POPULATION")
    parser.add_argument("--overview-only", action="store_true", help="summarize the three completed replays")
    args = parser.parse_args()
    assert {"evenorient", "cellsign"}.isdisjoint(sys.modules)
    if args.overview_only:
        write_overview()
        return
    names = [args.population] if args.population else ["extension", "second_sample", "census_starts"]
    for name in names:
        start_time = monotonic()
        if name == "census_starts":
            starting_holds, sampler = census(), None
            rounds, cap = 4, 40
        else:
            base, draws = (20261126, 1000) if name == "extension" else (20261200, 10_000)
            starting_holds, sampler = [], []
            for n in (6, 7, 8):
                roster, seed_record = sample(n, draws, base + n)
                starting_holds.extend(roster)
                sampler.append(seed_record)
            rounds, cap = 10, 3000
        outcome = audit(name, starting_holds, rounds, cap, args.probe)
        outcome["roster"] = (
            "Independent exhaustive enumeration of connected starts of three to five knots, "
            "with one or two shared distinctions at each meeting, zero to two loose at each knot, "
            "at least three places at each knot, at most twelve distinctions. One vote per class "
            "under relabelling, with indices inherited from the matching archived roster."
            if sampler is None else
            "Independent seeded proposals, with each accepted prefix compared with the archived sampler. Each "
            "possible pair meets with probability 1/3 and its multiplicity is uniform on {1,2} "
            "when present. Loose counts are uniform on {0,1,2}. Accept when connected with at "
            "least three places per knot and at most eighteen distinctions. One vote per accepted "
            "labelled sample with replacement, pooling equal numbers of samples by start size."
        )
        outcome["sampler"] = sampler
        outcome["choice weighting"] = "One per labelled choice at each positive-round closure in each mode."
        print(name, outcome["outcomes"], len(outcome["non-orientable even choices"]),
              "hit choices", len(outcome["saved rows and listings discrepancies"]), "archive disagreements",
              f"{monotonic() - start_time:.1f} seconds", flush=True)
        if args.probe is None:
            (HERE / f"population_counts_{name}.json").write_text(json.dumps(outcome, indent=2) + "\n")
    if args.probe is None and args.population is None:
        write_overview()


if __name__ == "__main__":
    main()
