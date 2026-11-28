"""Rebuild the named commuting choices and check all attachments at their fourfold cross pairs."""

from collections import Counter, defaultdict
from itertools import combinations, permutations, product
import json
from pathlib import Path
from random import Random
import sys


HERE = Path(__file__).resolve().parent
RESEARCH = HERE.parents[1]
ROOT = RESEARCH.parent
EARLIER = RESEARCH / "ENCODED-READERS-20261127-001/referee-R1"
BIRTH_INPUTS = RESEARCH / "READER-SPLIT-20261127-001/referee-R1/rebuilt_inputs.jsonl"
ENGINE = RESEARCH / "FORBID-EDITS-20261126-001"
CENSUS = ROOT / "artifacts/FOUR-READINGS-20261120-001A/FOUR-READINGS-20261120-001A-E001_signed_rules/census.json"
INDEX_EXHAUSTIVE_THROUGH = 7
ORDER_BITS_EXHAUSTIVE_THROUGH = 15
SETTING_BITS_EXHAUSTIVE_THROUGH = 10
SAMPLE = 64


class Classes:
    def __init__(self, labels):
        self.parents = {label: label for label in labels}

    def find(self, label):
        while self.parents[label] != label:
            parent = self.parents[label]
            self.parents[label] = self.parents[parent]
            label = self.parents[label]
        return label

    def join(self, left, right):
        left, right = sorted((self.find(left), self.find(right)))
        self.parents[right] = left


def unordered(left, right):
    return (left, right) if left < right else (right, left)


def as_terms(cycles):
    return [(unordered(a, c), unordered(b, d)) for a, b, c, d in cycles]


def canonical_terms(terms):
    return sorted(tuple(sorted((tuple(sorted(left)), tuple(sorted(right))))) for left, right in terms)


def ring_terms(size):
    mid = size // 2
    return [((j, size), ((j + mid) % size, (j - mid) % size)) for j in range(size)]


def unit_cycles(width, height):
    return [((x, y), (x + 1, y), (x + 1, y + 1), (x, y + 1))
            for x, y in product(range(width), range(height))]


def periodic_fixture(width, height, reflected=False):
    cycles = unit_cycles(width, height)
    quotient = Classes(product(range(width + 1), range(height + 1)))
    for y in range(height + 1):
        quotient.join((0, y), (width, y))
    for x in range(width + 1):
        quotient.join((x, height), ((-x) % width if reflected else x, 0))
    return [tuple(quotient.find(knot) for knot in cycle) for cycle in cycles]


def antipodal_grid(size):
    def boundary_representative(knot):
        return min(knot, tuple(size - x for x in knot)) if 0 in knot or size in knot else knot

    return [tuple(map(boundary_representative, cycle)) for cycle in unit_cycles(size, size)]


def cube_cycles(size, modulo_antipode=False):
    cycles = []
    for constant_axis, side in product(range(3), (0, size)):
        for cycle in unit_cycles(size, size):
            lifted = tuple(
                free[:constant_axis] + (side,) + free[constant_axis:] for free in cycle
            )
            antipodes = tuple(tuple(size - x for x in knot) for knot in lifted)
            if modulo_antipode and sorted(lifted) > sorted(antipodes):
                continue
            if modulo_antipode:
                lifted = tuple(min(knot, opposite) for knot, opposite in zip(lifted, antipodes))
            cycles.append(lifted)
    return cycles


def binary_basis(columns):
    pivots = {}
    for column in columns:
        while column:
            lead = column.bit_length() - 1
            if lead not in pivots:
                pivots[lead] = column
                break
            column ^= pivots[lead]
    return pivots


def walk_data(cycles):
    incidences = defaultdict(list)
    for index, walk in enumerate(cycles):
        for step, left in enumerate(walk):
            right = walk[(step + 1) % 4]
            incidences[unordered(left, right)].append((index, step, left < right))
    return incidences


