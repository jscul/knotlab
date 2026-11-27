"""Equal-weighting checks for even sign products on finite ring-free starts.

From the repository root, run with --pilot first and then with no arguments.
The pilot uses the full reader on one seven-knot start. All imports are from the standard library.
"""

import argparse
import itertools
import json
import math
import resource
import time
from collections import Counter, defaultdict
from fractions import Fraction
from pathlib import Path


MEMORY_CAP = 1_500_000_000
MAX_KNOTS = 7


def mask_of(places):
    return sum(1 << place for place in places)


def pattern_key(meetings):
    """A rooted tree is its unordered list of rooted subtrees. Try every root."""
    def encode(knot, previous):
        parts = (encode(other, knot) for other in meetings[knot] if other != previous)
        return "(" + "".join(sorted(parts)) + ")"

    return min(encode(knot, None) for knot in range(len(meetings)))


def ternary_patterns():
    """Append an end knot at every available place, identifying relabellings."""
    layers = [[((),)]]
    for size in range(1, MAX_KNOTS):
        following = {}
        for meetings in layers[-1]:
            for knot, others in enumerate(meetings):
                if len(others) == 3:
                    continue
                extended = list(meetings) + [(knot,)]
                extended[knot] = others + (size,)
                extended = tuple(extended)
                following.setdefault(pattern_key(extended), extended)
        layers.append([following[key] for key in sorted(following)])
    return layers


def name_distinctions(meetings):
    knots = [[] for _ in meetings]
    name = 0
    for knot, others in enumerate(meetings):
        for other in others:
            if knot < other:
                knots[knot].append(name)
                knots[other].append(name)
                name += 1
    for knot in knots:
        while len(knot) < 3:
            knot.append(name)
            name += 1
    return knots


def who_holds(knots):
    holders = defaultdict(list)
    for index, knot in enumerate(knots):
        for place in knot:
            holders[place].append(index)
    assert sorted(holders) == list(range(len(holders)))
    assert all(1 <= len(group) <= 2 for group in holders.values())
    return holders


def relation(knots):
    places = len(who_holds(knots))
    masks = [mask_of(knot) for knot in knots]
    return [int(all((state & mask) not in (0, mask) for mask in masks))
            for state in range(1 << places)]


def signed_sums(indicator):
    """Each entry becomes the count with even parity less the count with odd parity."""
    sums = indicator.copy()
    width = 1
    while width < len(sums):
        for base in range(0, len(sums), 2 * width):
            for first in range(base, base + width):
                second = first + width
                a, b = sums[first], sums[second]
                sums[first], sums[second] = a + b, a - b
        width *= 2
    return sums


def branch_masks(knots, holders):
    """For each place of a removed knot, which distinctions remain with it?"""
    result = []
    for removed, knot in enumerate(knots):
        branches = []
        for origin in knot:
            reached = {origin}
            seen_knots = {removed}
            pending = [origin]
            while pending:
                place = pending.pop()
                for other in holders[place]:
                    if other not in seen_knots:
                        seen_knots.add(other)
                        fresh = set(knots[other]) - reached
                        reached.update(fresh)
                        pending.extend(fresh)
            branches.append(mask_of(reached))
        assert sum(branches) == (1 << len(holders)) - 1
        assert all(a & b == 0 for a, b in itertools.combinations(branches, 2))
        result.append(branches)
    return result


def counts_and_routes(knots, holders):
    sums = signed_sums(relation(knots))
    branches = branch_masks(knots, holders)
    denominators = [math.prod((1 << (len(knot) - 1)) - 1
                              for i, knot in enumerate(knots) if selected & (1 << i))
                    for selected in range(1 << len(knots))]
    used = [0] * len(sums)
    for support, count in enumerate(sums):
        if support.bit_count() % 2:
            assert count == 0
            continue
        selected = mask_of(k for k, parts in enumerate(branches)
                           if any((support & part).bit_count() % 2 for part in parts))
        used[support] = selected
        assert count * denominators[selected] == (-1) ** selected.bit_count() * sums[0]
    return sums, used


def is_connected(group, meetings):
    first = (group & -group).bit_length() - 1
    reached = {first}
    pending = [first]
    while pending:
        for other in meetings[pending.pop()]:
            if group & (1 << other) and other not in reached:
                reached.add(other)
                pending.append(other)
    return len(reached) == group.bit_count()


def nonempty_even_parts(mask):
    part = mask
    while part:
        if part.bit_count() % 2 == 0:
            yield part
        part = (part - 1) & mask


