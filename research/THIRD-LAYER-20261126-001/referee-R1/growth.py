"""Rebuild ordinary parity growth and the frozen roster without importing study code."""

import argparse
import itertools
import json
import random
import resource
import time
from collections import Counter, defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
STUDY = HERE.parent
RESEARCH = STUDY.parent
SETS = ("census", "heldout", "sampled", "built", "merge")
CENSUS = RESEARCH / "FORBID-EDITS-20261126-001" / "starts.json"


def meeting_pattern(supports):
    """Return distinction holders, their meetings, and ordered loose distinctions."""
    holders = defaultdict(list)
    for knot, support in enumerate(supports):
        for distinction in support:
            holders[distinction].append(knot)
    neighbors = [set() for _ in supports]
    loose = {}
    for distinction, owners in holders.items():
        if len(owners) == 1:
            loose.setdefault(owners[0], []).append(distinction)
        elif len(owners) == 2 and owners[0] != owners[1]:
            a, b = owners
            neighbors[a].add(b)
            neighbors[b].add(a)
        else:
            raise ValueError(f"invalid holders for distinction {distinction}: {owners}")
    return holders, neighbors, loose


def candidate_pairs(neighbors, live):
    """Return unordered pairs of live knots with a third knot that meets both."""
    live = set(live)
    return {
        pair
        for contacts in neighbors
        for pair in itertools.combinations(sorted(contacts & live), 2)
    }


def components(adjacency):
    seen = set()
    for first in sorted(adjacency):
        if first in seen:
            continue
        seen.add(first)
        members = []
        pending = [first]
        while pending:
            knot = pending.pop()
            members.append(knot)
            new = adjacency[knot] - seen
            pending.extend(new)
            seen.update(new)
        yield tuple(sorted(members))


def family_components(neighbors, live, pairs=None):
    adjacency = {knot: set() for knot in live}
    if pairs is None:
        pairs = candidate_pairs(neighbors, live)
    for a, b in pairs:
        adjacency[a].add(b)
        adjacency[b].add(a)
    return tuple(components(adjacency))


def families(supports):
    """Return the live-knot families and each family's loose distinctions."""
    _, neighbors, loose = meeting_pattern(supports)
    groups = family_components(neighbors, loose)
    return groups, tuple(tuple(d for knot in group for d in loose[knot]) for group in groups)


def _members(mask):
    while mask:
        bit = mask & -mask
        yield bit.bit_length() - 1
        mask ^= bit


def _groups(neighbors, live, pairs=None):
    """Take maximal valid groups and candidate pairs that no such group covers."""
    if pairs is None:
        pairs = candidate_pairs(neighbors, live)
    if not pairs:
        return ()
    compatible = {knot: 0 for knot in live}
    for a, b in pairs:
        compatible[a] |= 1 << b
        compatible[b] |= 1 << a

    def maximal(group, pending, used):
        if not pending and not used:
            if len(group) >= 3 and not set.intersection(*(neighbors[k] for k in group)):
                yield tuple(sorted(group))
            return
        if pending:
            pivot = max(_members(pending | used), key=lambda k: (pending & compatible[k]).bit_count())
            for knot in _members(pending & ~compatible[pivot]):
                peers = compatible[knot]
                yield from maximal(group + (knot,), pending & peers, used & peers)
                pending ^= 1 << knot
                used |= 1 << knot

    large = tuple(sorted(maximal((), sum(1 << k for k, mask in compatible.items() if mask), 0)))
    # A valid group cannot gain a knot meeting all its members when it is enlarged.
    covered = {pair for group in large for pair in itertools.combinations(group, 2)}
    return large + tuple(sorted(pairs - covered))


def proposals(supports):
    """Return current candidate pairs, ordinary joins, and each live knot's shortage."""
    _, neighbors, loose = meeting_pattern(supports)
    pairs = candidate_pairs(neighbors, loose)
    groups = _groups(neighbors, loose, pairs)
    demand = Counter(knot for group in groups for knot in group)
    shortages = {knot: demand[knot] - len(seq) for knot, seq in loose.items() if demand[knot] > len(seq)}
    return pairs, groups, shortages


