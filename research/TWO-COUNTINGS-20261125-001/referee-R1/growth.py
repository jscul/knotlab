"""Rebuild the frozen rounds and check the recorded growth comparisons."""

import argparse
import json
import math
import resource
from collections import Counter, defaultdict
from dataclasses import dataclass
from fractions import Fraction
from functools import lru_cache
from itertools import combinations, product
from pathlib import Path
from time import perf_counter

import networkx as nx
import numpy as np
from pysat.solvers import Solver


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
TICKET = "TWO-COUNTINGS-20261125-001A"
INPUT = ROOT / "research" / TICKET
RECORD = ROOT / "artifacts" / TICKET / f"{TICKET}-E001_two_countings"
LAWS = {
    "ORDINARY": ("ORD", "STALL", None),
    "Q-OLDEST": ("ORD", "STALL", "Q-OLDEST"),
    "Q-NEWEST": ("ORD", "STALL", "Q-NEWEST"),
    "RING-LAW": ("CAP-3", "WAIT", None),
    "COPY-LAW(CANCEL-RETIRE)": ("FLOOR1", "RETIRE", None),
    "COPY-LAW(CANCEL-RETIRE)+MET(OLDEST)": ("FLOOR1", "RETIRE", "MET-OLDEST"),
}


@dataclass(frozen=True)
class Rule:
    law: str
    places: tuple


@dataclass(frozen=True)
class Birth:
    parents: tuple
    old: tuple
    fresh: tuple


@dataclass(frozen=True)
class Round:
    births: tuple
    choices: tuple
    status: str


def read(path):
    return json.loads(path.read_text())


def distinct(rules):
    return sorted({place for rule in rules for place in rule.places})


def rules_from_data(data):
    return tuple(Rule(law, tuple(places)) for law, places in data)


def number(rules, names=None, reverse_rules=False):
    if names is None:
        names = distinct(rules)
    renaming = {place: index for index, place in enumerate(names)}
    return tuple(
        Rule(rule.law, tuple(renaming[place] for place in rule.places))
        for rule in (reversed(rules) if reverse_rules else rules)
    )


def holders_and_meetings(places):
    holders = defaultdict(set)
    for index, row in enumerate(places):
        for place in row:
            holders[place].add(index)
    meets = [set() for _ in places]
    for owners in holders.values():
        for owner in owners:
            meets[owner].update(owners - {owner})
    return holders, meets


def groups(members, meets):
    met_sets = {frozenset(row & members) for row in meets if len(row & members) >= 2}
    pairs = {pair for met in met_sets for pair in combinations(sorted(met), 2)}
    if not pairs:
        return []
    graph = nx.Graph(pairs)
    large = sorted(
        tuple(sorted(clique))
        for clique in nx.find_cliques(graph)
        if len(clique) >= 3 and not any(set(clique) <= met for met in met_sets)
    )
    covered = {pair for row in large for pair in combinations(row, 2)}
    return large + sorted(pairs - covered)


def mask(places):
    return sum(1 << place for place in places)


def parity_basis(rules):
    basis = {}
    for rule in rules:
        assert rule.law == "even"
        reduced = reduce_parity(mask(rule.places), basis)
        if reduced:
            basis[reduced.bit_length()] = reduced
    return basis


def reduce_parity(row, basis):
    while row:
        pivot = row.bit_length()
        if pivot not in basis:
            break
        row ^= basis[pivot]
    return row


def make_round(rules, barred, law, newborn, selections=None):
    """Apply the shared definitions' groups and ration with the frozen taking rules."""
    ration, treatment, taking = LAWS[law]
    before = [rule.places for rule in rules]
    holders, meets = holders_and_meetings(before)
    loose = defaultdict(list)
    for place, owners in sorted(holders.items()):
        if len(owners) == 1 and place not in barred:
            loose[next(iter(owners))].append(place)
    members = set(loose)
    if not members:
        return Round((), (), "stopped"), barred
    proposed = groups(members, meets)
    owing = Counter(parent for group in proposed for parent in group)
    short = {parent for parent in members if len(loose[parent]) < owing[parent]}
    if short and treatment == "STALL":
        return Round((), (), "stalled"), barred
    kept = [group for group in proposed if not short.intersection(group)]
    paying = Counter(parent for group in kept for parent in group)
    parents = kept + [
        (parent,)
        for parent in sorted(members - short)
        for _ in range(len(loose[parent]) - paying[parent])
    ]
    if treatment == "RETIRE":
        barred = barred | {place for parent in short for place in loose[parent]}
    if not parents:
        return Round((), (), "jammed"), barred

    queued = {parent: iter(places) for parent, places in loose.items()}
    eligible = {place for place, owners in holders.items() if len(owners) >= 2}
    taking_options = []
    received = []
    for index, row in enumerate(parents):
        paid = tuple(next(queued[parent]) for parent in row)
        additional = set()
        if taking in {"Q-OLDEST", "Q-NEWEST"} and len(row) == 1:
            additional = eligible.intersection(before[row[0]])
        elif taking == "MET-OLDEST":
            common = set.intersection(*(meets[parent] for parent in row))
            present = {place for parent in row for place in before[parent]}
            additional = eligible.intersection(
                place for common_knot in common for place in before[common_knot]
            ) - present
        options = tuple(sorted(additional - set(paid)))
        taking_options.append(options)
        if options:
            selected = options[-1 if taking == "Q-NEWEST" else 0]
            if selections is not None:
                selected = selections[index]
                assert selected in options
            paid += (selected,)
        received.append(paid)

    after = before + received
    demand_holders, demand_meets = holders_and_meetings(after)
    demand_members = {
        next(iter(owners)) for place, owners in demand_holders.items()
        if len(owners) == 1 and place not in barred
    } | set(range(len(before), len(after)))
    demand = Counter(i for group in groups(demand_members, demand_meets) for i in group)
    basis = parity_basis(rules) if newborn == "even" else None
    next_name = max(holders) + 1
    births = []
    for index, (row, old) in enumerate(zip(parents, received), start=len(before)):
        floor = max(3 - len(old), 1)
        allotment = floor if ration == "FLOOR1" else max(demand[index], floor)
        if ration == "CAP-3":
            allotment = min(3, allotment)
        if basis is not None and not reduce_parity(mask(old), basis):
            allotment = 0
        fresh = tuple(range(next_name, next_name + allotment))
        births.append(Birth(row, old, fresh))
        next_name += allotment
    return Round(tuple(births), tuple(taking_options), "births"), barred