def setting_bits(terms, knots):
    x = dict.fromkeys(knots, 0)
    z = x.copy()
    for index, (left, right) in enumerate(terms):
        for knot in left:
            x[knot] |= 1 << index
        for knot in right:
            z[knot] |= 1 << index
    return x, z


def phase_exponent(x, z, order, swap=0):
    sign = 0
    queued_z = 0
    for knot in order:
        swap_here = (x[knot] ^ z[knot]) & swap
        sign ^= (queued_z & (x[knot] ^ swap_here)).bit_count() & 1
        queued_z ^= z[knot] ^ swap_here
    assert not queued_z
    return sign


def interleaving(terms, rank):
    count = 0
    for left, right in terms:
        lower, upper = sorted(rank[knot] for knot in left)
        count += sum(lower < rank[knot] < upper for knot in right) == 1
    return count % 2


def order_parities(incidences, reversals, references):
    forward = 0
    same = 0
    for pair_index, visits in enumerate(incidences.values()):
        baseline = 1 ^ ((references >> pair_index) & 1)
        agreeing = sum((direction ^ ((reversals >> index) & 1)) == baseline
                       for index, _, direction in visits)
        forward += agreeing
        same += len(visits) == 2 and agreeing in (0, 2)
    return forward % 2, same % 2


def order_checks(terms, incidences, knots, sign, rng):
    x, z = setting_bits(terms, knots)
    ordered = tuple(sorted(knots))
    if len(knots) <= INDEX_EXHAUSTIVE_THROUGH:
        orders = permutations(ordered)
        index_method = "all"
    else:
        orders = [ordered, ordered[::-1]] + [rng.sample(ordered, len(knots)) for _ in range(SAMPLE)]
        index_method = "fixed and seeded"

    index_count = 0
    for order in orders:
        rank = {knot: i for i, knot in enumerate(order)}
        swap = rng.getrandbits(len(terms))
        assert interleaving(terms, rank) == sign == phase_exponent(x, z, order, swap)
        index_count += 1

    if len(terms) <= SETTING_BITS_EXHAUSTIVE_THROUGH:
        swaps = range(1 << len(terms))
        setting_method = "all"
    else:
        swaps = [0, (1 << len(terms)) - 1] + [rng.getrandbits(len(terms)) for _ in range(SAMPLE)]
        setting_method = "fixed and seeded"
    for swap in swaps:
        assert phase_exponent(x, z, ordered, swap) == sign

    bits = len(terms) + len(incidences)
    if bits <= ORDER_BITS_EXHAUSTIVE_THROUGH:
        settings = product(range(1 << len(terms)), range(1 << len(incidences)))
        order_method = "all"
    else:
        all_cycle_bits = (1 << len(terms)) - 1
        all_pair_bits = (1 << len(incidences)) - 1
        settings = list(product((0, all_cycle_bits), (0, all_pair_bits)))
        settings.extend((rng.getrandbits(len(terms)), rng.getrandbits(len(incidences))) for _ in range(SAMPLE))
        order_method = "fixed and seeded"
    double = all(len(visits) == 2 for visits in incidences.values())
    order_count = 0
    for reversals, references in settings:
        same_order_input, same_order_pairs = order_parities(incidences, reversals, references)
        assert same_order_input == sign
        assert not double or same_order_pairs == sign
        order_count += 1
    return {
        "knot index orders": [index_method, index_count],
        "X and Z swaps in index order": [setting_method, len(swaps)],
        "cycle and reference order settings": [order_method, order_count],
    }


