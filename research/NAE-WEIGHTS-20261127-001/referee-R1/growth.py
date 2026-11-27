"""Rebuild one ordinary round and count completions under not-all-equal."""

import argparse
import json
import sys
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from fractions import Fraction
from itertools import combinations
from math import prod
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
RESEARCH = ROOT / "research"
LAYER = RESEARCH / "NAE-LAYER-20261127-001"
ARCHIVE = RESEARCH / "FORBID-EDITS-20261126-001" / "starts.json"
TARGET = Path(__file__).resolve().parents[1]
ENGINE = ROOT / "experiments" / "NAE-GROWTH-20261119-001B" / "NAE-GROWTH-20261119-001B-E001_nae"

SEVEN_KNOT_START = (
    (0, 1, 2), (0, 3, 6), (1, 4, 7), (2, 5, 8),
    (3, 9, 10), (4, 11, 12), (5, 13, 14),
)
FUNDED_SEVEN_KNOT_START = tuple(
    support + (14 + knot,) if 1 <= knot <= 3 else support
    for knot, support in enumerate(SEVEN_KNOT_START)
)


@dataclass(frozen=True)
class Birth:
    parents: tuple[int, ...]
    inputs: tuple[int, ...]
    demand: int
    implied: bool
    fresh: tuple[int, ...]


@dataclass(frozen=True)
class Round:
    status: str
    supports: tuple[tuple[int, ...], ...]
    births: tuple[Birth, ...] = ()
    shortages: tuple[tuple[int, int], ...] = ()


def holders(supports):
    out = defaultdict(list)
    for knot, support in enumerate(supports):
        for name in support:
            out[name].append(knot)
    return out


def names_and_masks(supports):
    names = sorted({name for support in supports for name in support})
    index = {name: 1 << bit for bit, name in enumerate(names)}
    masks = tuple(sum(index[name] for name in support) for support in supports)
    return names, masks


def allowed_states(supports):
    names, masks = names_and_masks(supports)
    states = [
        state for state in range(1 << len(names))
        if all((state & mask) not in (0, mask) for mask in masks)
    ]
    return names, states


def parent_groups(neighbors, live):
    """Maximal valid sets and the remaining candidate pairs, in payment order."""
    pairs = {
        (a, b) for a, b in combinations(live, 2)
        if neighbors[a] & neighbors[b]
    }
    candidates = defaultdict(set)
    for a, b in pairs:
        candidates[a].add(b)

    def valid_sets(prefix, remaining):
        for next_knot in sorted(remaining):
            group = (*prefix, next_knot)
            if len(group) >= 3 and not set.intersection(*(neighbors[knot] for knot in group)):
                yield group
            yield from valid_sets(group, remaining & candidates[next_knot])

    maximal = []
    for group in sorted(valid_sets((), set(live)), key=len, reverse=True):
        group_set = set(group)
        if not any(group_set <= other for other in maximal):
            maximal.append(group_set)
    groups = sorted(tuple(sorted(group)) for group in maximal)
    covered = {pair for group in groups for pair in combinations(group, 2)}
    return groups + sorted(pairs - covered)