def _reduce(mask, basis):
    while mask:
        row = basis.get(mask.bit_length())
        if row is None:
            break
        mask ^= row
    return mask


def _parity_basis(supports):
    basis = {}
    for support in supports:
        row = _reduce(sum(1 << distinction for distinction in support), basis)
        if row:
            basis[row.bit_length()] = row
    return basis


def grow(supports):
    """Return the next supports, funding status, and paid birth records."""
    supports = tuple(tuple(row) for row in supports)
    holders, neighbors, loose = meeting_pattern(supports)
    if not loose:
        return supports, "closed", ()
    groups = _groups(neighbors, loose)
    demand = Counter(knot for group in groups for knot in group)
    if any(demand[knot] > len(seq) for knot, seq in loose.items()):
        return supports, "stalled", ()

    available = {knot: iter(seq) for knot, seq in loose.items()}
    plan = [(group, tuple(sorted(next(available[knot]) for knot in group))) for group in groups]
    plan.extend(((knot,), (distinction,)) for knot in sorted(loose) for distinction in available[knot])
    newborns = range(len(supports), len(supports) + len(plan))
    paid_supports = supports + tuple(inputs for _, inputs in plan)
    _, prospective, _ = meeting_pattern(paid_supports)
    next_demand = Counter(knot for group in _groups(prospective, newborns) for knot in group)
    basis = _parity_basis(supports)

    first_fresh = max(holders) + 1
    births = []
    next_supports = list(supports)
    for knot, (parents, inputs) in zip(newborns, plan, strict=True):
        demand = next_demand[knot]
        implied = _reduce(sum(1 << distinction for distinction in inputs), basis) == 0
        count = demand if implied else max(demand, 3 - len(inputs), 1)
        fresh = tuple(range(first_fresh, first_fresh + count))
        first_fresh += count
        births.append({"knot": knot, "parents": parents, "inputs": inputs, "fresh": fresh,
                       "p": len(inputs), "D": demand, "f": count, "old_inputs_already_imply_law": implied})
        next_supports.append(inputs + fresh)
    return tuple(next_supports), "funded", tuple(births)


def stages(supports, rounds=4, cap=300):
    """Yield round number, readable supports or None, study status, and births."""
    births = ()
    for round_number in range(rounds + 1):
        if round_number:
            supports, status, births = grow(supports)
            if status != "funded":
                yield round_number, None, status, births
                return
        if len({d for row in supports for d in row}) > cap:
            yield round_number, None, "not read", births
            return
        yield round_number, supports, "stage", births


def _from_description(n, multipliers, loose):
    rows = [[] for _ in range(n)]
    names = itertools.count()
    for a, b, count in multipliers:
        for _ in range(count):
            distinction = next(names)
            rows[a].append(distinction)
            rows[b].append(distinction)
    for row, count in zip(rows, loose, strict=True):
        row.extend(next(names) for _ in range(count))
    return tuple(tuple(row) for row in rows)


def _draw_starts(n, count, seed, maximum):
    """The archived labelled weighting, drawn with replacement after rejection."""
    rng = random.Random(seed)
    pairs = tuple(itertools.combinations(range(n), 2))
    accepted = 0
    while accepted < count:
        chosen = [pair for pair in pairs if rng.random() < 1 / 3]
        multipliers = [(a, b, rng.choice((1, 2))) for a, b in chosen]
        loose = tuple(rng.choice((0, 1, 2)) for _ in range(n))
        if sum(loose) + sum(count for _, _, count in multipliers) > maximum:
            continue
        forms = _from_description(n, multipliers, loose)
        if min(map(len, forms)) < 3:
            continue
        _, neighbors, _ = meeting_pattern(forms)
        if len(next(components(dict(enumerate(neighbors))))) == n:
            yield forms
            accepted += 1