def audit_pattern(meetings):
    knots = name_distinctions(meetings)
    holders = who_holds(knots)
    sums, used = counts_and_routes(knots, holders)
    held_by = [mask_of(holders[d]) for d in range(len(holders))]
    sides = []
    for group in range(1, 1 << len(knots)):
        all_held = mask_of(d for d, h in enumerate(held_by) if h & group)
        exclusive = mask_of(d for d, h in enumerate(held_by) if h & group == h)
        supports = [(s, used[s], s.bit_count() == 2) for s in nonempty_even_parts(exclusive)]
        sides.append((group, all_held, supports, is_connected(group, meetings)))
    counts = Counter()
    for left, right in itertools.combinations(sides, 2):
        lgroup, lheld, lproducts, lconnected = left
        rgroup, rheld, rproducts, rconnected = right
        if lgroup & rgroup or lheld & rheld:
            continue
        counts["disjoint knot-set pairs with no shared distinction"] += 1
        if not (lproducts and rproducts):
            continue
        counts["knot-set pairs admitting two nonconstant even products"] += 1
        vulnerable = False
        for a, route_a, a_pair in lproducts:
            for b, route_b, b_pair in rproducts:
                dependent = sums[a ^ b] * sums[0] != sums[a] * sums[b]
                assert dependent == bool(route_a & route_b)
                vulnerable |= dependent
                counts["all nonconstant even-product pairs"] += 1
                counts["all dependent even-product pairs"] += dependent
                if a_pair and b_pair:
                    counts["two-place product pairs"] += 1
                    counts["dependent two-place product pairs"] += dependent
                if lconnected and rconnected:
                    counts["even-product pairs on two connected knot sets"] += 1
                    assert not dependent
        counts["knot-set pairs admitting dependent even products"] += vulnerable
    return {
        "shared distinctions by their two holders": [
            [k, other] for k, others in enumerate(meetings) for other in others if k < other
        ],
        "allowed states": sums[0],
        "even sign products compared with the local factors, including the empty product": len(sums) // 2,
        "counts": counts,
    }


def six_knot_chain(wider=False):
    knots = [[2 * i, 2 * i + 1, 2 * i + 2] for i in range(6)]
    if wider:
        knots[2].append(13)
    return knots


def witness():
    knots = six_knot_chain()
    sides = [[0, 5], [2, 3]]
    products = [[0, 12], [5, 7]]
    holders = who_holds(knots)
    side_places = [{d for k in side for d in knots[k]} for side in sides]
    assert side_places[0].isdisjoint(side_places[1])
    for side, support in zip(sides, products):
        assert all(len(holders[d]) == 1 and holders[d][0] in side for d in support)
    masks = [mask_of(support) for support in products]
    branches = branch_masks(knots, holders)
    used = [[k for k, parts in enumerate(branches) if any((mask & part).bit_count() % 2 for part in parts)]
            for mask in masks]
    table = [[0, 0], [0, 0]]
    for state, allowed in enumerate(relation(knots)):
        if allowed:
            a, b = ((state & mask).bit_count() % 2 for mask in masks)
            table[a][b] += 1
    pp, pm = table[0]
    mp, mm = table[1]
    total = pp + pm + mp + mm
    a = Fraction(pp + pm - mp - mm, total)
    b = Fraction(pp - pm + mp - mm, total)
    ab = Fraction(pp - pm - mp + mm, total)
    assert ab != a * b
    return {
        "knots, in order from zero": knots, "knot sets": sides,
        "two loose distinctions used on each side": products,
        "knots used by the two routes": used,
        "allowed states counted individually": total,
        "counts, rows and columns each ordered plus then minus": table,
        "means of the two products": [str(a), str(b)], "mean of their product": str(ab),
        "product of means": str(a * b), "covariance": str(ab - a * b),
        "table determinant": pp * mm - pm * mp,
    }