def grow_one_round(supports, names=None, states=None):
    """Apply the frozen complete-round joining rule and fewest count."""
    supports = tuple(tuple(support) for support in supports)
    held = holders(supports)
    if not held or any(len(row) < 3 or len(row) != len(set(row)) for row in supports):
        raise ValueError("expected nonempty supports of at least three distinct places")
    if any(len(owners) > 2 for owners in held.values()):
        raise ValueError("expected at most two holders per distinction")

    loose = {
        knot: tuple(name for name in support if len(held[name]) == 1)
        for knot, support in enumerate(supports)
        if any(len(held[name]) == 1 for name in support)
    }
    if not loose:
        return Round("closed", supports)
    neighbors = [set() for _ in supports]
    for owners in held.values():
        if len(owners) == 2:
            a, b = owners
            neighbors[a].add(b)
            neighbors[b].add(a)
    groups = parent_groups(neighbors, list(loose))
    current_demand = Counter(parent for group in groups for parent in group)
    shortages = tuple(
        (parent, current_demand[parent] - len(available))
        for parent, available in loose.items()
        if current_demand[parent] > len(available)
    )
    if shortages:
        return Round("stalled", supports, shortages=shortages)

    plan = []
    paid = Counter()
    for group in groups:
        inputs = tuple(loose[parent][paid[parent]] for parent in group)
        plan.append((group, inputs))
        paid.update(group)
    for parent, available in loose.items():
        plan.extend(((parent,), (name,)) for name in available[paid[parent]:])

    first_birth = len(supports)
    next_neighbors = neighbors + [set(parents) for parents, _ in plan]
    newborns = list(range(first_birth, first_birth + len(plan)))
    for knot, (parents, _) in zip(newborns, plan, strict=True):
        for parent in parents:
            next_neighbors[parent].add(knot)
    next_demand = Counter(knot for group in parent_groups(next_neighbors, newborns) for knot in group)

    if names is None or states is None:
        names, states = allowed_states(supports)
    index = {name: 1 << bit for bit, name in enumerate(names)}
    # All allowed states come in globally flipped pairs. Finding one all-zero
    # input therefore disproves implication in both orientations.
    next_name = max(held) + 1
    births = []
    for knot, (parents, inputs) in zip(newborns, plan, strict=True):
        mask = sum(index[name] for name in inputs)
        implied = not any((state & mask) == 0 for state in states)
        demand = next_demand[knot]
        count = demand if implied else max(demand, 3 - len(inputs), 1)
        fresh = tuple(range(next_name, next_name + count))
        births.append(Birth(parents, tuple(sorted(inputs)), demand, implied, fresh))
        next_name += count
    stage = supports + tuple(birth.inputs + birth.fresh for birth in births)
    return Round("funded", stage, tuple(births))


def completion_weights(births, names, states):
    index = {name: 1 << bit for bit, name in enumerate(names)}
    factors = [
        (sum(index[name] for name in birth.inputs), 1 << len(birth.fresh))
        for birth in births
    ]
    return {
        state: prod(total - ((state & mask) in (0, mask)) for mask, total in factors)
        for state in states
    }


def round_completion_weights(supports, names, states):
    """Return one positive integer per old state, or None for an unavailable round."""
    states = tuple(states)
    result = grow_one_round(supports, names, states)
    return completion_weights(result.births, names, states) if result.status == "funded" else None


def decode_start(record):
    count, shared, loose = record
    supports = [[] for _ in range(count)]
    name = 0
    for a, b, multiplicity in shared:
        names = list(range(name, name + multiplicity))
        supports[a].extend(names)
        supports[b].extend(names)
        name += multiplicity
    for knot, multiplicity in enumerate(loose):
        supports[knot].extend(range(name, name + multiplicity))
        name += multiplicity
    return tuple(map(tuple, supports))


def tree_shaped(supports):
    """The archived starts are connected and have at most two holders."""
    return sum(len(owners) == 2 for owners in holders(supports).values()) == len(supports) - 1