def ring_start(number, size, attachment, link):
    """The built starts with exact distinction numbering from their specification."""
    rows = [[] for _ in range(number * size)]
    names = itertools.count()

    def share(*knots):
        distinction = next(names)
        for knot in knots:
            rows[knot].append(distinction)
        return distinction

    rings = tuple(tuple(range(i * size, (i + 1) * size)) for i in range(number))
    for ring in rings:
        for a, b in zip(ring, ring[1:] + ring[:1], strict=True):
            share(a, b)
    loose = tuple(tuple(share(knot) for knot in ring for _ in range(2)) for ring in rings)
    used_attachments = [0] * number
    for a, b in itertools.combinations(range(number), 2):
        left, right = len(rows), len(rows) + 1
        rows.extend(([], []))
        for ring, connector in ((a, left), (b, right)):
            position = used_attachments[ring]
            used_attachments[ring] += 1
            ends = (2 * position, 2 * position) if attachment == "paired" else (position, position + 2)
            for end in ends:
                share(rings[ring][end % size], connector)
        share(left, right)
        if link == "double":
            share(left, right)
        else:
            extension = tuple(range(len(rows), len(rows) + 3))
            rows.extend([] for _ in extension)
            sequence = (left,) + extension + (right,)
            for source, target in itertools.pairwise(sequence):
                share(source, target)
                share(source, target)
    return tuple(tuple(row) for row in rows), rings, loose


def fourteen_start():
    """Return the built three-ring, fourteen-knot start and ring shared distinctions."""
    rows = [[] for _ in range(14)]
    names = itertools.count()

    def share(*knots):
        distinction = next(names)
        for knot in knots:
            rows[knot].append(distinction)
        return distinction

    rings = []
    for first in (0, 4, 8):
        a, b, c, d = range(first, first + 4)
        rings.append(tuple(share(i, j) for i, j in ((a, b), (b, c), (c, d), (d, a))))
        for knot in (b, d):
            share(knot)
            share(knot)
        share(a, 12)
        share(c, 13)
    share(12, 13)
    return tuple(tuple(row) for row in rows), tuple(rings)


def load_starts(which=None):
    """Yield named starts in frozen order, including the original full census sample."""
    if which is None:
        for case_set in SETS:
            yield from load_starts(case_set)
    elif which == "census":
        population = json.loads(CENSUS.read_text())
        for index in random.Random(20261215).sample(range(len(population)), 1000):
            yield f"census {index}", _from_description(*population[index])
    elif which == "heldout":
        for n in (6, 7, 8):
            for index, supports in enumerate(_draw_starts(n, 300, 20261206 + n, 18)):
                yield f"held out {n}-{index}", supports
    elif which == "sampled":
        for n in (9, 10, 11, 12):
            for index, supports in enumerate(_draw_starts(n, 100, 20261212 + n, 30)):
                yield f"sampled {n}-{index}", supports
    elif which in {"built", "merge"}:
        numbers = (3, 4) if which == "built" else (3,)
        for number, size, attachment, link in itertools.product(numbers, (4, 5, 6, 7),
                                                                  ("split", "paired"), ("double", "detour")):
            name = f"{number} rings of {size}, {attachment}, {link}"
            supports, rings, _ = ring_start(number, size, attachment, link)
            if which == "merge":
                name += " + a dead knot meeting rings 1 and 2"
                x = 1 + max(d for row in supports for d in row)
                rows = list(supports)
                rows[rings[0][0]] += (x, x + 1)
                rows[rings[1][0]] += (x + 2,)
                supports = tuple(rows) + ((x, x + 1, x + 2),)
            yield name, supports
        if which == "built":
            yield "the 14-knot start", fourteen_start()[0]
    else:
        raise ValueError(f"unknown case set {which}")


def _read_jsonl(path):
    with path.open() as rows:
        return [json.loads(row) for row in rows]