def grow(start, law, newborn, limit=3):
    stages = [start]
    rounds = []
    barred = set()
    for _ in range(limit):
        made, barred = make_round(stages[-1], barred, law, newborn)
        rounds.append(made)
        stages.append(stages[-1] + tuple(Rule(newborn, birth.old + birth.fresh) for birth in made.births))
    return stages, rounds


@lru_cache(maxsize=48)
def initial_states(rules):
    width = len(distinct(rules))
    packed = [(rule.law, mask(rule.places)) for rule in rules]
    segments = []
    for offset in range(0, 1 << width, 1 << 20):
        states = np.arange(offset, min(offset + (1 << 20), 1 << width), dtype=np.uint64)
        for law, bits in packed:
            part = states & bits
            if law == "nae":
                keep = (part != 0) & (part != bits)
            else:
                keep = (np.bitwise_count(part) & 1) == int(law == "odd")
            states = states[keep]
        segments.append(states)
    states = np.concatenate(segments)
    assert len(states)
    return states


@lru_cache(maxsize=None)
def completion_table(old_count, fresh_count):
    """Evaluate the newborn rule on every fresh assignment for each kind of old assignment."""
    fresh = np.arange(1 << fresh_count, dtype=np.uint64) << old_count
    old_all = (1 << old_count) - 1
    all_ones = (1 << (old_count + fresh_count)) - 1
    counts = []
    for old in (0, old_all, 1):
        joint = fresh | old
        counts.append(np.count_nonzero((joint != 0) & (joint != all_ones)))
    return tuple(counts)


def local_completions(states, birth):
    old_mask = mask(birth.old)
    old_part = states & old_mask
    all_zero, all_one, mixed = completion_table(len(birth.old), len(birth.fresh))
    return np.where(old_part == 0, all_zero, np.where(old_part == old_mask, all_one, mixed)).astype(np.uint64)


def complete_nae(states, divisors, births):
    """List allowed states and accumulate denominators for division at the births."""
    for birth in births:
        assert birth.fresh and birth.old
        divisors = divisors * local_completions(states, birth)
        old_part = states & mask(birth.old)
        fresh_mask = mask(birth.fresh)
        kept_states = []
        kept_divisors = []
        start = birth.fresh[0]
        for part in range(1 << len(birth.fresh)):
            bit_values = part << start
            if bit_values in (0, fresh_mask):
                keep = old_part != (mask(birth.old) if bit_values else 0)
                kept_states.append(states[keep] | bit_values)
                kept_divisors.append(divisors[keep])
            else:
                kept_states.append(states | bit_values)
                kept_divisors.append(divisors)
        states = np.concatenate(kept_states)
        divisors = np.concatenate(kept_divisors)
    return states, divisors


def state_weights(start, rounds):
    states = initial_states(start)
    divisors = np.full(len(states), len(states), dtype=np.uint64)
    for made in rounds:
        states, divisors = complete_nae(states, divisors, made.births)
    return {int(state): int(divisor) for state, divisor in zip(states, divisors)}


def exact_total_variation(divisor_hist):
    states = sum(divisor_hist.values())
    mass = sum(Fraction(count, divisor) for divisor, count in divisor_hist.items())
    assert mass == 1, (divisor_hist, mass)
    return sum(
        abs(Fraction(1, states) - Fraction(1, divisor)) * count
        for divisor, count in divisor_hist.items()
    ) / 2


def start_count_nae(start):
    """Inclusion-exclusion over the two forbidden assignments of each rule."""
    width = len(distinct(start))
    masks = [mask(rule.places) for rule in start]
    count = 0
    for choices in product((-1, 0, 1), repeat=len(masks)):
        zero, one, sign = 0, 0, 1
        for choice, forbidden in zip(choices, masks, strict=True):
            if choice == -1:
                zero |= forbidden
                sign *= -1
            elif choice == 1:
                one |= forbidden
                sign *= -1
        if not (zero & one):
            count += sign * (1 << (width - (zero | one).bit_count()))
    return count