def shared_distinction_check(knots):
    """Read both complete sides up to reversal, separately for each shared sign."""
    left = {d for knot in knots[:3] for d in knot}
    right = {d for knot in knots[3:] for d in knot}
    (shared,) = left & right
    left_mask, right_mask = mask_of(left), mask_of(right)
    tables = [Counter(), Counter()]
    for state, allowed in enumerate(relation(knots)):
        if allowed:
            sign = (state >> shared) & 1
            relative = ~state if sign else state
            tables[sign][relative & left_mask, relative & right_mask] += 1
    assert tables[0] == tables[1]
    first = tables[0]
    left_count, right_count = (len({key[i] for key in first}) for i in range(2))
    assert len(first) == left_count * right_count
    assert set(first.values()) == {1}
    return {
        "knots by number of places": list(map(len, knots)),
        "shared distinction": shared,
        "allowed states": sum(sum(table.values()) for table in tables),
        "allowed patterns up to reversal on each side": [left_count, right_count],
        "joint patterns given either value of the shared distinction": len(first),
        "least and greatest counts per joint pattern given either value": [1, 1],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot", action="store_true")
    args = parser.parse_args()
    soft, hard = resource.getrlimit(resource.RLIMIT_AS)
    limit = min([MEMORY_CAP] + [bound for bound in (soft, hard) if bound != resource.RLIM_INFINITY])
    resource.setrlimit(resource.RLIMIT_AS, (limit, hard))
    started = time.perf_counter()
    layers = ternary_patterns()
    pilot_tree = next(tree for tree in layers[-1] if max(map(len, tree)) == 2)
    before_pattern = time.perf_counter()
    pilot = audit_pattern(pilot_tree)
    pattern_seconds = time.perf_counter() - before_pattern
    before_control = time.perf_counter()
    separator = shared_distinction_check(six_knot_chain(True))
    control_seconds = time.perf_counter() - before_control
    pattern_count = sum(map(len, layers))
    pilot_record = {
        "single process, address-space cap in bytes": limit,
        "largest-size chain, seconds": round(pattern_seconds, 5),
        "four-place separator control, seconds": round(control_seconds, 5),
        "estimated seconds for full run, twice the pilot per pattern plus controls":
            round(2 * pattern_count * pattern_seconds + 4 * control_seconds, 3),
    }
    if args.pilot:
        print(json.dumps({"pilot": pilot_record, "seven-knot chain": pilot,
                          "separator control": separator}, indent=2))
        return
    by_size = []
    for size, layer in enumerate(layers, 1):
        patterns = [pilot if tree == pilot_tree else audit_pattern(tree) for tree in layer]
        totals = Counter()
        for sample in patterns:
            totals.update(sample["counts"])
        by_size.append({"knots": size, "meeting patterns": len(patterns), "totals": totals,
                        "patterns": patterns})
    first_failure = next(row["knots"] for row in by_size
                         if row["totals"]["all dependent even-product pairs"])
    result = {
        "weighting": "Every allowed state of the given start is counted once.",
        "candidate rule": (
            "Two nonempty unordered sets of knots whose full sets of distinctions are disjoint. "
            "Each product uses a nonempty even set of distinctions all of whose holders belong "
            "to its own set. The same product can occur for more than one choice of knot sets."
        ),
        "coverage": (
            "Every connected ring-free meeting pattern of one through seven three-place knots, "
            "at most two holders per distinction, up to relabelling. Removing an end knot "
            "from a pattern with at least two knots undoes one step of the generation. "
            "The canonical rooted encodings identify exactly the relabellings. "
            "For each candidate we compared integer sign sums from all states and the common-knot "
            "test in the argument below."
        ),
        "argument for all finite connected ring-free starts with one or two holders and at least three places per knot": [
            "Choose the sign at one distinction and an allowed pattern up to simultaneous reversal "
            "at each knot. The unique routes determine one global allowed state from these choices. "
            "Every global allowed state gives one such choice. Under the equal weighting all these "
            "choices are independent and uniform.",
            "For an even number of marked distinctions, remove each knot in turn. Select its "
            "places whose remaining components contain an odd number of marks. The local set "
            "has even size. The product of these local sign products is the marked product. "
            "A loose distinction occurs as many times modulo two as it is marked. For a shared "
            "distinction the two component counts add to the total marks plus its marked "
            "indicator, so the same holds.",
            "A local product over a nonempty even set on a knot of a places has mean -1/D, "
            "where D = 2^(a-1) - 1. Its sum over all patterns is zero and each excluded constant "
            "pattern contributes one. The mean of the global product therefore multiplies -1/D "
            "over exactly the knots with a nonempty selected local set.",
            "Multiplying two even sign products gives the product on the symmetric difference "
            "of their supports. At a knot used by both, the absolute ratio of the joint mean to the "
            "product of the means gains D squared when the two local sets agree and D when "
            "they differ. At every other knot the ratio gains one. Since D is at least three, "
            "the two sign products are independent exactly when their used knot sets are disjoint. "
            "For sign-valued readings equality of the joint mean and the product of means "
            "decides independence.",
            "Every pair of functions on two sets of distinctions that are each unchanged by "
            "simultaneous reversal is independent exactly when the within-set routes between "
            "pairs of distinctions have no knot in common across the two sets. Indeed, every "
            "knot used by an even sign product lies on a route between two of its marks. "
            "Every invariant event indicator is a linear combination of even sign products. "
            "Conversely, two within-set routes with a common knot supply dependent pair products. "
            "The necessity applies to the family of all such functions. Two chosen functions can "
            "remain independent even when their families are dependent.",
            "Conditioning on a single shared distinction that separates the readings makes "
            "the two sides independent. An invariant reading has the same distribution for "
            "either conditioning sign by simultaneous reversal. Such a reading is consequently "
            "independent of any reading wholly on the other side. More generally, arbitrary "
            "readings of local patterns up to reversal on disjoint sets of knots are independent "
            "by the first step. A product with marks on disconnected parts of a chosen set "
            "can use knots outside that set."
        ],
        "least number of three-place knots with a dependent eligible pair": first_failure,
        "all sizes": by_size,
        "six-knot counterexample with four loose distinctions": witness(),
        "two connected parts sharing one distinction": [
            shared_distinction_check(six_knot_chain()), separator,
        ],
        "not run": "Larger meeting patterns, other weightings and growth are outside this check.",
        "pilot": pilot_record,
        "wall seconds including repeated pilot and all checks": round(time.perf_counter() - started, 5),
        "maximum resident memory in KiB": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
    }
    path = Path(__file__).with_suffix(".json")
    path.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"output": str(path), "minimum": first_failure,
                      "sizes": [{k: v for k, v in row.items() if k != "patterns"} for row in by_size],
                      "wall seconds": result["wall seconds including repeated pilot and all checks"]}, indent=2))


if __name__ == "__main__":
    main()