def literal_fibers(births, names, states, fresh_names=None):
    """Test the full conjunction on every fresh assignment in parallel as bits.

    Bit j in a column represents assignment j to all fresh distinctions.
    This counts by conjunction and population count. It uses no product of
    counts of individual births.
    """
    if fresh_names is None:
        fresh_names = [name for birth in births for name in birth.fresh]
    assignment_count = 1 << len(fresh_names)
    all_assignments = (1 << assignment_count) - 1
    columns = {}
    for index, name in enumerate(fresh_names):
        if index < 3:
            pattern = bytes([(0b10101010, 0b11001100, 0b11110000)[index]])
            block = pattern * ((assignment_count + 7) // 8)
        else:
            run = 1 << (index - 3)
            pattern = bytes(run) + bytes([255]) * run
            block = pattern * (assignment_count >> (index + 1))
        columns[name] = int.from_bytes(block, "little") & all_assignments

    old_bit = {name: 1 << index for index, name in enumerate(names)}
    full_rules = []
    for birth in births:
        old_mask = sum(old_bit[name] for name in birth.inputs)
        zero_restriction = one_restriction = all_assignments
        for name in birth.fresh:
            zero_restriction &= ~columns[name]
            one_restriction &= columns[name]
        full_rules.append((old_mask, zero_restriction, one_restriction))

    fibers = {}
    attained = 0
    for state in states:
        good = all_assignments
        for old_mask, forbid_zero, forbid_one in full_rules:
            value = state & old_mask
            if value == 0:
                good &= ~forbid_zero
            elif value == old_mask:
                good &= ~forbid_one
        fibers[state] = good.bit_count()
        attained |= good
    return fibers, (attained.bit_count(), assignment_count)


def signed_expansion(supports, births, names):
    """Exact integer coefficients up to a common positive scaling factor."""
    position = {name: 1 << index for index, name in enumerate(names)}
    local_scopes = [(support, len(support)) for support in supports]
    local_scopes.extend((birth.inputs, len(birth.inputs) + len(birth.fresh)) for birth in births)
    product = {0: 1}
    for scope, arity in local_scopes:
        coefficients = {0: (1 << (arity - 1)) - 1}
        for size in range(2, len(scope) + 1, 2):
            for subset in combinations(scope, size):
                coefficients[sum(position[name] for name in subset)] = -1
        result = defaultdict(int)
        for a, va in product.items():
            for b, vb in coefficients.items():
                result[a ^ b] += va * vb
        product = {subset: value for subset, value in result.items() if value}
    return product


def moments(weights, width):
    result = [weights.get(word, 0) for word in range(1 << width)]
    for index in range(width):
        half = 1 << index
        for start in range(0, len(result), 2 * half):
            for lo in range(start, start + half):
                hi = lo + half
                a, b = result[lo], result[hi]
                result[lo], result[hi] = a + b, a - b
    return result


def compare_shared_engine(supports, rebuilt):
    """The shared engine supplies a comparison only."""
    if str(ENGINE) not in sys.path:
        sys.path.insert(0, str(ENGINE))
    import naelib

    model = naelib.S.from_junctions(supports)
    reference = {}

    def record_births(presentation, info, rng):
        reference.update((row["j"], row) for row in info)
        return naelib.F.fewest(presentation, info, rng)

    step = model.step(naelib.nae_rule(record_births))
    status = "stalled" if step is None else "funded" if step["new"] else "closed"
    old_holders = holders(supports)
    births = []
    for knot, info in reference.items():
        inputs = tuple(sorted(name for name in model.bits_of[knot] if name in old_holders))
        fresh = tuple(sorted(name for name in model.bits_of[knot] if name not in old_holders))
        parents = tuple(sorted(old_holders[name][0] for name in inputs))
        births.append(Birth(parents, inputs, info["d"], info["implied"], fresh))
    assert rebuilt.status == status, (supports, rebuilt.status, status)
    assert tuple(births) == rebuilt.births, (supports, births, rebuilt.births)
    assert tuple(map(sorted, model.bits_of)) == tuple(map(sorted, rebuilt.supports)), supports


def read_start(supports, compare_engine, expansion=True):
    names, states = allowed_states(supports)
    rebuilt = grow_one_round(supports, names, states)
    if compare_engine:
        compare_shared_engine(supports, rebuilt)
    row = {
        "supports": supports,
        "old_states": len(states),
        "status": rebuilt.status,
        "stage used for counting": "reached stage" if rebuilt.births else "identity control",
        "shortages": rebuilt.shortages,
        "births": [asdict(birth) for birth in rebuilt.births],
    }

    # On a stalled or closed start the actual round has no weighting.
    # The separately evaluated identity stage assigns each old state one completion.
    observed, fresh_patterns = literal_fibers(rebuilt.births, names, states)
    weights = completion_weights(rebuilt.births, names, states)
    assert observed == weights and all(observed.values()), supports
    assert round_completion_weights(supports, names, states) == (
        observed if rebuilt.status == "funded" else None
    ), supports
    row.update({
        "literal_fibers_checked": len(observed),
        "uniform_stage_states": sum(observed.values()),
        "fiber_size_counts": dict(sorted(Counter(observed.values()).items())),
        "loose_patterns_on_reached_stage": fresh_patterns if rebuilt.births else None,
        "stage_knots": len(rebuilt.supports),
    })
    if not expansion:
        return row

    expanded = signed_expansion(supports, rebuilt.births, names)
    measured = moments(observed, len(names))
    assert all(
        expanded.get(subset, 0) * measured[0] == measured[subset] * expanded[0]
        for subset in range(len(measured))
    ), supports
    row["moments_matching_local_expansion"] = len(measured)
    row["nonempty_even_moments_checked"] = len(measured) // 2 - 1
    row["nonzero_nonempty_even_moments_checked"] = sum(
        value != 0 for subset, value in enumerate(measured) if subset and subset.bit_count() % 2 == 0
    )

    equal = moments(dict.fromkeys(states, 1), len(names))
    unchanged = []
    for a, b in combinations(range(len(names)), 2):
        subset = (1 << a) | (1 << b)
        if equal[subset] * measured[0] == measured[subset] * equal[0]:
            unchanged.append((names[a], names[b]))
    row["pairs"] = len(names) * (len(names) - 1) // 2
    row["pairs_unchanged_from_equal_on_start"] = unchanged
    return row


def weighted_pair(weights, names, pair):
    mask = sum(1 << names.index(name) for name in pair)
    signed_total = sum(
        weight if (word & mask).bit_count() % 2 == 0 else -weight
        for word, weight in weights.items()
    )
    return Fraction(signed_total, sum(weights.values()))


def conditional_pair(weights, names, pair, given):
    counts = [0] * 4
    given_mask = sum(1 << names.index(name) for name in given)
    given_word = sum(value << names.index(name) for name, value in given.items())
    for word, weight in weights.items():
        if word & given_mask == given_word:
            a, b = ((word >> names.index(name)) & 1 for name in pair)
            counts[2 * a + b] += weight
    return counts


def chain_controls(supports):
    names, states = allowed_states(supports)
    actual = grow_one_round(supports, names, states)
    joint_birth, = tuple(birth for birth in actual.births if len(birth.parents) == 2)
    pair = joint_birth.inputs
    given = {0: 0, 1: 1, 2: 0}
    equal = dict.fromkeys(states, 1)
    weights = completion_weights(actual.births, names, states)
    offshoots = tuple(birth for birth in actual.births if len(birth.parents) == 1)
    fresh = [name for birth in actual.births for name in birth.fresh]
    no_join, _ = literal_fibers(offshoots, names, states, fresh_names=fresh)
    assert len(set(no_join.values())) == 1

    # Reordering two loose distinctions changes which one pays without changing
    # any rule of the labelled start.
    alternate = tuple((0, 4, 3) if support == (0, 3, 4) else support for support in supports)
    changed = grow_one_round(alternate, names, states)
    alternative_weights = completion_weights(changed.births, names, states)
    a_bit, b_bit = (1 << names.index(name) for name in (3, 4))
    for state in states:
        relabelled = state ^ (a_bit | b_bit) if bool(state & a_bit) != bool(state & b_bit) else state
        assert alternative_weights[state] == weights[relabelled]

    # One unequal counting on the old states preserves all even moments.
    tilted = {word: 2 if word & 1 else 1 for word in states}
    baseline, changed_weight = (moments(w, len(names)) for w in (equal, tilted))
    even = [i for i in range(len(baseline)) if i.bit_count() % 2 == 0]
    assert all(baseline[i] * changed_weight[0] == changed_weight[i] * baseline[0] for i in even)

    c = lambda a: Fraction(-1, (1 << (a - 1)) - 1)
    old_route = prod(c(len(support)) for support in supports)
    birth_route = c(len(joint_birth.inputs) + len(joint_birth.fresh))
    two_routes = (old_route + birth_route) / (1 + old_route * birth_route)
    assert weighted_pair(equal, names, pair) == old_route
    assert weighted_pair(weights, names, pair) == two_routes

    conditional = {}
    for label, w in (("equal on start", equal), ("completion", weights), ("without joint birth law", no_join)):
        cells = conditional_pair(w, names, pair, given)
        assert all(cells)
        conditional[label] = {
            "probabilities in order 00, 01, 10, 11": [str(Fraction(cell, sum(cells))) for cell in cells],
            "odds ratio": str(Fraction(cells[0] * cells[3], cells[1] * cells[2])),
        }
    return {
        "supports": supports,
        "old_pair": pair,
        "fixed old middle knot values": given,
        "conditional pair": conditional,
        "pair mean": {
            "equal on start": str(weighted_pair(equal, names, pair)),
            "completion": str(weighted_pair(weights, names, pair)),
            "without joint birth law": str(weighted_pair(no_join, names, pair)),
            "one route at birth alone": str(birth_route),
            "grown stage two routes": str(two_routes),
            "same named pair after changing which loose distinction pays": str(weighted_pair(alternative_weights, names, pair)),
        },
        "allowed old states retained": len(states),
        "birth deletion control fiber size": next(iter(no_join.values())),
        "alternative payment relabelling agrees on every old state": len(states),
        "positive unequal weights 1 and 2 by value of distinction 0": {
            "even moments matching equal weighting on the start": len(even),
            "mean sign of distinction 0 under equal weighting": str(Fraction(baseline[1], baseline[0])),
            "mean sign of distinction 0 under unequal weighting": str(Fraction(changed_weight[1], changed_weight[0])),
        },
    }


def run(pilot):
    census = json.loads(ARCHIVE.read_text())
    census_records = [json.loads(line) for line in (LAYER / "census.jsonl").read_text().splitlines()]
    assert census_records.pop()["tally"]["starts"] == len(census) == len(census_records)
    starts = [decode_start(record) for record in census]
    tree_ids = []
    cyclic_with_recorded_stage = []
    closed_ids = []
    for i, (supports, record) in enumerate(zip(starts, census_records, strict=True)):
        tree = tree_shaped(supports)
        assert record["start"] == f"census {i}" and tree == record["tree-shaped"]
        if tree:
            tree_ids.append(i)
        elif "C4 after one round" in record:
            cyclic_with_recorded_stage.append(i)
        if record["loose"] == 0:
            closed_ids.append(i)
    chosen = [0, 2, 89, 1107, closed_ids[0]] if pilot else sorted(
        set(tree_ids) | set(cyclic_with_recorded_stage[::50]) | {closed_ids[0]}
    )

    rows = {}
    for i in chosen:
        row = read_start(starts[i], compare_engine=True)
        record = census_records[i]
        if "C4 after one round" in record:
            assert list(row["loose_patterns_on_reached_stage"]) == record["C4 after one round"], i
            row["recorded loose patterns on stage"] = record["C4 after one round"]
        row["tree-shaped"] = record["tree-shaped"]
        rows[i] = row

    t7 = read_start(SEVEN_KNOT_START, compare_engine=True, expansion=False)
    fed_t7 = read_start(FUNDED_SEVEN_KNOT_START, compare_engine=True, expansion=False)
    t7_record = json.loads((LAYER / "t7.json").read_text())
    assert t7["status"] == t7_record["N5 T7 round 1"]
    assert t7["old_states"] == t7_record["N1 states"]
    assert fed_t7["status"] == t7_record["N5 its round 1"]
    assert fed_t7["old_states"] == t7_record["N5 T7 with 15, 16, 17: states"]
    assert fed_t7["stage_knots"] == t7_record["N5 stage after one round: knots"]
    assert list(fed_t7["loose_patterns_on_reached_stage"]) == t7_record["N5 loose patterns after one round"]

    two_knots = read_start(((0, 1, 2), (2, 3, 4)), compare_engine=True)
    assert two_knots["status"] == "funded" and len(two_knots["fiber_size_counts"]) == 1
    assert all(len(birth["parents"]) == 1 for birth in two_knots["births"])

    tree_rows = [rows[i] for i in tree_ids if i in rows]
    funded = [row for row in tree_rows if row["status"] == "funded"]
    assert all(
        max(len(birth["parents"]) for birth in row["births"]) == 2
        and len(row["fiber_size_counts"]) >= 2
        for row in funded
    )
    summary = {
        "archived census tree-shape labels matched": len(starts),
        "tree-shaped census records": len(tree_ids),
        "tree-shaped starts replayed": len(tree_rows),
        "tree-shaped starts funded": len(funded),
        "tree-shaped starts stalled": sum(row["status"] == "stalled" for row in tree_rows),
        "funded tree-shaped old fibers checked": sum(row["literal_fibers_checked"] for row in funded),
        "funded tree-shaped sign moments matching local expansion": sum(row["moments_matching_local_expansion"] for row in funded),
        "funded tree-shaped nonempty even moments checked": sum(row["nonempty_even_moments_checked"] for row in funded),
        "funded tree-shaped nonzero nonempty even moments checked": sum(row["nonzero_nonempty_even_moments_checked"] for row in funded),
        "two-parent births on funded tree-shaped starts": sum(len(birth["parents"]) == 2 for row in funded for birth in row["births"]),
        "offshoots on funded tree-shaped starts": sum(len(birth["parents"]) == 1 for row in funded for birth in row["births"]),
        "funded tree-shaped uniform stage states": sum(row["uniform_stage_states"] for row in funded),
        "pairs on funded tree-shaped starts": sum(row["pairs"] for row in funded),
        "pairs unchanged from equal on funded tree-shaped starts": sum(len(row["pairs_unchanged_from_equal_on_start"]) for row in funded),
        "archived census loose-stage counts matched": sum("recorded loose patterns on stage" in row for row in rows.values()),
        "shared engine comparisons matched": len(rows) + 3,
    }
    if not pilot:
        recorded = json.loads((TARGET / "weights.json").read_text())["completions"]["W1"]
        assert summary["pairs on funded tree-shaped starts"] == recorded["pairs"]
        assert summary["pairs unchanged from equal on funded tree-shaped starts"] == recorded["equal to the route product"]
        assert summary["tree-shaped starts stalled"] == recorded["not grown"]

    return {
        "summary": summary,
        "case selection": {
            "tree-shaped starts": tree_ids,
            "other archived starts": (
                "Pilot uses one start with a ring and one closed start." if pilot else
                "Every fiftieth non-tree-shaped census start with a C4 record, in archive order, and the first closed census start."
            ),
            "pilot": pilot,
        },
        "census cases": rows,
        "recorded seven-knot controls": {
            "three middle knots short of loose distinctions": t7,
            "one extra loose distinction on each of the three middle knots": fed_t7,
        },
        "touching pair with only offshoots": two_knots,
        "three-knot chain controls": chain_controls(starts[0]),
        "exact explanations": {
            "projection": "At any finite reached stage each old state's mass under projected equal weighting is its number of extensions divided by the total stage count.",
            "one-round product": "Each fresh distinction appears in only one birth. For p old inputs and f fresh distinctions a birth has 2^f completions minus one if all its inputs agree. Multiply over the births.",
            "positive factors": "Equivalently every factor is (2^f - 1) plus the indicator that its inputs are not all equal. An offshoot has a constant factor.",
            "signed factors": "For a birth of a = p + f places, the local factor after forgetting its fresh distinctions is proportional to the constant 2^(a-1)-1 minus the sum of all nonempty even sign products on its old inputs. The same expansion with p = a applies to original knots.",
            "conditional test": "Given all values of the middle knot of the three-knot chain, any product of factors confined to old knots separates the paid distinctions of the two outer knots. The projected stage has a conditional odds ratio 9/16 there. Deleting only the two-parent birth law restores ratio 1.",
            "availability": "The replay marks stalled and closed starts separately. Their literal count is an identity-stage control. The stipulated completion analysis omits them.",
        },
        "prior work": {
            "search": "scripts/track.py objects 'one round not-all-equal growth equal stage weighting completion count old projection marginal product of births local factors' --until 2026-11-27 --exclude NAE-WEIGHTS-20261127-001",
            "records": [
                "research/TWO-COUNTINGS-20261125-001A/results.md, lines 26–29: counting from the finish is a choice of weighting.",
                "research/UNREAD-COMPANION-AND-ORDER-FREE-WEIGHTING-20261121-001B/results.md, lines 16–18: unequal first-round extension fibers under not-all-equal and unchanged old marks on sources with only offshoots.",
                "research/SIGNED-COUNT-20261126-001/README.md, the one-extra-distinction mixture: one positive factor for a single edited knot.",
            ],
        },
        "shared comparator": "The shared growth engine was imported only to compare statuses, exact births, and reached supports after the independent reconstruction. The author's reading and analysis modules were not imported.",
        "not run": "Later rounds and literal growth outside the listed cases were not run. The local sign expansion was not enumerated on the two seven-knot controls.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = run(args.pilot)
    if args.output is not None:
        args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps(result["summary"], indent=2))


if __name__ == "__main__":
    main()