def direct_nae(start, rounds, measured, widths):
    """Check the reported direct rows and the originally stated size envelope."""
    initial_count = start_count_nae(start)
    if initial_count > 1 << 20 and not any(measured):
        return {}
    states = initial_states(start)
    assert len(states) == initial_count
    divisors = np.full(len(states), len(states), dtype=np.uint64)
    result = {}
    for index, made in enumerate(rounds):
        if widths[index + 1] > 60:
            assert not any(measured[index:])
            break
        if not any(measured[index:]):
            lower_bound = len(states) * math.prod((1 << len(birth.fresh)) - 1 for birth in made.births)
            if lower_bound > 1 << 20:
                break
        multiplicities = np.ones(len(states), dtype=np.uint64)
        for birth in made.births:
            multiplicities *= local_completions(states, birth)
        n_finish = int(multiplicities.sum())
        if measured[index] or n_finish <= 1 << 20:
            final_divisors = divisors * multiplicities
            labels, inverse = np.unique(final_divisors, return_inverse=True)
            counts = np.zeros(len(labels), dtype=np.uint64)
            np.add.at(counts, inverse, multiplicities)
            histogram = {int(label): int(count) for label, count in zip(labels, counts)}
            assert sum(histogram.values()) == n_finish
            result[index] = (n_finish, exact_total_variation(histogram))
        another_candidate = index + 2 < len(widths) and widths[index + 2] <= 60 and n_finish <= 1 << 20
        if not (another_candidate or any(measured[index + 1:])):
            break
        states, divisors = complete_nae(states, divisors, made.births)
    return result


def agreement(start, made):
    """Test all attainable equality patterns, stopping at two distinct products."""
    assert all(rule.law == "nae" for rule in start)
    assert all(birth.old and birth.fresh for birth in made.births)
    relevant = {}
    for birth in made.births:
        if len(birth.old) > 1:
            relevant.setdefault(tuple(sorted(birth.old)), []).append(len(birth.fresh))
    clauses = [
        [sign * (place + 1) for place in rule.places]
        for rule in start for sign in (-1, 1)
    ]
    first_indicator = len(distinct(start)) + 1
    for offset, old in enumerate(relevant):
        indicator = first_indicator + offset
        places = [place + 1 for place in old]
        first, *rest = places
        for place in rest:
            clauses.extend(([-indicator, -first, place], [-indicator, first, -place]))
        clauses.extend(([indicator, *places], [indicator, *(-p for p in places)]))
    with Solver(name="g4", bootstrap_with=clauses) as solver:
        varying = {
            first_indicator + offset: widths
            for offset, widths in enumerate(relevant.values())
            if solver.solve(assumptions=[first_indicator + offset])
            and solver.solve(assumptions=[-(first_indicator + offset)])
        }
        if not varying:
            return True, 0, 1
        possible_products = set()
        patterns = 0
        while solver.solve():
            model = set(solver.get_model())
            signs = [literal if literal in model else -literal for literal in varying]
            possible_products.add(math.prod(
                (1 << width) - int(signed > 0)
                for signed in signs for width in varying[abs(signed)]
            ))
            patterns += 1
            if len(possible_products) == 2:
                break
            solver.add_clause([-signed for signed in signs])
    return len(possible_products) == 1, sum(map(len, varying.values())), patterns


def incidence(stages, anchors, history=False):
    finish = stages[-1]
    width = len(distinct(finish))
    adjacent = [set() for _ in range(width + len(finish))]
    colors = [("distinction", anchors[i] if i < len(anchors) else None) for i in range(width)]
    stage_of = [index for index, stage in enumerate(stages) for _ in stage[len(stages[index - 1]) if index else 0:]]
    for index, (rule, stage) in enumerate(zip(finish, stage_of, strict=True), start=width):
        colors.append(("rule", rule.law, stage) if history else ("rule", rule.law))
        for place in rule.places:
            adjacent[index].add(place)
            adjacent[place].add(index)
    return adjacent, colors


def common_numbers(values_l, values_r):
    numbers = {value: index for index, value in enumerate(dict.fromkeys(values_l + values_r))}
    return [numbers[value] for value in values_l], [numbers[value] for value in values_r]


def stable_colors(adj_l, adj_r, c_l, c_r):
    classes = len(set(c_l))
    while True:
        signatures_l = [(c, tuple(sorted(c_l[j] for j in adj))) for c, adj in zip(c_l, adj_l)]
        signatures_r = [(c, tuple(sorted(c_r[j] for j in adj))) for c, adj in zip(c_r, adj_r)]
        if Counter(signatures_l) != Counter(signatures_r):
            return None
        c_l, c_r = common_numbers(signatures_l, signatures_r)
        refined = len(set(c_l))
        if refined == classes:
            return c_l, c_r
        classes = refined


def exact_isomorphism(left, right):
    """Joint color refinement followed by exact individualization on ambiguous classes."""
    adj_l, colors_l = left
    adj_r, colors_r = right
    if Counter(colors_l) != Counter(colors_r):
        return None

    def refine_and_match(c_l, c_r):
        stable = stable_colors(adj_l, adj_r, c_l, c_r)
        if stable is None:
            return None
        c_l, c_r = stable

        cells_l, cells_r = defaultdict(list), defaultdict(list)
        for vertex, c in enumerate(c_l):
            cells_l[c].append(vertex)
        for vertex, c in enumerate(c_r):
            cells_r[c].append(vertex)
        mapping = [None] * len(c_l)
        for c, cell in cells_l.items():
            for x, y in zip(cell, cells_r[c], strict=True):
                mapping[x] = y
        if all({mapping[j] for j in adj} == adj_r[mapping[x]] for x, adj in enumerate(adj_l)):
            return mapping

        c = min(
            (c for c in cells_l if len(cells_l[c]) > 1),
            key=lambda color: (len(cells_l[color]), -len(adj_l[cells_l[color][0]])),
            default=None,
        )
        if c is None:
            return None
        x = cells_l[c][0]
        individual = len(cells_l)
        c_l[x] = individual
        for y in cells_r[c]:
            next_r = c_r.copy()
            next_r[y] = individual
            mapping = refine_and_match(c_l, next_r)
            if mapping is not None:
                return mapping
        return None

    return refine_and_match(*common_numbers(colors_l, colors_r))