def _prior_birth_records():
    prior = RESEARCH / "BUILT-BINDING-20261126-001"
    data = {}
    for which in ("census", "heldout", "built"):
        for row in _read_jsonl(prior / f"closing_{which}_parity.jsonl"):
            if "start" in row:
                data[row["start"]] = row["births"]
    data["the 14-knot start"] = data.pop("built base")
    return data


def _prior_built_counts():
    prior = RESEARCH / "BUILT-BINDING-20261126-001" / "frozen_built.jsonl"
    result = {}
    for row in _read_jsonl(prior):
        if "new carriers" in row:
            record = row["new carriers"]
            result[record["family"]] = [record["distinctions"]] + [r["distinctions"] for r in record["rounds"]]
    return result


def _family_rule(supports, family_supports):
    original = _parity_basis(supports)
    carriers = [sum(1 << d for d in names) for names in family_supports]
    total_is_implied = not _reduce(sum(carriers), original)
    basis = original.copy()
    for mask in carriers:
        reduced = _reduce(mask, basis)
        if reduced:
            basis[reduced.bit_length()] = reduced
    image_rank = len(basis) - len(original)
    return 1 << image_rank, total_is_implied and image_rank == max(len(carriers) - 1, 0)


def _transition_record(supports, births, round_number):
    _, neighbors, loose = meeting_pattern(supports)
    component_loose = {}
    for component in components(dict(enumerate(neighbors))):
        distinctions = {d for knot in component for d in loose.get(knot, ())}
        component_loose.update((knot, distinctions) for knot in component)
    return [{"round": round_number, "parents": list(birth["parents"]), "p": birth["p"], "f": birth["f"],
             "implied": birth["old_inputs_already_imply_law"],
             "takes all": set(birth["inputs"]) == component_loose[birth["parents"][0]]} for birth in births]