def parity_balance(visit_lists):
    equations = []
    for visits in visit_lists:
        rhs = (sum(direction for _, _, direction in visits) - len(visits) // 2) % 2
        mask = sum(1 << (index + 1) for index, _, _ in visits)
        equations.append(mask | rhs)
    return 0 not in binary_basis(equations)


def exact_balance(incidences, cycle_count):
    if all(len(visits) == 2 for visits in incidences.values()):
        return parity_balance(incidences.values())
    assert cycle_count <= 12
    return any(
        all(sum(direction ^ ((mask >> index) & 1) for index, _, direction in visits) * 2 == len(visits)
            for visits in incidences.values())
        for mask in range(1 << cycle_count)
    )


def two_colourable(pairs):
    neighbours = defaultdict(set)
    for left, right in pairs:
        neighbours[left].add(right)
        neighbours[right].add(left)
    colours = {}
    for knot in neighbours:
        if knot in colours:
            continue
        colours[knot] = 0
        todo = [knot]
        while todo:
            current = todo.pop()
            colour = 1 - colours[current]
            for other in neighbours[current]:
                if other not in colours:
                    colours[other] = colour
                    todo.append(other)
                elif colours[other] != colour:
                    return False
    return True


def pairings(visits):
    if len(visits) == 2:
        return [((visits[0], visits[1]),)]
    assert len(visits) == 4
    return [((visits[0], other), tuple(visit for visit in visits[1:] if visit != other))
            for other in visits[1:]]


def paired_reading(cycles, attached):
    cycle_parts = Classes(range(len(cycles)))
    occurrences = Classes(range(4 * len(cycles)))
    matched = []
    for first, other in attached:
        fi, fj, forward = first
        oi, oj, other_forward = other
        cycle_parts.join(fi, oi)
        f_corners = [4 * fi + fj, 4 * fi + (fj + 1) % 4]
        o_corners = [4 * oi + oj, 4 * oi + (oj + 1) % 4]
        if forward != other_forward:
            o_corners.reverse()
        for index, (f, o) in enumerate(zip(f_corners, o_corners)):
            assert cycles[f // 4][f % 4] == cycles[o // 4][o % 4]
            occurrences.join(f, o)
        matched.append(f_corners)
    separated = [tuple(occurrences.find(4 * i + p) for p in range(4)) for i in range(len(cycles))]
    separated_pairs = [unordered(occurrences.find(a), occurrences.find(b)) for a, b in matched]
    sizes = defaultdict(Counter)
    for i, cycle in enumerate(cycles):
        for p, knot in enumerate(cycle):
            sizes[knot][separated[i][p]] += 1
    knots_after = sum(map(len, sizes.values()))
    sign_after = interleaving(as_terms(separated), {knot: knot for cycle in separated for knot in cycle})
    return {
        "knots": knots_after,
        "cross pair copies": len(separated_pairs),
        "distinct pairs after separation": len(set(separated_pairs)),
        "Euler count": knots_after - len(separated_pairs) + len(cycles),
        "pinched knots": sum(len(parts) > 1 for parts in sizes.values()),
        "extra knots on separation": knots_after - len(sizes),
        "link cycle lengths at pinched knots": [
            [knot, sorted(parts.values())] for knot, parts in sorted(sizes.items()) if len(parts) > 1
        ],
        "two-colourable": two_colourable(separated_pairs),
        "orientable": parity_balance(attached),
        "components through attached cross pairs": len({cycle_parts.find(i) for i in range(len(cycles))}),
        "sign": sign_after,
    }


def commutation_columns(terms, incidences):
    codes = {pair: 1 << j for j, pair in enumerate(incidences)}
    return [sum(codes[unordered(a, b)] for a, b in product(left, right)) for left, right in terms]


def small_nullity_check(columns, nullity):
    if len(columns) > 12:
        return None
    cumulative = 0
    proper_commuting = 0
    for word in range(1, 1 << len(columns)):
        cumulative ^= columns[(word & -word).bit_length() - 1]
        proper_commuting += cumulative == 0
    proper_commuting -= 1  # The full choice commutes and occurs once in the enumeration.
    assert proper_commuting == (1 << nullity) - 2
    return proper_commuting


def count_merges(terms):
    settings_per_knot = Counter(knot for term in terms for holders in term for knot in holders)
    opponents = defaultdict(list)
    for index, (left, right) in enumerate(terms):
        opponents[right].append((index, left))
        opponents[left].append((index, right))
    ordinary = forced = doubled = 0
    for choices in opponents.values():
        for (left_index, left), (right_index, right) in combinations(choices, 2):
            if left_index == right_index:
                continue
            if left == right:
                doubled += 1
                continue
            for knot in set(left) & set(right):
                ordinary += 1
                forced += settings_per_knot[knot] == 2
    return {"ordinary": ordinary, "forced": forced, "doubled pair deletions": doubled // 2}


def analyze(raw_terms, rng):
    terms = canonical_terms(raw_terms)
    cycles = [(a, c, b, d) for (a, b), (c, d) in terms]
    incidences = walk_data(cycles)
    knots = set(knot for cycle in cycles for knot in cycle)
    assert all(len(set(cycle)) == 4 for cycle in cycles)
    covers = Counter(map(len, incidences.values()))
    assert all(count % 2 == 0 for count in covers)
    columns = commutation_columns(terms, incidences)
    xor = 0
    for column in columns:
        xor ^= column
    assert xor == 0

    index_order = {knot: j for j, knot in enumerate(sorted(knots))}
    sign = interleaving(terms, index_order)
    check_coverage = order_checks(terms, incidences, knots, sign, rng)
    nullity = len(columns) - len(binary_basis(columns))
    double = set(covers) == {2}
    result = {
        "pairs": len(terms),
        "knots": len(knots),
        "cross pairs": len(incidences),
        "coverage counts": covers,
        "four distinct knots in every cell": True,
        "exactly two": double,
        "most at a cross pair": max(covers),
        "Euler count": len(knots) - len(incidences) + len(cycles),
        "sign": sign,
        "order count": sign,
        "order count again": sign,
        "order and settings checks": check_coverage,
        "orientable": exact_balance(incidences, len(cycles)),
        "weak even condition": parity_balance(incidences.values()),
        "two-colourable": two_colourable(incidences),
        "one cycle at every knot": False,
        "minimal": nullity == 1,
        "commuting subcollections": 1 << nullity,
    }
    assert not sign or not any(result[key] for key in ("orientable", "weak even condition", "two-colourable"))
    proper_commuting = small_nullity_check(columns, nullity)
    if proper_commuting is not None:
        result["proper nonempty commuting subcollections enumerated"] = proper_commuting
    if double:
        reading = paired_reading(cycles, [visits for visits in incidences.values()])
        assert reading["distinct pairs after separation"] == len(incidences)
        assert reading["sign"] == sign and reading["orientable"] == result["orientable"]
        result.update({
            "same-order parity": order_parities(incidences, 0, 0)[1],
            "one cycle at every knot": reading["pinched knots"] == 0,
            "pinched knots": reading["pinched knots"],
            "extra knots on separation": reading["extra knots on separation"],
            "separated Euler count": reading["Euler count"],
            "separated two-colourable": reading["two-colourable"],
            "separated sign": reading["sign"],
            "separated components through cross pairs": reading["components through attached cross pairs"],
            "link cycle lengths at pinched knots": reading["link cycle lengths at pinched knots"],
        })
    return result


def attachment_control(raw_terms):
    terms = canonical_terms(raw_terms)
    cycles = [(a, c, b, d) for (a, b), (c, d) in terms]
    incidence = walk_data(cycles)
    signs = set()
    summary = Counter()
    first = {}
    variable = [j for j, visits in enumerate(incidence.values()) if len(visits) == 4]
    alternatives = []
    for attached_per_pair in product(*(pairings(visits) for visits in incidence.values())):
        attached = [pair for pairs in attached_per_pair for pair in pairs]
        reading = paired_reading(cycles, attached)
        setting = [
            [[list(first[:2]), list(other[:2])] for first, other in attached_per_pair[j]]
            for j in variable
        ]
        alternatives.append({"pairings in zero-based cycle and step indices": setting, **reading})
        signs.add(reading["sign"])
        metric_key = reading["Euler count"], reading["orientable"], reading["components through attached cross pairs"]
        summary[metric_key] += 1
        first.setdefault(metric_key, alternatives[-1])
    assert len(signs) == 1
    return {
        "cycles": cycles,
        "fourfold cross pairs": [list(incidence)[j] for j in variable],
        "attachments tested": len(alternatives),
        "all paired readings" if len(alternatives) <= 3 else "first reading for each result": (
            alternatives if len(alternatives) <= 3 else list(first.values())
        ),
        "counts by Euler count, orientability and components": [[*key, number] for key, number in sorted(summary.items())],
        "signs": sorted(signs),
    }


def source_terms(supports, marked):
    holders = defaultdict(list)
    for knot, support in enumerate(supports):
        for distinction in support:
            holders[distinction].append(knot)
    assert all(len(pair) == 2 for pair in holders.values())
    assert len({d for pair in marked for d in pair}) == 2 * len(marked)
    return canonical_terms((holders[left], holders[right]) for left, right in marked)


def replay_growth(indices):
    sys.path.insert(0, str(ENGINE))
    from forbid import grown, supports_of

    starts = json.loads((ENGINE / "starts.json").read_text())
    rows = {}
    for index in indices:
        current = supports_of(starts[index])
        birth = [0] * len(current)
        for generation in range(1, 5):
            grown_supports, status, _ = grown(current, "parity", "ordinary")
            assert status == "funded" and len(current) < len(grown_supports) <= 40
            assert grown_supports[:len(current)] == current
            birth += [generation] * (len(grown_supports) - len(current))
            current = grown_supports
            counts = Counter(d for support in current for d in support)
            if set(counts.values()) == {2}:
                rows[index] = (current, birth)
                break
        assert index in rows
    return rows


def eligible_pairs(supports, birth):
    holders = defaultdict(list)
    for knot, support in enumerate(supports):
        for distinction in support:
            holders[distinction].append(knot)
    choices = []
    for a, b in combinations(sorted(holders), 2):
        jointly = holders[a] + holders[b]
        if len(set(jointly)) != 4:
            continue
        first_a, last_a = sorted(birth[knot] for knot in holders[a])
        first_b, last_b = sorted(birth[knot] for knot in holders[b])
        if max(first_a, first_b) <= min(last_a, last_b):
            choices.append([a, b])
    return choices


def strict_commuting_words(supports, eligible):
    holders = defaultdict(list)
    for knot, support in enumerate(supports):
        for distinction in support:
            holders[distinction].append(knot)
    pair_ids = {pair: 1 << (j + 1) for j, pair in enumerate(combinations(range(len(supports)), 2))}
    row = defaultdict(list)
    for index, (first, second) in enumerate(eligible):
        (a, b), (c, d) = holders[first], holders[second]
        sign = ((a < c < b) != (a < d < b))
        column = sum(pair_ids[unordered(left, right)] for left, right in product((a, b), (c, d))) | sign
        row[first].append((second, index, column))
    words_by_sign = {0: [], 1: []}

    def visit(remaining, total, word):
        if not remaining:
            if total in (0, 1) and word:
                words_by_sign[total].append(tuple(sorted(word)))
            return
        first, *rest = remaining
        visit(rest, total, word)
        for other, index, column in row[first]:
            if other in rest:
                visit([d for d in rest if d != other], total ^ column, (*word, index))

    visit(sorted(holders), 0, ())
    return words_by_sign


def grown_attachment_control():
    # Select the first recorded closure with a fourfold minimal strict even choice.
    with (HERE.parent / "results.jsonl").open() as stream:
        for line in stream:
            recorded = json.loads(line)
            tally = recorded["tallies"].get("minimal strict even", {})
            if tally.get("most at a cross pair", {}).get("4"):
                start = recorded["start"]
                break
        else:
            raise AssertionError("missing a recorded fourfold minimal strict even choice")
    supports, births = replay_growth([start])[start]
    eligible = eligible_pairs(supports, births)
    words = strict_commuting_words(supports, eligible)
    results = []
    for word in words[0]:
        marked = [eligible[index] for index in word]
        terms = source_terms(supports, marked)
        cycles = [(a, c, b, d) for (a, b), (c, d) in terms]
        visits = walk_data(cycles)
        if max(map(len, visits.values())) != 4:
            continue
        columns = commutation_columns(terms, visits)
        if len(binary_basis(columns)) != len(word) - 1:
            continue
        original_orientability = exact_balance(visits, len(cycles))
        attached = attachment_control(terms)
        assert attached["signs"] == [0]
        assert original_orientability == any(
            row[1] for row in attached["counts by Euler count, orientability and components"]
        )
        results.append({"distinction pairs": marked, "holder lists": terms,
                        "original exact balance": original_orientability, "attachments": attached})
    assert len(results) == tally["most at a cross pair"]["4"]
    return {"zero-based census start index": start, "birth round": max(births),
            "every fourfold minimal strict even choice at this closure": results}


def named_sources():
    cells = json.loads((EARLIER / "cells.json").read_text())
    earlier_shapes = json.loads((EARLIER / "shapes.json").read_text())
    ten_pair = json.loads((EARLIER / "shapes_size_stress.json").read_text())["classes"][0]
    prior_fixtures = json.loads((EARLIER / "merge_fixtures.json").read_text())
    witness = cells["coverage_of_all_listed_words"]["first_fewest_word_with_some_coverage_above_two"]
    base_names = ("grown six-pair game", "census six-pair game", "census eight-pair game")
    archive_inputs = {}
    archived_modes = {("birth", witness["id"])}
    for entry in earlier_shapes["classes"]:
        original = entry["one_original_witness"]
        pop = "birth" if original["population"] == "closure" else "type"
        archived_modes.add((pop, original["id"]))
    with BIRTH_INPUTS.open() as stream:
        for line in stream:
            row = json.loads(line)
            key = row["population"], row["key"]
            if key in archived_modes:
                archive_inputs[key] = row
    assert set(archive_inputs) == archived_modes
    grown_inputs = replay_growth([index for pop, index in sorted(archived_modes) if pop == "birth"])
    census = json.loads(CENSUS.read_text())

    cases = {}
    provenance = {}
    originals = [(name, entry["one_original_witness"]) for name, entry in zip(base_names, earlier_shapes["classes"])]
    originals.append(("start 4786 fourfold witness", witness))
    for name, original in originals:
        index = original["id"]
        pop = "birth" if original["population"] == "closure" else "type"
        archived = archive_inputs[pop, index]
        if pop == "birth":
            supports, births = grown_inputs[index]
        else:
            sharing = census[index]["sharing"]
            supports = [[d for d, pair in enumerate(sharing) if knot in pair] for knot in range(7)]
            births = [0] * len(supports)
        assert [list(support) for support in supports] == archived["supports"]
        eligible = eligible_pairs(supports, births)
        assert eligible == archived["pairs"]
        marked = [eligible[j] for j in original["word"]]
        cases[name] = source_terms(supports, marked)
        assert cases[name] == canonical_terms(original["holder_lists"])
        provenance[name] = {"source": "census start grown to closure" if pop == "birth" else "finished census type",
                            "zero-based index": index, "distinction pairs": marked, "birth round": max(births)}
    start_name = "start 4786 fourfold witness"
    supports, births = grown_inputs[witness["id"]]
    words = strict_commuting_words(supports, eligible_pairs(supports, births))[1]
    words_by_size = Counter(map(len, words))
    assert min(words_by_size) == len(cases[start_name]) and tuple(witness["word"]) in words
    provenance[start_name]["all strict odd choices by size at this closure"] = words_by_size

    for original in ten_pair["witnesses"]:
        index = original["id"]
        name = "census ten-pair game" if index == 171 else "ten-pair witness at finished census type 172"
        sharing = census[index]["sharing"]
        supports = [[d for d, pair in enumerate(sharing) if knot in pair] for knot in range(7)]
        marked = original["original_pairs"]
        eligible = eligible_pairs(supports, [0] * len(supports))
        assert all(pair in eligible for pair in marked)
        cases[name] = source_terms(supports, marked)
        assert cases[name] == canonical_terms(original["holder_lists"])
        provenance[name] = {"source": "finished census type", "zero-based index": index, "distinction pairs": marked}
    assert any(
        canonical_terms((tuple(order[k] for k in left), tuple(order[k] for k in right))
                        for left, right in cases["census ten-pair game"])
        == cases["ten-pair witness at finished census type 172"]
        for order in permutations(range(7))
    )
    cases["five-pair fourfold witness"] = prior_fixtures["operator_sectors"]["readers_X_then_Z"]
    cases["nine-knot choice"] = cells["other_controls"]["nine-knot design fixture"]["paired_holder_lists"]
    # Each pair from the first three knots gets one matching of the other four.
    remaining = {3, 4, 5, 6}
    matchings = [((3, other), tuple(sorted(remaining - {3, other}))) for other in (4, 5, 6)]
    cases["even seven-knot control"] = [
        (left, right) for left, matching in zip(combinations(range(3), 2), matchings) for right in matching
    ]
    assert canonical_terms(cases["even seven-knot control"]) == canonical_terms(
        cells["other_controls"]["even seven-knot replacement"]["paired_holder_lists"]
    )
    provenance["five-pair fourfold witness"] = {
        "source": "earlier exact signed-product control with two repetition-code sectors, merge_fixtures.json"
    }
    provenance["nine-knot choice"] = {"source": "earlier design item 7, checked holder lists in cells.json"}
    provenance["even seven-knot control"] = {
        "source": "earlier explicit replacement control in cells.json, rebuilt from the three matchings of four knots"
    }
    return cases, provenance


def all_cases():
    cases, provenance = named_sources()
    cases["three-reader game"] = ring_terms(3)
    for size, label in ((5, "five"), (7, "seven"), (9, "nine")):
        cases[f"ring game of {label}"] = ring_terms(size)
    cases["cube"] = as_terms(cube_cycles(1))
    for n, m in product(range(3, 6), repeat=2):
        cases[f"torus grid {n}x{m}"] = as_terms(periodic_fixture(n, m))
        cases[f"Klein bottle grid {n}x{m}"] = as_terms(periodic_fixture(n, m, reflected=True))
    for size in (3, 4):
        cases[f"projective grid {size}x{size}"] = as_terms(antipodal_grid(size))
    for size in (1, 2, 3):
        cases[f"cube {size}x{size} mod antipodal"] = as_terms(cube_cycles(size, modulo_antipode=True))
    extensions = {
        "ring game of eleven": ring_terms(11),
        "torus grid 6x6": as_terms(periodic_fixture(6, 6)),
        "Klein bottle grid 6x6": as_terms(periodic_fixture(6, 6, reflected=True)),
        "Klein bottle grid 7x6": as_terms(periodic_fixture(7, 6, reflected=True)),
        "projective grid 5x5": as_terms(antipodal_grid(5)),
        "cube 4x4 mod antipodal": as_terms(cube_cycles(4, modulo_antipode=True)),
        "cube 5x5 mod antipodal": as_terms(cube_cycles(5, modulo_antipode=True)),
        "two-colourability restored by separating one pinched knot": as_terms([
            tuple((0, 0) if knot == (1, 2) else knot for knot in cycle)
            for cycle in periodic_fixture(4, 4)
        ]),
        "four copies of one cycle": [((0, 2), (1, 3))] * 4,
        "two disjoint copies of the three-reader game": [
            (tuple(knot + shift for knot in left), tuple(knot + shift for knot in right))
            for shift in (0, 4) for left, right in ring_terms(3)
        ],
    }
    extensions["ten-pair witness at finished census type 172"] = cases.pop(
        "ten-pair witness at finished census type 172"
    )
    return cases, extensions, provenance


def main():
    cases, extensions, sources = all_cases()
    rng = Random(92701)
    recorded = {name: analyze(terms, rng) for name, terms in cases.items()}
    beyond = {name: analyze(terms, rng) for name, terms in extensions.items()}
    for name, raw_terms in {**cases, **extensions}.items():
        if name in sources or name == "three-reader game" or name.startswith("ring game"):
            result = recorded.get(name, beyond.get(name))
            terms = canonical_terms(raw_terms)
            result["holder lists"] = terms
            result["possible merges"] = count_merges(terms)
            result["strict by distinct marked setting identities"] = True

    # Constructed countercontrol: a single unpaired cycle does not commute.
    lone_cycle = [(0, 1, 2, 3)]
    incidences = walk_data(lone_cycle)
    order_before, _ = order_parities(incidences, 0, 0)
    order_after, _ = order_parities(incidences, 0, 1)
    assert (order_before, order_after) == (1, 0)

    fourfold = {
        name: attachment_control(cases[name] if name in cases else extensions[name])
        for name in ("start 4786 fourfold witness", "five-pair fourfold witness", "four copies of one cycle")
    }
    for name, result in fourfold.items():
        original = recorded.get(name, beyond.get(name))
        assert result["signs"] == [original["sign"]]
    for name in ("start 4786 fourfold witness", "five-pair fourfold witness"):
        assert len({row[0] for row in fourfold[name]["counts by Euler count, orientability and components"]}) > 1
    repeated = fourfold["four copies of one cycle"]["counts by Euler count, orientability and components"]
    assert {row[1] for row in repeated} == {False, True}
    pinched = beyond["two-colourability restored by separating one pinched knot"]
    assert not pinched["two-colourable"] and pinched["separated two-colourable"]
    assert pinched["pinched knots"] == 1 and pinched["sign"] == pinched["separated sign"] == 0
    disjoint = beyond["two disjoint copies of the three-reader game"]
    assert disjoint["exactly two"] and disjoint["one cycle at every knot"]
    assert disjoint["separated components through cross pairs"] == 2 and disjoint["sign"] == 0

    # Compare only after reconstructing the choices and computing all metrics.
    archive = json.loads((HERE.parent / "fixtures.json").read_text())
    assert set(archive) == set(recorded)
    differences = []
    fields = 0
    for name, old in archive.items():
        for key, value in old.items():
            rebuilt = recorded[name][key]
            fields += 1
            if value != rebuilt:
                differences.append({"fixture": name, "field": key, "recorded": value, "recomputed": rebuilt})
    study_order = ("three-reader game", "ring game of five", "grown six-pair game", "census six-pair game",
                   "census eight-pair game", "census ten-pair game")
    result = {
        "reading": "A directly rebuilt finite check. Classical fixture names follow the cited study.",
        "source records": [str(path.relative_to(ROOT)) for path in (
            EARLIER / "cells.json", EARLIER / "shapes.json", EARLIER / "shapes_size_stress.json",
            EARLIER / "merge_fixtures.json", BIRTH_INPUTS, ENGINE / "starts.json", CENSUS,
        )],
        "independence": "The earlier independent referee supplies the marked word identities and holder lists for the named controls. The cross pairs, cycle orders, orientation, separation and commuting subcollections are recomputed.",
        "comparison": {"named fixtures": len(recorded), "recorded fields compared": fields, "differences": differences},
        "six games in prediction order": list(study_order),
        "six games all odd and minimal": all(
            recorded[name]["sign"] == 1 and recorded[name]["minimal"] for name in study_order
        ),
        "six games have no first merge": all(
            not any(recorded[name]["possible merges"].values()) for name in study_order
        ),
        "six game Euler counts": [recorded[name]["Euler count"] for name in study_order],
        "six game separated Euler counts": [recorded[name]["separated Euler count"] for name in study_order],
        "source positions": sources,
        "named fixtures": recorded,
        "extensions and controls": beyond,
        "fourfold attachments": fourfold,
        "grown even attachment control": grown_attachment_control(),
        "negative control": {"choice": lone_cycle, "mutual commutation": False,
                             "order parity before and after changing one reference": [order_before, order_after]},
    }
    (HERE / "fixture_audit.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({key: result[key] for key in ("comparison", "six game Euler counts",
                                                   "six game separated Euler counts")}))


if __name__ == "__main__":
    main()