def can_exchange_stages(finish, staged):
    adjacent, colors = finish
    classes, _ = stable_colors(adjacent, adjacent, *common_numbers(colors, colors))
    rules = defaultdict(list)
    for x, color in enumerate(classes):
        if colors[x][0] == "rule":
            rules[color].append(x)
    mixed_pairs = 0
    for cell in rules.values():
        for x, y in combinations(cell, 2):
            if staged[1][x] == staged[1][y]:
                continue
            mixed_pairs += 1
            left, right = colors.copy(), colors.copy()
            left[x] = ("marked", left[x])
            right[y] = ("marked", right[y])
            if exact_isomorphism((adjacent, left), (adjacent, right)) is not None:
                return True, mixed_pairs
    return False, mixed_pairs


def carry_state(state, mapping):
    return sum(1 << to for start, to in enumerate(mapping) if state & (1 << start))


def same_finish_weight_counterexample():
    # Names x,y,z,u,t,v in that order. Both added rules extend in either order.
    start = (Rule("nae", (0, 1, 2)),)
    left = (Birth((), (0, 1), (3, 4)), Birth((), (0, 3), (5,)))
    right = (Birth((), (0,), (3, 5)), Birth((), (0, 1, 3), (4,)))
    assert {frozenset(b.old + b.fresh) for b in left} == {frozenset(b.old + b.fresh) for b in right}
    state = 0b100010  # x=0, y=1, z=0, u=0, t=0, v=1
    assert (state & 7) in initial_states(start)
    for birth in left:
        projection = state & mask(birth.old + birth.fresh)
        assert 0 < projection < mask(birth.old + birth.fresh)
    size = len(initial_states(start))
    factors = [
        [int(local_completions(np.array([state], dtype=np.uint64), birth)[0]) for birth in births]
        for births in (left, right)
    ]
    weights = [str(Fraction(1, size * math.prod(row))) for row in factors]
    assert weights == ["1/24", "1/36"]
    return {
        "scope": "Two supplied histories, outside the registered renumbered growths",
        "start": "nae(x,y,z)",
        "births": ["nae(x,y,u,t)", "nae(x,u,v)"],
        "state in the order (x,y,z,u,t,v)": "010001",
        "same order as listed and reversed: factors": factors,
        "same order as listed and reversed: weights": weights,
    }


def check_renumbering(limit):
    structures = read(INPUT / "structures.json")
    census = read(INPUT / "census_index.json")["starts"]
    recorded = read(RECORD / "part7_grow_again.json")["rows"]
    starts = {"smallest gain: part": rules_from_data(structures["smallest gain: part"])}
    starts.update({f"census {row['census_index']}": tuple(Rule("nae", tuple(places)) for places in row["stars"])
                   for row in census[:10]})
    rows = []
    counts = Counter()
    by_start = defaultdict(Counter)
    interchangeable = []
    mismatches = []
    for original in recorded:
        start_name = original["start"]
        rules = starts[start_name]
        names = distinct(rules)
        roster = list(product(range(len(names)), (False, True), (False, True)))
        assert len(roster) == original["renumberings"]
        for law, data in original["laws"].items():
            baseline, baseline_rounds = grow(number(rules, names), law, "nae")
            base_finish = incidence(baseline, names)
            base_history = incidence(baseline, names, history=True)
            exchanges_ages, mixed_pairs = can_exchange_stages(base_finish, base_history)
            interchangeable.append([start_name, law, exchanges_ages, mixed_pairs])
            base_weights = None
            assert len(data["rows"]) == len(roster)
            collection = by_start[(start_name, law)]
            for (offset, reverse_names, reverse_rules), raw in zip(roster, data["rows"], strict=True):
                if limit is not None and collection["comparisons"] >= limit:
                    break
                assert [offset, reverse_names, reverse_rules] == [raw["k"], raw["reversed"], raw["knots reversed"]]
                rotated = names[offset:] + names[:offset]
                numbered = rotated[::-1] if reverse_names else rotated
                actual, rounds = grow(number(rules, numbered, reverse_rules), law, "nae")
                births = [len(made.births) for made in rounds]
                grew = any(births)
                identity = offset == 0 and not reverse_names and not reverse_rules
                assert len(actual[-1]) == len(rules) + sum(births)
                width = len(distinct(actual[-1]))
                match = exact_isomorphism(incidence(actual, numbered), base_finish)
                same_finish = match is not None
                same_history = False
                states = None
                weights_equal = None
                if same_finish:
                    staged = exact_isomorphism(incidence(actual, numbered, history=True), base_history)
                    same_history = staged is not None
                    if width <= 24:
                        if base_weights is None:
                            base_weights = state_weights(baseline[0], baseline_rounds)
                        weights = state_weights(actual[0], rounds)
                        states = len(weights)
                        weights_equal = {
                            carry_state(state, (staged or match)[:width]): divisor
                            for state, divisor in weights.items()
                        } == base_weights
                        verdict = "same" if weights_equal else "DIFFERENT"
                    else:
                        verdict = "same by the renaming of the whole history" if same_history else "not decided (size)"
                        if same_history:
                            weights_equal = True
                else:
                    verdict = "no comparison"
                row = {
                    "start": start_name,
                    "law": law,
                    "k": offset,
                    "reversed": reverse_names,
                    "knots reversed": reverse_rules,
                    "births per round": births,
                    "stalled": any(made.status == "stalled" for made in rounds),
                    "knots": len(actual[-1]),
                    "distinctions": width,
                    "same finished structure": same_finish,
                    "same history (rounds kept)": same_history,
                    "weighting": verdict,
                    "allowed states": states,
                }
                for key in ("births per round", "stalled", "knots", "same finished structure",
                            "same history (rounds kept)", "weighting", "allowed states"):
                    # The record describes its final stall, not whether any round could stall thereafter.
                    if row[key] != raw.get(key):
                        mismatches.append({"row": len(rows), "field": key, "recounted": row[key], "record": raw.get(key)})
                rows.append(row)
                for summary in (counts, collection):
                    summary["comparisons"] += 1
                    summary["identity comparisons"] += identity
                    summary["no births"] += not grew
                    summary["different finished structures"] += not same_finish
                    summary["different numbers of rules"] += len(actual[-1]) != len(baseline[-1])
                    summary["same finished structure"] += same_finish
                    summary["same finish, different stages"] += same_finish and not same_history
                    summary["same finish, birth made"] += same_finish and grew
                    summary["same finish, birth made, nonidentity numbering"] += same_finish and grew and not identity
                    summary["same history exact isomorphism, above enumeration width"] += same_history and states is None
                    summary["numerical weights checked"] += states is not None
                    summary["numerical weights with birth"] += states is not None and grew
                    summary["unequal weights"] += weights_equal is False
    return {
        "counts": counts,
        "by start and law": {f"{start} / {law}": count for (start, law), count in by_start.items()},
        "baseline finish automorphisms exchanging stages (Boolean, candidate pairs tried)": interchangeable,
        "mismatches": mismatches,
        "general scope control": same_finish_weight_counterexample(),
        "rows": rows,
    }