def _audit_start(name, source, counts, by_round, issues):
    source_groups, family_supports = families(source)
    lineages = {knot: frozenset((i,)) for i, group in enumerate(source_groups) for knot in group}
    counts[f"starts with {len(source_groups)} start families"] += 1
    tuples, rule_ok = _family_rule(source, family_supports)
    rounds = []
    prior_births = []
    multiple_family_rounds = 0
    mixed_births = 0
    supports = source
    end = "read to round 4"

    for round_number in range(5):
        stage = by_round[round_number]
        stage["stages read"] += 1
        rounds.append((round_number, None))
        _, neighbors, loose = meeting_pattern(supports)
        pairs = candidate_pairs(neighbors, loose)
        family_ids = set().union(*(lineages[knot] for knot in loose))
        stage["active lineages across stages"] += len(family_ids)
        if len(family_ids) >= 2:
            stage["stages with at least two active lineages"] += 1
        if round_number == 4:
            break

        stage["attempted next rounds"] += 1
        cross_pairs = sum(len(lineages[a] | lineages[b]) > 1 for a, b in itertools.combinations(loose, 2))
        stage["co-live pairs from different start families"] += cross_pairs
        stage["candidate pairs"] += len(pairs)
        mixed_pairs = [(a, b) for a, b in sorted(pairs) if len(lineages[a] | lineages[b]) > 1]
        stage["candidate pairs mixing start families"] += len(mixed_pairs)
        if mixed_pairs:
            issues.append((name, round_number, "candidate pairs mixing start families", mixed_pairs))
        groups = _groups(neighbors, loose, pairs)
        stage["proposed joins"] += len(groups)
        mixed_groups = [group for group in groups if len(set().union(*(lineages[p] for p in group))) > 1]
        stage["proposed joins mixing start families"] += len(mixed_groups)
        if mixed_groups:
            issues.append((name, round_number, "proposed joins mixing start families", mixed_groups))

        new, status, births = grow(supports)
        stage[f"next round {status}"] += 1
        if status != "funded":
            end = status
            rounds.append((round_number + 1, status))
            if round_number < 3:
                prior_births.append({"round": round_number + 1, "end": status})
            break

        if len(family_ids) >= 2:
            multiple_family_rounds += 1
            stage["births when at least two start families are active"] += len(births)
        old_loose = {d for seq in loose.values() for d in seq}
        if Counter(d for birth in births for d in birth["inputs"]) != Counter(old_loose):
            issues.append((name, round_number, "birth plan did not spend every loose distinction exactly once"))
        stage["loose distinctions spent"] += len(old_loose)
        stage["funded births"] += len(births)
        if round_number < 3:
            prior_births.extend(_transition_record(supports, births, round_number + 1))
        for birth in births:
            parents = birth["parents"]
            lineage = frozenset().union(*(lineages[p] for p in parents))
            lineages[birth["knot"]] = lineage
            stage[f"births with {len(parents)} parents"] += 1
            stage["funded births with no fresh distinction"] += birth["f"] == 0
            if len(lineage) != 1:
                issues.append((name, round_number + 1, "funded birth ancestry", birth["knot"], sorted(lineage)))
            stage["funded births mixing start families"] += len(lineage) > 1
            mixed_births += len(lineage) > 1
        if len(family_ids) >= 2:
            stage["joins when at least two start families are active"] += sum(b["p"] >= 2 for b in births)

        new_holders, new_neighbors, new_loose = meeting_pattern(new)
        dynamic = family_components(new_neighbors, new_loose)
        stage["next live families (sum over funded rounds)"] += len(dynamic)
        by_lineage = Counter(i for component in dynamic for i in set().union(*(lineages[k] for k in component)))
        for i, amount in by_lineage.items():
            if amount > 1:
                issues.append((name, round_number + 1, "lineage split", i, amount))
        lost = family_ids - set(by_lineage)
        for i in lost:
            closing = [b for b in births if i in lineages[b["knot"]]]
            if len(closing) != 1 or closing[0]["f"] != 0:
                issues.append((name, round_number + 1, "lost lineage without a sole closing birth", i))
        stage["surviving lineage transitions"] += len(by_lineage)
        stage["split lineage transitions"] += sum(n > 1 for n in by_lineage.values())
        stage["ended lineage transitions"] += len(lost)
        stage["funded rounds with at least one birth of at least two parents"] += any(b["p"] >= 2 for b in births)
        if len(new_holders) > 300:
            stage["next funded stage exceeds 300 distinctions"] += 1
            end = "not read"
            rounds.append((round_number + 1, end))
            break
        supports = new

    counts[f"end: {end}"] += 1
    counts["rounds read"] += sum(stop is None for _, stop in rounds)
    counts["starts with rounds 3 and 4"] += rounds[-1] == (4, None)
    counts["starts with funded rounds with at least two active lineages"] += bool(multiple_family_rounds)
    counts["funded rounds with at least two active lineages"] += multiple_family_rounds
    return len(source_groups), tuples, rule_ok, mixed_births, rounds, prior_births