def check_census(limit):
    starts = read(INPUT / "census_index.json")["starts"]
    if limit is not None:
        starts = starts[:limit]
    raw = read(RECORD / "part9_engine_check.json")
    recorded = {(row["census_index"], row["law"], row["knot law"]): row for row in raw["rows"]}
    counts = defaultdict(Counter)
    mismatches = []
    diagnostics = []
    threshold_exceptions = []
    missing_eligible_checks = []
    width_cap_mismatches = []
    rows = []
    for row in starts:
        for law, knot_law in product(LAWS, ("parity", "nae")):
            start_id = row["census_index"]
            key = (start_id, law, knot_law)
            old = recorded[key]
            newborn = "even" if knot_law == "parity" else "nae"
            start = tuple(Rule(newborn, tuple(places)) for places in row["stars"])
            stages, rounds = grow(start, law, newborn)
            widths = [len(distinct(stage)) for stage in stages]
            grew = any(made.births for made in rounds)
            for label, value in [
                ("rounds done", len(rounds)),
                ("births per round", [len(made.births) for made in rounds]),
                ("stalled", [made.status == "stalled" for made in rounds]),
                ("made a birth", grew),
            ]:
                if value != old[label]:
                    mismatches.append([*key, label, value, old[label]])
            assert len(rounds) == len(old["rounds"])
            compared = [isinstance(value["direct"], dict) for value in old["rounds"]]
            census_counts = counts[f"{law} / {knot_law}"]
            census_counts["growths"] += 1
            census_counts["made a birth"] += grew
            direct = direct_nae(start, rounds, compared, widths) if knot_law == "nae" else {}
            first = None
            round_rows = []
            for index, (made, raw_round) in enumerate(zip(rounds, old["rounds"], strict=True)):
                n_round = index + 1
                if compared[index] != (widths[n_round] <= 24):
                    width_cap_mismatches.append([*key, n_round, widths[n_round], compared[index]])
                if knot_law == "parity":
                    basis_before = parity_basis(stages[index])
                    basis_after = parity_basis(stages[n_round])
                    assert len(basis_after) == len(basis_before) + sum(bool(birth.fresh) for birth in made.births)
                    assert all(birth.fresh or not reduce_parity(mask(birth.old), basis_before) for birth in made.births)
                    census_counts["implied births with nothing fresh"] += sum(not birth.fresh for birth in made.births)
                    n_finish = 1 << (widths[n_round] - len(basis_after))
                    if compared[index] or (widths[n_round] <= 60 and n_finish <= 1 << 20):
                        direct[index] = (n_finish, Fraction(0))
                still_comparable = first is None
                if still_comparable:
                    if knot_law == "nae":
                        holds, varying, patterns = agreement(stages[index], made)
                    else:
                        holds, varying, patterns = True, 0, 1
                    if not holds:
                        first = n_round
                    verdict = "agree" if holds else "part"
                    if verdict != raw_round.get("verdict"):
                        mismatches.append([*key, n_round, "verdict", verdict, raw_round.get("verdict")])
                    if varying != raw_round.get("varying births"):
                        mismatches.append([*key, n_round, "varying births", varying, raw_round.get("varying births")])
                    if patterns != raw_round.get("patterns"):
                        diagnostics.append([*key, n_round, "patterns visited", patterns, raw_round.get("patterns")])
                    census_counts["rounds through first parting"] += 1
                    census_counts["rounds through first parting with births"] += bool(made.births)
                    census_counts["rounds through first parting with a multi-input birth"] += any(len(b.old) >= 2 for b in made.births)
                    census_counts["rounds through first parting with varying birth(s)"] += bool(varying)
                    if index in direct and holds != (direct[index][1] == 0):
                        mismatches.append([*key, n_round, "rule against direct", verdict, str(direct[index][1])])
                    if compared[index]:
                        census_counts["rounds through first parting checked directly"] += 1
                        census_counts["rounds through first parting with births checked directly"] += bool(made.births)
                        census_counts["rounds through first parting with a multi-input birth checked directly"] += any(len(b.old) >= 2 for b in made.births)
                        census_counts["rounds through first parting with varying birth(s) checked directly"] += bool(varying)
                    if first == n_round:
                        census_counts[f"first parting at round {n_round}"] += 1
                        census_counts[f"first parting at round {n_round} checked directly"] += compared[index]
                        census_counts[f"first parting at round {n_round} additionally checked directly"] += index in direct and not compared[index]
                else:
                    verdict, varying, patterns = None, None, None
                numerical = None
                if index in direct:
                    states, tv = direct[index]
                    numerical = {"states": states, "tv": str(tv), "agree": not tv, "kept": "1"}
                    if compared[index]:
                        census_counts["rounds checked directly"] += 1
                        if numerical != raw_round["direct"]:
                            mismatches.append([*key, n_round, "direct", numerical, raw_round["direct"]])
                        if states > 1 << 20 or widths[n_round] > 60:
                            threshold_exceptions.append([*key, n_round, widths[n_round], states])
                    else:
                        census_counts["additional direct checks"] += 1
                        census_counts["additional direct checks through first parting"] += still_comparable
                        census_counts["additional direct checks through first parting with births"] += still_comparable and bool(made.births)
                        missing_eligible_checks.append([*key, n_round, widths[n_round], states])
                round_rows.append({
                    "round": n_round,
                    "state": made.status,
                    "distinctions": widths[n_round],
                    "births": len(made.births),
                    "varying births": varying,
                    "patterns visited": patterns,
                    "verdict": verdict,
                    "direct": numerical,
                    "direct in the record": compared[index],
                })
            if first != old["first parting round"]:
                mismatches.append([*key, "first parting round", first, old["first parting round"]])
            census_counts["not parted, birth made"] += grew and first is None
            rows.append({"census_index": start_id, "law": law, "knot law": knot_law, "rounds": round_rows,
                         "made a birth": grew, "first parting round": first})
    return {
        "counts": counts,
        "direct checks beyond the recorded size limit": threshold_exceptions,
        "formerly omitted direct checks within the stated size limit": missing_eligible_checks,
        "mismatches with direct checking at width at most 24": width_cap_mismatches,
        "mismatches": mismatches,
        "search diagnostics": diagnostics,
        "rows": rows,
    }


SETTING_PAIRS = tuple(product(range(2), repeat=2))


def joint_weights(states, divisors, record_a, record_b):
    bins = Counter()
    for state, divisor in zip(states, divisors, strict=True):
        state = int(state)
        first = sum((state >> place & 1) << bit for bit, place in enumerate(record_a))
        second = sum((state >> place & 1) << bit for bit, place in enumerate(record_b))
        bins[first, second, int(divisor)] += 1
    joint = defaultdict(Fraction)
    for (first, second, divisor), count in bins.items():
        joint[first, second] += Fraction(count, divisor)
    assert sum(joint.values()) == 1
    return joint


def record_score(tables):
    denom = math.lcm(*(w.denominator for table in tables.values() for w in table.values()))
    raw = np.zeros((2, 2, 16, 16), dtype=np.int64)
    for (a, b), table in tables.items():
        for (first, second), value in table.items():
            raw[a, b, first, second] = int(value * denom)
    change_a = max(np.abs(raw[a, 0].sum(axis=1) - raw[a, 1].sum(axis=1)).sum() for a in range(2))
    change_b = max(np.abs(raw[0, b].sum(axis=0) - raw[1, b].sum(axis=0)).sum() for b in range(2))

    parities = np.fromiter(
        ((-1) ** (value & selected).bit_count() for selected in range(1, 16) for value in range(16)),
        dtype=np.int64,
    ).reshape(15, 16)
    correlations = parities @ raw @ parities.T
    lifts = (
        correlations[0, 0][:, None, :, None],
        correlations[0, 1][:, None, None, :],
        correlations[1, 0][None, :, :, None],
        correlations[1, 1][None, :, None, :],
    )
    total = sum(lifts)
    scores = [total - 2 * v for v in lifts]
    signed = max(m.max() for m in scores)
    absolute = max(np.abs(m).max() for m in scores)

    counts_first = (raw.sum(axis=(1, 3)) > 0).sum()
    counts_second = (raw.sum(axis=(0, 2)) > 0).sum()
    if counts_second < counts_first:
        raw = raw.transpose(1, 0, 3, 2)
    response = []
    for setting in range(2):
        values = np.where(raw[setting].sum(axis=(0, 2)) > 0)[0]
        signs = np.array(list(product((1, -1), repeat=len(values))), dtype=np.int64)
        if setting:
            signs = signs[signs[:, 0] == 1]
        response.append([signs @ raw[setting, other][values] for other in range(2)])
    opt = 0
    for a, b in SETTING_PAIRS:
        value = 0
        for other in range(2):
            base = response[0][other][:, None, :]
            rest = response[1][other][None, :, :]
            signed_base = -base if (a, b) == (0, other) else base
            signed_rest = -rest if (a, b) == (1, other) else rest
            value += np.abs(signed_base + signed_rest).sum(axis=2)
        opt = max(opt, int(value.max()))
    return {
        "score_all": str(Fraction(opt, denom)),
        "score_parity": str(Fraction(int(signed), denom)),
        "score_parity_abs": str(Fraction(int(absolute), denom)),
        "change_first": str(Fraction(int(change_a), 2 * denom)),
        "change_second": str(Fraction(int(change_b), 2 * denom)),
        "hidden": not (change_a or change_b),
    }