def run(pilot=False):
    began = time.perf_counter()
    prior = _prior_birth_records()
    prior_built = _prior_built_counts()
    baseline = {}
    result = {}
    issues = []
    pilots = {
        "census": {0, 1, 2, 997, 998, 999},
        "heldout": {0, 1, 2, 300, 301, 302, 600, 601, 602},
        "sampled": {0, 1, 100, 101, 200, 201, 300, 301},
        "built": {0, 1, 8, 9, 24, 25, 26, 27, 32},
        "merge": {0, 1, 4, 8, 9, 15},
    }

    for which in SETS:
        rows = _read_jsonl(STUDY / f"frozen_{which}.jsonl")
        counts, by_round = Counter(), [Counter() for _ in range(5)]
        for index, ((name, source), record) in enumerate(zip(load_starts(which), rows, strict=True)):
            if which == "built":
                baseline[name] = len(families(source)[0])
            if pilot and index not in pilots[which]:
                continue
            counts["starts"] += 1
            family_count, tuples, rule_ok, mixed_births, rounds, births = _audit_start(name, source, counts, by_round, issues)
            archived_rounds = [(r["round"], r.get("end")) for r in record["rounds"]]
            comparisons = {"start": name, "knots": len(source), "families": family_count,
                           "rounds": rounds, "T1 births across families": mixed_births}
            if family_count:
                comparisons["T2 tuples"] = tuples
                comparisons["T2 one rule, every proper subfamily free"] = rule_ok
                counts["starts testing the family parity rule"] += 1
                counts["starts with exactly the family parity rule"] += rule_ok
            for field, value in comparisons.items():
                expected = archived_rounds if field == "rounds" else record.get(field)
                if value != expected:
                    issues.append((name, "frozen record differs", field, expected, value))
            if which == "merge":
                original = name.removesuffix(" + a dead knot meeting rings 1 and 2")
                if family_count != baseline[original] - 1:
                    issues.append((name, "merge did not remove exactly one family", baseline[original], family_count))
                else:
                    counts["merge controls removing exactly one start family"] += 1
            if name in prior:
                if births != prior[name]:
                    mismatch = next((i for i, (old, new) in enumerate(zip(prior[name], births)) if old != new), None)
                    issues.append((name, "prior birth rows differ", mismatch, len(prior[name]), len(births)))
                else:
                    counts["starts agreeing with prior raw birth records"] += 1
                    counts["prior raw births matched"] += sum("parents" in b for b in births)
                    counts["prior raw stop rows matched"] += sum("end" in b for b in births)
            if name in prior_built:
                features = [len({d for row in support for d in row}) for _, support, _, _ in stages(source, 3, float("inf"))]
                if features != prior_built[name]:
                    issues.append((name, "prior distinction counts differ", prior_built[name], features))
                else:
                    counts["starts agreeing with prior raw distinction counts"] += 1
                    counts["prior raw distinction counts matched"] += len(features)

        result[which] = {"counts": dict(sorted(counts.items())),
                         "by input round": {str(t): dict(sorted(c.items())) for t, c in enumerate(by_round)}}
    totals = Counter()
    opportunities = [Counter() for _ in range(5)]
    for record in result.values():
        totals.update(record["counts"])
        for t, stage in record["by input round"].items():
            opportunities[int(t)].update(stage)
    overall = Counter()
    for stage in opportunities:
        overall.update(stage)
    return {
        "scope": "Frozen roster, ordinary parity growth. Rounds zero through four subject to the original cap.",
        "input provenance": {
            "census": "The frozen seeded sample of 1,000 from the archived 7,075 canonical starts.",
            "heldout": "The archived labelled rejection weighting independently regenerated at six to eight knots.",
            "sampled": "The same weighting at nine to twelve knots with the archived seeds and distinction cap.",
            "built and merge": "Independently reconstructed, retaining the declared distinction numbering.",
        },
        "reference scope": "Raw parity closing records to round three for matching census, held-out and fourteen-knot starts. Raw distinction counts through round three from every built ring start.",
        "counting conventions": [
            "A co-live pair from different start families supplies an opportunity before requiring a common meeting witness.",
            "A birth is counted on its input round. Births and lineage transitions at the first funded cap-crossing transition are included, as in T1. The resulting stage is outside the frozen fact readings.",
            "A lineage split requires descendants of one start family in more than one live family on the same next stage.",
            "Round four records a read stage only. Its successor was outside the frozen roster.",
        ],
        "pilot": pilot,
        "totals": dict(sorted(totals.items())),
        "opportunities across input rounds": dict(sorted(overall.items())),
        "opportunities by input round": {str(t): dict(sorted(c.items())) for t, c in enumerate(opportunities)},
        "sets": result,
        "mismatches or anomalies": issues,
        "wall seconds": round(time.perf_counter() - began, 3),
        "peak memory KiB": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot", action="store_true", help="replay a fixed prefix of each size and larger built controls")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = run(args.pilot)
    if args.output:
        args.output.write_text(json.dumps(result, indent=2) + "\n")
    else:
        print(json.dumps(result, indent=2))
    raise SystemExit(bool(result["mismatches or anomalies"]))