def rule_text(rule):
    return f"{rule.law}({','.join(rule.places)})"


def rule_set(text):
    return Counter((rule.split("(")[0], tuple(sorted(rule.split("(")[1][:-1].split(",")))) for rule in text)


def ten_rule_rounds(named, label):
    names = distinct(named)
    start = number(named, names)
    old_states = initial_states(start)
    trial, _ = make_round(start, set(), "Q-OLDEST", "nae")
    options = {names[birth.old[0]]: values for birth, values in zip(trial.births, trial.choices, strict=True)}
    modes = {"x1": "za", "y1": "zb", next(key for key in options if key not in {"x1", "y1"}): "f3"}
    assert len(options) == 3 and all(birth.fresh and len(birth.parents) == 1 for birth in trial.births)
    variants = {}
    order = list(options)
    for selections in product(*options.values()):
        outcome, _ = make_round(start, set(), "Q-OLDEST", "nae", selections=selections)
        fresh_names = {
            birth.fresh[0]: modes[name]
            for name, birth in zip(order, outcome.births, strict=True)
        }
        assert all(len(birth.fresh) == 1 for birth in outcome.births)
        readable = {**dict(enumerate(names)), **fresh_names}
        given = [rule_text(rule) for rule in named] + [
            rule_text(Rule("nae", tuple(readable[place] for place in birth.old + birth.fresh)))
            for birth in outcome.births
        ]
        states, div_from_start = complete_nae(
            old_states, np.full(len(old_states), len(old_states), dtype=np.uint64), outcome.births,
        )
        by_side = ([outcome.births[order.index("x1")]],
                   [birth for name, birth in zip(order, outcome.births) if name != "x1"])
        intermediates = []
        for top, after in (by_side, by_side[::-1]):
            stage_states, _ = complete_nae(old_states, np.ones(len(old_states), dtype=np.uint64), top)
            div = np.full(len(states), len(stage_states), dtype=np.uint64)
            for birth in after:
                div *= local_completions(states, birth)
            intermediates.append(div)

        name_to_index = {name: i for i, name in readable.items()}
        record_a = tuple(name_to_index[name] for name in ("x1", "x2", "x3", "za"))
        record_b = tuple(name_to_index[name] for name in ("y1", "y2", "y3", "zb"))
        joint = {
            "from the start": joint_weights(states, div_from_start, record_a, record_b),
            "from the finish": joint_weights(states, np.full(len(states), len(states)), record_a, record_b),
            "mixed stage (the first observer first)": joint_weights(states, intermediates[0], record_a, record_b),
            "mixed stage (the second observer first)": joint_weights(states, intermediates[1], record_a, record_b),
        }
        variants[tuple(names[selections[order.index(name)]] for name in modes)] = (given, len(states), joint)
    return {
        "name": label,
        "start states": len(old_states),
        "options": {name: [names[place] for place in values] for name, values in options.items()},
        "variations": variants,
    }


def check_tens(limit):
    data = read(INPUT / "structures.json")
    raw = read(RECORD / "part2_lemma.json")
    starts = {
        key[:5]: ten_rule_rounds(rules_from_data(value), key[:5])
        for key, value in data.items()
        if key.startswith("ten ")
    }
    items = [row["result"] for row in raw["items"] if row["item"].startswith("two 10-knot starts")]
    if limit is not None:
        items = items[:limit]
    mismatches = []
    checked = []
    for item in items:
        name, options = item["name"].rsplit(" ", 1)
        start = starts[name]
        a_settings, b_settings = (side.split("-") for side in options.split("/"))
        choice_points = [values for _, values in raw["ten round 1"][name]["choice points"]]
        if list(start["options"].values()) != choice_points:
            mismatches.append([name, "choice points", list(start["options"].values()), choice_points])
        scores = []
        selected = []
        for variant in item["variants"]:
            third = variant["label"].rsplit(" ", 1)[-1]
            made = {
                (a, b): start["variations"][a_settings[a], b_settings[b], third]
                for a, b in SETTING_PAIRS
            }
            selected.append(made)
            for pair, (finished, state_count, _) in made.items():
                raw_text = variant["finished"][str(pair)]
                if rule_set(finished) != rule_set(raw_text):
                    mismatches.append([item["name"], third, pair, "rules", finished, raw_text])
                raw_count = variant["info"]["allowed at the finish"][str(pair)]
                if state_count != raw_count:
                    mismatches.append([item["name"], third, pair, "states", state_count, raw_count])
            computed = {
                casting: record_score({pair: row[2][casting] for pair, row in made.items()})
                for casting in next(iter(made.values()))[2]
            }
            for casting, value in computed.items():
                raw_value = {key: variant["rows"][casting][key] for key in value}
                if value != raw_value:
                    mismatches.append([item["name"], third, casting, value, raw_value])
            scores.append({"third birth takes": third, "weightings": computed})
        pools = {}
        for casting, raw_score in item["pooled"].items():
            source = "from the start" if casting.startswith("from the start") else "from the finish"
            pooled = {}
            for pair in SETTING_PAIRS:
                part = [made[pair] for made in selected]
                share = [row[1] if "each history and state once" in casting else 1 for row in part]
                joint = defaultdict(Fraction)
                for w, row in zip(share, part, strict=True):
                    for record_value, prob in row[2][source].items():
                        joint[record_value] += Fraction(w, sum(share)) * prob
                pooled[pair] = joint
            computed = record_score(pooled)
            pools[casting] = computed
            if computed != raw_score:
                mismatches.append([item["name"], casting, computed, raw_score])
        checked.append({"option pair": item["name"], "per history": scores, "pooled": pools})
    return {
        "starts": {name: {"start states": data["start states"], "options": data["options"],
                           "distinct grown structures": len(data["variations"])} for name, data in starts.items()},
        "finished structures checked with repeats": sum(len(row["per history"]) * 4 for row in checked),
        "mismatches": mismatches,
        "items": checked,
    }


def two_bit_score(contexts):
    correlation = [p[0] + p[3] - p[1] - p[2] for p in contexts]
    selected_marginals = [
        [p[2] + p[3] for p in contexts],
        [p[1] + p[3] for p in contexts],
    ]
    own_setting_tv = [
        [abs(rows[i] - rows[j]) for i, j in pairs]
        for rows, pairs in zip(selected_marginals, (((0, 1), (2, 3)), ((0, 2), (1, 3))), strict=True)
    ]
    return {
        "correlations": list(map(str, correlation)),
        "signed score": str(sum(correlation) - 2 * correlation[-1]),
        "maximum over sign placements": str(max(abs(sum(correlation) - 2 * value) for value in correlation)),
        "selected-output change by side and own setting": [list(map(str, row)) for row in own_setting_tv],
    }


def check_copied_funding(limit):
    """Recalculate copied scores from the archived exact output tables, keeping their type weights explicit."""
    source = "WHOLE-STAGE-SETTINGS-20261120-001C"
    path = ROOT / "artifacts" / source / f"{source}-E001_masking" / "masking.json"
    laws = list(read(path)["laws"].items())
    mismatches = []
    outcome = {}
    for law, data in laws[:limit]:
        outcome[law] = {}
        batches = {"primary": data["primary"], "uniform final (equal mass per preparation)": data["controls"]["uniform_final"]}
        for label, batch in batches.items():
            contexts = [tuple(Fraction(count, row["denominator"]) for count in row["counts"]) for row in batch["contexts"]]
            assert all(sum(row) == 1 for row in contexts)
            score = two_bit_score(contexts)
            raw_scores = [batch["correlations"], batch["signed_S"], batch["max_CHSH"], [row["selected"] for row in batch["TV"].values()]]
            if list(score.values()) != raw_scores:
                mismatches.append([law, label, score, raw_scores])
            score["archived within-record change by side and own setting"] = [row["full_local"] for row in batch["TV"].values()]
            outcome[law][label] = score
            if label == "primary":
                continue
            pooled = []
            for settings, row, table in zip(("00", "01", "10", "11"), batch["contexts"], contexts, strict=True):
                stalled = (1, 0, 0, 0)
                funded = tuple(4 * q - 3 * p for p, q in zip(stalled, table, strict=True))
                assert all(0 <= p <= 1 for p in funded) and sum(funded) == 1
                totals = {name: info["complete_states"] for name, info in row["types"].items()}
                funded_share = Fraction(totals[settings], sum(totals.values()))
                pooled.append(tuple(funded_share * p + (1 - funded_share) * q for p, q in zip(funded, stalled, strict=True)))
            outcome[law]["uniform final (each history and state once)"] = two_bit_score(pooled)
    return {"source": str(path.relative_to(ROOT)), "recounted T20 and T22": outcome, "mismatches": mismatches}


def main():
    sections = {"tens": check_tens, "renumbering": check_renumbering, "census": check_census, "funding": check_copied_funding}
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("section", choices=sections)
    cli.add_argument("--limit", type=int, help="Pilot on a prefix without writing a record")
    args = cli.parse_args()
    t0 = perf_counter()
    checked = sections[args.section](args.limit)
    checked["runtime"] = {"elapsed seconds": round(perf_counter() - t0, 3),
                          "peak resident KiB": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}
    if args.limit is None:
        output = HERE / f"growth_{args.section}.json"
        output.write_text(json.dumps(checked, indent=1) + "\n")
    summary = {key: value for key, value in checked.items() if key not in {"rows", "items", "search diagnostics", "by start and law"}}
    for key in ("direct checks beyond the recorded size limit", "formerly omitted direct checks within the stated size limit",
                "mismatches with direct checking at width at most 24", "baseline finish automorphisms exchanging stages (Boolean, candidate pairs tried)"):
        if key in summary:
            summary[key] = len(summary[key]) if not key.startswith("baseline") else sum(row[2] for row in summary[key])
    if "mismatches" in summary:
        summary["mismatch count"] = len(summary["mismatches"])
        summary["mismatches"] = summary["mismatches"][:18]
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
